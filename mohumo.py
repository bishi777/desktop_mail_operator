import cloudscraper
import time
import requests
import json
import os
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
print(777)

load_dotenv()

CAPSOLVER_API_KEY = os.environ.get("CAPSOLVER_API_KEY", "")
SITE_KEY = os.environ.get("SITE_KEY", "")
TARGET_URL = "https://pcmax.jp/pcm/file.php?f=login_form"
CAPSOLVER_API_URL = "https://api.capsolver.com"
COOKIE_FILE = "cf_clearance.txt"

if not CAPSOLVER_API_KEY or not SITE_KEY:
    print("Warning: CAPSOLVER_API_KEY or SITE_KEY environment variables are not set.")
    print("Please set these variables in your environment or .env file.")
    print("Example .env file content:")
    print("CAPSOLVER_API_KEY=your_api_key_here")
    print("SITE_KEY=your_site_key_here")

def solve_turnstile_token():
    """
    Retrieve a Cloudflare Turnstile token from CapSolver.
    
    Returns:
        str: The token if successful, None otherwise.
    """
    print("Getting Turnstile token from CapSolver...")
    
    task_data = {
        "clientKey": CAPSOLVER_API_KEY,
        "task": {
            "type": "AntiTurnstileTaskProxyLess",
            "websiteURL": TARGET_URL,
            "websiteKey": SITE_KEY
        }
    }
    
    response = requests.post(f"{CAPSOLVER_API_URL}/createTask", json=task_data)
    task_result = response.json()
    
    if task_result.get("errorId") != 0:
        print(f"Error creating task: {task_result.get('errorDescription')}")
        return None
    
    task_id = task_result.get("taskId")
    print(f"Task created with ID: {task_id}")
    
    while True:
        response = requests.post(f"{CAPSOLVER_API_URL}/getTaskResult", 
                                json={"clientKey": CAPSOLVER_API_KEY, "taskId": task_id})
        result = response.json()
        
        if result.get("status") == "ready":
            token = result.get("solution", {}).get("token")
            print(f"Successfully obtained Turnstile token")
            return token
        
        elif result.get("status") == "failed":
            print(f"Task failed: {result.get('errorDescription')}")
            return None
            
        print("Waiting for token...")
        time.sleep(2)

def inject_token_and_submit(token):
    """
    Use cloudscraper to inject the token and submit the form.
    
    Args:
        token (str): The Turnstile token to inject.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    print("Creating cloudscraper session...")
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    try:
        print(f"Accessing {TARGET_URL}")
        response = scraper.get(TARGET_URL)
        
        if response.status_code != 200:
            print(f"Failed to access the page. Status code: {response.status_code}")
            return False
        
        print("Successfully accessed the page. Preparing form data...")
        
        form_data = {
            'cf-turnstile-response': token
        }
        
        submit_url = TARGET_URL
        
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for input_tag in soup.select('form input'):
                if input_tag.has_attr('name'):
                    name = input_tag['name']
                    if isinstance(name, str):
                        value = ''
                        if input_tag.has_attr('value'):
                            value = input_tag['value']
                            if isinstance(value, str):
                                form_data[name] = value
                        else:
                            form_data[name] = value
            
            form_tags = soup.find_all('form')
            if form_tags and len(form_tags) > 0:
                form_tag = form_tags[0]
                if hasattr(form_tag, 'attrs') and 'action' in form_tag.attrs:
                    action = form_tag.attrs['action']
                    if isinstance(action, str):
                        if action.startswith('http'):
                            submit_url = action
                        elif action.startswith('/'):
                            base_url = '/'.join(TARGET_URL.split('/')[:3])
                            submit_url = f"{base_url}{action}"
        except Exception as e:
            print(f"Error parsing form: {str(e)}")
        
        print(f"Form data prepared: {form_data}")
        print(f"Submitting form to: {submit_url}")
        
        response = scraper.post(submit_url, data=form_data, allow_redirects=True)
        
        print(f"Form submission status: {response.status_code}")
        
        cf_cookie = None
        print("Available cookies:")
        for name, value in scraper.cookies.items():
            print(f"  {name}: {value}")
            if name == 'cf_clearance':
                cf_cookie = value
                break
        
        if cf_cookie:
            print(f"Successfully obtained cf_clearance cookie")
            with open(COOKIE_FILE, 'w') as f:
                f.write(cf_cookie)
            print(f"Saved cf_clearance cookie to {COOKIE_FILE}")
            return True
        else:
            print("Failed to obtain cf_clearance cookie directly")
            
            if 'Set-Cookie' in response.headers:
                print("Checking Set-Cookie header")
                cookies_header = response.headers['Set-Cookie']
                print(f"Set-Cookie: {cookies_header}")
                cf_match = re.search(r'cf_clearance=([^;]+)', cookies_header)
                if cf_match:
                    cf_cookie = cf_match.group(1)
                    print(f"Extracted cf_clearance from headers: {cf_cookie}")
                    with open(COOKIE_FILE, 'w') as f:
                        f.write(cf_cookie)
                    print(f"Saved cf_clearance cookie to {COOKIE_FILE}")
                    return True
            
            for name, value in scraper.cookies.items():
                if name.startswith('cf_') or name.startswith('__cf'):
                    print(f"Saving Cloudflare-related cookie {name} as fallback")
                    with open(COOKIE_FILE, 'w') as f:
                        f.write(f"{name}={value}")
                    return True
            
            if 'SID' in scraper.cookies:
                print("Saving SID cookie as last resort")
                with open(COOKIE_FILE, 'w') as f:
                    f.write(f"SID={scraper.cookies['SID']}")
                return True
            
            print("No suitable cookies found, saving token as last resort")
            with open(COOKIE_FILE, 'w') as f:
                f.write(f"token={token}")
            return True
            
    except Exception as e:
        print(f"Error during token injection and submission: {str(e)}")
        return False

def main():
    token = solve_turnstile_token()
    
    if not token:
        print("Failed to get Turnstile token. Exiting.")
        return
    
    success = inject_token_and_submit(token)
    
    if success:
        print("Successfully bypassed Cloudflare Turnstile protection!")
    else:
        print("Failed to bypass Cloudflare Turnstile protection.")

if __name__ == "__main__":
    main()

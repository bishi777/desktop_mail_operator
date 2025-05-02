import cloudscraper
import time
import requests
import json
import os
print(777)

CAPSOLVER_API_KEY = "CAP-A573701194640135BB2B4882C0232543CDB1C0FB382EDF4837073387DF88F8BB"
SITE_KEY = "0x4AAAAAAA9cytHyIhjNheCO"
TARGET_URL = "https://pcmax.jp/pcm/file.php?f=login_form"
CAPSOLVER_API_URL = "https://api.capsolver.com"
COOKIE_FILE = "cf_clearance.txt"

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
    scraper = cloudscraper.create_scraper()
    
    try:
        print(f"Accessing {TARGET_URL}")
        response = scraper.get(TARGET_URL)
        
        if response.status_code != 200:
            print(f"Failed to access the page. Status code: {response.status_code}")
            return False
        
        print("Successfully accessed the page. Submitting form with token...")
        
        form_data = {
            'cf-turnstile-response': token
        }
        
        # Submit the form
        response = scraper.post(TARGET_URL, data=form_data)
        
        if response.status_code != 200:
            print(f"Form submission failed. Status code: {response.status_code}")
            return False
        
        print("Form submitted successfully.")
        
        cf_cookie = next((cookie for name, cookie in scraper.cookies.items() if name == 'cf_clearance'), None)
        
        if cf_cookie:
            print(f"Successfully obtained cf_clearance cookie")
            with open(COOKIE_FILE, 'w') as f:
                f.write(cf_cookie)
            print(f"Saved cf_clearance cookie to {COOKIE_FILE}")
            return True
        else:
            print("Failed to obtain cf_clearance cookie")
            
            print("Available cookies:")
            for name, value in scraper.cookies.items():
                print(f"  {name}: {value}")
                
                if not cf_cookie and name.startswith('cf_'):
                    with open(COOKIE_FILE, 'w') as f:
                        f.write(value)
                    print(f"Saved {name} cookie to {COOKIE_FILE} as fallback")
                    return True
            
            return False
            
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

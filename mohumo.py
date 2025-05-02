import cloudscraper
import time
import undetected_chromedriver as uc
import requests
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    Use undetected_chromedriver to inject the token into the Turnstile field and submit the form.
    
    Args:
        token (str): The Turnstile token to inject.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    print("Launching browser with undetected_chromedriver...")
    driver = uc.Chrome()
    
    try:
        print(f"Navigating to {TARGET_URL}")
        driver.get(TARGET_URL)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        
        inject_script = """
        (function() {
            // Create the textarea if it doesn't exist
            let textarea = document.querySelector('textarea[name="cf-turnstile-response"]');
            if (!textarea) {
                textarea = document.createElement('textarea');
                textarea.setAttribute('name', 'cf-turnstile-response');
                document.querySelector('form').appendChild(textarea);
            }
            
            // Focus the element
            textarea.focus();
            
            // Set the value
            textarea.value = arguments[0];
            
            // Dispatch events
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            textarea.dispatchEvent(new Event('change', { bubbles: true }));
            textarea.blur();
            
            // Submit the form
            document.querySelector('form').submit();
            
            return true;
        })();
        """
        
        result = driver.execute_script(inject_script, token)
        print(f"Token injection and form submission: {'Successful' if result else 'Failed'}")
        
        time.sleep(5)
        
        cf_cookie = next((cookie for cookie in driver.get_cookies() if cookie['name'] == 'cf_clearance'), None)
        
        if cf_cookie:
            print(f"Successfully obtained cf_clearance cookie")
            with open(COOKIE_FILE, 'w') as f:
                f.write(cf_cookie['value'])
            print(f"Saved cf_clearance cookie to {COOKIE_FILE}")
            return True
        else:
            print("Failed to obtain cf_clearance cookie")
            return False
            
    except Exception as e:
        print(f"Error during token injection and submission: {str(e)}")
        return False
    finally:
        driver.quit()

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

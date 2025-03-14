import time
from widget import happymail, func, pcmax
import time
import random
import os
import time
from selenium.webdriver.common.by import By

import os
import time
from DrissionPage import Chromium
from DrissionPage.errors import BrowserConnectError, PageDisconnectedError, ElementNotFoundError

user_data = func.get_user_data()

wait_time = 1.5
pcmax_data = user_data["pcmax"][4]
happy_data = user_data["happymail"][4]
name = pcmax_data["name"]
login_id = pcmax_data["login_id"]
login_pass = pcmax_data["password"]
print(f"{login_id}  {login_pass}  {name}")

h_name = happy_data["name"]
h_login_id = happy_data["login_id"]
h_login_pass = happy_data["password"]

func.change_tor_ip()

chromium = func.test_get_DrissionPage(None, False, max_retries=3)
# page = ChromiumPage()
# driver,wait = func.test_get_driver("", False)
# drission_page_pcmax_login(name, login_id, login_pass, page)
pcmax.drission_page_login(name, login_id, login_pass, chromium)
  

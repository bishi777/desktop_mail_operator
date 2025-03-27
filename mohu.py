import time
from widget import happymail, func, pcmax_drissionPage
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

page = func.test_get_DrissionPage(None, False, max_retries=3)

pcmax_drissionPage.login(name, login_id, login_pass, page)
print(888)
print(page.tab)

tab2 = page.new_tab("https://pcmax.jp")
print(page.tab)
pcmax_drissionPage.get_header_menu(page, "プロフ検索")
for i in range(2):
  profile_link_btns = page.ele(".profile_link_btn")
  print(777)
  print(len(profile_link_btns))
  for profile_link_btn in profile_link_btns:
    profile_link_btn.click()
    break

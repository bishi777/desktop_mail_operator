import time
from widget import happymail, func, pcmax_drissionPage
import time
import random
import os
import time
from selenium.webdriver.common.by import By
from DrissionPage.common import Settings
import os
import time
from DrissionPage import Chromium
from DrissionPage.errors import BrowserConnectError, PageDisconnectedError, ElementNotFoundError

user_data = func.get_user_data()

wait_time = 1.5
pcmax_data = user_data["pcmax"]
happy_data = user_data["happymail"]
pcmax_datas = pcmax_data[3:4]




func.change_tor_ip()
chromium = func.test_get_DrissionChromium(None, False, max_retries=3)
chromium.set.cookies.clear()
first_tab = True
for index, i in enumerate(pcmax_datas):
  print(777777)
  print(index)
  name = i["name"]
  login_id = i["login_id"]
  login_pass = i["password"]
  print(f"{login_id}  {login_pass}  {name}")
  if index == 0:
    tab1 = chromium.latest_tab  # アクティブなタブを取得
  else:
    tab1 = chromium.new_tab(new_context=True)
  
  pcmax_drissionPage.login(name, login_id, login_pass, tab1)
  tab2 = chromium.new_tab("https://pcmax.jp")
  # print(888)
  # print(chromium.tabs_count)
  # print(chromium.get_tabs())
  # pcmax_drissionPage.get_header_menu(tab1, "プロフ検索")



print(chromium.get_tabs())
# for i in range(2):
#   profile_link_btns = tab1.ele(".profile_link_btn")
#   print(777)
#   print(len(profile_link_btns))
#   for profile_link_btn in profile_link_btns:
#     profile_link_btn.click()
#     break

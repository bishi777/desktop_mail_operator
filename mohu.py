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
pcmax_datas = pcmax_data[1:3]
chromiums = []  # ← 複数のChromiumをここに格納する
PROFILE_BASE = "./profiles"
os.makedirs(PROFILE_BASE, exist_ok=True)
headress = False
func.change_tor_ip()

# chromium.set.cookies.clear()
tabs = {}
for index, i in enumerate(pcmax_datas):
  name = i["name"]
  login_id = i["login_id"]
  login_pass = i["password"]
  print(f"{login_id}  {login_pass}  {name}")
  # プロファイルごとの保存先
  user_profile_dir = os.path.join(PROFILE_BASE, name)
  os.makedirs(user_profile_dir, exist_ok=True)
  print(666)
  print(user_profile_dir)
  # 🔽 Chromiumを別インスタンスとして起動
  chromium = func.test_get_DrissionChromium(user_profile_dir, headress, max_retries=3)
  chromiums.append(chromium)  # ← ここで複数保持
  tab1 = chromium.latest_tab  # アクティブなタブを取得
  pcmax_drissionPage.login(name, login_id, login_pass, tab1)
  tab2 = chromium.new_tab("https://pcmax.jp")
  tabs[name] = {"tab1":tab1, "tab2":tab2}
print(777)
print("\nすべてのChromiumインスタンス:")
for c in chromiums:
    print(f"browser_id: {c.latest_tab.browser}, tabs: {[t.tab_id for t in c.get_tabs()]}")

# print(tabs)
# print(888)
# print(chromium.tabs_count)
# for i in range(2):
#   profile_link_btns = tab1.ele(".profile_link_btn")
#   print(777)
#   print(len(profile_link_btns))
#   for profile_link_btn in profile_link_btns:
#     profile_link_btn.click()
#     break

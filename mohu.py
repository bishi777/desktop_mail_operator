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
import traceback

user_data = func.get_user_data()
wait_time = 1.5
pcmax_data = user_data["pcmax"]
happy_data = user_data["happymail"]
pcmax_datas = pcmax_data[3:4]
arrangement_list = [] 
PROFILE_BASE = "./profiles"
os.makedirs(PROFILE_BASE, exist_ok=True)
headress = False
func.change_tor_ip()

# chromium.set.cookies.clear()
for index, i in enumerate(pcmax_datas):
  dict = {}
  name = i["name"]
  login_id = i["login_id"]
  login_pass = i["password"]
  fst_message = i["fst_mail"]
  # print(f"{login_id}  {login_pass}  {name}")
  # プロファイルごとの保存先
  user_profile_dir = os.path.join(PROFILE_BASE, name)
  os.makedirs(user_profile_dir, exist_ok=True)
  # 🔽 Chromiumを別インスタンスとして起動
  chromium = func.test_get_DrissionChromium(user_profile_dir, headress, max_retries=3)
  tab1 = chromium.latest_tab  # アクティブなタブを取得
  pcmax_drissionPage.login(name, login_id, login_pass, tab1)
  tab2 = chromium.new_tab("https://pcmax.jp")
  dict["name"] = name
  dict["fst_message"] = fst_message
  dict["chromium"] = chromium
  arrangement_list.append(dict)
for c in arrangement_list:
  send_cnt = 0
  try:
    tab1 = c["chromium"].get_tabs()[1]
    # pcmax_drissionPage.set_fst_mail(c["name"], c["chromium"], tab1, c["fst_message"], send_cnt)
    time.sleep(1.5)
    tab2 = c["chromium"].get_tabs()[0]
    pcmax_drissionPage.check_mail(tab2)
  except Exception as e:
    print(f"❌ ブラウザ  の操作でエラー: {e}")
    traceback.print_exc() 
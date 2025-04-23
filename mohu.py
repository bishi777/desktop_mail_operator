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
mailserver_address = user_data['user'][0]['gmail_account']
mailserver_password = user_data['user'][0]['gmail_account_password']
receiving_address = user_data['user'][0]['user_email']
pcmax_data = user_data["pcmax"]
happy_data = user_data["happymail"]
pcmax_datas = pcmax_data[1:8]
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
  
  # print(f"{login_id}  {login_pass}  {name}")
  # プロファイルごとの保存先
  user_profile_dir = os.path.join(PROFILE_BASE, name)
  os.makedirs(user_profile_dir, exist_ok=True)
  # 🔽 Chromiumを別インスタンスとして起動
  chromium = func.test_get_DrissionChromium(user_profile_dir, headress, max_retries=3)
  tab1 = chromium.latest_tab  # アクティブなタブを取得

  login_flug = pcmax_drissionPage.login(name, login_id, login_pass, tab1)
  if not login_flug:
    continue
  # tab2 = chromium.new_tab("https://pcmax.jp")
  dict["login_id"] = login_id
  dict["login_pass"] = login_pass
  dict["name"] = name
  dict["gmail_address"] = i["mail_address"]
  dict["gmail_password"] = i["gmail_password"]
  dict["fst_message"] = i["fst_mail"]
  dict["second_message"] = i["second_message"]
  dict["condition_message"] = i["condition_message"]
  dict["chromium"] = chromium
  arrangement_list.append(dict)

if arrangement_list != []:
  while True:
    for c in arrangement_list:
      send_cnt = 2
      try:
        tab1 = c["chromium"].get_tabs()[0]
        pcmax_drissionPage.set_fst_mail(c["name"], c["chromium"], tab1, c["fst_message"], send_cnt)
        time.sleep(1.5)   
        print("新着メールチェック開始")     
        pcmax_drissionPage.check_mail(c["name"], tab1, c["login_id"], c["login_pass"], c["gmail_address"], c["gmail_password"], c["fst_message"], c["second_message"], c["condition_message"], mailserver_address, mailserver_password)
        tab1.get("https://pcmax.jp/pcm/member.php")
      except Exception as e:
        print(f"❌ ブラウザ  の操作でエラー: {e}")
        traceback.print_exc() 
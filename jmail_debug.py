from widget import func, jmail
import signal
import sys
from selenium.webdriver.support.ui import WebDriverWait
import time
import requests
import traceback
from datetime import datetime
from selenium.common.exceptions import TimeoutException

user_data = func.get_user_data()
wait_time = 1.5
mailserver_address = user_data['user'][0]['gmail_account']
mailserver_password = user_data['user'][0]['gmail_account_password']
receiving_address = user_data['user'][0]['user_email']
pcmax_datas = user_data["jmail"]
post_areas = ["神奈川", "千葉", "埼玉", "栃木", "静岡"]
base_path = "chrome_profiles/j_footprint"
api_url = "https://meruopetyan.com/api/update-submitted-users/"
# api_url = "http://127.0.0.1:8000/api/update-submitted-users/"



def jmail_debug(headless):
  repost_flug = False
  user_data = func.get_user_data()
  jmail_datas = user_data["jmail"]
  
  drivers = jmail.start_jmail_drivers(jmail_datas, headless, base_path)
  while True:
    start_loop_time = time.time()
    now = datetime.now()
    if drivers == {}:
      break
    for name, data in drivers.items():
      print(f"  📄 ---------- {name} ------------")
      driver = drivers[name]["driver"]
      wait = drivers[name]["wait"]
      try:
        submitted_users = jmail.check_mail(name,data, driver, wait)
      except TimeoutException as e:
        print("新着メールチェックTimeoutException")
        driver.refresh()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2) 
      except Exception as e:
        print(f"❌ {name} エラー発生:", e)
        traceback.print_exc()
        continue
      # # 足あと返し
      # try:
      #   jmail.return_footprint(data,driver,wait,submitted_users)
      # except TimeoutException as e:
      #   print(f"足跡返し　TimeoutException")
      #   driver.refresh()
      # 足あと付け
      # try:
      #   jmail.make_footprints( driver, wait)
      # except TimeoutException as e:
      #   print(f"足跡付け　TimeoutException")
      #   driver.refresh()
      #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      #   time.sleep(2)
      
      #   if repost_flug:
      #     driver.refresh()
      #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      #     time.sleep(2)
      #     jmail.re_post(data, post_areas, driver,wait)
      #     repost_flug = False
      #     driver.refresh()
      #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      #     time.sleep(2)
      # except Exception as e:
      #   print(f"❌ {name} エラー発生:", e)
      #   traceback.print_exc()
      #   continue
      # 送信履歴ユーザー更新
      print(777)
      print(f"{drivers[name]['login_id']}:{drivers[name]['password']}:{submitted_users}")
      payload = {
        "login_id": drivers[name]["login_id"],
        "password": drivers[name]["password"],
        "submitted_users": submitted_users
      }
      try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
          print(f"✅ {name} 送信済ユーザー更新成功:", response.json())
        else:
          print(f"❌ {name} 送信済ユーザー更新失敗（ステータス: {response.status_code}）:", response.json())
      except requests.exceptions.RequestException as e:
        print("⚠️ 通信エラー:", e)
        traceback.print_exc()  
    elapsed_time = time.time() - start_loop_time
    while elapsed_time < 600:
      time.sleep(20)
      elapsed_time = time.time() - start_loop_time
      print(f"待機中~~ {elapsed_time} ")
    print("<<<<<<<<<<<<<ループ折り返し>>>>>>>>>>>>>>>>>>>>>")
    elapsed_time = time.time() - start_loop_time
    minutes, seconds = divmod(int(elapsed_time), 60)
    print(f"タイム: {minutes}分{seconds}秒")  
    if 6 == now.hour or 20 == now.hour:
      repost_flug = True
    else:
      repost_flug = False
    
if __name__ == '__main__':
  headless = True
  jmail_debug(headless)

from widget import func, jmail
import signal
import sys
from selenium.webdriver.support.ui import WebDriverWait
import time
import requests
import traceback
from datetime import datetime
from selenium.common.exceptions import TimeoutException
import random

user_data = func.get_user_data()
wait_time = 1.5
user_mail_info = [
  user_data['user'][0]['user_email'],
  user_data['user'][0]['gmail_account'],
  user_data['user'][0]['gmail_account_password'],
  ]
spare_mail_info = [
  "siliboco68@gmail.com",
  "gifopeho@kmail.li",
  "akkcxweqzdplcymh",
]

pcmax_datas = user_data["jmail"]
post_areas = ["神奈川", "千葉", "埼玉", "栃木", "静岡"]
base_path = "chrome_profiles/j_footprint"
api_url = "https://meruopetyan.com/api/update-submitted-users/"
# api_url = "http://127.0.0.1:8000/api/update-submitted-users/"



def jmail_debug(headless):
  repost_flug = True
  user_data = func.get_user_data()
  jmail_datas = user_data["jmail"]
  chara_name_list = [data["name"] for data in jmail_datas]
  drivers = jmail.start_jmail_drivers(jmail_datas, headless, base_path)
  
  while True:
    mail_info = random.choice([user_mail_info, spare_mail_info])
    start_loop_time = time.time()
    now = datetime.now()
    if drivers == {}:
      break
    for name, data in drivers.items():
      print(f"  📄 ---------- {name} ------------")
      driver = drivers[name]["driver"]
      wait = drivers[name]["wait"]
      try:
        submitted_users = jmail.check_mail(name,data, driver, wait, mail_info)
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
      # print(f"{drivers[name]['login_id']}:{drivers[name]['password']}:{submitted_users}")
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
    
    if (8 <= now.hour <= 9) or (20 <= now.hour <= 21):
      if repost_flug:
        if chara_name_list:
          repost_chara = chara_name_list.pop()
          # 掲示板投稿
          for name, data in drivers.items():
            if name == repost_chara:            
              print(f"📢 再投稿: {name}")
              driver = drivers[name]["driver"]
              wait = drivers[name]["wait"]
              jmail.re_post(data, post_areas, driver,wait)
              time.sleep(5)
              driver.refresh()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
              break
        else:
          repost_flug = False
          chara_name_list = [data["name"] for data in jmail_datas]   
    else:
      repost_flug = True

    if 17 <= now.hour <= 18:
      if name == "ゆっこ":
        if repost_flug:
          if chara_name_list:
            repost_chara = chara_name_list.pop()
            # 掲示板投稿
            for name, data in drivers.items():
              if name == repost_chara:            
                print(f"📢 再投稿: {name}")
                driver = drivers[name]["driver"]
                wait = drivers[name]["wait"]
                jmail.re_post(data, post_areas, driver,wait)
                time.sleep(5)
                driver.refresh()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(2)
                break
          else:
            repost_flug = False
            chara_name_list = [data["name"] for data in jmail_datas]   
      else:
        repost_flug = True

    elapsed_time = time.time() - start_loop_time
    while elapsed_time < 600:
      time.sleep(20)
      elapsed_time = time.time() - start_loop_time
      print(f"待機中~~ {elapsed_time} ")
    print("<<<<<<<<<<<<<ループ折り返し>>>>>>>>>>>>>>>>>>>>>")
    elapsed_time = time.time() - start_loop_time
    minutes, seconds = divmod(int(elapsed_time), 60)
    print(f"タイム: {minutes}分{seconds}秒")  
    
    
if __name__ == '__main__':
  headless = False
  jmail_debug(headless)

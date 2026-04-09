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
  "gifopeho@kmail.li",
  "siliboco68@gmail.com",
  "akkcxweqzdplcymh",
]
post_areas = ["神奈川", "千葉", "埼玉", "栃木", "静岡"]
base_path = "chrome_profiles/j_footprint"
api_url = "https://meruopetyan.com/api/update-submitted-users/"
# api_url = "http://127.0.0.1:8000/api/update-submitted-users/"
rf_flug = True

def _get_fst_time_slot(hour):
  """現在の時刻がfst送信対象の時間帯ならスロット名を返す"""
  if 6 <= hour < 8:
    return "morning"
  elif 18 <= hour < 20:
    return "evening"
  elif 20 <= hour < 22:
    return "night"
  return None

def _is_send_day(send_on="even"):
  """今日がfst送信日かどうか（1日おき）
  send_on: "even"=偶数日に送信, "odd"=奇数日に送信
  """
  yday = datetime.now().timetuple().tm_yday
  if send_on == "odd":
    return yday % 2 == 1
  return yday % 2 == 0

def jmail_debug(headless, send_on="even"):
  repost_flug = True
  user_data = func.get_user_data()
  jmail_datas = user_data["jmail"]
  chara_name_list = [data["name"] for data in jmail_datas]

  drivers = jmail.start_jmail_drivers(jmail_datas, headless, base_path)
  loop_cnt = 0
  # キャラごと・時間帯ごとのfst送信済みフラグ {name: {"morning": "2026-04-09", ...}}
  fst_sent_today = {}
  while True:
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    if (7 <= now.hour <= 23):
      mail_info = random.choice([user_mail_info, spare_mail_info])
      start_loop_time = time.time()
      if drivers == {}:
        break
      for chara_idx, (name, data) in enumerate(drivers.items()):
        now = datetime.now()
        print(f"  📄 ---------- {name} ------------{now.strftime('%Y-%m-%d %H:%M:%S')}")
        driver = drivers[name]["driver"]
        wait = drivers[name]["wait"]
        try:
          young_submitted_users, submitted_users  = jmail.check_mail(name,data, driver, wait, mail_info)
        except TimeoutException as e:
          print("新着メールチェックTimeoutException")
          driver.refresh()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
        except Exception as e:
          print(f"❌ {name} エラー発生:", e)
          traceback.print_exc()
          continue
        print(f"ループ回数: {loop_cnt}")
        # fst_message送信（1日おき、6-8時/18-20時/20-22時に各1回、キャラごとにずらす）
        time_slot = _get_fst_time_slot(now.hour)
        should_send_fst = False
        # "even" or "odd"を指定  
        send_on = "even"  
        # send_on = "odd"  
        if _is_send_day(send_on) and time_slot:
          if name not in fst_sent_today:
            fst_sent_today[name] = {}
          # 日付が変わったらリセット
          for slot in list(fst_sent_today[name].keys()):
            if fst_sent_today[name][slot] != today_str:
              del fst_sent_today[name][slot]
          # この時間帯で未送信ならキャラごとにずらして実行
          if time_slot not in fst_sent_today[name]:
            # 時間帯内でキャラごとにずらす（ループごとに1キャラずつ）
            already_sent_count = sum(1 for n, slots in fst_sent_today.items() if time_slot in slots and slots[time_slot] == today_str)
            if already_sent_count == chara_idx:
              should_send_fst = True

        if should_send_fst:
          try:
            fst_message = data.get('fst_message', '')
            image_path = data.get('chara_image', '')
            sent_to, submitted_users = jmail.score_and_send_fst_message(
              name, driver, wait, fst_message, image_path,
              submitted_users=submitted_users,
              user_check_cnt=random.randint(7, 11)
            )
            if sent_to:
              print(f"  [{name}] fst送信完了: {sent_to}")
            fst_sent_today[name][time_slot] = today_str
          except Exception as e:
            print(f"  [{name}] fst送信エラー: {e}")
            traceback.print_exc()
        elif time_slot and not _is_send_day(send_on):
          pass  # 送信しない日
          
        # 送信履歴ユーザー更新
        # print(f"{drivers[name]['login_id']}:{drivers[name]['password']}:{submitted_users}")
        payload = {
          "login_id": drivers[name]["login_id"],
          "password": drivers[name]["password"],
          "submitted_users": submitted_users,
          "young_submitted_users": young_submitted_users,
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

      
      # # if True:
      #   if repost_flug:
      #     if chara_name_list:
      #       print(chara_name_list)
      #       repost_chara = chara_name_list.pop()
      #       print(chara_name_list)
      #       # 掲示板投稿
      #       for name, data in drivers.items():
      #         if name == repost_chara:            
      #           print(f"📢 再投稿: {name}")
      #           driver = drivers[name]["driver"]
      #           wait = drivers[name]["wait"]
      #           jmail.re_post(data, post_areas, driver,wait)
      #           time.sleep(5)
      #           driver.refresh()
      #           wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      #           time.sleep(2)
      #           break
            
      #     else:
      #       repost_flug = False
      #       chara_name_list = [data["name"] for data in jmail_datas]   
      # else:
      #   repost_flug = True

      
      loop_cnt += 1
      elapsed_time = time.time() - start_loop_time
      wait_cnt = 0
      while elapsed_time < random.randint(580,860):
        time.sleep(20)
        elapsed_time = time.time() - start_loop_time
        if wait_cnt % 3 == 0:
          print(f"待機中~~ {elapsed_time} ")
        wait_cnt += 1
      print("<<<<<<<<<<<<<ループ折り返し>>>>>>>>>>>>>>>>>>>>>")
      elapsed_time = time.time() - start_loop_time
      minutes, seconds = divmod(int(elapsed_time), 60)
      print(f"タイム: {minutes}分{seconds}秒")  
     
if __name__ == '__main__':
  headless = False
  jmail_debug(headless)

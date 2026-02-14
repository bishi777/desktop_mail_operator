from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import random
import time
from selenium.webdriver.common.by import By
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from selenium.webdriver.support.ui import WebDriverWait
import traceback
from widget import happymail, func
import sqlite3
from selenium.webdriver.chrome.service import Service
from datetime import timedelta
from tkinter import messagebox
from selenium.common.exceptions import NoSuchWindowException
import signal
import shutil
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from urllib3.exceptions import ReadTimeoutError
from datetime import datetime
import settings

user_data = func.get_user_data()
happy_info = user_data["happymail"]
headless = False
# リストを2つに分割する
n = len(happy_info)  
half = n // 2
first_half = happy_info
# first_half = happy_info[half:]  # 後半
# profile_path = "chrome_profiles/h_footprint"
# drivers = {}
service = Service(ChromeDriverManager().install())  # Chrome v141に合うDriverを取得
options = Options()
options.add_experimental_option("debuggerAddress", f"127.0.0.1:{settings.happymail_drivers_port}")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)
handles = driver.window_handles
mailaddress = user_data['user'][0]['gmail_account']
gmail_password = user_data['user'][0]['gmail_account_password']
receiving_address = user_data['user'][0]['user_email']

last_reset_hour = None  
send_flug = True

if mailaddress and gmail_password and receiving_address:
  user_mail_info = [
    receiving_address, mailaddress, gmail_password, 
  ]
spare_mail_info = [
  "ryapya694@ruru.be",  
  "siliboco68@gmail.com",
  "akkcxweqzdplcymh",
]

try:
  # drivers = happymail.start_the_drivers_login(spare_mail_info, first_half, headless, profile_path, True)
  # 足跡付け、チェックメール　ループ
  return_foot_counted = 0
  matching_daily_limit = 77
  returnfoot_daily_limit = 0
  total_daily_limit = 77
  oneday_total_match = 77
  oneday_total_returnfoot = 0
  last_reset_date = (datetime.now() - timedelta(days=1)).date()
  report_dict = {}
  mf_cnt = random.randint(5,9)
  mf_type_cnt = 2
  execution_flag = True
  for i in first_half:
    report_dict[i["name"]] = [0, send_flug, []]
  loop_cnt = 1
  # schedulerを初期化
  from widget.human_scheduler import HumanScheduler
  scheduler = HumanScheduler()

  while True:
    if scheduler.is_active(): 
    # if False:
      if execution_flag:
        mail_info = random.choice([user_mail_info, spare_mail_info])
        start_loop_time = time.time()
        now = datetime.now()    
        for idx, handle in enumerate(handles): 
          for index, i in enumerate(first_half):

            driver.switch_to.window(handle)
            time.sleep(1)
            current_url = driver.current_url
            if not "happymail.co.jp/app/html/mbmenu.php" in current_url:
              driver.get("https://happymail.co.jp/app/html/mbmenu.php")
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(0.5)
            name_ele = driver.find_elements(By.CLASS_NAME, value="ds_user_display_name")
            if name_ele:
              name = name_ele[0].text
            else:
              print("名前の取得に失敗しました")
              print(driver.current_url)
              continue
            if name == i["name"]:
            # if True:
              
              print(f"  📄 ---------- {name} ------------{now.strftime('%Y-%m-%d %H:%M:%S')}")
              # if "きりこ" != name:
              #   total_daily_limit = 10
              #   continue
              # else:
              #   total_daily_limit = 10
              happymail_new_list = []
              top_image_check = None
              happymail_new = None
              login_id = i["login_id"]
              password = i["password"]
              return_foot_message = i["return_foot_message"]
              fst_message = i["fst_message"]
              post_return_message = i["post_return_message"]
              second_message = i["second_message"]
              conditions_message = i["condition_message"]
              confirmation_mail = i["confirmation_mail"]
              return_foot_img = i["chara_image"]
              gmail_address = i["mail_address"]
              gmail_password = i["gmail_password"]
              matching_cnt = 1
              type_cnt = 1
              return_foot_cnt = 1
              return_check_cnt = 2
              # print("変更前:", func.get_current_ip())
              # func.change_tor_ip()
              # time.sleep(6)
              # print("変更後:", func.get_current_ip())
            
              # 新着メールチェック
              try:
                happymail_new = happymail.multidrivers_checkmail(name, driver, wait, login_id, password, return_foot_message, fst_message, post_return_message, second_message, conditions_message, confirmation_mail,return_foot_img, gmail_address, gmail_password, return_check_cnt)
                
                if happymail_new:
                  print(777)
                  print(happymail_new)
                  happymail_new_list.extend(happymail_new)
                if happymail_new_list:
                  title = f"happy新着 {name}"
                  text = ""
                  img_path = None
                  for new_mail in happymail_new_list:
                    text = text + new_mail + ",\n"
                    if "警告" in text or "NoImage" in text or "利用" in text :
                      if mail_info:
                        img_path = f"{i['name']}_ban.png"
                        driver.save_screenshot(img_path)
                        # 圧縮（JPEG化＋リサイズ＋品質調整）
                        img_path = func.compress_image(img_path)  # 例: screenshot2_compressed.jpg ができる
                        title = "メッセージ"
                        text = f"ハッピーメール {i['name']}:{i['login_id']}:{i['password']}:  {text}"   
                  # メール送信
                  if mail_info:
                    print(666)
                    func.send_mail(text, mail_info, title, img_path)
                  else:
                    print("通知メールの送信に必要な情報が不足しています")
                    print(f"{mailaddress}   {gmail_password}  {receiving_address}")
              except NoSuchWindowException:
                pass
              except ReadTimeoutError as e:
                print("🔴 ページの読み込みがタイムアウトしました:", e)
                driver.refresh()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              except Exception as e:
                print(traceback.format_exc())
              # 作成して三日たってないキャラリスト
              # if name  in ["りな", "いおり"]:
              #   continue
              # マッチング返し、
              if loop_cnt ==1:
                send_cnt = 1
              elif loop_cnt % 10 == 0:
                send_cnt = 1
              elif loop_cnt % 5 == 0:
                send_cnt = 1
              else:
                send_cnt = 0
                
              print(f"{loop_cnt}回目のループ処理 send_cnt: {send_cnt} ")
              if send_cnt:
                # print(f"{name}の送信数 {report_dict[name][0]} ")
                # print(f"返しフラグ {report_dict[name][1]} ")
                if report_dict[name][1] and "利用できません" not in happymail_new_list:
                  try:
                    return_foot_counted = happymail.return_footpoint(name, driver, wait, return_foot_message, matching_cnt, type_cnt, return_foot_cnt, return_foot_img, fst_message, matching_daily_limit, returnfoot_daily_limit, oneday_total_match, oneday_total_returnfoot, send_cnt)
                    # print(return_foot_counted)
                    # [matching_counted, type_counted, return_cnt, matching_limit_flug, returnfoot_limit_flug]
                    # report_dict[name][0] = report_dict[name][0] + return_foot_counted[0] + return_foot_counted[2]   
                    # report_dict[name][2].extend(return_foot_counted[5])
                    # if total_daily_limit <= report_dict[name][0]:
                    #   print("午前中のマッチング返しの上限に達しました。")
                    #   limit_text = f"送信数：{report_dict[name][0]} \n"
                    #   func.send_mail(f"マッチング、足跡返しの上限に達しました。 送信数 {report_dict[name][0]}\n{name}\n{login_id}\n{password}", mail_info, f"ハッピーメール {name} 送信数 {report_dict[name][0]}")
                    #   report_dict[name][1] = False
                      
                  except Exception as e:
                    print(f"{name}")
                    print(traceback.format_exc())
                    func.send_error(f"{name}", traceback.format_exc())
              # 足跡付け
              try:
                happymail.mutidriver_make_footprints(name, login_id, password, driver, wait, mf_cnt, mf_type_cnt)
              except NoSuchWindowException:
                print(f"NoSuchWindowExceptionエラーが出ました, {e}")
                pass
              except ReadTimeoutError as e:
                print("🔴 ページの読み込みがタイムアウトしました:", e)
                driver.refresh()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              except Exception as e:
                print(traceback.format_exc())
            # elif index == 1:　2個目のタブの処理があれば記載
              if top_image_check:
                happymail_new_list.append(top_image_check)  
        # ループの間隔を調整
        elapsed_time = time.time() - start_loop_time  # 経過時間を計算する   
        wait_cnt = 0

        
        # ７時と２０時、かつ直前に初期化されていない場合
        # if (now.hour == 7 or now.hour == 20) and now.hour != last_reset_hour:
        #   last_reset_hour = now.hour  # 初期化済みとして記録
        #   for i in first_half:
        #     report_dict[i["name"]] = [0, True, []]
        if now.hour == 7 and now.hour != last_reset_hour:
          last_reset_hour = now.hour  # 初期化済みとして記録
          for i in first_half:
            report_dict[i["name"]] = [0, True, []]
        if now.hour == 20 and now.hour != last_reset_hour:
          last_reset_hour = now.hour  # 初期化済みとして記録
          for i in first_half:
            # if i["name"] == "すい":   
              report_dict[i["name"]] = [0, True, []]
      

        # 待機時間をSchedulerから取得
        sleep_duration =  scheduler.get_sleep_duration()
        while elapsed_time < sleep_duration: # 元の720から変更
          time.sleep(10) # 30から変更
          elapsed_time = time.time() - start_loop_time  # 経過時間を計算する
          if wait_cnt % 2 == 0:
            print(f"待機中~~ {elapsed_time:.1f}/{sleep_duration:.1f} ")
          wait_cnt += 1
        loop_cnt += 1
    else:
      # HumanSchedulerが非アクティブ（睡眠中または休憩中）の場合
      # ループを回し続けるため、少し待機して再確認
      time.sleep(60)
except KeyboardInterrupt:
  # Ctrl+C が押された場合
  print("プログラムが Ctrl+C により中断されました。")
  sys.exit(0)
except Exception as e:
  # 予期しないエラーが発生した場合
  sys.exit(0)
  print("エラーが発生しました:", e)
  traceback.print_exc()
finally:
  # 正常終了時・エラー終了時を問わず、最後に WebDriver を閉じる
  # print('finalyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
  traceback.print_exc() 
  sys.exit(0)

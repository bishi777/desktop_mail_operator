import tkinter as tk
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


user_data = func.get_user_data()
happy_info = user_data["happymail"]
headless = False

# リストを2つに分割する
n = len(happy_info)  
half = n // 2
first_half = happy_info
# first_half = happy_info[half:]  # 後半
profile_path = "chrome_profiles/h_footprint"
drivers = {}
mailaddress = user_data['user'][0]['gmail_account']
gmail_password = user_data['user'][0]['gmail_account_password']
receiving_address = user_data['user'][0]['user_email']
mail_info = None
if mailaddress and gmail_password and receiving_address:
  mail_info = [
    receiving_address, mailaddress, gmail_password, 
  ]
try:
  drivers = happymail.start_the_drivers_login(mail_info, first_half, headless, profile_path, True)
      
  # 足跡付け、チェックメール　ループ
  return_foot_counted = 0
  matching_daily_limit = 777
  returnfoot_daily_limit = 777
  total_daily_limit = 10
  oneday_total_match = 0
  oneday_total_returnfoot = 0
  returnfoot_flug = True
  last_reset_date = (datetime.now() - timedelta(days=1)).date()

  while True:
    start_loop_time = time.time()
    if drivers == {}:
      break
    now = datetime.now()
    # 7時または20時、かつ直前に初期化されていない場合
    if now.hour in [7, 20] and now.hour != last_reset_hour:
      oneday_total_match = 0
      oneday_total_returnfoot = 0
      returnfoot_flug = True
      last_reset_hour = now.hour  # 初期化済みとして記録
   
    for name, data in drivers.items():
      happymail_new_list = []
      top_image_check = None
      happymail_new = None
      driver = drivers[name]["driver"]
      wait = drivers[name]["wait"]
      tabs = driver.window_handles
      login_id = drivers[name]["login_id"]
      password = drivers[name]["password"]
      return_foot_message = drivers[name]["return_foot_message"]
      fst_message = drivers[name]["fst_message"]
      conditions_message = drivers[name]["conditions_message"]
      return_foot_img = drivers[name]["mail_img"]
      matching_cnt = 1
      type_cnt = 1
      return_foot_cnt = 1
      
      for index, tab in enumerate(tabs):
        driver.switch_to.window(tab) 
        # print(f"現在のタブ: {index + 1},")
        if index  == 0:
          # 新着メールチェック
          try:
            happymail_new = happymail.multidrivers_checkmail(name, driver, wait, login_id, password, return_foot_message, fst_message, conditions_message)
            if happymail_new:
              happymail_new_list.extend(happymail_new)
            if happymail_new_list:
              title = "新着メッセージ"
              text = ""
              for new_mail in happymail_new_list:
                text = text + new_mail + ",\n"
                if "警告" in text or "NoImage" in text or "利用" in text :
                  title = "メッセージ"
              # メール送信
              smtpobj = None
              if mail_info:
                func.send_mail(text, mail_info, title)
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
          # マッチング返し、足跡返し
          if returnfoot_flug:
            try:
              return_foot_counted = happymail.return_footpoint(name, driver, wait, return_foot_message, matching_cnt, type_cnt, return_foot_cnt, return_foot_img, fst_message, matching_daily_limit, returnfoot_daily_limit, oneday_total_match, oneday_total_returnfoot)
              # print(return_foot_counted)
              # [matching_counted, type_counted, return_cnt, matching_limit_flug, returnfoot_limit_flug]
              oneday_total_match += return_foot_counted[0]
              oneday_total_returnfoot += return_foot_counted[2]
              print(f"本日のマッチング数: {oneday_total_match}, 足跡返し数: {oneday_total_returnfoot}")
              # if name == "ハル":
              #   total_daily_limit = 25
              if total_daily_limit <= oneday_total_match + oneday_total_returnfoot:
                print("マッチング、足跡返しの上限に達しました。")
                limit_text = f"マッチング返し：{oneday_total_match} \n足跡返し：{oneday_total_returnfoot}"
                func.send_error(f"{name} マッチング、足跡返しの上限に達しました。", limit_text)
                returnfoot_flug = False
                
            except Exception as e:
              print(f"足跡返しエラー{name}")
              print(traceback.format_exc())
              func.send_error(f"足跡返しエラー{name}", traceback.format_exc())

            try:
              happymail.mutidriver_make_footprints(name, login_id, password, driver, wait)
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
    while elapsed_time < 720:
      time.sleep(30)
      elapsed_time = time.time() - start_loop_time  # 経過時間を計算する
      # print(f"待機中~~ {elapsed_time} ")
except KeyboardInterrupt:
  # Ctrl+C が押された場合
  print("プログラムが Ctrl+C により中断されました。")
  func.close_all_drivers(drivers)
  os._exit(0)
except Exception as e:
  # 予期しないエラーが発生した場合
  func.close_all_drivers(drivers)
  print("エラーが発生しました:", e)
  traceback.print_exc()
finally:
  # 正常終了時・エラー終了時を問わず、最後に WebDriver を閉じる
  # print('finalyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
  # print(drivers)
  func.close_all_drivers(drivers)
  os._exit(0)

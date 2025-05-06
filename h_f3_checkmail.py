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
n = len(happy_info)  # dataはリスト
half = n // 2
# first_half = happy_info[:half]  # 前半
# first_half = happy_info[6:8]  
first_half = happy_info

profile_path = "chrome_profiles/h_footprint"
drivers = {}
mailaddress = user_data['user'][0]['gmail_account']
gmail_password = user_data['user'][0]['gmail_account_password']
receiving_address = user_data['user'][0]['user_email']
mail_info = None
send_messages_list = []

if mailaddress and gmail_password and receiving_address:
  mail_info = [
    receiving_address, mailaddress, gmail_password, 
  ]
try:
  drivers = happymail.start_the_drivers_login(mail_info, first_half, headless, profile_path, True)
  # タブを切り替えて操作
  # tab1で足跡付け, tab2でチェックメールSET
  for name, data in drivers.items():
    driver = drivers[name]["driver"]
    wait = drivers[name]["wait"]
    tabs = driver.window_handles
    login_id = drivers[name]["login_id"]
    password = drivers[name]["password"]
    for index, tab in enumerate(tabs):
      driver.switch_to.window(tab)
      if index + 1 == 1:
        nav_flug = happymail.nav_item_click("プロフ検索", driver, wait)
        if not nav_flug:
          break
        happymail.set_mutidriver_make_footprints(drivers[name]["driver"], drivers[name]["wait"])
        time.sleep(2)  
    send_messages_list.append({"名前": name, "マッチング総数": 0, "足跡返し総数": 0, "合計": 0})
  # 足跡付け、チェックメール　ループ
  loop_cnt = 1
  sent_cnt = 0
  daily_limit = 111
  last_sent_date = datetime.now().date()
  while True:
    if drivers == {}:
      break
    for name, data in drivers.items():
      happymail_new_list = []
      top_image_check = None
      happymail_new = None
      driver = drivers[name]["driver"]
      wait = drivers[name]["wait"]
      login_id = drivers[name]["login_id"]
      password = drivers[name]["password"]
      tabs = driver.window_handles
      print(f"-------------- {name} ---------------")
      # print(f"名前、ID、PASSチェック {name} : {login_id} : {password}")
      for index, tab in enumerate(tabs):
        driver.switch_to.window(tab) 
        if index  == 0:
          login_id = drivers[name]["login_id"]
          password = drivers[name]["password"]
          return_foot_message = drivers[name]["return_foot_message"]
          fst_message = drivers[name]["fst_message"]
          conditions_message = drivers[name]["conditions_message"]
          mail_img = drivers[name]["mail_img"]
          if loop_cnt % 10 == 0:
            try:
              driver.get("https://happymail.co.jp/sp/app/html/mbmenu.php")
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(1.5)
              nav_flug = happymail.nav_item_click("プロフ検索", driver, wait)
              if not nav_flug:
                break
              happymail.set_mutidriver_make_footprints(drivers[name]["driver"], drivers[name]["wait"])
              time.sleep(2)  
            except NoSuchWindowException:
                print(f"set_mutidriver_make_footprintsの操作でエラーが出ました, {e}")
                print("スクショします")
                filename = f'screenshot_{time.strftime("%Y%m%d_%H%M%S")}.png'
                driver.save_screenshot(filename)
                pass
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
        elif index == 1:
          top_image_check = happymail.check_top_image(name, driver, wait)  
          if top_image_check:
            if "ブラウザ" in top_image_check:
              print("11111111111111111111111111111111")
              happymail_new_list.append(top_image_check)
          warning = happymail.catch_warning_screen(driver)
          if warning:
            print(f"{name} {warning}")
            happymail_new_list.append(f"{name} {warning}")
          else:
            top_image_check = happymail.check_top_image(name, driver, wait)  
            if top_image_check:
              if "ブラウザ" in top_image_check:
                print(top_image_check)
                happymail_new_list.append(top_image_check)
            try:
              now = datetime.now()
              today = now.date()
              # 日付が変わっていたらカウントをリセット
              if today != last_sent_date:
                  print(f"✅ 日付が変わったので {name} のカウントをリセットします（{last_sent_date} → {today}）")
                  sent_cnt = 0
                  last_sent_date = today
              if 6 <= now.hour < 22:
                if sent_cnt >= daily_limit:
                  print(f"🔴 {name} : 足跡返しの上限 {daily_limit} に達しています。スキップします。")
                else:
                  try:
                    happymail_cnt = happymail.return_footpoint(
                        name, driver, wait, return_foot_message, 5, 5, 5, mail_img, fst_message
                    )
                    total_cnt = happymail_cnt[0] + happymail_cnt[2]
                    for i in send_messages_list:
                      if i["名前"] == name:
                        i["マッチング総数"] += happymail_cnt[0]
                        i["足跡返し総数"] += happymail_cnt[2]
                        i["合計"] += total_cnt
                    print(f"足跡返し{happymail_cnt[2]} 件")
                  except NoSuchWindowException:
                    print(f"NoSuchWindowExceptionエラーが出ました, {e}")
                    pass
                  except ReadTimeoutError as e:
                    print("🔴 ページの読み込みがタイムアウトしました:", e)
                    driver.refresh()
                    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  except Exception as e:
                    print(traceback.format_exc())
              else:
                print(f"⏸ {name}: 現在は足跡返し実行時間外（{now.hour}時）です")
            except NoSuchWindowException:
              pass
            except ReadTimeoutError as e:
              print("🔴 ページの読み込みがタイムアウトしました:", e)
              driver.refresh()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            except Exception as e:
              print(traceback.format_exc())
            print(f"{name} 新着メールチェック...")
            new_message_flug = happymail.nav_item_click("メッセージ", driver, wait)
            if new_message_flug == "新着メールなし" and top_image_check is False:
              print(f"{name}　新着メールなし")
            else:  
              login_id = drivers[name]["login_id"]
              password = drivers[name]["password"]
              return_foot_message = drivers[name]["return_foot_message"]
              fst_message = drivers[name]["fst_message"]
              conditions_message = drivers[name]["conditions_message"]
              mail_img = drivers[name]["mail_img"]
              try:
                happymail_new = happymail.multidrivers_checkmail(name, driver, wait, login_id, password, return_foot_message, fst_message, conditions_message)
              except NoSuchWindowException:
                pass
              except ReadTimeoutError as e:
                print("🔴 ページの読み込みがタイムアウトしました:", e)
                driver.refresh()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              except Exception as e:
                print(traceback.format_exc())
          if top_image_check:
            happymail_new_list.append(top_image_check)
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
    print("<<<<<<<<<<<<<ループ折り返し>>>>>>>>>>>>>>>>>>>>>")
    print(send_messages_list)
    loop_cnt += 1
        
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

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


user_data = func.get_user_data()
happy_info = user_data["happymail"]
profile_path = "chrome_profiles/h_footprint"
headless = False
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
  drivers = happymail.start_the_drivers_login(mail_info, happy_info, headless, profile_path, True)
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
  # 足跡付け、チェックメール　ループ
  while True:
    if drivers == {}:
      break
    for name, data in drivers.items():
      driver = drivers[name]["driver"]
      wait = drivers[name]["wait"]
      tabs = driver.window_handles
      
      for index, tab in enumerate(tabs):
        driver.switch_to.window(tab) 
        # print(f"現在のタブ: {index + 1},")
        if index + 1 == 1:
          try:
            happymail.mutidriver_make_footprints(name, login_id, password, driver, wait)
          except NoSuchWindowException:
            pass
          except Exception as e:
            print(traceback.format_exc())
        elif index + 1 == 2:
          happymail.check_top_image(name, driver, wait)
          new_message_flug = happymail.nav_item_click("メッセージ", driver, wait)
          if new_message_flug == "新着メールなし":
            print(f"{name}　新着メールなし")
            continue
          else:
            login_id = drivers[name]["login_id"]
            password = drivers[name]["password"]
            return_foot_message = drivers[name]["return_foot_message"]
            fst_message = drivers[name]["fst_message"]
            conditions_message = drivers[name]["conditions_message"]
            try:
              happymail_new = happymail.multidrivers_checkmail(name, driver, wait, login_id, password, return_foot_message, fst_message, conditions_message)
            except NoSuchWindowException:
              pass
            except Exception as e:
              print(traceback.format_exc())
            if happymail_new:
              title = "新着メッセージ"
              text = ""
              for new_mail in happymail_new:
                text = text + new_mail + ",\n"
                if "警告" in text:
                    title = "メッセージ"
              # メール送信
              smtpobj = None
              if mail_info:
                func.send_mail(text, mail_info, title)
              else:
                print("通知メールの送信に必要な情報が不足しています")
                print(f"{mailaddress}   {gmail_password}  {receiving_address}")
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

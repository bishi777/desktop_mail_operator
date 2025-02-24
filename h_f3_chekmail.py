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


user_data = func.get_user_data()["happymail"]
profile_path = "chrome_profiles/h_footprint"
headless = False
drivers = {}


try:
  drivers = happymail.start_the_drivers_login(user_data, headless, profile_path, True)
  # タブを切り替えて操作
  # tab1で足跡付け, tab2でチェックメールSET
  for name, data in drivers.items():
    driver = drivers[name]["driver"]
    wait = drivers[name]["wait"]
    tabs = driver.window_handles
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
        print(f"現在のタブ: {index + 1},")
        if index + 1 == 1:
          happymail.mutidriver_make_footprints(name,drivers[name]["driver"], drivers[name]["wait"])
        elif index + 1 == 2:
          driver.refresh()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1.5)
          new_message_flug = happymail.nav_item_click("メッセージ", driver, wait)
          if new_message_flug == "新着メールなし":
            print(f"{name}　新着メールなし")
            continue
          else:
            happymail_new = happymail.multidrivers_checkmail(drivers[name]["driver"])
            if happymail_new:
              # メール送信
              smtpobj = None
              mailaddress = user_data['user'][0]['gmail_account']
              gmail_password = user_data['user'][0]['gmail_account_password']
              receiving_address = user_data['user'][0]['user_email']
              if mailaddress and gmail_password and receiving_address:
                title = "新着メッセージ"
                mail_info = [
                  mailaddress, gmail_password, receiving_address
                ]
                func.send_mail(happymail_new, mail_info, title)
              else:
                print("通知メールの送信に必要な情報が不足しています")
                print(f"{mailaddress}   {gmail_password}  {receiving_address}")
except KeyboardInterrupt:
  # Ctrl+C が押された場合
  print("プログラムが Ctrl+C により中断されました。")
  print(drivers)
  time.sleep(7)
  func.close_all_drivers(drivers)
  
except Exception as e:
  # 予期しないエラーが発生した場合
  func.close_all_drivers(drivers)
  print("エラーが発生しました:", e)
  traceback.print_exc()
finally:
  # 正常終了時・エラー終了時を問わず、最後に WebDriver を閉じる
  print('finalyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
  print(drivers)
  func.close_all_drivers(drivers)
  os._exit(0)

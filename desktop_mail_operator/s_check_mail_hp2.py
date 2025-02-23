from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import random
from selenium.webdriver.common.by import By
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from widget import pcmax, happymail, func
from selenium.webdriver.support.ui import WebDriverWait
import traceback
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import sqlite3
import time 
from datetime import datetime, timedelta, time as dt_time  
import socket
from selenium.common.exceptions import WebDriverException
import urllib3
import gc
from requests import exceptions
import requests
from stem import Signal
from stem.control import Controller
import shutil
import traceback

base_path = "./chrome_profiles/check_mail"

def wait_if_near_midnight():
  now = datetime.now()
  current_hour = now.hour
  current_minute = now.minute
  # もし現在時刻が23:55を過ぎていたら
  if current_hour == 23 and 55 <= current_minute:
      print("現在時刻は0時に近づいています。処理を一時中断します。")
      #     # ここに実行したい動作を追加
      time.sleep(600)
      print("処理を再開します。")
  return

def check_mail(user_data, headless):
  happymail_list = user_data['happymail']
  pcmax_list = user_data['pcmax']
  jmail_list = user_data['jmail']
  mailaddress = user_data['user'][0]['gmail_account']
  gmail_password = user_data['user'][0]['gmail_account_password']
  receiving_address = user_data['user'][0]['user_email']

  #   print(f"*****{mailaddress}*****{gmail_password}*****{receiving_address}")
  try:
    happymail_drivers = happymail.start_the_drivers_login(happymail_list, headless, base_path, 2)
    while True:
      send_flug = True
      start_time = time.time() 
      current_datetime = datetime.utcfromtimestamp(int(start_time))
      # ハッピーメール
      print(f'~~~~~~~~~~~~ハピメ:新着メールチェック開始~~~~~~~~~~~~')
      for name, data in happymail_drivers.items():
        new_mail_lists = []
        new_message_flug = happymail.nav_item_click("メッセージ", happymail_drivers[name]["driver"], happymail_drivers[name]["wait"])
        if new_message_flug == "新着メールなし":
          print(f"{name}　新着メールなし")
          continue
        else:  
        # 新着があった
        # if True:
          try:
            happymail_new = happymail.multidrivers_checkmail(happymail_drivers[name])
            if happymail_new:
              for i in happymail_new:
                print("-------通知メールーーーーーーーー")
                print(i)
                print("-------ーーーーーーーー")
                new_mail_lists.append(i)
              # メール送信
              smtpobj = None
              if mailaddress and gmail_password and receiving_address:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f'チェック完了　要確認メールあり  {now}')
                print(new_mail_lists)
                text = ""
                subject = "新着メッセージ"
                for new_mail_list in new_mail_lists:
                  # print('<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>')
                  # print(new_mail_list)
                  for new_mail in new_mail_list:
                    text = text + new_mail + ",\n"
                    if "警告" in text:
                      subject = "メッセージ"
              else:
                print("~~~~~~~~~~~~")
                print(f"自動送信に必要な情報が不足しています。　{mailaddress} {gmail_password} {receiving_address}")   
                continue
              try:
                smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
                smtpobj.starttls()
                smtpobj.set_debuglevel(0)
                smtpobj.login(mailaddress, gmail_password)
                msg = MIMEText(text)
                msg['Subject'] = subject
                msg['From'] = mailaddress
                msg['To'] = receiving_address
                msg['Date'] = formatdate()
                smtpobj.send_message(msg)
              except smtplib.SMTPDataError as e:
                print(f"SMTPDataError: {e}")
              except Exception as e:
                print(f"An error occurred: {e}")
              finally:
                if smtpobj: 
                    smtpobj.close()   
          except Exception as e:
            print(f"<<<<<<<<<<メールチェックエラー：ハッピーメール{name}>>>>>>>>>>>")
            print(traceback.format_exc())
            try:
              func.send_error(f"メールチェックエラー：ハッピーメール{name}", traceback.format_exc())    
            except smtplib.SMTPDataError as e:
              print(f"SMTPDataError: {e}")
            except Exception as e:
              print(f"An error occurred: {e}")
            finally:
              if smtpobj: 
                  smtpobj.close()   
      wait_if_near_midnight()
      time.sleep(2)
      temp_dir = func.get_the_temporary_folder("check_mail")
      driver,wait = func.test_get_driver(temp_dir, headless)
      # pcmax
      print(f"<<<<<<<<<<<<PCMAX:新着メール開始>>>>>>>>>>>>")
      for pcmax_info in pcmax_list:  
          # if pcmax_info["name"] != "ゆっこ":
          #     continue
          func.change_tor_ip()  
          new_mail_lists = []
          try:
              result = pcmax.check_new_mail(pcmax_info, driver, wait)
              if result is not None:
                  pcmax_new, return_foot_cnt = result
              else:
                  pcmax_new, return_foot_cnt = 1, 0
              if pcmax_new != 1:
                  new_mail_lists.append(pcmax_new)
              # メール送信
              smtpobj = None 
              if len(new_mail_lists) == 0:
                  now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                  print(f'{pcmax_info["name"]}チェック完了  {now}')
                  pass
              else:
                  # print("~~~~~~~~~~~~")
                  # print(f"{mailaddress} {gmail_password} {receiving_address}")
                  if mailaddress and gmail_password and receiving_address:
                      now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                      print(f'チェック完了 要確認メールあり  {now}')
                      print(new_mail_lists) 
                      text = ""
                      subject = "新着メッセージ"
                      for new_mail_list in new_mail_lists:
                          # print('<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>')
                          # print(new_mail_list)
                          for new_mail in new_mail_list:
                              text = text + new_mail + ",\n"
                              if "警告" in text or "番号" in text:
                                  subject = "メッセージ"
                  try:
                      smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
                      smtpobj.starttls()
                      smtpobj.set_debuglevel(0)
                      smtpobj.login(mailaddress, gmail_password)
                      msg = MIMEText(text)
                      msg['Subject'] = subject
                      msg['From'] = mailaddress
                      msg['To'] = receiving_address
                      msg['Date'] = formatdate()
                      smtpobj.send_message(msg)
                  except smtplib.SMTPDataError as e:
                      print(f"SMTPDataError: {e}")
                  except Exception as e:
                      print(f"An error occurred: {e}")
                  finally:
                      if smtpobj: 
                          smtpobj.close()   
          except (smtplib.SMTPException, socket.gaierror) as e:
              print(f"メール送信中にエラーが発生しました: {e}")
              print("5分間待機して再試行します...")
              driver.quit()
              shutil.rmtree(temp_dir)
              time.sleep(300)  # 300秒（5分）間待機
              check_mail(user_data, headless)
          except (WebDriverException, urllib3.exceptions.MaxRetryError) as e:
              print(f"タイムアウトエラーが発生しました: {e}")      
              print("30秒後に再接続します。")
              time.sleep(30)  # 30秒待機して再試行
              check_mail(user_data, headless)
              
          except Exception as e:
              print(f"<<<<<<<<<<PCMAX{pcmax_info['name']}>>>>>>>>>>>")
              print(traceback.format_exc())
              traceback.print_exc() 
              func.send_error(f"PCMAX{pcmax_info['name']}", traceback.format_exc())    
          wait_if_near_midnight()
          if return_foot_cnt:     
              continue
              # for r_f_user in pcmax_return_foot_count_dic:
              #     if order_info[0] == r_f_user:
              #         # print(777)
              #         # print(return_foot_count_dic[r_f_user])
              #         pcmax_return_foot_count_dic[r_f_user] = pcmax_return_foot_count_dic[r_f_user] + return_foot_cnt
              #         # print(return_foot_count_dic[r_f_user])
      wait_if_near_midnight()
      # driver.refresh()
          # jmail
          # try:
          #     driver, wait = get_driver(debug)
          #     jmail_new, return_foot_cnt = jmail.check_new_mail(driver, wait, jmail_list)
          #     if jmail_new == 2:
          #         new_mail_lists.append(f"jmail:{order_info[0]} ログインできませんでした")
          #     elif jmail_new != 1:
          #         new_mail_lists.append(jmail_new)
          #     if return_foot_cnt:     
          #         for r_f_user in jmail_return_foot_count_dic:
          #             if order_info[0] == r_f_user:
          #                 # print(777)
          #                 # print(jmail_return_foot_count_dic[r_f_user])
          #                 # print(return_foot_cnt)
          #                 jmail_return_foot_count_dic[r_f_user] = jmail_return_foot_count_dic[r_f_user] + return_foot_cnt
          #                 # print(jmail_return_foot_count_dic[r_f_user])
          #     driver.quit()
          # except Exception as e:
          #     print(f"<<<<<<<<<<メールチェックエラー：jmail{order_info[0]}>>>>>>>>>>>")
          #     print(traceback.format_exc())
          #     func.send_error(f"メールチェックエラー：jmail{order_info[0]}", traceback.format_exc())
          #     driver.quit()
  except KeyboardInterrupt:
    print("プログラムが Ctrl+C により中断されました。")

  finally:
    # すべてのドライバを適切に閉じる      
    func.close_all_drivers(happymail_drivers)
      
        
                    
    
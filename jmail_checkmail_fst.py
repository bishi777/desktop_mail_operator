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
from widget import pcmax, happymail, func, jmail
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
  jmail_list = user_data['jmail']
  mailaddress = user_data['user'][0]['gmail_account']
  gmail_password = user_data['user'][0]['gmail_account_password']
  receiving_address = user_data['user'][0]['user_email']
  try_cnt = 0
#   print(f"*****{mailaddress}*****{gmail_password}*****{receiving_address}")
  while True:
    send_flug = True
    start_time = time.time() 
    current_datetime = datetime.utcfromtimestamp(int(start_time))
    # jmail
    now = datetime.now()
    # 午前6時から午後23時の間だけ実行
    if 6 <= now.hour < 23:
        print(f"<<<<<<<<<<<<Jmail:新着メール開始>>>>>>>>>>>>")     
        try:
            driver, wait = func.get_driver(headless)
            for jmail_info in jmail_list:  
                jmail_send_info = jmail.check_new_mail(driver, wait, jmail_info, try_cnt)
            # メール送信
            smtpobj = None
            if len(jmail_send_info) == 0:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f'{jmail_info["name"]}チェック完了  {now}')
                pass
            else:
                if mailaddress and gmail_password and receiving_address:
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f'チェック完了　要確認メールあり  {now}')
                    print(jmail_send_info)
                    text = ""
                    subject = "新着メッセージ"
                    for new_mail_list in jmail_send_info:
                        print('<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>')
                        print(new_mail_list)
                        text = text + new_mail_list + ",\n"
                        print('<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>')
                        print(text)
                        if "警告" in text:
                            subject = "メッセージ"
                        
                            
                else:
                    print("~~~~~~~~~~~~")
                    print(f"自動送信に必要な情報が不足しています。　{mailaddress} {gmail_password} {receiving_address}")
                    
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
                        # print(jmail_return_foot_count_dic[r_f_user])
            driver.quit()
            try_cnt += 1
            time.sleep(600)
        except Exception as e:
            print(f"<<<<<<<<<<メールチェックエラー：jmail{jmail_info['name']}>>>>>>>>>>>")
            print(traceback.format_exc())
            func.send_error(f"メールチェックエラー：jmail{jmail_info['name']}", traceback.format_exc())
            driver.quit()
            
        
        driver.quit()
        time.sleep(1)
        gc.collect()
    else:
        time.sleep(600)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    cnt = 20
  
  user_data = func.get_user_data()
  headless = False
  check_mail(user_data, headless)

        

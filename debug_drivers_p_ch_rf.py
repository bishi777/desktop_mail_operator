from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from widget import func, pcmax_2, pcmax
import settings
import random
import os
from email.utils import formatdate
from email.mime.text import MIMEText
import time
import smtplib
import traceback
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import sys

arg1 = sys.argv[1] if len(sys.argv) > 1 else None
user_data = func.get_user_data()
wait_time = 1.5
mailserver_address = user_data['user'][0]['gmail_account']
mailserver_password = user_data['user'][0]['gmail_account_password']
receiving_address = user_data['user'][0]['user_email']
pcmax_datas = user_data["pcmax"]
# pcmax_datas = pcmax_datas[:9]
options = Options()
options.add_experimental_option("debuggerAddress", f"127.0.0.1:{settings.chrome_user_profiles[int(arg1)]['port']}")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)
handles = driver.window_handles
report_dict = {}
send_flug = False

while True:
  start_loop_time = time.time()
  now = datetime.now()
  for idx, handle in enumerate(handles): 
    WebDriverWait(driver, 40).until(lambda d: handle in d.window_handles)
    driver.switch_to.window(handle)
    login_flug = pcmax_2.catch_warning_pop("", driver)
    if login_flug and "制限" in login_flug:
      print("制限がかかっているため、スキップを行います")
      continue
    print(f"  📄 タブ{idx+1}: {driver.current_url}")
    # urls = [
    #   "pcmax.jp/pcm/index.php"
    # ]
    if not "pcmax.jp/pcm/index.php" in driver.current_url:
      driver.get("https://pcmax.jp/mobile/mymenu.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1.5)  
      # print("PCMAXのマイメニューに移動しました")
      # print(driver.current_url)
    try:
      name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
      
      while not len(name_on_pcmax):
        # 再ログイン処理
        main_photo = driver.find_elements(By.CLASS_NAME, 'main_photo')
        if len(main_photo):
          login_form = driver.find_elements(By.CLASS_NAME, 'login-sub')   
          if len(login_form):
            login = login_form[0].find_elements(By.TAG_NAME, 'a')
            login[0].click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')          
        else:
          print("メイン写真が見つかりません")
          # スクショ
          # driver.save_screenshot("screenshot.png")
        time.sleep(8.5)
        login_button = driver.find_element(By.NAME, "login")
        login_button.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1.5)
        login_flug = pcmax_2.catch_warning_pop("", driver)
        if login_flug and "制限" in login_flug:
          print("制限がかかっているため、スキップを行います")
          continue    
        name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
        re_login_cnt = 0
        while not len(name_on_pcmax):
          login_form = driver.find_elements(By.CLASS_NAME, 'login-sub')   
          if len(login_form):
            if login_form[0].is_displayed():
              login = login_form[0].find_elements(By.TAG_NAME, 'a')
              login[0].click()
              time.sleep(5)
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')   
          driver.refresh()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(150)
          login_button = driver.find_element(By.NAME, "login")
          login_button.click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1.5)
          pcmax_2.catch_warning_pop("", driver)
          name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
          re_login_cnt += 1
          if re_login_cnt > 5:
            print("再ログイン失敗")
            break   
        name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
        func.send_error(name_on_pcmax[0].text, f"リンクルチェックメール、足跡がえしの処理中に再ログインしました")   
      name_on_pcmax = name_on_pcmax[0].text
      print(f"~~~~~~~~~~~~{name_on_pcmax}~~~~~~~~~~~~")  
    except Exception as e:
      print(f"~~~~~❌ ログインの操作でエラー: {e}")
      traceback.print_exc()  
      driver.get("https://pcmax.jp/pcm/index.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1.5)
      continue
    for index, i in enumerate(pcmax_datas):
      login_id = ""
      if name_on_pcmax != "めあり":
        continue
      if name_on_pcmax == i['name']:
        if name_on_pcmax not in report_dict:
          report_dict[name_on_pcmax] = 0
          print(f"777 {report_dict[name_on_pcmax]}")
        name = i["name"]
        login_id = i["login_id"]
        login_pass = i["password"]
        # print(f"{login_id}   {login_pass}")
        gmail_address = i["mail_address"]
        gmail_password= i["gmail_password"]
        fst_message = i["fst_mail"]
        second_message = i["second_message"]
        condition_message = i["condition_message"]
        mail_img = i["mail_img"]
        return_foot_message = i["return_foot_message"]
        send_cnt = 3  
        try:
          top_image_flug = pcmax_2.check_top_image(name,driver)
          if top_image_flug:
            func.send_mail(
              f"pcmax {name}のTOP画像が更新されました。NOIMAGE",
              [receiving_address,mailserver_address,mailserver_password,],
              f"PCMAX トップ画像の更新 {now.strftime('%Y-%m-%d %H:%M:%S')}",
            )
        except Exception as e:
          print(f"{name}❌ トップ画像のチェック  の操作でエラー: {e}")
          traceback.print_exc()
        try:
          print("新着メールチェック開始")   
          pcmax_2.check_mail(name, driver, login_id, login_pass, gmail_address, gmail_password, fst_message, second_message, condition_message, mailserver_address, mailserver_password, receiving_address)
        except Exception as e:
          print(f"{name}❌ メールチェック  の操作でエラー: {e}")
          traceback.print_exc()  
        if 7 <= now.hour < 23 or (now.hour == 23 and now.minute <= 45):
          try:
            print("足跡返し送信開始")
            if send_cnt > 0:
              rf_cnt = pcmax_2.return_footmessage(name, driver, return_foot_message, send_cnt, mail_img)   
            report_dict[name] = report_dict[name] + rf_cnt
          except Exception as e:
            print(f"{name}❌ 足跡返し  の操作でエラー: {e}")
            traceback.print_exc()   
          if  now.hour % 6 == 0 or now.hour == 1:
            if send_flug:
              try:
                func.send_mail(
                  f"足跡返しの報告\n{report_dict}\n",
                  [receiving_address,mailserver_address,mailserver_password,],
                  f"PCMAX 足跡返しの報告 {now.strftime('%Y-%m-%d %H:%M:%S')}",
                )
                send_flug = False
                report_dict = {}
              except Exception as e:
                print(f"{name}❌ 足跡返しの報告  の操作でエラー: {e}")
                traceback.print_exc()   
          else:
            send_flug = True
         
  elapsed_time = time.time() - start_loop_time  # 経過時間を計算する   
  while elapsed_time < 720:
    time.sleep(10)
    elapsed_time = time.time() - start_loop_time  # 経過時間を計算する
    print(f"待機中~~ {elapsed_time} ")
  print("<<<<<<<<<<<<<ループ折り返し>>>>>>>>>>>>>>>>>>>>>")
  elapsed_time = time.time() - start_loop_time  # 経過時間を計算する   
  minutes, seconds = divmod(int(elapsed_time), 60)
  print(f"タイム: {minutes}分{seconds}秒")  
  
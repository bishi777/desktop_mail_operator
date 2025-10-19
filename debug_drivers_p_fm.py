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

user_data = func.get_user_data()
wait_time = 1.5
user_mail_info = [
  user_data['user'][0]['user_email'],
  user_data['user'][0]['gmail_account'],
  user_data['user'][0]['gmail_account_password'],
  ]
spare_mail_info = [
  "ryapya694@ruru.be",
  "siliboco68@gmail.com",
  "akkcxweqzdplcymh",
]
pcmax_datas = user_data["pcmax"]
# pcmax_datas = pcmax_datas[:9]
options = Options()
options.add_experimental_option("debuggerAddress", f"127.0.0.1:{settings.pcmax_ch_port}")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)
report_dict = {}
send_flug = False
roll_cnt = 0


while True:
  mail_info = random.choice([user_mail_info, spare_mail_info])
  start_loop_time = time.time()
  now = datetime.now()
  handles = driver.window_handles

  for idx, handle in enumerate(handles): 
    # WebDriverWait(driver, 40).until(lambda d: handle in d.window_handles)
    driver.switch_to.window(handle)
    login_flug = pcmax_2.catch_warning_pop("", driver)
    if login_flug and "制限" in login_flug:
      print("制限がかかっているため、スキップを行います")
      continue
    # print(f"  📄 タブ{idx+1}: {driver.current_url}")
    # urls = [
    #   "pcmax.jp/pcm/index.php"
    # ]
    if not "/pcm/index.php" in driver.current_url:
      if "linkleweb" in driver.current_url:
        driver.get("https://linkleweb.jp/mobile/index.php")
      elif "pcmax" in driver.current_url:
        driver.get("https://pcmax.jp/mobile/index.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1.5)  
      # print("PCMAXのTOPに移動しました")
      # print(driver.current_url)
    try:
      name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')   
      if name_on_pcmax:
        name = name_on_pcmax[0].text
        # if ("いおり" and "りな") != name:
        #   continue

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
          print(driver.current_url)
          if "linkleweb" in driver.current_url:
            print("linklewebのログイン実装に移動")
            driver.find_elements(By.CLASS_NAME, 'login')[0].click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            pcmax_2.catch_warning_pop("", driver)
            time.sleep(130)
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
      now = datetime.now()
      print(f"~~~~~~~~~~~~{name_on_pcmax}~~~~~~~~~~~~{now.strftime('%Y-%m-%d %H:%M:%S')}~~~~~~~~~~~~")  
    except Exception as e:
      print(f"~~~~~❌ ログインの操作でエラー: {e}")
      traceback.print_exc()  
      if "pcmax" in driver.current_url:
        driver.get("https://pcmax.jp/pcm/index.php")
      elif "linkleweb" in driver.current_url:
        driver.get("https://linkleweb.jp/pcm/index.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1.5)
      continue
    # メイン処理
    for index, i in enumerate(pcmax_datas):
      login_id = ""   
      if name_on_pcmax == i['name']:
        if name_on_pcmax not in report_dict:
          report_dict[name_on_pcmax] = 0
          # print(f"{report_dict[name_on_pcmax]}")
        name = i["name"]
        login_id = i["login_id"]
        login_pass = i["password"]
        # print(f"{login_id}   {login_pass}")
        gmail_address = i["mail_address"]
        gmail_password= i["gmail_password"]
        fst_message = i["fst_mail"]
        second_message = i["second_message"]
        condition_message = i["condition_message"]
        confirmation_mail = i["confirmation_mail"]
        mail_img = i["mail_img"]
        return_foot_message = i["return_foot_message"]
        send_cnt = 2
        
        try:
          top_image_flug = pcmax_2.check_top_image(name,driver)
          if top_image_flug:
            func.send_mail(
              f"pcmax {name}のTOP画像が更新されました。\nNOIMAGE\n{now.strftime('%Y-%m-%d %H:%M:%S')}",
              mail_info,
              f"PCMAX トップ画像の更新 ",
            )
        except Exception as e:
          print(f"{name}❌ トップ画像のチェック  の操作でエラー: {e}")
          traceback.print_exc()
        try:
          print("✅新着メールチェック開始")   
          unread_user = pcmax_2.check_mail(name, driver, login_id, login_pass, gmail_address, gmail_password, fst_message, return_foot_message, mail_img, second_message, condition_message, confirmation_mail, mail_info)
          print("✅新着メールチェック終了")
        except Exception as e:
          print(f"{name}❌ メールチェック  の操作でエラー: {e}")
          traceback.print_exc()  
        if 7 <= now.hour < 23 or (now.hour == 23 and now.minute <= 45):
          print(f"✅fstメール送信開始 送信数:{send_cnt}")
          fm_cnt = pcmax_2.set_fst_mail(name, driver, fst_message, send_cnt, mail_img)
          print(f"✅fstメール送信終了　トータルカウント{report_dict[name] + fm_cnt}")
          report_dict[name] = report_dict[name] + fm_cnt
          
          if now.hour % 6 == 0:
            if send_flug:
              try:
                func.send_mail(
                  f"PCMAX 1時間のfstmailの報告\n{report_dict}\n",
                  mail_info,
                  f"PCMAX 1時間のfstmailの報告 {now.strftime('%Y-%m-%d %H:%M:%S')}",
                )
                send_flug = False
                report_dict = {}
              except Exception as e:
                print(f"{name}❌ fstmailの報告  の操作でエラー: {e}")
                traceback.print_exc()   
                print('~~~~~~~~~')
                print(mail_info)
          else:
            send_flug = True
  
  elapsed_time = time.time() - start_loop_time  # 経過時間を計算する   
  wait_cnt = 0
  while elapsed_time < 720:
    time.sleep(10)
    elapsed_time = time.time() - start_loop_time  # 経過時間を計算する
    if wait_cnt % 6 == 0:
      print(f"待機中~~ {elapsed_time} ")
    wait_cnt += 1
  print("<<<<<<<<<<<<<ループ折り返し>>>>>>>>>>>>>>>>>>>>>")
  elapsed_time = time.time() - start_loop_time  # 経過時間を計算する   
  minutes, seconds = divmod(int(elapsed_time), 60)
  print(f"タイム: {minutes}分{seconds}秒")  
  #カウント 
  roll_cnt += 1
  if roll_cnt % 6 == 0:
    print(f"🔄 {roll_cnt}回目のループ完了 {now.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
      func.send_mail(
        f"PCMAX 6時間のfstmailの報告\n{report_dict}\n",
        mail_info,
        f"PCMAX 6時間のfstmailの報告 {now.strftime('%Y-%m-%d %H:%M:%S')}",
      )
      send_flug = False
    except Exception as e:
      print(f"{name}❌ 6時間のfstmailの報告  の操作でエラー: {e}")
      traceback.print_exc()   
      print('~~~~~~~~~')
      print(mail_info)
         
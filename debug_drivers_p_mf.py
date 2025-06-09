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

user_data = func.get_user_data()
wait_time = 1.5
mailserver_address = user_data['user'][0]['gmail_account']
mailserver_password = user_data['user'][0]['gmail_account_password']
receiving_address = user_data['user'][0]['user_email']
pcmax_datas = user_data["pcmax"]
# pcmax_datas = pcmax_datas[:9]
options = Options()
options.add_experimental_option("debuggerAddress", f"127.0.0.1:{settings.chrome_user_profiles[0]['port']}")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)
handles = driver.window_handles
current_step = 0
current_step_flug = False
search_profile_flug = False
six_minute_index = 0  #



for i in range(99999):
  start_loop_time = time.time()
  now = datetime.now()
  start_time = time.time() 
  for idx, handle in enumerate(handles): 
    driver.switch_to.window(handle)
    login_flug = pcmax_2.catch_warning_pop("", driver)
    if login_flug and "制限" in login_flug:
      print("制限がかかっているため、スキップを行います")
      time.sleep(0.5)
      continue
    # ユーザーをクリック 
    try:
      if "pcmax.jp/mobile/profile_list.php" in driver.current_url:
        mohu_flug = False
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        user_list = driver.find_elements(By.CLASS_NAME, 'profile_card')
        if current_step < len(user_list):
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", user_list[current_step])
          time.sleep(0.4)
          user_list[current_step].find_element(By.CLASS_NAME, "profile_link_btn").click()
          print(f"足跡付け {current_step}件")    
          time.sleep(1)
          search_profile_flug = False
        else:
          print("足跡付けのユーザーがいません")
          search_profile_flug = True
      else:
        print("pcmax.jp/mobile/profile_list.phpにいません")
        print(f"現在のURL: {driver.current_url}")
        search_profile_flug = True
    except Exception as e:
      print(f"❌  足跡付けの操作でエラー: {e}")
      traceback.print_exc()  
  # <<<<<<<<<<<<<プロフ検索再セット>>>>>>>>>>>>>>>>>>>"
  if search_profile_flug:
    current_step = 0
    for idx, handle in enumerate(handles): 
      driver.switch_to.window(handle)
      login_flug = pcmax_2.catch_warning_pop("", driver)
      if login_flug and "制限" in login_flug:
        # print("制限がかかっているため、スキップを行います")
        continue
      print("<<<<<<<<<<<<<プロフ検索再セット>>>>>>>>>>>>>>>>>>>")
      try:    
        driver.get("https://pcmax.jp/pcm/index.php")   
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(0.5)
        pcmax_2.catch_warning_pop("", driver)
        name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
        print(f"名前: {name_on_pcmax[0].text if name_on_pcmax else '名前が見つかりません'}")
        pcmax_2.profile_search(driver)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        continue
      except Exception as e:
        print(f"❌  の操作でエラー: {e}")
        traceback.print_exc()  
  else:  
    # ユーザー詳細画面から戻る
    for idx, handle in enumerate(handles): 
      driver.switch_to.window(handle)
      login_flug = pcmax_2.catch_warning_pop("", driver)
      if login_flug and "制限" in login_flug:
        # print("制限がかかっているため、スキップを行います")
        continue
      try:
        login_flug = pcmax_2.catch_warning_pop("", driver)
        if login_flug and "制限" in login_flug:
          # print("制限がかかっているため、スキップを行います")
          continue
        if "pcmax.jp/mobile/profile_detail.php" in driver.current_url:
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          driver.back()
          current_step_flug = True
        else:
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
                # スクショします
                # driver.save_screenshot("screenshot.png")
              time.sleep(8.5)
              login_button = driver.find_element(By.NAME, "login")
              login_button.click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(1.5)
              login_flug = pcmax_2.catch_warning_pop("", driver)
              if login_flug and "制限" in login_flug:
                # print("制限がかかっているため、スキップを行います8888888888")
                break      
              name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
              re_login_cnt = 0
              while not len(name_on_pcmax):
                time.sleep(5)
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
              name_on_pcmax = name_on_pcmax[0].text
              print(f"~~~~~~~~~~~~{name_on_pcmax}~~~~~~~~~~~~")
              pcmax_2.profile_search(driver)
          except Exception as e:
            print(f"~~~~~❌ ログインの操作でエラー: {e}")
            traceback.print_exc()  
            driver.get("https://pcmax.jp/pcm/index.php")
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(1.5)
            continue
      except Exception as e:
        print(f"❌  の操作でエラー: {e}")
        traceback.print_exc()  
  if current_step_flug:
    current_step += 1
  
  elapsed_time = time.time() - start_time  # 経過時間を計算する   
  print("<<<<<<<<<<<<<ループ折り返し>>>>>>>>>>>>>>>>>>>>>")
  elapsed_time = time.time() - start_loop_time  # 経過時間を計算する   
  minutes, seconds = divmod(int(elapsed_time), 60)
  print(f"タイム: {minutes}分{seconds}秒")  
  if now.minute % 2 == 0:
    if six_minute_flug:
      print("2分おきの処理")
      handle_to_use = handles[six_minute_index % len(handles)]
      driver.switch_to.window(handle_to_use)
      try:
        driver.get("https://pcmax.jp/pcm/index.php")
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        pcmax_2.catch_warning_pop("", driver)
        name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(f"名前: {name_on_pcmax[0].text if name_on_pcmax else '名前が見つかりません'}")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        driver.back()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        six_minute_flug = False
      except Exception as e:
        print(f"❌ 6分おき処理でエラー: {e}")
        traceback.print_exc()
      six_minute_index += 1  
  else:
    six_minute_flug = True
    
    


    

    
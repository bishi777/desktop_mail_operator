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

for i in range(9999):
  start_loop_time = time.time()
  now = datetime.now()
  start_time = time.time() 
  for idx, handle in enumerate(handles): 
    driver.switch_to.window(handle)
    login_flug = pcmax_2.catch_warning_pop("", driver)
    if login_flug and "制限" in login_flug:
      print("制限がかかっているため、スキップを行います")
      continue
    # ユーザーをクリック
    try:
      if "pcmax.jp/mobile/profile_list.php" in driver.current_url:
        mohu_flug = False
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        user_list = driver.find_elements(By.CLASS_NAME, 'profile_card')
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", user_list[current_step])
        time.sleep(0.4)
        user_list[current_step].find_element(By.CLASS_NAME, "profile_link_btn").click()
        print(f"足跡付け {current_step}件")    
        time.sleep(1.5)
    except Exception as e:
      print(f"❌  足跡付けの操作でエラー: {e}")
      traceback.print_exc()  
  for idx, handle in enumerate(handles): 
    driver.switch_to.window(handle)
    login_flug = pcmax_2.catch_warning_pop("", driver)
    if login_flug and "制限" in login_flug:
      # print("制限がかかっているため、スキップを行います")
      continue
    print(f"-------------{idx}------------------")
    print(f"-------------{i % len(handles)}------------------")
    if idx == i % len(handles):
      if current_step % 5 == 0:
        print("<<<<<<<<<<<<<プロフ検索再セット>>>>>>>>>>>>>>>>>>>")
        try:    
          driver.get("https://pcmax.jp/pcm/index.php")   
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(0.5)
          pcmax_2.catch_warning_pop("", driver)
          pcmax_2.profile_search(driver)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          continue
        except Exception as e:
          print(f"❌  の操作でエラー: {e}")
          traceback.print_exc()  
    # ユーザー詳細画面から戻る
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
              driver.save_screenshot("screenshot.png")
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
    
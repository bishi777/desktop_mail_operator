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

mohu = 0
for i in range(9999):
  start_loop_time = time.time()
  now = datetime.now()
  start_time = time.time() 
  for idx, handle in enumerate(handles): 
    driver.switch_to.window(handle)
    if mohu == 50:
      driver.get("https://pcmax.jp/pcm/index.php")   
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      pcmax_2.profile_search(driver)
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      mohu = 0
    # 足跡付け
    try:
      if "pcmax.jp/mobile/profile_list.php" in driver.current_url:
        mohu_flug = False
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        user_list = driver.find_elements(By.CLASS_NAME, 'profile_card')
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", user_list[mohu])
        time.sleep(1)
        user_list[mohu].find_element(By.CLASS_NAME, "profile_link_btn").click()
      elif "pcmax.jp/mobile/profile_detail.php" in driver.current_url:
        mohu_flug = True
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        driver.back()
        time.sleep(1)
    except Exception as e:
      print(f"❌  の操作でエラー: {e}")
      traceback.print_exc()  
  if mohu_flug:
    mohu += 1
    print(f"足跡付け {mohu}件")    
    elapsed_time = time.time() - start_time  # 経過時間を計算する   
    print("<<<<<<<<<<<<<ループ折り返し>>>>>>>>>>>>>>>>>>>>>")
    elapsed_time = time.time() - start_loop_time  # 経過時間を計算する   
    minutes, seconds = divmod(int(elapsed_time), 60)
    print(f"タイム: {minutes}分{seconds}秒")  
  



# driver.execute_script("window.open('https://pcmax.jp/pcm/index.php');")
          # time.sleep(1)
          # tabs = driver.window_handles
          # driver.switch_to.window(tabs[1])
          # print("新着メールチェック開始")   
          # pcmax_2.check_mail(name, driver, login_id, login_pass, gmail_address, gmail_password, fst_message, second_message, condition_message, mailserver_address, mailserver_password, receiving_address)
          # driver.get("https://pcmax.jp/pcm/index.php")   
          # print("足跡がえし")
          # pcmax_2.return_footmessage(name, driver, return_foot_message, 1, mail_img)
          #  finally:
          # driver.close()
          # # 残っている元のタブに戻る
          # driver.switch_to.window(tabs[0])
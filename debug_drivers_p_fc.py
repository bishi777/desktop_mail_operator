from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from widget import func, pcmax_2
import settings
import random
import os
import time
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
print(f"タブ数: {len(handles)}")
while True:
  now = datetime.now()
  if 6 <= now.hour < 23 or (now.hour == 23 and now.minute <= 45):
    start_time = time.time() 
    for idx, handle in enumerate(handles): 
      driver.switch_to.window(handle)
      print(f"  📄 タブ{idx+1}: {driver.current_url}")
      skip_urls = [
        "profile_reference.php",
        "profile_rest_list.php",
        "profile_list.php",
        "profile_detail.php",
        "profile_rest_reference.php",
      ]
      if any(part in driver.current_url for part in skip_urls):
        driver.get("https://pcmax.jp/pcm/index.php")
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1.5)  
      if driver.current_url not in ["https://pcmax.jp/pcm/member.php", "https://pcmax.jp/pcm/index.php"]:
        continue
      name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
      print(9999)
      print(name_on_pcmax)
      if not len(name_on_pcmax):
        pcmax_2.catch_warning_pop("", driver)
        login_form = driver.find_elements(By.CLASS_NAME, 'login-sub')   
        if len(login_form):
          print(99999999)
          login = login_form.find_elements(By.TAG_NAME, 'a')
          login[0].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1.5)
      print(f"~~~{name_on_pcmax[0].text}~~~")
      for index, i in enumerate(pcmax_datas):
        login_id = ""
        if name_on_pcmax[0].text == i['name']:
          name = i["name"]
          # if  "りこ" != name:
          #   print(name)
          #   continue
          login_id = i["login_id"]
          login_pass = i["password"]
          # print(f"{login_id}   {login_pass}")
          gmail_address = i["mail_address"]
          gmail_password= i["gmail_password"]
          fst_message = i["fst_mail"]
          second_message = i["second_message"]
          condition_message = i["condition_message"]
          send_cnt = 3
          try:
            print("新着メールチェック開始")     
            pcmax_2.check_mail(name, driver, login_id, login_pass, gmail_address, gmail_password, fst_message, second_message, condition_message, mailserver_address, mailserver_password)
            driver.get("https://pcmax.jp/pcm/index.php")
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(1.5)
          except Exception as e:
            print(f"{name}❌ メールチェック  の操作でエラー: {e}")
            traceback.print_exc() 
         
          try:
            print("fst_mail送信開始")
            pcmax_2.set_fst_mail(name, driver, fst_message, send_cnt)
            time.sleep(1.5)   
          except Exception as e:
            print(f"{name}❌ fst_mail  の操作でエラー: {e}")
            traceback.print_exc()   
          driver.get("https://pcmax.jp/pcm/index.php")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1.5)
    elapsed_time = time.time() - start_time  # 経過時間を計算する   
    while elapsed_time < 720:
      time.sleep(30)
      elapsed_time = time.time() - start_time  # 経過時間を計算する
      print(f"待機中~~ {elapsed_time} ")
  # driver.quit()
  time.sleep(2)

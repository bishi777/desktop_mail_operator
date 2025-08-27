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

# DevTools Protocol で User-Agent を変更
# driver.execute_cdp_cmd('Network.setUserAgentOverride', {
#     "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
# })
# user_agent_type = "iPhone"
# driver.refresh()
# wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
# print(777)
# time.sleep(1000.5)

print(f"タブ数: {len(handles)}")
roop_index = 0
while True:
  start_loop_time = time.time()
  now = datetime.now()
  start_time = time.time() 
  for idx, handle in enumerate(handles): 
    WebDriverWait(driver, 10).until(lambda d: handle in d.window_handles)
    driver.switch_to.window(handle)
    print(f"  📄 タブ{idx+1}: {driver.current_url}")
    skip_urls = [
      "profile_reference.php",
      "profile_rest_list.php",
      "profile_list.php",
      "profile_detail.php",
      "profile_rest_reference.php",
      "pcmax.jp/pcm/file.php"
    ]
    if any(part in driver.current_url for part in skip_urls):
      driver.get("https://pcmax.jp/pcm/index.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1.5)  

    if driver.current_url not in ["https://pcmax.jp/pcm/member.php", "https://pcmax.jp/pcm/index.php"]:
      continue
    try:
      login_flug = pcmax_2.catch_warning_pop("", driver)
      print(login_flug)   
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
    except Exception as e:
      print(f"~~~~~❌ ログインの操作でエラー: {e}")
      traceback.print_exc()  
      driver.get("https://pcmax.jp/pcm/index.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1.5)
      continue
    for index, i in enumerate(pcmax_datas):
      login_id = ""
      if name_on_pcmax == i['name']:
        name = i["name"]
        # if  "レイナ" != name:
        #   continue
        login_id = i["login_id"]
        login_pass = i["password"]
        # print(f"{login_id}   {login_pass}")
        gmail_address = i["mail_address"]
        gmail_password= i["gmail_password"]
        fst_message = i["fst_mail"]
        second_message = i["second_message"]
        condition_message = i["condition_message"]
        mail_img = i["mail_img"]
        send_cnt = 3
        
        try:
          print("新着メールチェック開始")   
          driver.refresh()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
          pcmax_2.check_mail(name, driver, login_id, login_pass, gmail_address, gmail_password, fst_message, second_message, condition_message, mailserver_address, mailserver_password, receiving_address)
          driver.get("https://pcmax.jp/pcm/index.php")   
        except Exception as e:
          print(f"{name}❌ メールチェック  の操作でエラー: {e}")
          traceback.print_exc()  
        if 6 <= now.hour < 23 or (now.hour == 23 and now.minute <= 45):
          try:
            print("fst_mail送信開始")
            if  "りな" == name:
              print(name)
              print(roop_index)
              if roop_index % 5 == 0:
                send_cnt = 4
            if send_cnt > 0:
              pcmax_2.set_fst_mail(name, driver, fst_message, send_cnt, mail_img)
              time.sleep(1.5)   
          except Exception as e:
            print(f"{name}❌ fst_mail  の操作でエラー: {e}")
            traceback.print_exc()   
          driver.get("https://pcmax.jp/pcm/index.php")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1.5)
  elapsed_time = time.time() - start_time  # 経過時間を計算する   
  while elapsed_time < 720:
    time.sleep(10)
    elapsed_time = time.time() - start_time  # 経過時間を計算する
    print(f"待機中~~ {elapsed_time} ")
  print("<<<<<<<<<<<<<ループ折り返し>>>>>>>>>>>>>>>>>>>>>")
  roop_index += 1
  elapsed_time = time.time() - start_loop_time  # 経過時間を計算する   
  minutes, seconds = divmod(int(elapsed_time), 60)
  print(f"タイム: {minutes}分{seconds}秒")  
  # driver.quit()
  time.sleep(2)

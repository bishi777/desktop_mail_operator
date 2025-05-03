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

user_data = func.get_user_data()
wait_time = 1.5
mailserver_address = user_data['user'][0]['gmail_account']
mailserver_password = user_data['user'][0]['gmail_account_password']
receiving_address = user_data['user'][0]['user_email']
pcmax_datas = user_data["pcmax"]
# pcmax_datas = pcmax_datas[:9]
profiles = settings.chrome_user_profiles
for p in profiles:
  print(f"🔁 操作中: {p['name']}")
  options = Options()
  options.add_experimental_option("debuggerAddress", f"127.0.0.1:{p['port']}")
  driver = webdriver.Chrome(options=options)
  # 例：ページタイトル取得
  print(f"✅ {p['name']}のURL:", driver.current_url)
  if driver.current_url != "https://pcmax.jp/pcm/member.php" and  driver.current_url != "https://pcmax.jp/pcm/index.php":
    continue
  name = ""

  while True:
    start_time = time.time() 
    for index, i in enumerate(pcmax_datas):
      if p['name'] == i['name']:
        name = i["name"]
        # if  "ゆっこ" != name:
        #   print(name)
        #   continue
        login_id = i["login_id"]
        login_pass = i["password"]
        print(f"{login_id}   {login_pass}")
        gmail_address = i["mail_address"]
        gmail_password= i["gmail_password"]
        fst_message = i["fst_mail"]
        second_message = i["second_message"]
        condition_message = i["condition_message"]
    if name:
      time.sleep(2)
      send_cnt = 2
      try:
          print("新着メールチェック開始")     
          pcmax_2.check_mail(name, driver, login_id, login_pass, gmail_address, gmail_password, fst_message, second_message, condition_message, mailserver_address, mailserver_password)
          driver.get("https://pcmax.jp/pcm/member.php")
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

    elapsed_time = time.time() - start_time  # 経過時間を計算する   
    while elapsed_time < 600:
      time.sleep(30)
      elapsed_time = time.time() - start_time  # 経過時間を計算する
      print(f"待機中~~ {elapsed_time} ")

  

 
  
      
  # driver.quit()
  time.sleep(2)

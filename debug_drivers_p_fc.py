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

# # DevTools Protocol で User-Agent を変更
# driver.execute_cdp_cmd('Network.setUserAgentOverride', {
#     "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
# })
# user_agent_type = "iPhone"
# driver.refresh()
# wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
# time.sleep(0.5)
user_agent_type = "PC"

print(f"タブ数: {len(handles)}")
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
      if user_agent_type == "iPhone":
        name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'header-user-name')
      elif user_agent_type == "PC":
        name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
      while not len(name_on_pcmax):
        main_photo = driver.find_elements(By.CLASS_NAME, 'main_photo')
        if len(main_photo):
          print(8888888888888)
          login_form = driver.find_elements(By.CLASS_NAME, 'login-sub')   
          if len(login_form):
            print(99999999)
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
        pcmax_2.catch_warning_pop("", driver)
        if user_agent_type == "iPhone":
          name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'header-user-name')
        else:
          name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
        re_login_cnt = 0
        while not len(name_on_pcmax):
          time.sleep(5)
          login_button = driver.find_element(By.NAME, "login")
          login_button.click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1.5)
          pcmax_2.catch_warning_pop("", driver)
          if user_agent_type == "iPhone":
            name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'header-user-name')
          else:
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
        # if  "りな" != name:
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
          if user_agent_type == "PC":
            pcmax_2.check_mail(name, driver, login_id, login_pass, gmail_address, gmail_password, fst_message, second_message, condition_message, mailserver_address, mailserver_password, user_agent_type)
            driver.get("https://pcmax.jp/pcm/index.php")
          elif user_agent_type == "iPhone":
            wait = WebDriverWait(driver, 10)
            new_mail_lists = []
            result = pcmax.check_new_mail(i, driver, wait)
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
                print(f'{i["name"]}チェック完了  {now}')
                pass
            else:
                # print("~~~~~~~~~~~~")
                # print(f"{mailaddress} {gmail_password} {receiving_address}")
                if mailserver_address and gmail_password and receiving_address:
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
                    smtpobj.login(mailserver_address, gmail_password)
                    msg = MIMEText(text)
                    msg['Subject'] = subject
                    msg['From'] = mailserver_address
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
          print(f"{name}❌ メールチェック  の操作でエラー: {e}")
          traceback.print_exc()  
        if 6 <= now.hour < 23 or (now.hour == 23 and now.minute <= 45):
          try:
            print("fst_mail送信開始")
            if send_cnt > 0:
              pcmax_2.set_fst_mail(name, driver, fst_message, send_cnt, user_agent_type)
              time.sleep(1.5)   
          except Exception as e:
            print(f"{name}❌ fst_mail  の操作でエラー: {e}")
            traceback.print_exc()   
          driver.get("https://pcmax.jp/pcm/index.php")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1.5)
    elapsed_time = time.time() - start_time  # 経過時間を計算する   
    while elapsed_time < 720:
      time.sleep(20)
      elapsed_time = time.time() - start_time  # 経過時間を計算する
      print(f"待機中~~ {elapsed_time} ")
  print("<<<<<<<<<<<<<ループ折り返し>>>>>>>>>>>>>>>>>>>>>")
  elapsed_time = time.time() - start_loop_time  # 経過時間を計算する   
  minutes, seconds = divmod(int(elapsed_time), 60)
  print(f"タイム: {minutes}分{seconds}秒")  
  # driver.quit()
  time.sleep(2)

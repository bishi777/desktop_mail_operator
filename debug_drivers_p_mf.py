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
from math import ceil
from selenium.common.exceptions import NoSuchElementException


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
minute_index = 0  
minute_flug = True
tab_count = len(handles)
interval_minute = ceil(150 / tab_count)
reset_profile_search_cnt = 0

for i in range(99999):
  start_loop_time = time.time()
  now = datetime.now()
  start_time = time.time() 
  for idx, handle in enumerate(handles): 
    try:
      driver.switch_to.window(handle)
      login_flug = pcmax_2.catch_warning_pop("", driver)
      if login_flug and "制限" in login_flug:
        print("制限がかかっているため、スキップを行います")
        time.sleep(0.5)
        continue
      pcmax_2.catch_warning_pop("", driver)
      pcmax_2.profile_search(driver) 
      # 〜〜〜〜〜〜〜〜〜〜〜〜ユーザーをクリック 〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜
      # https://pcmax.jp/mobile/profile_reference.php
      if "pcmax.jp/mobile/profile_list.php" in driver.current_url:
        mohu_flug = False
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        user_list = driver.find_elements(By.CLASS_NAME, 'profile_card')
        if current_step < len(user_list):
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", user_list[current_step])
          time.sleep(0.4)
          user_list[current_step].find_element(By.CLASS_NAME, "profile_link_btn").click()        
          print(f"足跡付け {current_step}件")    
          time.sleep(0.4)
          search_profile_flug = False
          current_step_flug = True   
        else:
          print("足跡付けのユーザーがいません")
          search_profile_flug = True
      # 〜〜〜〜〜〜〜〜〜〜〜〜〜ユーザー詳細画面から戻る〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜
      elif "pcmax.jp/mobile/profile_detail.php" in driver.current_url:
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          driver.back()
      else:
        print(f"現在のURL: {driver.current_url}")
        name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
        pcmax_2.catch_warning_pop("", driver)
        print(f"名前: {name_on_pcmax[0].text if name_on_pcmax else '名前が見つかりません'}")
        driver.get("https://pcmax.jp/pcm/index.php")   
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(0.5)
        pcmax_2.catch_warning_pop("", driver)
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
          func.send_error(name_on_pcmax[0].text, f"リンクル足跡付けの処理中に再ログインしました")
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(0.5)
        pcmax_2.profile_search(driver)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(0.5)
    # except NoSuchElementException as e:
    #   print("📡 ネット接続エラーの可能性。5分待ってリトライします...")
    #   time.sleep(300)
    #   try:
    #     driver.refresh()
    #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    #     time.sleep(1.5)
    #   except Exception as e2:
    #     print("📨 再実行でも失敗。メール通知します。")
    #     func.send_error("PCMAX ネット接続エラー", str(e2))
    #     raise  # ここで終了するか、ログだけで続行するかは自由
    except Exception as e:
      print(f"❌  足跡付けの操作でエラー: {e}")
      traceback.print_exc()  
    # https://pcmax.jp/mobile/telno_verify_regist.php
  # <<<<<<<<<<<<<プロフ検索再セット>>>>>>>>>>>>>>>>>>>"
  if search_profile_flug:
    current_step = 0
    for idx, handle in enumerate(handles): 
      try:  
        driver.switch_to.window(handle)
        login_flug = pcmax_2.catch_warning_pop("", driver)
        if login_flug and "制限" in login_flug:
          # print("制限がかかっているため、スキップを行います")
          continue
        print("<<<<<<<<<<<<<プロフ検索再セット>>>>>>>>>>>>>>>>>>>")
        driver.get("https://pcmax.jp/pcm/index.php")   
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(0.5)
        pcmax_2.catch_warning_pop("", driver)
        name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
        print(f"名前: {name_on_pcmax[0].text if name_on_pcmax else '名前が見つかりません'}")
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
        pcmax_2.profile_search(driver)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        continue
      # except NoSuchElementException as e:
      #   print("📡 ネット接続エラーの可能性。5分待ってリトライします...")
      #   time.sleep(300)
      #   try:
      #     driver.refresh()
      #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      #     time.sleep(1.5)
      #   except Exception as e2:
      #     print("📨 再実行でも失敗。メール通知します。")
      #     func.send_error("PCMAX ネット接続エラー", str(e2))
      #     raise  # ここで終了するか、ログだけで続行するかは自由
      except Exception as e:
        print(f"❌  プロフ再セット　の操作でエラー: {e}")
        traceback.print_exc()  
      
  if i % 2 == 0:
    print(77777777777)
    print(reset_profile_search_cnt)
    for idx, handle in enumerate(handles): 
      if reset_profile_search_cnt % len(handles) == idx:
        driver.switch_to.window(handle) 
        try:
          driver.get("https://pcmax.jp/pcm/index.php")   
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(0.5)
          pcmax_2.catch_warning_pop("", driver)
          name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
          print(f"名前: {name_on_pcmax[0].text if name_on_pcmax else '名前が見つかりません'}　<<<プロフ検索再セット>>>")
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
          pcmax_2.profile_search(driver)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        # except NoSuchElementException as e:
        #   print("📡 ネット接続エラーの可能性。5分待ってリトライします...")
        #   time.sleep(300)
        #   try:
        #     driver.refresh()
        #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        #     time.sleep(1.5)
        #   except Exception as e2:
        #     print("📨 再実行でも失敗。メール通知します。")
        #     func.send_error("PCMAX ネット接続エラー", str(e2))
        #     raise  # ここで終了するか、ログだけで続行するかは自由
        except Exception as e:
          print(f"❌  プロフ検索再セットの操作でエラー: {e}")
          traceback.print_exc()  
        finally:
          reset_profile_search_cnt += 1
          break
    if reset_profile_search_cnt >= len(handles):
      reset_profile_search_cnt = 0
      print("プロフ検索再セットカウントをリセットしました")
    current_step += 1
    elapsed_time = time.time() - start_time  # 経過時間を計算する   
    print("<<<<<<<<<<<<<ループ折り返し>>>>>>>>>>>>>>>>>>>>>")
    elapsed_time = time.time() - start_loop_time  # 経過時間を計算する   
    minutes, seconds = divmod(int(elapsed_time), 60)
    print(f"タイム: {minutes}分{seconds}秒")  
  if 7 <= now.hour <= 22:
    # if True:
    if now.minute % interval_minute == 0:
      if minute_flug:
        print(f"{interval_minute}分おきの処理")
        handle_to_use = handles[minute_index % len(handles)]
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
          for key in pcmax_datas:
            # print(f"名前: {key['name']}")
            if name_on_pcmax[0].text == key["name"]:
              post_title = key["post_title"]
              post_content = key["post_content"]
              if not post_title or not post_content:
                print("掲示板タイトルと投稿内容が設定されていません")
                print(  f"名前: {key['name']}, タイトル: {key['post_title']}, 内容: {key['post_content']}")
              else:
                pcmax_2.re_post(driver,wait, post_title, post_content)
                driver.get("https://pcmax.jp/pcm/index.php")
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                pcmax_2.catch_warning_pop("", driver)
              pcmax_2.profile_search(driver)
              minute_flug = False
              break
        # except NoSuchElementException as e:
        #   print("📡 ネット接続エラーの可能性。5分待ってリトライします...")
        #   time.sleep(300)
        #   try:
        #     driver.refresh()
        #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        #     time.sleep(1.5)
        #   except Exception as e2:
        #     print("📨 再実行でも失敗。メール通知します。")
        #     func.send_error("PCMAX ネット接続エラー", str(e2))
        #     raise  # ここで終了するか、ログだけで続行するかは自由
        except Exception as e:
          print(f"❌ {interval_minute}分おき処理でエラー: {e}")
          traceback.print_exc()
        minute_index += 1  
    else:
      minute_flug = True
    
    


    

    
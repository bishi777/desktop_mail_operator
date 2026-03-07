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
import argparse
import re

def reset_metrics_keep_check_date(d: dict) -> dict:
    metric_keys = ["fst", "rf", "check_first", "check_second", "gmail_condition", "check_more"]
    new_d = {}
    for name, v in (d or {}).items():
        if isinstance(v, dict):
            cd = v.get("check_date", None)
        else:
            # 旧仕様: v が int の場合は fst の値、check_date は無し
            cd = None
        new_d[name] = {k: 0 for k in metric_keys}
        new_d[name]["check_date"] = cd
    return new_d

def parse_port():
    p = argparse.ArgumentParser()
    p.add_argument("port", nargs="?", type=int, help="remote debugging port")
    args = p.parse_args()
    if args.port is not None:
        return args.port
    return getattr(settings, "pcmax_ch_port", None)

def main_syori():
  PORT = parse_port()
  user_data = func.get_user_data()
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
  spare_mail_info_2 = [
    "ryapya694@ruru.be",
    "misuzu414510@gmail.com",
    "xdcwqbnhosxnvtbp",
  ]
  
  pcmax_datas = user_data["pcmax"]
  options = Options()

  if PORT is not None:
      options.add_experimental_option("debuggerAddress", f"127.0.0.1:{PORT}")
  else:
      print("[INFO] No remote-debugging port provided. Launching Chrome normally.")
  driver = webdriver.Chrome(options=options)
  wait = WebDriverWait(driver, 10)
  report_dict = {}
  one_hour_report_dict = {}
  send_flug = False
  roll_cnt = 1
  start_time = datetime.now()
  active_chara_list = []

  while True:
    mail_info = random.choice([user_mail_info, spare_mail_info, spare_mail_info_2])
    start_loop_time = time.time()
    now = datetime.now()
    handles = driver.window_handles
    print(f"タブ数:{len(handles)}")
    print("<<<<<<<ループスタート🏃‍♀️🏃‍♀️🏃‍♀️🏃‍♀️🏃‍♀️>>>>>>>>>>>>>>>>>>>>>>>>>")
    for idx, handle in enumerate(handles): 
      driver.switch_to.window(handle)
      if "pcmax" not in driver.current_url and "linkleweb" not in driver.current_url:
        continue
      login_flug = pcmax_2.catch_warning_pop("", driver)
      if login_flug and "制限" in login_flug:
        print("制限がかかっているため、スキップを行います")
        continue
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
        pcmax_2.catch_warning_pop("", driver)
        name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')   
        if name_on_pcmax:
          name = name_on_pcmax[0].text
        login_retry_cnt = 0
        while not len(name_on_pcmax):
          # 再ログイン処理
          pcmax_2.catch_warning_pop("", driver)
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
              time.sleep(140)
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
            if re_login_cnt > 2:
              print("再ログイン失敗")
              break   
          name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
          if len(name_on_pcmax):
            func.send_error(name_on_pcmax[0].text, f"リンクルチェックメール、足跡がえしの処理中に再ログインしました")   
          else:
            func.send_error("", f"リンクルチェックメール、足跡がえしの処理中に再ログインしました")
        name_on_pcmax = name_on_pcmax[0].text
        now = datetime.now()
        print(f"~~~~~~~~~~~{idx+1}キャラ目:{name_on_pcmax}~~~~~{now.strftime('%m-%d %H:%M:%S')}~~~~~~~~~~")  
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
      for idex, i in enumerate(pcmax_datas):
        login_id = ""   
        if name_on_pcmax == i['name']:
        # if name_on_pcmax == "ゴン太":
          if name_on_pcmax not in active_chara_list:
            active_chara_list.append(name_on_pcmax)
          if name_on_pcmax not in report_dict:
            report_dict[name_on_pcmax] = {"fst":0,"rf":0, "check_first":0, "check_second":0, "gmail_condition":0, "check_more":0, "check_date": None}
          if name_on_pcmax not in one_hour_report_dict:
            one_hour_report_dict[name_on_pcmax] = {"fst":0,"rf":0, "check_first":0, "check_second":0, "gmail_condition":0, "check_more":0, "check_date": None}
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
          two_messages_flug = i["two_message_flug"]
          fst_flug = i["fst_flug"]
          chara_prompt = i["system_prompt"]
          if two_messages_flug:
            print(f"******{name}は2通メール送信対象キャラです******")
          # if roll_cnt % 2 == 0:
          #   send_cnt = 3
          # else:
          #   send_cnt = 2  
          # print(777)
          # print(PORT)
          # print(PORT == "9223")
          # if PORT == 9223:
          #   print("変更前:", func.get_current_ip())
          #   func.change_tor_ip()
          #   time.sleep(6)
          #   print("変更後:", func.get_current_ip())
          if 6 <= now.hour < 24:  
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
              unread_user, check_first, check_second, gmail_condition, check_more, check_date = pcmax_2.check_mail(name, driver, login_id, login_pass, gmail_address, gmail_password, fst_message, return_foot_message, mail_img, second_message, condition_message, confirmation_mail, mail_info, chara_prompt)
              print("新着メールチェック終了✅")
              report_dict[name]["check_first"] = report_dict[name]["check_first"] + check_first
              report_dict[name]["check_second"] = report_dict[name]["check_second"] + check_second
              report_dict[name]["gmail_condition"] = report_dict[name]["gmail_condition"] + gmail_condition
              report_dict[name]["check_more"] = report_dict[name]["check_more"] + check_more
              if check_date:
                report_dict[name]["check_date"] = check_date
                one_hour_report_dict[name]["check_date"] = check_date
              one_hour_report_dict[name]["check_first"] = one_hour_report_dict[name]["check_first"] + check_first
              one_hour_report_dict[name]["check_second"] = one_hour_report_dict[name]["check_second"] + check_second
              one_hour_report_dict[name]["gmail_condition"] = one_hour_report_dict[name]["gmail_condition"] + gmail_condition
              one_hour_report_dict[name]["check_more"] = one_hour_report_dict[name]["check_more"] + check_more
            except Exception as e:
              print(f"{name}❌ メールチェック  の操作でエラー: {e}")
              traceback.print_exc()  
          
          if name == "777":
            iikamo_cnt = 3
            footprint_count = 14
            returnfoot_cnt = 2
          else:
            iikamo_cnt = 1
            footprint_count = random.randint(7,11)
            returnfoot_cnt = 1
          if fst_flug:
            if 6 <= now.hour < 24:  
              # roll_cntが0の時
              if roll_cnt % 2 == 0:
                send_cnt = 3
              else:
                send_cnt = 2
              try:
                print(f"✅fstメール送信開始 送信数:{send_cnt}")
                fm_cnt = pcmax_2.set_fst_mail(name, driver, fst_message, send_cnt, mail_img, iikamo_cnt, two_messages_flug, mail_info)
                print(f"✅fstメール送信終了　トータルカウント{report_dict[name]['fst'] + fm_cnt}")
                report_dict[name]["fst"] = report_dict[name]["fst"] + fm_cnt
                one_hour_report_dict[name]["fst"] = one_hour_report_dict[name]["fst"] + fm_cnt
              except Exception as e:
                print(f"{name}❌ fstメール送信  の操作でエラー: {e}")
                traceback.print_exc()  
              if roll_cnt % 6 == 0:   
                print(f"🏃‍♀️rfメール送信開始 送信数:{returnfoot_cnt}") 
                try:
                  rf_cnt = pcmax_2.return_footmessage(name, driver, return_foot_message, returnfoot_cnt, mail_img, unread_user, two_messages_flug) 
                  report_dict[name]["rf"] = report_dict[name]["rf"] + rf_cnt
                  one_hour_report_dict[name]["rf"] = one_hour_report_dict[name]["rf"] + rf_cnt
                  print(f"rfメール送信終了　送信数{rf_cnt}🏃‍♀️")
                except Exception as e:
                  print(f"rfメール送信終了　送信数{rf_cnt}🏃‍♀️")
                  print(driver.current_url)
                  print(f"{name}❌ rfメール送信失敗: {type(e).__name__} → {str(e)}")
                  print(traceback.format_exc())
          else:
            if 6 <= now.hour < 23:  
              print(f"🏃‍♀️rfメール送信開始 送信上限:{returnfoot_cnt}") 
              rf_cnt = 0
              try:
                rf_cnt = pcmax_2.return_footmessage(name, driver, return_foot_message, returnfoot_cnt, mail_img, unread_user, two_messages_flug) 
                report_dict[name]["rf"] = report_dict[name]["rf"] + rf_cnt
                one_hour_report_dict[name]["rf"] = one_hour_report_dict[name]["rf"] + rf_cnt
                print(f"rfメール送信終了　送信数{rf_cnt}🏃‍♀️")
              except Exception as e:
                print(f"rfメール送信終了　送信数{rf_cnt}🏃‍♀️")
                print(driver.current_url)
                print(f"{name}❌ rfメール送信失敗: {type(e).__name__} → {str(e)}")
                print(traceback.format_exc())
              try:
                print(f"🐾🐾🐾🐾足跡付け開始 {footprint_count}件 いいかも{iikamo_cnt}件🐾🐾🐾🐾")
                pcmax_2.make_footprint(name, driver, footprint_count, iikamo_cnt)
              except Exception as e:
                print(f"{name}❌ 足跡付け  の操作でエラー: {e}")
                traceback.print_exc()
          if now.hour % 6 == 0 or now.hour == 22:
            if send_flug:
              try:
                body = func.format_progress_mail(report_dict, now)
                func.send_mail(
                  body,
                  mail_info,
                  f"PCMAX 6時間の進捗報告  開始時間：{start_time.strftime('%Y-%m-%d %H:%M:%S')}",
                )
                send_flug = False
                report_dict = reset_metrics_keep_check_date(report_dict)
                start_time = datetime.now()
              except Exception as e:
                print(f"{name}❌ 6時間の進捗報告  の操作でエラー: {e}")
                traceback.print_exc()   
                print('~~~~~~~~~')
                print(mail_info)
          else:
            send_flug = True

    elapsed_time = time.time() - start_loop_time  # 経過時間を計算する   
    wait_cnt = 0
    while elapsed_time < 600:
      time.sleep(10)
      elapsed_time = time.time() - start_loop_time  # 経過時間を計算する
      if wait_cnt % 6 == 0:
        print(f"待機中~~ {elapsed_time} ")
      wait_cnt += 1
    print("🎉🎉🎉<<<<<<<<<<<<<ループ終了>>>>>>>>>>>>>>>>>>>>>🎉🎉🎉")
    elapsed_time = time.time() - start_loop_time  # 経過時間を計算する   
    minutes, seconds = divmod(int(elapsed_time), 60)
    print(f"🏁🏁🏁タイム: {minutes}分{seconds}秒　🏁🏁🏁") 
    
    #カウント 
    roll_cnt += 1
    # if roll_cnt % 12 == 0:
    #   now = datetime.now()
    #   if 6 <= now.hour < 23:
    #     print(f"🔄 {roll_cnt}回目のループ完了 {now.strftime('%Y-%m-%d %H:%M:%S')}")
    #     try:
    #       body = func.format_progress_mail(one_hour_report_dict, now)
    #       func.send_mail(
    #           body,
    #           mail_info,
    #           f"PCMAX 2時間の進捗報告",
    #       )
    #       send_flug = False
    #       one_hour_report_dict = reset_metrics_keep_check_date(one_hour_report_dict)
    #     except Exception as e:
    #       print(f"{name}❌ 2時間のfstmailの報告  の操作でエラー: {e}")
    #       traceback.print_exc()   
    #       print('~~~~~~~~~')
    #       print(mail_info)

if __name__ == "__main__":
  try:
    # ===== あなたのメイン処理 =====
    main_syori()

  except KeyboardInterrupt:
    print("\n🛑 手動終了 (Ctrl + C) により処理を中断しました。安全に終了します。")
    
  except Exception as e:
    print(f"\n❌ 予期せぬエラーが発生しました: {e}")
    traceback.print_exc()
       
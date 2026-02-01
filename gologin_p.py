#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test_gologin.py
起動済みの GoLogin(Orbita) プロファイルに attach して happymail 処理を実行する
"""

import sys
import time
import random
import traceback
import re
import subprocess
from datetime import datetime
from typing import Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from urllib3.exceptions import ReadTimeoutError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import settings
from widget import pcmax_2, func
import linecache

# ==========================
# 既存設定（そのまま）
# ==========================
user_data = func.get_user_data()
pcmax_info = user_data["pcmax"]

mailaddress = user_data['user'][0]['gmail_account']
gmail_password = user_data['user'][0]['gmail_account_password']
receiving_address = user_data['user'][0]['user_email']

user_mail_info = [
    receiving_address, mailaddress, gmail_password,
] if mailaddress and gmail_password and receiving_address else None

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

matching_daily_limit = 77
returnfoot_daily_limit = 77
oneday_total_match = 77
oneday_total_returnfoot = 77
return_check_cnt = 2
report_dict = {}
one_hour_report_dict = {}
roll_cnt = 1

CHROMEDRIVER_VERSION = settings.GOLOGIN_CHROMEDRIVER_VERSION

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
# ==========================
# 起動中プロファイル取得
# ==========================
def get_running_profiles() -> Dict[str, int]:
    """
    return:
      { profile_name: remote_debugging_port }
    """
    cmd = ["bash", "-lc", "ps -axww -o command="]
    out = subprocess.check_output(cmd, text=True, errors="ignore")

    profiles = {}

    for line in out.splitlines():
        if "/Orbita-Browser.app/Contents/MacOS/Orbita" not in line:
            continue

        m_profile = re.search(r"--gologin-profile=([^\s]+)", line)
        m_port = re.search(r"--remote-debugging-port=(\d+)", line)

        if m_profile and m_port:
            profiles[m_profile.group(1)] = int(m_port.group(1))

    return profiles


# ==========================
# attach
# ==========================


def attach_driver(port: int) -> webdriver.Chrome:
    opts = Options()
    opts.add_experimental_option(
        "debuggerAddress", f"127.0.0.1:{port}"
    )

    service = Service(
        ChromeDriverManager(driver_version=CHROMEDRIVER_VERSION).install()
    )

    return webdriver.Chrome(service=service, options=opts)


# ==========================
# main
# ==========================
def main():
    target_names = sys.argv[1:]  # [] or ["デバック", "レイナ"]
    drivers = {}  # profile_name -> webdriver
    waits = {}    # 
    running_profiles = get_running_profiles()

    if not running_profiles:
        print("[ERROR] 起動中の GoLogin プロファイルがありません")
        sys.exit(1)

    # 対象決定
    if target_names:
        targets = {
            name: running_profiles[name]
            for name in target_names
            if name in running_profiles
        }

        for name in target_names:
            if name not in running_profiles:
                print(f"[WARN] 未起動プロファイル: {name}")

        if not targets:
            print("[ERROR] 指定プロファイルは全て未起動")
            sys.exit(1)
    else:
        # 引数なし → 全プロファイル
        targets = running_profiles

    print(f"[INFO] 実行対象プロファイル数: {len(targets)}")

    # ==========================
    # pcmax メインループ
    # ==========================
    while True:
      mail_info = random.choice([user_mail_info, spare_mail_info, spare_mail_info_2])
      if 6 <= datetime.now().hour < 22: 
        for profile_name, port in targets.items():        
          start_loop_time = time.time()
          try:
            # ===== attach は1回だけ =====
            if profile_name not in drivers or drivers[profile_name] is None:
                print(f"[ATTACH] {profile_name} port={port}")
                driver = attach_driver(port)
                drivers[profile_name] = driver
                waits[profile_name] = WebDriverWait(driver, 10)
            else:
                driver = drivers[profile_name]

            wait = waits[profile_name]
            

            pcmax_2.catch_warning_pop("", driver)

            ds_user_display_name = driver.find_elements(
                By.CLASS_NAME, "mydata_name"
            )
            if not ds_user_display_name:
               ds_user_display_name = driver.find_element(By.ID, "overview").find_elements(By.TAG_NAME, "p")
            ds_user_display_name = ds_user_display_name[0].text
            for i in pcmax_info:
              if i["name"] != ds_user_display_name:
                  continue
              # ===== 以降 pcmax 既存処理 =====
              if ds_user_display_name not in report_dict:
                report_dict[ds_user_display_name] = {"fst":0,"rf":0, "check_first":0, "check_second":0, "gmail_condition":0, "check_more":0, "check_date": None}
              if ds_user_display_name not in one_hour_report_dict:
                one_hour_report_dict[ds_user_display_name] = {"fst":0,"rf":0, "check_first":0, "check_second":0, "gmail_condition":0, "check_more":0, "check_date": None}
              name = i["name"]
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
              if two_messages_flug:
                print(f"******{name}は2通メール送信対象キャラです******")
                                
              if 6 <= datetime.now().hour < 23:
                try:
                  top_image_flug = pcmax_2.check_top_image(name,driver)
                  if top_image_flug:
                    now = datetime.now()
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
                  unread_user, check_first, check_second, gmail_condition, check_more, check_date = pcmax_2.check_mail(name, driver, login_id, login_pass, gmail_address, gmail_password, fst_message, return_foot_message, mail_img, second_message, condition_message, confirmation_mail, mail_info)
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
                  footprint_count = random.randint(4,8)
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
                  now = datetime.now()
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
          
          except WebDriverException as e:
              tb = e.__traceback__
              last = traceback.extract_tb(tb)[-1]

              print("[ERROR]", e)
              traceback.print_exc()
              continue
          except Exception:
              print(traceback.format_exc())
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
       




if __name__ == "__main__":
    main()

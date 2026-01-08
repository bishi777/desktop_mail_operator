#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test_gologin.py
起動済みの GoLogin(Orbita) プロファイルに後から attach して Selenium で操作する。

使い方例:
  python test_gologin.py --profile 22
  python test_gologin.py --profile レイナ
"""
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchWindowException, WebDriverException, TimeoutException
from urllib3.exceptions import ReadTimeoutError
import random
import traceback
import argparse
import re
import subprocess
import sys
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from widget import happymail, func

user_data = func.get_user_data()
happy_info = user_data["happymail"]
mailaddress = user_data['user'][0]['gmail_account']
gmail_password = user_data['user'][0]['gmail_account_password']
receiving_address = user_data['user'][0]['user_email']
if mailaddress and gmail_password and receiving_address:
  user_mail_info = [
    receiving_address, mailaddress, gmail_password, 
  ]
spare_mail_info = [
  "ryapya694@ruru.be",  
  "siliboco68@gmail.com",
  "akkcxweqzdplcymh",
]

matching_daily_limit, returnfoot_daily_limit, oneday_total_match, oneday_total_returnfoot = 77, 77, 77, 77
def find_remote_debugging_port(profile: str) -> Optional[int]:
    """
    macOSの ps から、指定した gologin-profile の remote-debugging-port を探す。
    起動済みプロファイルを操作するために必要。
    """
    # Orbita本体プロセスのコマンドラインを全部読む
    cmd = ["bash", "-lc", "ps -axww -o command="]
    out = subprocess.check_output(cmd, text=True, errors="ignore")

    # Orbita本体 + gologin-profile が付いてる行を探す
    # 例:
    # .../Orbita ... --remote-debugging-port=19316 ... --gologin-profile=22 ...
    for line in out.splitlines():
        if "/Orbita-Browser.app/Contents/MacOS/Orbita" not in line:
            continue
        if f"--gologin-profile={profile}" not in line:
            continue

        m = re.search(r"--remote-debugging-port=(\d+)", line)
        if m:
            return int(m.group(1))

    return None


def attach_driver(port: int, driver_version: str = "141.0.7390.54") -> webdriver.Chrome:
    """
    DevTools port に attach して既存ブラウザを操作できる driver を返す。
    Orbitaのバージョンに合う chromedriver を使う（あなたの環境では 141.0.7390.54）。
    """
    debugger_address = f"127.0.0.1:{port}"

    opts = Options()
    opts.add_experimental_option("debuggerAddress", debugger_address)

    service = Service(ChromeDriverManager(driver_version=driver_version).install())
    return webdriver.Chrome(service=service, options=opts)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, help="GoLoginの起動済みプロファイル名（例: 22 / レイナ）")
    parser.add_argument("--url", default="https://happymail.co.jp", help="開くURL（テスト用）")
    parser.add_argument("--driver-version", default="141.0.7390.54", help="chromedriverのバージョン（Orbitaに合わせる）")
    args = parser.parse_args()
    port = find_remote_debugging_port(args.profile)
    if port is None:
        print(f"[ERROR] profile '{args.profile}' の remote-debugging-port が見つかりません。")
        print("  - start_gologin.py でそのプロファイルを起動しているか確認")
        print("  - もしくは `ps -axww | grep remote-debugging-port | grep gologin-profile` で確認")
        sys.exit(1)
    # print(f"[OK] profile={args.profile} port={port}")
    driver = None
    for loop_cnt in range(99999):
        start_loop_time = time.time()
        try:
            happymail_new_list = []
            driver = attach_driver(port, driver_version=args.driver_version)
            wait = WebDriverWait(driver, 10)
            mail_info = random.choice([user_mail_info, spare_mail_info])
            # 例: 操作テスト
            
            print("[INFO] title:", driver.title)
            print("[INFO] current_url:", driver.current_url)
            
            # ここにあなたのSelenium操作を追加していけばOK
            happymail.catch_warning_screen(driver)
            if not "happymail.co.jp/app/html/mbmenu.php" in driver.current_url:
                driver.get("https://happymail.co.jp/app/html/mbmenu.php")
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(0.5)
            ds_user_display_name = driver.find_element(By.CLASS_NAME, value="ds_user_display_name").text
            for i in happy_info:
                name = i["name"]
                if name != ds_user_display_name:
                    continue
                login_id = i["login_id"]
                password = i["password"]
                print(f"Processing user: {name}")
                return_foot_message = i["return_foot_message"]
                fst_message = i["fst_message"]
                post_return_message = i["post_return_message"]
                second_message = i["second_message"]
                conditions_message = i["condition_message"]
                confirmation_mail = i["confirmation_mail"]
                return_foot_img = i["chara_image"]
                gmail_address = i["mail_address"]
                gmail_password = i["gmail_password"]
                

                #### 新着メールチェック ###
                # try:
                #     happymail_new = happymail.multidrivers_checkmail(name, driver, wait, login_id, password, return_foot_message, fst_message, post_return_message, second_message, conditions_message, confirmation_mail,return_foot_img, gmail_address, gmail_password)
                #     if happymail_new:
                #         happymail_new_list.extend(happymail_new)
                #     if happymail_new_list:
                #         title = f"happy新着 {name}"
                #         text = ""
                #         img_path = None
                #         for new_mail in happymail_new_list:
                #             text = text + new_mail + ",\n"
                #         if "警告" in text or "NoImage" in text or "利用" in text :
                #             if mail_info:
                #                 img_path = f"{i['name']}_ban.png"
                #                 driver.save_screenshot(img_path)
                #                 # 圧縮（JPEG化＋リサイズ＋品質調整）
                #                 img_path = func.compress_image(img_path)  # 例: screenshot2_compressed.jpg ができる
                #                 title = "メッセージ"
                #                 text = f"ハッピーメール {i['name']}:{i['login_id']}:{i['password']}:  {text}"   
                #         # メール送信
                #         if mail_info:
                #             func.send_mail(text, mail_info, title, img_path)
                #         else:
                #             print("通知メールの送信に必要な情報が不足しています")
                #             print(f"{mailaddress}   {gmail_password}  {receiving_address}")
                #     print(f"{name} ✅ 新着メールチェック完了")
                # except NoSuchWindowException:
                #     pass
                # except ReadTimeoutError as e:
                #     print("🔴 ページの読み込みがタイムアウトしました:", e)
                #     driver.refresh()
                #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                # except Exception as e:
                #     print(traceback.format_exc())
                # time.sleep(1)
                ### マッチング、足跡返し
                now = datetime.now()
                # if 6 <= now.hour < 22:
                #     try:
                #         if loop_cnt % 2 == 0:
                #             send_cnt = 2
                #         else:
                #             send_cnt = 1
                #         return_foot_counted = happymail.return_footpoint(name, driver, wait, return_foot_message, 2, 3, 2, return_foot_img, fst_message, matching_daily_limit, returnfoot_daily_limit, oneday_total_match, oneday_total_returnfoot, send_cnt)
                #         # print(return_foot_counted) 
                #     except NoSuchWindowException:
                #         pass
                #     except ReadTimeoutError as e:
                #         print("🔴 ページの読み込みがタイムアウトしました:", e)
                #         driver.refresh()
                #         wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                #     except Exception as e:
                #         print(traceback.format_exc())
                #     time.sleep(1)
                ### 足跡付け ###
                try:
                    mf_cnt = 7
                    mf_type_cnt = 1
                    happymail.mutidriver_make_footprints(name, login_id, password, driver, wait, mf_cnt, mf_type_cnt)
                except NoSuchWindowException:
                    print(f"NoSuchWindowExceptionエラーが出ました, {e}")
                    pass
                except ReadTimeoutError as e:
                    print("🔴 ページの読み込みがタイムアウトしました:", e)
                    driver.refresh()
                    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                except Exception as e:
                    print(traceback.format_exc())
                
        except WebDriverException as e:
            print("[ERROR] WebDriverException:", e)
            print("再接続を試みます...")
            time.sleep(3)
            continue
        # ループの間隔を調整
        elapsed_time = time.time() - start_loop_time  # 経過時間を計算する  
        while elapsed_time < 720:
            time.sleep(30)
            elapsed_time = time.time() - start_loop_time  # 経過時間を計算する
            if wait_cnt % 2 == 0:
                print(f"待機中~~ {elapsed_time} ")
            wait_cnt += 1 
    # finally:
    #     # “ブラウザを閉じたくない”場合でも quit は基本OK（Selenium接続が切れるだけのことが多い）
    #     # もし閉じてしまうなら、この行をコメントアウトして運用してください。
    #     if driver:
    #         try:
    #             driver.quit()
    #         except Exception:
    #             pass


if __name__ == "__main__":
    main()

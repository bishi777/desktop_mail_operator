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
from widget import happymail, func
import linecache

# ==========================
# 既存設定（そのまま）
# ==========================
user_data = func.get_user_data()
happy_info = user_data["happymail"]

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

matching_daily_limit = 77
returnfoot_daily_limit = 77
oneday_total_match = 77
oneday_total_returnfoot = 77

CHROMEDRIVER_VERSION = settings.GOLOGIN_CHROMEDRIVER_VERSION


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
    # happymail メインループ
    # ==========================
    for loop_cnt in range(99999):
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
                # driver = attach_driver(port)
                # wait = WebDriverWait(driver, 10)

                happymail.catch_warning_screen(driver)

                if "mbmenu.php" not in driver.current_url:
                    driver.get("https://happymail.co.jp/app/html/mbmenu.php")
                    wait.until(
                        lambda d: d.execute_script(
                            "return document.readyState"
                        ) == "complete"
                    )

                ds_user_display_name = driver.find_element(
                    By.CLASS_NAME, "ds_user_display_name"
                ).text

                for i in happy_info:
                    if i["name"] != ds_user_display_name:
                        continue

                    name = i["name"]
                    print(f"Processing user: {name}")

                    # ===== 以降 happymail 既存処理（完全そのまま） =====
                    happymail.multidrivers_checkmail(
                        name, driver, wait,
                        i["login_id"], i["password"],
                        i["return_foot_message"],
                        i["fst_message"],
                        i["post_return_message"],
                        i["second_message"],
                        i["condition_message"],
                        i["confirmation_mail"],
                        i["chara_image"],
                        i["mail_address"],
                        i["gmail_password"]
                    )
                    
                    if 6 <= datetime.now().hour < 22:
                        if loop_cnt % 10 == 0:
                            send_cnt = 2
                        elif loop_cnt % 5 == 0:
                            send_cnt = 1
                        else:
                            send_cnt = 0

                        if send_cnt:
                            happymail.return_footpoint(
                                name, driver, wait,
                                i["return_foot_message"],
                                2, 3, 2,
                                i["chara_image"],
                                i["fst_message"],
                                matching_daily_limit,
                                returnfoot_daily_limit,
                                oneday_total_match,
                                oneday_total_returnfoot,
                                send_cnt,
                            )

                    happymail.mutidriver_make_footprints(
                        name,
                        i["login_id"],
                        i["password"],
                        driver,
                        wait,
                        7,
                        1
                    )

            
            except WebDriverException as e:
                tb = e.__traceback__
                last = traceback.extract_tb(tb)[-1]

                print("[ERROR]", e)
                traceback.print_exc()
                continue
            except Exception:
                print(traceback.format_exc())

        # 12分待機
        while time.time() - start_loop_time < 720:
            print(" 次のループまで待機中...")
            time.sleep(30)



if __name__ == "__main__":
    main()

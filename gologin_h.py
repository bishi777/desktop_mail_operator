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
import subprocess
import re
from typing import Optional


def get_orbita_chrome_version() -> Optional[str]:
    """
    Orbita の Chromium バージョンを取得する
    return: "141.0.7390.54" or None
    """
    try:
        cmd = [
            "bash", "-lc",
            "ls ~/.gologin/browser | grep orbita-browser | tail -n 1"
        ]
        folder = subprocess.check_output(cmd, text=True).strip()

        orbita_path = (
            f"~/.gologin/browser/{folder}/"
            "Orbita-Browser.app/Contents/MacOS/Orbita"
        )

        out = subprocess.check_output(
            ["bash", "-lc", f"{orbita_path} --version"],
            text=True,
            errors="ignore"
        )

        m = re.search(r"Chromium\s+([\d\.]+)", out)
        if m:
            return m.group(1)

    except Exception:
        pass

    return None
def check_chromedriver_version():
    orbita_version = get_orbita_chrome_version()

    if not orbita_version:
        print("[WARN] Orbita の Chrome バージョンを取得できませんでした")
        return

    if orbita_version != settings.gologin_chrome_version:
        print("⚠️ [VERSION MISMATCH]")
        print(f"  Orbita Chrome : {orbita_version}")
        print(f"  settings      : {settings.gologin_chrome_version}")
        print("  👉 chromedriver が attach 失敗する可能性があります")
    else:
        print(f"[OK] Chrome version matched: {orbita_version}")

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

CHROMEDRIVER_VERSION = settings.gologin_chrome_version


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

    return webdriver.Chrome(options=opts)


# ==========================
# main
# ==========================
def main():
    check_chromedriver_version()
    target_names = sys.argv[1:]
    running_profiles = get_running_profiles()

    if not running_profiles:
        print("[ERROR] 起動中の GoLogin プロファイルがありません")
        sys.exit(1)

    if target_names:
        targets = {
            name: running_profiles[name]
            for name in target_names
            if name in running_profiles
        }
    else:
        targets = running_profiles

    print(f"[INFO] 実行対象プロファイル数: {len(targets)}")

    # ==========================
    # driver をプロファイルごとに1回 attach
    # ==========================
    drivers = {}

    for profile_name, port in targets.items():
        try:
            print(f"[ATTACH] {profile_name} port={port}")
            driver = attach_driver(port)
            wait = WebDriverWait(driver, 10)
            drivers[profile_name] = {
                "driver": driver,
                "wait": wait,
                "port": port
            }
        except Exception:
            print(f"[ERROR] attach失敗: {profile_name}")
            print(traceback.format_exc())

    # ==========================
    # 無限ループ（1周＝全プロファイル1回ずつ）
    # ==========================
    loop_cnt = 0

    while True:
        loop_cnt += 1
        print(f"\n[LOOP] ===== {loop_cnt} 周目 =====")

        start_loop_time = time.time()

        for profile_name, ctx in drivers.items():
            driver = ctx["driver"]
            wait = ctx["wait"]
            port = ctx["port"]

            print(f"[RUN] profile={profile_name}")

            try:
                happymail.catch_warning_screen(driver)

                if "mbmenu.php" not in driver.current_url:
                    driver.get("https://happymail.co.jp/app/html/mbmenu.php")
                    wait.until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )

                ds_user_display_name = driver.find_element(
                    By.CLASS_NAME, "ds_user_display_name"
                ).text

                for i in happy_info:
                    if i["name"] != ds_user_display_name:
                        continue

                    name = i["name"]

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
                print(f"[ERROR] {profile_name} WebDriverException")
                print(e)

                # 再 attach（このプロファイルだけ）
                try:
                    driver.quit()
                except Exception:
                    pass

                time.sleep(3)
                new_driver = attach_driver(port)
                drivers[profile_name]["driver"] = new_driver
                drivers[profile_name]["wait"] = WebDriverWait(new_driver, 10)

            except Exception:
                print(traceback.format_exc())

        # ==========================
        # 全プロファイル終わったら待機
        # ==========================
        while time.time() - start_loop_time < 720:
            print(" 次のループまで待機中...")
            time.sleep(30)




if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import re
import time
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


CHROMEDRIVER_VERSION = "141.0.7390.54"


# ===============================
# 起動中の GoLogin プロファイル一覧取得
# ===============================
def get_running_profiles() -> Dict[str, int]:
    """
    戻り値:
      {
        "デバック": 33045,
        "えりか": 33102,
        ...
      }
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
            profile = m_profile.group(1)
            port = int(m_port.group(1))
            profiles[profile] = port

    return profiles


# ===============================
# Selenium attach
# ===============================
def attach_driver(port: int) -> webdriver.Chrome:
    debugger_address = f"127.0.0.1:{port}"

    options = Options()
    options.add_experimental_option("debuggerAddress", debugger_address)

    service = Service(
        ChromeDriverManager(driver_version=CHROMEDRIVER_VERSION).install()
    )
    return webdriver.Chrome(service=service, options=options)


# ===============================
# main
# ===============================
def main():
    # 引数（プロファイル名）取得
    target_profiles: List[str] = sys.argv[1:]

    running_profiles = get_running_profiles()

    if not running_profiles:
        print("[ERROR] 起動中の GoLogin プロファイルが見つかりません")
        sys.exit(1)

    # 対象プロファイル決定
    if target_profiles:
        targets = {
            name: running_profiles[name]
            for name in target_profiles
            if name in running_profiles
        }

        not_found = set(target_profiles) - set(targets.keys())
        for name in not_found:
            print(f"[WARN] プロファイル未起動: {name}")

        if not targets:
            print("[ERROR] 指定したプロファイルが1つも起動していません")
            sys.exit(1)
    else:
        # 引数なし → 全部
        targets = running_profiles

    print(f"[INFO] 操作対象プロファイル数: {len(targets)}")

    # ===============================
    # 各プロファイルを操作
    # ===============================
    for profile, port in targets.items():
        print(f"[OK] profile={profile} port={port}")

        try:
            driver = attach_driver(port)
            print("[INFO] title:", driver.title)
            print("[INFO] current_url:", driver.current_url)

            # 🔽 ここに既存の happymail 処理をそのまま入れてOK
            # driver.get("https://happymail.co.jp/app/html/mbmenu.php")

            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] profile={profile}", e)


if __name__ == "__main__":
    main()

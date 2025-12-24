#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test_gologin.py
起動済みの GoLogin(Orbita) プロファイルに後から attach して Selenium で操作する。

使い方例:
  python test_gologin.py --profile 22
  python test_gologin.py --profile レイナ
"""

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

    print(f"[OK] profile={args.profile} port={port}")

    driver = None
    try:
        driver = attach_driver(port, driver_version=args.driver_version)

        # 例: 操作テスト
        driver.get(args.url)
        time.sleep(2)

        print("[INFO] title:", driver.title)
        print("[INFO] current_url:", driver.current_url)

        # ここにあなたのSelenium操作を追加していけばOK
        # 例: driver.find_element(...).click()

        time.sleep(1)

    finally:
        # “ブラウザを閉じたくない”場合でも quit は基本OK（Selenium接続が切れるだけのことが多い）
        # もし閉じてしまうなら、この行をコメントアウトして運用してください。
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    main()

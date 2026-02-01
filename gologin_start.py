import requests
import time
import argparse
from gologin import GoLogin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
import settings
# =====================
# 設定
# =====================
CHROMEDRIVER_VERSION = settings.GOLOGIN_CHROMEDRIVER_VERSION

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OTI2OTRjMjExODY3MzExN2Y3M2ZjMjYiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2OTI2YTJhNjZhMWI0NGE3OTEzM2NlYzcifQ.F8VKng9UTpAyVE7maKDSbaiFFCfoRGim2qQhyIlQME4"
if not TOKEN:
    raise RuntimeError("GOLOGIN_TOKEN が設定されていません")

API_URL = "https://api.gologin.com/browser/v2"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

# =====================
# 引数処理（複数位置引数）
# =====================
parser = argparse.ArgumentParser()
parser.add_argument(
    "profiles",
    nargs="*",   # ← 複数受け取り
    help="起動するGoLoginプロファイル名（複数指定可 / 省略時は全プロファイル）"
)
args = parser.parse_args()

target_profile_names = args.profiles  # [] or ["デバック", "えりか"]
# PROXY_HOST = settings.JPROXY_PROXYS[target_profile_names]["HOST"]
# PROXY_PORT = settings.JPROXY_PROXYS[target_profile_names]["PORT"]
# PROXY_USER =  settings.JPROXY_PROXYS[target_profile_names]["USER"]
# PROXY_PASS = settings.JPROXY_PROXYS[target_profile_names]["PASS"]
# =====================
# プロファイル一覧取得
# =====================
res = requests.get(API_URL, headers=HEADERS)
res.raise_for_status()
data = res.json()

profiles = data.get("profiles", [])
if not profiles:
    print("プロファイルが見つかりません")
    exit()

# =====================
# 起動対象フィルタ
# =====================
if target_profile_names:
    profiles = [
        p for p in profiles
        if p["name"] in target_profile_names
    ]

    if not profiles:
        print(f"指定されたプロファイルが見つかりません: {target_profile_names}")
        exit()

# =====================
# 起動処理
# =====================
for p in profiles:
    print(f"[START] profile={p['name']}")
    gl = GoLogin({
        "token": TOKEN,
        "profile_id": p["id"],
        "skipProxyCheck": True,
        "setTimezone": False,
        "extra_params": ["--log-level=3"],
        
        
        
        "canvas": {
            "mode": "noise"
        },
        "audioContext": {
            "mode": "noise"
        },
        "webgl": {
            "mode": "noise"
        }
    })

    debugger_address = gl.start()
    print(f"[OK] debugger_address={debugger_address}")

    chrome_options = Options()
    chrome_options.add_experimental_option(
        "debuggerAddress", debugger_address
    )

    service = Service(
        ChromeDriverManager(
            driver_version=CHROMEDRIVER_VERSION
        ).install()
    )

    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )


import requests
import time
import argparse
from gologin import GoLogin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# =====================
# 設定
# =====================
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OTI2OTRjMjExODY3MzExN2Y3M2ZjMjYiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2OTI2YTJhNjZhMWI0NGE3OTEzM2NlYzcifQ.F8VKng9UTpAyVE7maKDSbaiFFCfoRGim2qQhyIlQME4"

API_URL = "https://api.gologin.com/browser/v2"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

# =====================
# 引数処理
# =====================
parser = argparse.ArgumentParser()
parser.add_argument(
    "--profile",
    help="起動するGoLoginプロファイル名（省略時は全プロファイル）"
)
args = parser.parse_args()

target_profile_name = args.profile  # None or str

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
# 起動対象プロファイル選別
# =====================
if target_profile_name:
    profiles = [
        p for p in profiles
        if p["name"] == target_profile_name
    ]

    if not profiles:
        print(f"指定されたプロファイルが見つかりません: {target_profile_name}")
        exit()

# =====================
# プロファイル起動
# =====================
for p in profiles:
    print(f"[START] profile={p['name']}")

    gl = GoLogin({
        "token": TOKEN,
        "profile_id": p["id"],
        "extra_params": [
            "--log-level=3"
        ]
    })

    debugger_address = gl.start()
    print(f"[OK] debugger_address={debugger_address}")

    chrome_options = Options()
    chrome_options.add_experimental_option(
        "debuggerAddress", debugger_address
    )

    service = Service(
        ChromeDriverManager(
            driver_version="141.0.7390.54"
        ).install()
    )

    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )

    driver.get("https://happymail.co.jp/login/")
    time.sleep(3)

    # ※ 必要に応じてここで操作処理を書く
    # driver.qui
    # gl.stop()

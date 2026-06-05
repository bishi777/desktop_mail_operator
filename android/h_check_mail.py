import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback
from datetime import datetime
from widget import func, happymail
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
  StaleElementReferenceException,
  ElementClickInterceptedException,
  InvalidArgumentException,
  NoSuchElementException,
  TimeoutException,
)

import settings  # Android 実機の UDID 等をここに入れておく想定
import h_login


REPOST_TIMES = [(6, 0), (10, 0), (19, 0)]






# 実機の情報（adb devices で表示されるID）
ANDROID_UDID = "OI6LHMB082804428"
# ANDROID_UDID = "a02aca5e"

# ================ ユーティリティ =====================

def create_driver():
    """
    Android 実機 + Chrome 用の Appium WebDriver を生成
    """
    caps = {
        "platformName": "Android",
        "deviceName": ANDROID_UDID,
        "udid": ANDROID_UDID,
        "automationName": "UiAutomator2",
        "browserName": "Chrome",

        "noReset": True,
        "appium:autoGrantPermissions": True,
        "appium:chromedriver_autodownload": True,
        # "appium:chromedriverAutodownload": True,

        "appium:skipDeviceInitialization": True,
        "appium:ignoreHiddenApiPolicyError": True,
        "appium:ignoreSettingsAppInstall": True,
    }
    options = UiAutomator2Options().load_capabilities(caps)
    driver = webdriver.Remote("http://localhost:4723", options=options)
    return driver

def switch_to_web_context(driver, timeout=15):
    """
    NATIVE_APP → CHROMIUM/WEBVIEW へ切り替え
    """
    end = time.time() + timeout
    while time.time() < end:
        contexts = driver.contexts
        # print("contexts:", contexts)
        for ctx in contexts:
            if "CHROMIUM" in ctx or "WEBVIEW" in ctx:
                driver.switch_to.context(ctx)
                return
        time.sleep(0.5)
    raise TimeoutException("Web コンテキストが見つかりませんでした")



# ================== メイン処理 =======================

def run_loop(happy_info):
  android_flug = True
  name = happy_info["name"]
  login_id = happy_info["login_id"]
  login_pass = happy_info["password"]
  post_title = happy_info.get("post_title", "")
  post_contents = happy_info.get("post_contents", "")

  print(f"{login_id} : {login_pass}")
  print(f"=== {name} ログイン処理開始 ===")

  driver = create_driver()
  wait = WebDriverWait(driver, 15)
  # Webコンテキストへ切替（※browserName=ChromeでもNATIVEのことがある）
  switch_to_web_context(driver)
  # ★ 引数の順番に注意：driver, wait, happy_info
  login_ok = h_login.run_loop(driver, wait, happy_info)
  if not login_ok:
    print("ログインに失敗したので処理を中止します")
    return

  # 起動時に既に過ぎている時刻は本日スキップ扱い
  startup = datetime.now()
  def _time_already_past(hm, now):
    target = now.replace(hour=hm[0], minute=hm[1], second=0, microsecond=0)
    return now > target
  repost_done_today = {hm: _time_already_past(hm, startup) for hm in REPOST_TIMES}
  current_date = startup.date()
  skipped = [f"{h:02d}:{m:02d}" for (h, m) in REPOST_TIMES if repost_done_today[(h, m)]]
  if skipped:
    print(f"起動時刻 {startup.strftime('%H:%M')} で過ぎている掲示板投稿時刻をスキップ: {skipped}")

  while True:
    start_loop_time = time.time()
    now = datetime.now()

    # 日付が変わったらフラグをリセット
    if now.date() != current_date:
      repost_done_today = {hm: False for hm in REPOST_TIMES}
      current_date = now.date()
      print(f"日付変更 → 掲示板投稿フラグをリセット")

    # 新着メールチェック
    print("新着チェック")
    try:
      happymail.check_new_mail(happy_info, driver, wait, android_flug)
    except Exception:
      print(traceback.format_exc())
    print("新着チェック完了")

    # 掲示板投稿: 指定時刻を過ぎていて未実行のものがあれば1件だけ実行
    for hm in REPOST_TIMES:
      if repost_done_today[hm]:
        continue
      target = now.replace(hour=hm[0], minute=hm[1], second=0, microsecond=0)
      if now >= target:
        print(f"掲示板投稿開始 (時刻={hm[0]:02d}:{hm[1]:02d})")
        try:
          happymail.re_post(name, driver, wait, post_title, post_contents)
        except Exception:
          print(traceback.format_exc())
        finally:
          repost_done_today[hm] = True
          print(f"掲示板投稿完了 (時刻={hm[0]:02d}:{hm[1]:02d})")
        break

    # ループの間隔を調整
    elapsed_time = time.time() - start_loop_time
    wait_cnt = 0
    while elapsed_time < 600:
      time.sleep(30)
      elapsed_time = time.time() - start_loop_time
      if wait_cnt % 2 == 0:
        print(f"待機中~~ {elapsed_time} ")
      wait_cnt += 1

if __name__ == "__main__":
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
  happy_datas = user_data["happymail"]
  
  for i in happy_datas:
     if i["name"] == "レイナ":
        happy_info = i
 
  run_loop(happy_info)

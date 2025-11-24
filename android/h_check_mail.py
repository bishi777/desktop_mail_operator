import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback
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
  name = happy_info["name"]
  login_id = happy_info["login_id"]
  login_pass = happy_info["password"]
  return_foot_message = happy_info["return_foot_message"]
  return_foot_img = happy_info["chara_image"]
  fst_message = happy_info["fst_message"]

  matching_cnt = 1
  type_cnt = 1
  return_foot_cnt = 1
  matching_daily_limit = 10
  daily_limit = 20
  oneday_total_match = 0
  oneday_total_returnfoot = 0

  print(f"{login_id} : {login_pass}")
  print(f"=== {name} ログイン処理開始 ===")
  print("変更前:", func.get_current_ip())
  func.change_tor_ip()
  time.sleep(6)
  print("変更後:", func.get_current_ip())

  driver = create_driver()
  wait = WebDriverWait(driver, 15)
  # Webコンテキストへ切替（※browserName=ChromeでもNATIVEのことがある）
  switch_to_web_context(driver)
  # ★ 引数の順番に注意：driver, wait, happy_info
  login_ok = h_login.run_loop(driver, wait, happy_info)
  if not login_ok:
    print("ログインに失敗したので処理を中止します")
    return
  while True:
    # 新着メールチェック
    print("新着チェック")
    happymail.check_new_mail(happy_info, driver, wait)
    print("新着チェック完了")
    print("足跡返し")
    happymail.return_footpoint(name, driver, wait, return_foot_message, matching_cnt, type_cnt, return_foot_cnt, return_foot_img, fst_message, matching_daily_limit, daily_limit, oneday_total_match, oneday_total_returnfoot)
    # 足跡付け

    try:
      print("足跡づけ")
      happymail.mutidriver_make_footprints(name, login_id, login_pass, driver, wait)
   
    except Exception as e:
      print(traceback.format_exc())

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

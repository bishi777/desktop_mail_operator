import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidArgumentException, NoSuchElementException, TimeoutException
import time
import traceback
from widget import func, happymail
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementClickInterceptedException,
)
import settings  # Android 実機の UDID 等をここに入れておく想定

# ================= 共通データ ======================




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

def find_by_name(driver, name: str):
    """
    Android Chrome + Appium で By.NAME が invalid locator になる問題を吸収するラッパー

    1. 通常どおり By.NAME を試す
    2. invalid locator の場合は CSSセレクタ [name="..."] で再トライ
    """
    try:
        return driver.find_element(By.NAME, name)
    except InvalidArgumentException:
        # モバイル Chrome だと NAME ロケータが invalid になる場合がある
        return driver.find_element(By.CSS_SELECTOR, f'[name="{name}"]')

# ================== メイン処理 =======================

def run_loop(happy_info):   
  name = happy_info["name"]
  login_id = happy_info["login_id"]
  login_pass = happy_info["password"]
  
  # login_id = "50036634290"
  # login_pass = "ebbh7278"



  print(f"{login_id} : {login_pass}")
  # print(f"=== {name} ログイン処理開始 ===")
  # print("変更前:", func.get_current_ip())
  # func.change_tor_ip()
  # time.sleep(6)
  # print("変更後:", func.get_current_ip())
  driver = None

  driver = create_driver()
  wait = WebDriverWait(driver, 15)
  # Webコンテキストへ切替（※browserName=ChromeでもNATIVEのことがある）
  switch_to_web_context(driver)
  # ログインフォームへ遷移
  url = "https://happymail.co.jp/login/?Log=newspa"
  driver.get(url)
  wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
  # ページロード待ち
  time.sleep(1)

  # フォーム入力
  id_form = func.find_by_id(driver, "TelNo")
  id_form.send_keys(login_id)
  time.sleep(1)
  pass_form = func.find_by_id(driver, "pass_input")
  pass_form.send_keys(login_pass)
  time.sleep(1)   
  send_form = func.find_by_id(driver, "login_btn")
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", send_form)
  time.sleep(1)
  try:
    send_form.click()
    print("クリックした")
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(7)
    print(driver.current_url)
    while ("mbmenu" in driver.current_url) is False:
        time.sleep(5)
        if send_form.is_displayed():
          send_form.click()
          print("クリックした")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(4)
        print(driver.current_url)
    print(f"{name} ✅ ログイン成功")
    print(driver.current_url)
    time.sleep(50)
  except StaleElementReferenceException:
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
  # 遷移完了待 ち
  time.sleep(3)
  # ログイン成功判定
  if "mbmenu" in driver.current_url:
      print(f"{name} ✅ ログイン成功")
  else:
      print(f"{name} ⚠ ログイン成功URLっぽくない: {driver.current_url}")
  # 新着メールチェック
  happymail.check_new_mail(happy_info, driver, wait)



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
 
  run_loop(i)

"""ハッピーメール Androidネイティブアプリ メールチェック (Appium / UiAutomator2)

使い方:
  myenv/bin/python h_app_checkmail_android.py <キャラ名>
  例: myenv/bin/python h_app_checkmail_android.py さとー

前提:
  - 端末がADB接続済み (`adb devices` で device 表示)
  - 端末で対象アプリにログイン済み
  - Appiumサーバが未起動なら本スクリプトが自動起動する
"""
import os
import sys
import time
import socket
import subprocess
import traceback

sys.path.insert(0, os.path.dirname(__file__))

from appium import webdriver
from appium.options.android import UiAutomator2Options
from widget import func, happymail_android


UDID = "a02aca5e"
APP_PACKAGE = "jp.co.i_bec.suteki_happy"
APP_ACTIVITY = "jp.co.i_bec.happymailapp.activity.SplashActivity"
APPIUM_PORT = 4723
APPIUM_URL = f"http://localhost:{APPIUM_PORT}"
APPIUM_BIN = "/Users/yamamotokenta/.nodebrew/current/bin/appium"


def _appium_alive(port=APPIUM_PORT):
  try:
    with socket.create_connection(("127.0.0.1", port), timeout=1):
      return True
  except OSError:
    return False


def start_appium_if_needed():
  if _appium_alive():
    print("[Appium] 既存サーバを使用")
    return None
  print("[Appium] サーバ起動中…")
  proc = subprocess.Popen(
    [APPIUM_BIN, "-p", str(APPIUM_PORT)],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
  )
  for _ in range(30):
    if _appium_alive():
      print("[Appium] サーバ起動完了")
      return proc
    time.sleep(1)
  proc.terminate()
  raise RuntimeError("Appiumサーバの起動に失敗")


def create_driver():
  options = UiAutomator2Options()
  options.platform_name = "Android"
  options.device_name = "Android"
  options.udid = UDID
  options.app_package = APP_PACKAGE
  options.app_activity = APP_ACTIVITY
  options.no_reset = True
  options.auto_grant_permissions = True
  options.new_command_timeout = 300
  options.uiautomator2_server_install_timeout = 120000
  return webdriver.Remote(APPIUM_URL, options=options)


def main():
  if len(sys.argv) < 2:
    print("使い方: myenv/bin/python h_app_checkmail_android.py <キャラ名>")
    sys.exit(1)

  chara_name = sys.argv[1]

  user_data = func.get_user_data()
  if not user_data or user_data == 2:
    print("ユーザーデータ取得失敗")
    sys.exit(1)

  chara_data = next(
    (c for c in user_data.get("happymail", []) if c["name"] == chara_name),
    None,
  )
  if not chara_data:
    print(f"「{chara_name}」が見つかりません")
    print("happymailキャラ一覧:", [c["name"] for c in user_data.get("happymail", [])])
    sys.exit(1)

  print(f"{chara_name} データ取得完了 (login_id: {chara_data.get('login_id')})")

  appium_proc = start_appium_if_needed()
  driver = None
  try:
    print("[Appium] driver作成中…")
    driver = create_driver()
    time.sleep(3)

    result = happymail_android.check_mail(
      name=chara_data["name"],
      driver=driver,
      login_id=chara_data.get("login_id", ""),
      password=chara_data.get("password", ""),
      fst_message=chara_data.get("fst_message", ""),
      second_message=chara_data.get("second_message", ""),
      post_return_message=chara_data.get("post_return_message", ""),
      conditions_message=chara_data.get("condition_message", ""),
      confirmation_mail=chara_data.get("confirmation_mail", ""),
      mail_img=chara_data.get("chara_image", ""),
      gmail_address=chara_data.get("mail_address", ""),
      gmail_password=chara_data.get("gmail_password", ""),
      chara_prompt=chara_data.get("system_prompt", ""),
    )

    if result:
      print("\n--- 通知一覧 ---")
      for r in result:
        print(r)
        print("---")
    else:
      print("\n通知なし")

  except Exception:
    print("実行中エラー:")
    traceback.print_exc()
  finally:
    if driver is not None:
      try:
        driver.quit()
      except Exception:
        pass
      print("[Appium] driver終了")
    if appium_proc is not None:
      appium_proc.terminate()
      try:
        appium_proc.wait(timeout=5)
      except Exception:
        appium_proc.kill()
      print("[Appium] サーバ終了")


if __name__ == "__main__":
  main()

"""ハッピーメール Androidネイティブアプリ プロフィール編集 (Appium / UiAutomator2)

使い方:
  myenv/bin/python h_app_profile_edit_android.py [キャラ名 ...]
  例: myenv/bin/python h_app_profile_edit_android.py いおり

  - 引数なし → user_data の happymail 全キャラを順に処理（端末でログイン中の
    アカウントと login_id が一致するキャラのみ実際に編集される想定）
  - 引数あり → 指定キャラだけ処理

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
from selenium.common.exceptions import WebDriverException
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
  options.new_command_timeout = 600
  options.uiautomator2_server_install_timeout = 120000
  return webdriver.Remote(APPIUM_URL, options=options)


def recover_driver(holder):
  """driver を作り直す。Appium プロセスが応答しないなら kill して再起動。"""
  try:
    holder["driver"].quit()
  except Exception:
    pass
  time.sleep(2)
  if not _appium_alive():
    subprocess.call(["pkill", "-9", "-f", "node.*appium"])
    time.sleep(2)
    start_appium_if_needed()
  time.sleep(2)
  holder["driver"] = create_driver()
  time.sleep(3)
  happymail_android.dismiss_popups(holder["driver"])


def edit_chara_with_retry(chara_data, holder, max_attempts=5):
  """1 キャラに対して re_registration → 検証 → 未反映だけ partial 再実行を最大5回。
  UiAutomator2 クラッシュ時は driver 再作成して継続。
  返り値: 全項目反映で True、失敗で False。
  """
  name = chara_data.get("name", "")
  missing_labels = None
  for attempt in range(1, max_attempts + 1):
    print(f"\n--- [{name}] 試行 {attempt}/{max_attempts} ---")
    try:
      if attempt == 1:
        happymail_android.re_registration(chara_data, holder["driver"])
      else:
        happymail_android.re_registration_partial(chara_data, holder["driver"], missing_labels)
    except WebDriverException as e:
      print(f"[CRASH:{name}] 編集処理: {str(e)[:200]}")
      print(f"[RECOVERY:{name}] driver 再作成中...")
      recover_driver(holder)
    except Exception:
      print(traceback.format_exc())
    time.sleep(2)
    try:
      diffs = happymail_android.verify_profile(holder["driver"], chara_data)
    except WebDriverException as e:
      print(f"[CRASH:{name}] 検証: {str(e)[:200]}")
      recover_driver(holder)
      continue
    if not diffs:
      print(f"[{name}] ✅ 全項目反映完了 (試行{attempt}回)")
      return True
    missing_labels = {label for label, _, _ in diffs}
    print(f"[{name}] 未反映 {len(diffs)} 項目: {sorted(missing_labels)}")
  print(f"[{name}] ❌ {max_attempts}回試行しても全反映に至らず")
  for label, exp, act in diffs:
    print(f"  - {label}: 期待={exp} 実際={act!r}")
  return False


def main():
  target_names = sys.argv[1:]

  user_data = func.get_user_data()
  if not user_data or user_data == 2:
    print("[ERROR] ユーザーデータの取得に失敗しました")
    sys.exit(1)

  happy_info = user_data.get("happymail", [])
  if not happy_info:
    print("[ERROR] happymail キャラが見つかりません")
    sys.exit(1)

  if target_names:
    targets = [c for c in happy_info if c["name"] in target_names]
    missing = [n for n in target_names if not any(c["name"] == n for c in happy_info)]
    for n in missing:
      print(f"[WARN] 未登録キャラ: {n}")
    if not targets:
      print("[ERROR] 指定キャラは全てuser_dataに存在しません")
      sys.exit(1)
  else:
    targets = happy_info

  print(f"[INFO] 実行対象キャラ数: {len(targets)}")

  appium_proc = start_appium_if_needed()
  holder = {"driver": None}
  try:
    print("[Appium] driver作成中…")
    holder["driver"] = create_driver()
    time.sleep(3)
    happymail_android.dismiss_popups(holder["driver"])

    for chara_data in targets:
      name = chara_data["name"]
      print(f"\n=== Processing user: {name} (login_id: {chara_data.get('login_id')}) ===")
      try:
        edit_chara_with_retry(chara_data, holder)
      except Exception:
        print(traceback.format_exc())

  finally:
    if holder["driver"] is not None:
      try:
        holder["driver"].quit()
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

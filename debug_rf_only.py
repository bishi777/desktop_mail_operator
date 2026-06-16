"""足跡返し (return_footmessage) のみを 9223 で 1 回走らせるデバッグスクリプト。
新着メールチェック / fst / 足跡付けはスキップ。"""
import sys
import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from widget import func, pcmax_2

PORT = sys.argv[1] if len(sys.argv) > 1 else "9223"
RF_CNT = int(sys.argv[2]) if len(sys.argv) > 2 else 1

options = Options()
options.add_experimental_option("debuggerAddress", f"127.0.0.1:{PORT}")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# ログイン中キャラ名を取得
print("== STEP 1: ログイン中キャラ確認 ==")
if "pcmax" not in driver.current_url and "linkleweb" not in driver.current_url:
  driver.get("https://pcmax.jp/mobile/index.php")
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
name_ele = driver.find_elements(By.CLASS_NAME, 'mydata_name')
if not name_ele:
  print("❌ ログイン情報が取れません。9223 で pcmax にログインしてください")
  sys.exit(1)
chara_name = name_ele[0].text
print(f"  ログイン中: {chara_name}")
print(f"  URL: {driver.current_url}")

# user_data から該当キャラのデータ取得
print("\n== STEP 2: user_data から chara データ取得 ==")
user_data = func.get_user_data()
chara = None
for c in user_data.get("pcmax", []):
  if c.get("name") == chara_name:
    chara = c
    break
if not chara:
  print(f"❌ user_data に {chara_name} のデータがありません")
  sys.exit(1)

return_foot_message = chara["return_foot_message"]
mail_img = chara["mail_img"]
two_messages_flug = chara["two_message_flug"]
print(f"  return_foot_message (先頭60文字): {return_foot_message[:60]!r}...")
print(f"  mail_img: {mail_img}")
print(f"  two_message_flug: {two_messages_flug}")

# mail_info（通知メール先）
print("\n== STEP 3: mail_info 構築 ==")
mail_info = [
  user_data['user'][0]['user_email'],
  user_data['user'][0]['gmail_account'],
  user_data['user'][0]['gmail_account_password'],
]
print(f"  通知メール受信先: {mail_info[0]}")

# return_footmessage を1回走らせる
print(f"\n== STEP 4: return_footmessage 実行 (send_limit_cnt={RF_CNT}) ==")
unread_user = []
try:
  rf_cnt = pcmax_2.return_footmessage(
    chara_name, driver, return_foot_message, RF_CNT, mail_img,
    unread_user, two_messages_flug, mail_info=mail_info,
  )
  print(f"\n結果: rf_cnt={rf_cnt}")
except Exception as e:
  print(f"❌ 例外: {e}")
  traceback.print_exc()

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import random
import time
from selenium.webdriver.common.by import By
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from selenium.webdriver.support.ui import WebDriverWait
import traceback
from widget import happymail, func
import sqlite3
from selenium.webdriver.chrome.service import Service
from datetime import timedelta
from tkinter import messagebox
from selenium.common.exceptions import NoSuchWindowException
import signal
import shutil
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from urllib3.exceptions import ReadTimeoutError
from datetime import datetime
import settings

user_data = func.get_user_data()
happy_info = user_data["happymail"]
headless = False
# リストを2つに分割する
n = len(happy_info)  
half = n // 2
first_half = happy_info
# first_half = happy_info[half:]  # 後半
# profile_path = "chrome_profiles/h_footprint"
# drivers = {}
service = Service(ChromeDriverManager().install())  # Chrome v141に合うDriverを取得
options = Options()
options.add_experimental_option("debuggerAddress", f"127.0.0.1:{settings.happymail_drivers_port}")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)
handles = driver.window_handles
mailaddress = user_data['user'][0]['gmail_account']
gmail_password = user_data['user'][0]['gmail_account_password']
receiving_address = user_data['user'][0]['user_email']
android = False
last_reset_hour = None  
send_flug = True

if mailaddress and gmail_password and receiving_address:
  user_mail_info = [
    receiving_address, mailaddress, gmail_password, 
  ]
spare_mail_info = [
  "ryapya694@ruru.be",  
  "siliboco68@gmail.com",
  "akkcxweqzdplcymh",
]

try:
  # drivers = happymail.start_the_drivers_login(spare_mail_info, first_half, headless, profile_path, True)
  # 足跡付け、チェックメール　ループ
  return_foot_counted = 0
  mf_cnt = random.randint(5, 9)
  mf_type_cnt = 2
  report_dict = {}
  for i in first_half:
    report_dict[i["name"]] = [0, send_flug, []]

  run_today = True  # 初日は実行、以降は交互に切り替え

  while True:
    now = datetime.now()
    # 開始・終了時刻に ±30分のランダム幅を設定
    start_offset = random.randint(-30, 30)
    end_offset = random.randint(-30, 30)
    today_start = now.replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(minutes=start_offset)
    today_end   = now.replace(hour=22, minute=0, second=0, microsecond=0) + timedelta(minutes=end_offset)

    if run_today:
      # 開始時刻前なら待機
      if now < today_start:
        wait_sec = (today_start - now).total_seconds()
        print(f"本日の開始時刻({today_start.strftime('%H:%M')})まで待機... ({wait_sec/60:.0f}分後)")
        time.sleep(wait_sec)
        now = datetime.now()

      # 終了時刻を過ぎていたら本日はスキップ
      if now >= today_end:
        print(f"終了時刻({today_end.strftime('%H:%M')})を過ぎたため本日はスキップ")
      else:
        # 一日ごとの上限をランダムに設定（5〜15）
        daily_limit = random.randint(6, 11)
        matching_daily_limit = daily_limit
        returnfoot_daily_limit = daily_limit
        oneday_total_match = daily_limit
        oneday_total_returnfoot = daily_limit

        mail_info = random.choice([user_mail_info, spare_mail_info])
        now = datetime.now()
        print(f"\n{'='*50}")
        print(f"本日の処理開始: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"開始:{today_start.strftime('%H:%M')} / 終了:{today_end.strftime('%H:%M')} / 上限:{daily_limit}件")
        print(f"{'='*50}")

        round_cnt = 1
        MIN_ROUND_SEC = 12 * 60  # 1周の最小時間（秒）
        daily_done = {i["name"]: 0 for i in first_half}  # キャラごとの当日累計処理数
        while datetime.now() < today_end:
          now = datetime.now()
          round_start = now
          print(f"\n--- {round_cnt}周目 ({now.strftime('%H:%M:%S')}) ---")
          for idx, handle in enumerate(handles):
            for index, i in enumerate(first_half):

              driver.switch_to.window(handle)
              time.sleep(1)
              current_url = driver.current_url
              if not "happymail.co.jp/app/html/mbmenu.php" in current_url:
                driver.get("https://happymail.co.jp/app/html/mbmenu.php")
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(0.5)
              name_ele = driver.find_elements(By.CLASS_NAME, value="ds_user_display_name")
              if name_ele:
                name = name_ele[0].text
              else:
                print("名前の取得に失敗しました")
                print(driver.current_url)
                continue
              if name == i["name"]:
              # if True:

                print(f"  📄 ---------- {name} ------------{now.strftime('%Y-%m-%d %H:%M:%S')}")
                happymail_new_list = []
                top_image_check = None
                happymail_new = None
                login_id = i["login_id"]
                password = i["password"]
                return_foot_message = i["return_foot_message"]
                fst_message = i["fst_message"]
                post_return_message = i["post_return_message"]
                second_message = i["second_message"]
                conditions_message = i["condition_message"]
                confirmation_mail = i["confirmation_mail"]
                return_foot_img = i["chara_image"]
                gmail_address = i["mail_address"]
                gmail_password = i["gmail_password"]
                chara_prompt = i["system_prompt"]
                matching_cnt = 1
                type_cnt = 1
                return_foot_cnt = 1
                return_check_cnt = 2
                # print("変更前:", func.get_current_ip())
                # func.change_tor_ip()
                # time.sleep(6)
                # print("変更後:", func.get_current_ip())

                # 新着メールチェック
                try:
                  happymail_new = happymail.multidrivers_checkmail(name, driver, wait, login_id, password, return_foot_message, fst_message, post_return_message, second_message, conditions_message, confirmation_mail,return_foot_img, gmail_address, gmail_password, return_check_cnt,android,  chara_prompt,)
                  if happymail_new:
                    happymail_new_list.extend(happymail_new)
                  if happymail_new_list:
                    title = f"happy新着 {name}"
                    text = ""
                    img_path = None
                    for new_mail in happymail_new_list:
                      text = text + new_mail + ",\n"
                      if "警告" in text or "NoImage" in text or "利用" in text :
                        if mail_info:
                          img_path = f"{i['name']}_ban.png"
                          driver.save_screenshot(img_path)
                          # 圧縮（JPEG化＋リサイズ＋品質調整）
                          img_path = func.compress_image(img_path)  # 例: screenshot2_compressed.jpg ができる
                          title = "メッセージ"
                          text = f"ハッピーメール {i['name']}:{i['login_id']}:{i['password']}:  {text}"
                    # メール送信
                    if mail_info:
                      func.send_mail(text, mail_info, title, img_path)
                    else:
                      print("通知メールの送信に必要な情報が不足しています")
                      print(f"{mailaddress}   {gmail_password}  {receiving_address}")
                except NoSuchWindowException:
                  pass
                except ReadTimeoutError as e:
                  print("🔴 ページの読み込みがタイムアウトしました:", e)
                  driver.refresh()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                except Exception as e:
                  print(traceback.format_exc())
                
                # マッチング返し・足跡返し・足跡付け（daily_limit未達の場合のみ）
                if daily_done[name] >= daily_limit:
                  print(f"  {name}: daily_limit({daily_limit})到達済み({daily_done[name]}件) → 新着メールチェックのみ")
                else:
                  send_cnt = 1
                  print(f"  {name}: マッチング返し・足跡返し実行 ({daily_done[name]}/{daily_limit}件)")
                  if report_dict[name][1] and "利用できません" not in happymail_new_list:
                    try:
                      return_foot_counted = happymail.return_footpoint(name, driver, wait, return_foot_message, matching_cnt, type_cnt, return_foot_cnt, return_foot_img, fst_message, matching_daily_limit, returnfoot_daily_limit, oneday_total_match, oneday_total_returnfoot, send_cnt)
                      # [matching_counted, type_counted, return_cnt, matching_limit_flug, returnfoot_limit_flug]
                      if return_foot_counted and len(return_foot_counted) >= 3:
                        done = (return_foot_counted[0] or 0) + (return_foot_counted[2] or 0)
                        daily_done[name] += done
                        print(f"  {name}: 今回+{done}件 → 累計{daily_done[name]}/{daily_limit}件")
                    except Exception as e:
                      print(f"{name}")
                      print(traceback.format_exc())
                      func.send_error(f"{name}", traceback.format_exc())
                # 足跡付け
                if mf_cnt and daily_done[name] < daily_limit:
                  try:
                    happymail.mutidriver_make_footprints(name, login_id, password, driver, wait, mf_cnt, mf_type_cnt)
                  except NoSuchWindowException:
                    print(f"NoSuchWindowExceptionエラーが出ました, {e}")
                    pass
                  except ReadTimeoutError as e:
                    print("🔴 ページの読み込みがタイムアウトしました:", e)
                    driver.refresh()
                    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  except Exception as e:
                    print(traceback.format_exc())
              # elif index == 1:　2個目のタブの処理があれば記載
                if top_image_check:
                  happymail_new_list.append(top_image_check)

          elapsed = (datetime.now() - round_start).total_seconds()
          print(f"  {round_cnt}周目完了: {datetime.now().strftime('%H:%M:%S')} (経過: {elapsed:.0f}秒)")
          wait_sec = MIN_ROUND_SEC - elapsed
          if wait_sec > 0 and datetime.now() < today_end:
            print(f"  次の周まで {wait_sec:.0f}秒待機...")
            time.sleep(wait_sec)
          round_cnt += 1

        print(f"\n本日の処理完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 翌日フラグを切り替え（実行日→スキップ日→実行日...）
    run_today = not run_today

    # 翌日の開始時刻（7時 ± 30分）まで待機
    next_offset = random.randint(-30, 30)
    next_start = (datetime.now() + timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(minutes=next_offset)
    wait_sec = (next_start - datetime.now()).total_seconds()
    status = "実行" if run_today else "スキップ"
    print(f"翌日は【{status}】日。次回チェック: {next_start.strftime('%Y-%m-%d %H:%M')} ({wait_sec/3600:.1f}時間後)")
    time.sleep(wait_sec)
except KeyboardInterrupt:
  # Ctrl+C が押された場合
  print("プログラムが Ctrl+C により中断されました。")
  sys.exit(0)
except Exception as e:
  # 予期しないエラーが発生した場合
  sys.exit(0)
  print("エラーが発生しました:", e)
  traceback.print_exc()
finally:
  # 正常終了時・エラー終了時を問わず、最後に WebDriver を閉じる
  # print('finalyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
  traceback.print_exc() 
  sys.exit(0)

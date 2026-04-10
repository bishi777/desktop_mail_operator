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
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from urllib3.exceptions import ReadTimeoutError
from datetime import datetime
import settings

user_data = func.get_user_data()
happy_info = user_data["happymail"]
first_half = happy_info
port = sys.argv[1] if len(sys.argv) > 1 else settings.happymail_drivers_port
service = Service(ChromeDriverManager().install())
options = Options()
options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
driver = webdriver.Chrome(service=service, options=options)
# [F] CDP経由でnavigator.webdriverを除去
happymail.stealth_setup(driver)
wait = WebDriverWait(driver, 10)
handles = driver.window_handles
mailaddress = user_data['user'][0]['gmail_account']
gmail_password = user_data['user'][0]['gmail_account_password']
receiving_address = user_data['user'][0]['user_email']
android = False
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


def _human_round_interval():
  """[A] 周回間隔を正規分布でランダム化（平均15分、8〜30分）"""
  mean = 15 * 60
  std = 5 * 60
  t = max(8 * 60, min(30 * 60, random.gauss(mean, std)))
  return t


def _should_take_break(round_cnt):
  """[A] 2〜4時間に1回、離席を模倣（20〜40分の休憩）"""
  # 平均10周（15分×10=150分≒2.5時間）ごとに休憩
  if round_cnt > 0 and round_cnt % random.randint(8, 12) == 0:
    return True
  return False


def _process_chara(name, i, driver, wait, mail_info, daily_done, daily_limit,
                   report_dict, fst_daily_done, fst_daily_limit, last_fst_sent,
                   matching_daily_limit, returnfoot_daily_limit,
                   oneday_total_match, oneday_total_returnfoot):
  """1キャラ分の処理（メールチェック→マッチング返し→fst送信）"""
  now = datetime.now()
  print(f"  ---------- {name} ------------{now.strftime('%Y-%m-%d %H:%M:%S')}")
  happymail_new_list = []
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
  gmail_password_c = i["gmail_password"]
  chara_prompt = i["system_prompt"]
  matching_cnt = 1
  type_cnt = 1
  return_foot_cnt = 1
  return_check_cnt = 2

  # [C] 処理リストをシャッフル
  tasks = ["checkmail", "return_foot", "fst"]
  random.shuffle(tasks)
  # ただし一部の周ではランダムにスキップ（人間は毎回全部やらない）
  if random.random() < 0.2:
    skip = random.choice(["return_foot", "fst"])
    tasks = [t for t in tasks if t != skip]
    print(f"  [{name}] 今回は {skip} をスキップ")

  for task in tasks:
    if task == "checkmail":
      # [B] 操作前に人間的な待機
      happymail.human_sleep(1.0, 3.0)
      try:
        happymail_new = happymail.multidrivers_checkmail(
          name, driver, wait, login_id, password, return_foot_message,
          fst_message, post_return_message, second_message, conditions_message,
          confirmation_mail, return_foot_img, gmail_address, gmail_password_c,
          return_check_cnt, android, chara_prompt,
        )
        if happymail_new:
          happymail_new_list.extend(happymail_new)
        if happymail_new_list:
          title = f"happy新着 {name}"
          text = ""
          img_path = None
          for new_mail in happymail_new_list:
            text = text + new_mail + ",\n"
            if "警告" in text or "NoImage" in text or "利用" in text:
              if mail_info:
                img_path = f"{i['name']}_ban.png"
                driver.save_screenshot(img_path)
                img_path = func.compress_image(img_path)
                title = "メッセージ"
                text = f"ハッピーメール {i['name']}:{i['login_id']}:{i['password']}:  {text}"
          if mail_info:
            func.send_mail(text, mail_info, title, img_path)
      except NoSuchWindowException:
        pass
      except ReadTimeoutError as e:
        print("ページの読み込みがタイムアウトしました:", e)
        driver.refresh()
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      except Exception as e:
        print(traceback.format_exc())

    elif task == "return_foot":
      if daily_done[name] >= daily_limit:
        print(f"  {name}: daily_limit({daily_limit})到達済み({daily_done[name]}件)")
        continue
      send_cnt = 1
      print(f"  {name}: マッチング返し・足跡返し実行 ({daily_done[name]}/{daily_limit}件)")
      if report_dict[name][1] and "利用できません" not in happymail_new_list:
        happymail.human_sleep(2.0, 5.0)
        try:
          return_foot_counted = happymail.return_footpoint(
            name, driver, wait, return_foot_message, matching_cnt, type_cnt,
            return_foot_cnt, return_foot_img, fst_message,
            matching_daily_limit, returnfoot_daily_limit,
            oneday_total_match, oneday_total_returnfoot, send_cnt,
          )
          if isinstance(return_foot_counted, list) and len(return_foot_counted) >= 3:
            done = (return_foot_counted[0] or 0) + (return_foot_counted[2] or 0)
            daily_done[name] += done
            print(f"  {name}: 今回+{done}件 → 累計{daily_done[name]}/{daily_limit}件")
        except Exception as e:
          print(f"{name}")
          print(traceback.format_exc())
          func.send_error(f"{name}", traceback.format_exc())

    elif task == "fst":
      fst_interval = random.randint(50, 70) * 60
      elapsed_since_fst = (
        (datetime.now() - last_fst_sent[name]).total_seconds()
        if last_fst_sent[name] else fst_interval + 1
      )
      if fst_daily_done[name] < fst_daily_limit[name] and elapsed_since_fst >= fst_interval:
        happymail.human_sleep(2.0, 5.0)
        try:
          sent_to = happymail.score_and_send_fst_message(
            name, driver, wait, fst_message, return_foot_img,
            user_check_cnt=random.randint(7, 11),
          )
          if sent_to:
            fst_daily_done[name] += 1
            last_fst_sent[name] = datetime.now()
            print(f"  {name}: fst送信済み {fst_daily_done[name]}/{fst_daily_limit[name]}件")
        except NoSuchWindowException:
          print("NoSuchWindowExceptionエラーが出ました")
        except ReadTimeoutError as e:
          print("ページの読み込みがタイムアウトしました:", e)
          driver.refresh()
          wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        except Exception as e:
          print(traceback.format_exc())
      else:
        next_fst = max(0, fst_interval - elapsed_since_fst)
        print(f"  {name}: fst送信スキップ ({fst_daily_done[name]}/{fst_daily_limit[name]}件, 次回まで約{next_fst//60:.0f}分)")

    # [B] タスク間に人間的な待機
    happymail.human_sleep(1.5, 4.0)


try:
  return_foot_counted = 0
  report_dict = {}
  for i in first_half:
    report_dict[i["name"]] = [0, send_flug, []]

  run_today = True

  while True:
    now = datetime.now()
    start_offset = random.randint(-30, 30)
    end_offset = random.randint(-30, 30)
    today_start = now.replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(minutes=start_offset)
    today_end   = now.replace(hour=22, minute=0, second=0, microsecond=0) + timedelta(minutes=end_offset)

    if run_today:
      if now < today_start:
        wait_sec = (today_start - now).total_seconds()
        print(f"本日の開始時刻({today_start.strftime('%H:%M')})まで待機... ({wait_sec/60:.0f}分後)")
        time.sleep(wait_sec)
        now = datetime.now()

      if now >= today_end:
        print(f"終了時刻({today_end.strftime('%H:%M')})を過ぎたため本日はスキップ")
      else:
        daily_limit = random.randint(1, 2)
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
        daily_done = {i["name"]: 0 for i in first_half}
        fst_daily_limit = {i["name"]: random.randint(1, 2) for i in first_half}
        fst_daily_done  = {i["name"]: 0 for i in first_half}
        last_fst_sent   = {i["name"]: None for i in first_half}
        print("fst送信上限:", {k: v for k, v in fst_daily_limit.items()})

        while datetime.now() < today_end:
          now = datetime.now()
          round_start = now
          print(f"\n--- {round_cnt}周目 ({now.strftime('%H:%M:%S')}) ---")

          # [A] 離席模倣
          if _should_take_break(round_cnt):
            break_min = random.randint(20, 40)
            print(f"  離席模倣: {break_min}分休憩")
            time.sleep(break_min * 60)
            if datetime.now() >= today_end:
              break

          # [C] タブ順をシャッフル
          shuffled_handles = list(enumerate(handles))
          random.shuffle(shuffled_handles)

          for idx, handle in shuffled_handles:
            # [C] キャラ順もシャッフル
            shuffled_charas = list(first_half)
            random.shuffle(shuffled_charas)

            for i in shuffled_charas:
              driver.switch_to.window(handle)
              happymail.human_sleep(0.5, 1.5)
              current_url = driver.current_url
              if "happymail.co.jp/app/html/mbmenu.php" not in current_url:
                driver.get("https://happymail.co.jp/app/html/mbmenu.php")
                wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
                happymail.human_sleep(1.0, 2.5)
              name_ele = driver.find_elements(By.CLASS_NAME, value="ds_user_display_name")
              if name_ele:
                name = name_ele[0].text
              else:
                print("名前の取得に失敗しました")
                continue
              if name == i["name"]:
                _process_chara(
                  name, i, driver, wait, mail_info,
                  daily_done, daily_limit, report_dict,
                  fst_daily_done, fst_daily_limit, last_fst_sent,
                  matching_daily_limit, returnfoot_daily_limit,
                  oneday_total_match, oneday_total_returnfoot,
                )

          elapsed = (datetime.now() - round_start).total_seconds()
          print(f"  {round_cnt}周目完了: {datetime.now().strftime('%H:%M:%S')} (経過: {elapsed:.0f}秒)")
          # [A] 周回間隔を正規分布でランダム化
          min_round_sec = _human_round_interval()
          wait_sec = min_round_sec - elapsed
          if wait_sec > 0 and datetime.now() < today_end:
            print(f"  次の周まで {wait_sec/60:.0f}分待機...")
            time.sleep(wait_sec)
          round_cnt += 1

        print(f"\n本日の処理完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    run_today = not run_today

    next_offset = random.randint(-30, 30)
    next_start = (datetime.now() + timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(minutes=next_offset)
    wait_sec = (next_start - datetime.now()).total_seconds()
    status = "実行" if run_today else "スキップ"
    print(f"翌日は【{status}】日。次回チェック: {next_start.strftime('%Y-%m-%d %H:%M')} ({wait_sec/3600:.1f}時間後)")
    time.sleep(wait_sec)
except KeyboardInterrupt:
  print("プログラムが Ctrl+C により中断されました。")
  sys.exit(0)
except Exception as e:
  print("エラーが発生しました:", e)
  traceback.print_exc()
  sys.exit(0)
finally:
  traceback.print_exc()
  sys.exit(0)

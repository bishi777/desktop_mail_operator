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


_DEFAULT_REPOST_TIMES = [(6, 0), (10, 0), (19, 0)]


def _parse_repost_times(args):
  """`6:16` `10:33` `19:00` のような H:MM 形式の複数引数を (hour, minute) リストに。
  空 or 全て不正なら既定の [(6,0), (10,0), (19,0)] を返す。"""
  result = []
  for arg in args:
    s = (arg or "").strip()
    if not s:
      continue
    try:
      if ":" in s:
        h_str, m_str = s.split(":", 1)
      else:
        h_str, m_str = s, "0"
      h = int(h_str)
      m = int(m_str)
      if 0 <= h <= 23 and 0 <= m <= 59:
        result.append((h, m))
    except Exception:
      continue
  if not result:
    return list(_DEFAULT_REPOST_TIMES)
  return sorted(set(result))


def _fmt_time(hm):
  return f"{hm[0]:02d}:{hm[1]:02d}"


user_data = func.get_user_data()
happy_info = user_data["happymail"]
first_half = happy_info
port = sys.argv[1] if len(sys.argv) > 1 else settings.happymail_drivers_port
repost_times = _parse_repost_times(sys.argv[2:])
print(f"再投稿時刻: {[_fmt_time(t) for t in repost_times]}")

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

# キャラ名 → キャラデータ の高速ルックアップ用 dict
chara_by_name = {i["name"]: i for i in first_half}

SCORE_RF_DAILY_LIMIT = 6
OTHER_AREAS = ["千葉県", "埼玉県", "神奈川県", "栃木県", "静岡県"]


def _human_round_interval():
  """[A] 周回間隔を正規分布でランダム化（平均15分、8〜30分）"""
  mean = 15 * 60
  std = 5 * 60
  t = max(8 * 60, min(30 * 60, random.gauss(mean, std)))
  return t


def _should_take_break(round_cnt):
  """[A] 2〜4時間に1回、離席を模倣（20〜40分の休憩）"""
  if round_cnt > 0 and round_cnt % random.randint(8, 12) == 0:
    return True
  return False


def _pending_repost_time(now, name, repost_done_today):
  """now 時点で未実行かつ過ぎている再投稿時刻 (h,m) のうち最古を返す。なければ None。"""
  for hm in repost_times:
    if repost_done_today[name][hm]:
      continue
    h, m = hm
    target = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if now >= target:
      return hm
  return None


def _process_chara(name, chara, driver, wait, mail_info, report_dict,
                   repost_done_today, score_rf_remaining, score_rf_daily_done):
  """1キャラ分の処理: checkmail / re_post / score_and_return_foot"""
  now = datetime.now()
  print(f"  ---------- {name} ------------{now.strftime('%Y-%m-%d %H:%M:%S')}")
  happymail_new_list = []
  return_foot_message = chara["return_foot_message"]
  fst_message = chara["fst_message"]
  post_return_message = chara["post_return_message"]
  second_message = chara["second_message"]
  conditions_message = chara["condition_message"]
  confirmation_mail = chara["confirmation_mail"]
  return_foot_img = chara["chara_image"]
  gmail_address = chara["mail_address"]
  gmail_password_c = chara["gmail_password"]
  chara_prompt = chara["system_prompt"]
  login_id = chara["login_id"]
  password = chara["password"]
  post_title = chara.get("post_title", "")
  post_contents = chara.get("post_contents", "")
  return_check_cnt = 10

  # 当該キャラの未実行 re_post 時刻
  pending_time = _pending_repost_time(now, name, repost_done_today)
  will_repost = pending_time is not None

  # タスク決定: 「re_post 直後の2ラウンドで score_and_return_foot」を実現するため、
  # 残機があるラウンドは score を優先し、re_post は後回しにする
  tasks = ["checkmail"]
  if (score_rf_remaining[name] > 0
      and score_rf_daily_done[name] < SCORE_RF_DAILY_LIMIT):
    tasks.append("score_and_return_foot")
  elif will_repost:
    tasks.append("re_post")

  random.shuffle(tasks)
  # 20% でランダムスキップ（checkmail は対象外）
  if random.random() < 0.2:
    skippable = [t for t in tasks if t != "checkmail"]
    if skippable:
      skip = random.choice(skippable)
      tasks = [t for t in tasks if t != skip]
      print(f"  [{name}] 今回は {skip} をスキップ")

  for task in tasks:
    if task == "checkmail":
      happymail.human_sleep(1.0, 3.0)
      try:
        happymail_new = happymail.multidrivers_checkmail(
          name, driver, wait, login_id, password, return_foot_message,
          fst_message, post_return_message, second_message, conditions_message,
          confirmation_mail, return_foot_img, gmail_address, gmail_password_c,
          return_check_cnt, android, chara_prompt, post_title=post_title,
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
                img_path = f"{chara['name']}_ban.png"
                driver.save_screenshot(img_path)
                img_path = func.compress_image(img_path)
                title = "メッセージ"
                text = f"ハッピーメール {chara['name']}:{chara['login_id']}:{chara['password']}:  {text}"
          if mail_info:
            func.send_mail(text, mail_info, title, img_path)
      except NoSuchWindowException:
        pass
      except ReadTimeoutError as e:
        print("ページの読み込みがタイムアウトしました:", e)
        driver.refresh()
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      except Exception:
        print(traceback.format_exc())

    elif task == "re_post":
      area_list = ["東京都"] + random.sample(OTHER_AREAS, 2)
      print(f"  [{name}] re_post 開始 (時刻={_fmt_time(pending_time)} / 地域={area_list})")
      happymail.human_sleep(1.5, 4.0)
      try:
        happymail.re_post(
          name, driver, wait, post_title, post_contents, area_list=area_list,
        )
      except Exception:
        print(traceback.format_exc())
        func.send_error(f"ハッピーメール掲示板{name}", traceback.format_exc())
      finally:
        # 成否に関わらず実行済みにして無限リトライを防ぐ
        repost_done_today[name][pending_time] = True
        score_rf_remaining[name] = 2
        print(f"  [{name}] re_post 完了 → 次の2ラウンドで足跡返しスコア送信")

    elif task == "score_and_return_foot":
      happymail.human_sleep(2.0, 5.0)
      try:
        sent_to = happymail.score_and_return_foot(
          name, driver, wait, return_foot_message, return_foot_img,
          user_check_cnt=random.randint(8, 14),
        )
        if sent_to:
          score_rf_daily_done[name] += 1
          print(f"  [{name}] 足跡返し送信済み {score_rf_daily_done[name]}/{SCORE_RF_DAILY_LIMIT}件")
      except NoSuchWindowException:
        print("NoSuchWindowExceptionエラーが出ました")
      except ReadTimeoutError as e:
        print("ページの読み込みがタイムアウトしました:", e)
        driver.refresh()
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      except Exception:
        print(traceback.format_exc())
      finally:
        score_rf_remaining[name] = max(0, score_rf_remaining[name] - 1)

    happymail.human_sleep(1.5, 4.0)


try:
  report_dict = {}
  for chara in first_half:
    report_dict[chara["name"]] = [0, send_flug, []]

  run_today = True

  while True:
    now = datetime.now()
    start_offset = random.randint(-30, 30)
    end_offset = random.randint(-30, 30)
    today_start = now.replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(minutes=start_offset)
    today_end = now.replace(hour=22, minute=0, second=0, microsecond=0) + timedelta(minutes=end_offset)

    if run_today:
      if now < today_start:
        wait_sec = (today_start - now).total_seconds()
        print(f"本日の開始時刻({today_start.strftime('%H:%M')})まで待機... ({wait_sec/60:.0f}分後)")
        time.sleep(wait_sec)
        now = datetime.now()

      if now >= today_end:
        print(f"終了時刻({today_end.strftime('%H:%M')})を過ぎたため本日はスキップ")
      else:
        mail_info = random.choice([user_mail_info, spare_mail_info])
        now = datetime.now()
        print(f"\n{'='*50}")
        print(f"本日の処理開始: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"開始:{today_start.strftime('%H:%M')} / 終了:{today_end.strftime('%H:%M')} / 再投稿:{[_fmt_time(t) for t in repost_times]}")
        print(f"{'='*50}")

        round_cnt = 1
        # 1日ごとの状態リセット
        # 当日処理開始時点で既に過ぎている時刻は当日スキップ（done=True 扱い）。
        # 例: 14:00 起動なら 6:00, 12:30 はスキップ、19:00 のみ 19:00 到達時に発火。
        processing_now = datetime.now()
        def _time_already_past(hm):
          h, m = hm
          target = processing_now.replace(hour=h, minute=m, second=0, microsecond=0)
          return processing_now > target
        repost_done_today = {
          chara["name"]: {hm: _time_already_past(hm) for hm in repost_times}
          for chara in first_half
        }
        skipped = [_fmt_time(t) for t in repost_times if _time_already_past(t)]
        if skipped:
          print(f"  ※ 起動時刻 {processing_now.strftime('%H:%M')} 時点で過ぎている repost_times をスキップ: {skipped}")
        score_rf_remaining = {chara["name"]: 0 for chara in first_half}
        score_rf_daily_done = {chara["name"]: 0 for chara in first_half}

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

          # タブ順をシャッフル
          shuffled_handles = list(handles)
          random.shuffle(shuffled_handles)

          for handle in shuffled_handles:
            try:
              driver.switch_to.window(handle)
            except NoSuchWindowException:
              continue
            happymail.human_sleep(0.5, 1.5)
            current_url = driver.current_url
            if "happymail.co.jp/app/html/mbmenu.php" not in current_url:
              driver.get("https://happymail.co.jp/app/html/mbmenu.php")
              wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
              happymail.human_sleep(1.0, 2.5)
            name_ele = driver.find_elements(By.CLASS_NAME, value="ds_user_display_name")
            if not name_ele:
              print("名前の取得に失敗しました")
              continue
            name = name_ele[0].text
            chara = chara_by_name.get(name)
            if not chara:
              print(f"  キャラデータに {name} が見つかりません（タブをスキップ）")
              continue
            _process_chara(
              name, chara, driver, wait, mail_info, report_dict,
              repost_done_today, score_rf_remaining, score_rf_daily_done,
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

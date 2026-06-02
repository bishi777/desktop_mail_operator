from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import random
import time
from selenium.webdriver.common.by import By
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import traceback
from widget import happymail, func
import sqlite3
from datetime import timedelta
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from urllib3.exceptions import ReadTimeoutError
from datetime import datetime
import settings


_DEFAULT_REPOST_TIMES = [(6, 0), (10, 0), (19, 0)]
_RUN_KEYWORDS = {"run", "true", "yes", "1"}
_SKIP_KEYWORDS = {"skip", "false", "no", "0"}


def _parse_cli_args(args):
  """引数の中から run/skip キーワードと H:MM 形式の時刻を分離して返す。
  戻り値: (run_today_initial: bool, repost_times: list[(h,m)])
  時刻リストが空なら既定 [(6,0),(10,0),(19,0)]。
  run/skip 指定が無ければ True がデフォルト。"""
  run_today_initial = True
  times = []
  for arg in args:
    s = (arg or "").strip()
    if not s:
      continue
    sl = s.lower()
    if sl in _RUN_KEYWORDS:
      run_today_initial = True
      continue
    if sl in _SKIP_KEYWORDS:
      run_today_initial = False
      continue
    try:
      if ":" in s:
        h_str, m_str = s.split(":", 1)
      else:
        h_str, m_str = s, "0"
      h = int(h_str)
      m = int(m_str)
      if 0 <= h <= 23 and 0 <= m <= 59:
        times.append((h, m))
    except Exception:
      continue
  if not times:
    times = list(_DEFAULT_REPOST_TIMES)
  return run_today_initial, sorted(set(times))


def _fmt_time(hm):
  return f"{hm[0]:02d}:{hm[1]:02d}"


BEGINNER_DAYS = 7


def _is_beginner(chara):
  """date_created から1週間未満なら True（足跡返しスキップ対象）。
  None / 不正値 / 1週間以上経過なら False。"""
  raw = chara.get("date_created")
  if not raw:
    return False
  try:
    if isinstance(raw, datetime):
      dt = raw
    elif isinstance(raw, str):
      dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    else:
      return False
  except (ValueError, TypeError):
    return False
  now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
  return (now - dt) < timedelta(days=BEGINNER_DAYS)


user_data = func.get_user_data()
happy_info = user_data["happymail"]
first_half = happy_info
port = sys.argv[1] if len(sys.argv) > 1 else settings.happymail_drivers_port
run_today_initial, repost_times = _parse_cli_args(sys.argv[2:])
print(f"再投稿時刻: {[_fmt_time(t) for t in repost_times]}")
print(f"run_today 初期値: {run_today_initial}")

options = Options()
options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
driver = webdriver.Chrome(options=options)
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

SCORE_RF_DAILY_LIMIT = 15
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
                   score_rounds_until_next, score_rf_daily_done,
                   checkmail_only=False):
  """1キャラ分の処理: checkmail / score_and_type
  checkmail_only=True なら checkmail のみ実行（スキップ日用）"""
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
  mailaddress_img = chara.get("mail_address_image", "")
  return_check_cnt = 10

  if checkmail_only:
    # スキップ日: checkmail のみ
    tasks = ["checkmail"]
  else:
    beginner = _is_beginner(chara)
    # 幼期キャラ（作成から1週間未満）は checkmail のみ。
    # それ以外は毎ラウンド return_matching を試行し、4〜7 ラウンドに1回
    # score_and_type を発火（上限 SCORE_RF_DAILY_LIMIT）。
    tasks = ["checkmail"]
    if not beginner:
      tasks.append("return_matching")
      score_rounds_until_next[name] -= 1
      if (score_rounds_until_next[name] <= 0
          and score_rf_daily_done[name] < SCORE_RF_DAILY_LIMIT):
        tasks.append("score_and_type")
        score_rounds_until_next[name] = random.randint(4, 7)

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
          mailaddress_img=mailaddress_img
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

    elif task == "return_matching":
      happymail.human_sleep(1.5, 4.0)
      try:
        happymail.return_matching_one(name, driver, wait, fst_message)
      except NoSuchWindowException:
        print("NoSuchWindowExceptionエラーが出ました")
      except ReadTimeoutError as e:
        print("ページの読み込みがタイムアウトしました:", e)
        driver.refresh()
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      except Exception:
        print(traceback.format_exc())

    elif task == "score_and_type":
      happymail.human_sleep(2.0, 5.0)
      try:
        sent_to = happymail.score_and_type(
          name, driver, wait,
          user_check_cnt=random.randint(8, 14),
        )
        if sent_to:
          score_rf_daily_done[name] += 1
          print(f"  [{name}] タイプ送信済み {score_rf_daily_done[name]}/{SCORE_RF_DAILY_LIMIT}件")
      except NoSuchWindowException:
        print("NoSuchWindowExceptionエラーが出ました")
      except ReadTimeoutError as e:
        print("ページの読み込みがタイムアウトしました:", e)
        driver.refresh()
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      except Exception:
        print(traceback.format_exc())

    happymail.human_sleep(1.5, 4.0)


try:
  report_dict = {}
  for chara in first_half:
    report_dict[chara["name"]] = [0, send_flug, []]

  run_today = run_today_initial

  while True:
    now = datetime.now()
    start_offset = random.randint(-30, 30)
    end_offset = random.randint(-30, 30)
    today_start = now.replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(minutes=start_offset)
    today_end = now.replace(hour=22, minute=0, second=0, microsecond=0) + timedelta(minutes=end_offset)

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
      mode_label = "通常" if run_today else "スキップ日(checkmailのみ)"
      print(f"\n{'='*50}")
      print(f"本日の処理開始 [{mode_label}]: {now.strftime('%Y-%m-%d %H:%M:%S')}")
      print(f"開始:{today_start.strftime('%H:%M')} / 終了:{today_end.strftime('%H:%M')} / タイプ上限:{SCORE_RF_DAILY_LIMIT}")
      print(f"{'='*50}")

      round_cnt = 1
      score_rounds_until_next = None
      score_rf_daily_done = None
      if run_today:
        # 1日ごとの状態リセット
        # 各キャラ「次に score_and_type を発火するまでの残ラウンド数」を 4〜7 で初期化
        score_rounds_until_next = {chara["name"]: random.randint(4, 7) for chara in first_half}
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
            score_rounds_until_next, score_rf_daily_done,
            checkmail_only=not run_today,
          )

        elapsed = (datetime.now() - round_start).total_seconds()
        if score_rf_daily_done:
          type_summary = ", ".join(
            f"{n} {score_rf_daily_done[n]}/{SCORE_RF_DAILY_LIMIT}"
            for n in score_rf_daily_done
          )
          print(f"  {round_cnt}周目完了: {datetime.now().strftime('%H:%M:%S')} (経過: {elapsed:.0f}秒) [タイプ付け {type_summary}]")
        else:
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

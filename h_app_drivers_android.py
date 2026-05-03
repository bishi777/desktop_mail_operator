"""ハッピーメール Androidネイティブアプリ 巡回ドライバ (フェーズ1).

7:00-22:00 (±30分) の間に隔日で巡回し、新着メール (check_mail) を処理する。
能動送信 (return_foot / fst) はフェーズ2 / フェーズ4 で実装する。
詳細仕様は DESIGN_h_app_drivers_android.md を参照。

使い方:
  myenv/bin/python h_app_drivers_android.py <login_id>

device_mapping.json で login_id ↔ UDID/Appiumポート群 を解決する。
1端末1アカウント前提。並列で複数端末を回す場合はプロセスを端末数だけ起動する。
"""
import argparse
import json
import os
import random
import socket
import subprocess
import sys
import time
import traceback
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import WebDriverException

from widget import func, happymail_android


# ============================================================
# 定数
# ============================================================
APP_PACKAGE = "jp.co.i_bec.suteki_happy"
APP_ACTIVITY = "jp.co.i_bec.happymailapp.activity.SplashActivity"
APPIUM_BIN = "/Users/yamamotokenta/.nodebrew/current/bin/appium"
MAPPING_FILE = os.path.join(os.path.dirname(__file__), "device_mapping.json")
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs_android")

# 巡回スペック (DESIGN_h_app_drivers_android.md §6 と一致)
DAILY_LIMIT_RANGE = (8, 10)         # return_foot 1日上限
FST_DAILY_LIMIT_RANGE = (1, 2)      # fst 1日上限
ROUND_INTERVAL_MEAN_SEC = 15 * 60   # 1周平均15分
ROUND_INTERVAL_STD_SEC = 5 * 60
ROUND_INTERVAL_MIN_SEC = 8 * 60
ROUND_INTERVAL_MAX_SEC = 30 * 60
BREAK_EVERY_ROUNDS = (8, 12)        # 何周ごとに休憩を挟むか
BREAK_DURATION_MIN = (20, 40)       # 休憩は何分
DAILY_START_HOUR = 7
DAILY_END_HOUR = 22
DAILY_OFFSET_MIN = 30               # 開始/終了時刻 ±30分
RUN_EVERY_OTHER_DAY = True          # 隔日運用
ACTIVE_SKIP_PROB = 0.2              # 周回内で能動送信を完全スキップする確率
FST_INTERVAL_MIN_SEC = 50 * 60      # FST 間隔 50-70分
FST_INTERVAL_MAX_SEC = 70 * 60

# 通報メールの予備宛先 (h_ch_ma_fm.py と同じ)
SPARE_MAIL_INFO = [
  "ryapya694@ruru.be",
  "siliboco68@gmail.com",
  "akkcxweqzdplcymh",
]


# ============================================================
# 人間らしさ (h_ch_ma_fm.py から移植)
# ============================================================
def _human_round_interval():
  """周回間隔を正規分布でランダム化（平均15分、8〜30分）。"""
  t = random.gauss(ROUND_INTERVAL_MEAN_SEC, ROUND_INTERVAL_STD_SEC)
  return max(ROUND_INTERVAL_MIN_SEC, min(ROUND_INTERVAL_MAX_SEC, t))


def _should_take_break(round_cnt):
  """8〜12周ごとに離席を模倣する。"""
  if round_cnt > 0 and round_cnt % random.randint(*BREAK_EVERY_ROUNDS) == 0:
    return True
  return False


# ============================================================
# デバイスマッピング
# ============================================================
def load_device_mapping(login_id):
  """device_mapping.json から login_id 対応のエントリを返す。"""
  if not os.path.exists(MAPPING_FILE):
    raise RuntimeError(f"{MAPPING_FILE} が存在しない")
  with open(MAPPING_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)
  for m in data.get("mappings", []):
    if m.get("login_id") == login_id:
      return m
  registered = [m.get("login_id") for m in data.get("mappings", [])]
  raise ValueError(
    f"login_id={login_id} が device_mapping.json に未登録。 登録済み: {registered}"
  )


# ============================================================
# Appium 制御 (h_app_profile_edit_android.py から移植 + マルチ端末対応)
# ============================================================
def _appium_alive(port):
  try:
    with socket.create_connection(("127.0.0.1", port), timeout=1):
      return True
  except OSError:
    return False


def start_appium_if_needed(appium_port):
  """Appium サーバが指定ポートで未起動なら起動。

  並列実行時は端末ごとに別ポートで複数の Appium サーバを起動する想定。
  """
  if _appium_alive(appium_port):
    print(f"[Appium:{appium_port}] 既存サーバを使用")
    return None
  print(f"[Appium:{appium_port}] サーバ起動中…")
  proc = subprocess.Popen(
    [APPIUM_BIN, "-p", str(appium_port)],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
  )
  for _ in range(30):
    if _appium_alive(appium_port):
      print(f"[Appium:{appium_port}] サーバ起動完了")
      return proc
    time.sleep(1)
  proc.terminate()
  raise RuntimeError(f"Appium サーバ ({appium_port}) の起動に失敗")


def create_driver(device_cfg):
  """UiAutomator2 driver を作成。

  並列実行時の衝突を避けるため system_port / mjpeg_server_port を必ず指定。
  """
  options = UiAutomator2Options()
  options.platform_name = "Android"
  options.device_name = "Android"
  options.udid = device_cfg["udid"]
  options.app_package = APP_PACKAGE
  options.app_activity = APP_ACTIVITY
  options.no_reset = True
  options.auto_grant_permissions = True
  options.new_command_timeout = 600
  options.uiautomator2_server_install_timeout = 120000
  options.system_port = device_cfg["system_port"]
  options.mjpeg_server_port = device_cfg["mjpeg_server_port"]
  url = f"http://localhost:{device_cfg['appium_port']}"
  return webdriver.Remote(url, options=options)


def recover_driver(holder, device_cfg):
  """driver を作り直す。Appium が応答しないなら kill して再起動。"""
  try:
    holder["driver"].quit()
  except Exception:
    pass
  time.sleep(2)
  if not _appium_alive(device_cfg["appium_port"]):
    subprocess.call(
      ["pkill", "-9", "-f", f"node.*appium.*-p {device_cfg['appium_port']}"],
    )
    time.sleep(2)
    start_appium_if_needed(device_cfg["appium_port"])
  time.sleep(2)
  holder["driver"] = create_driver(device_cfg)
  time.sleep(3)
  happymail_android.dismiss_popups(holder["driver"])


def _save_screenshot(driver, device_cfg, label):
  """logs_android/<udid>/<label>_<timestamp>.png にスクショ保存。"""
  try:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(LOG_DIR, device_cfg["udid"])
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{label}_{ts}.png")
    driver.save_screenshot(path)
    return path
  except Exception:
    print(f"[screenshot:{label}] 保存失敗")
    print(traceback.format_exc())
    return None


def _handle_crash(holder, device_cfg, name, task, exc):
  """WebDriverException時の共通処理: スクショ保存 → driver 再作成。"""
  print(f"[CRASH:{name}] {task}: {str(exc)[:200]}")
  if holder["driver"] is not None:
    _save_screenshot(holder["driver"], device_cfg, f"crash_{task}")
  print(f"[RECOVERY:{name}] driver 再作成中...")
  try:
    recover_driver(holder, device_cfg)
  except Exception:
    print("[RECOVERY] 失敗:")
    print(traceback.format_exc())


# ============================================================
# 通報メール
# ============================================================
def _build_user_mail_info(user_data):
  """user_data['user'][0] から通報メール宛先を構築。失敗時 None。"""
  try:
    info = user_data["user"][0]
    address = info.get("user_email")
    gmail = info.get("gmail_account")
    pwd = info.get("gmail_account_password")
    if address and gmail and pwd:
      return [address, gmail, pwd]
  except (KeyError, IndexError, TypeError):
    pass
  return None


def _pick_mail_info(user_mail_info):
  """user/spare からランダム選択。h_ch_ma_fm.py の挙動を踏襲。"""
  if user_mail_info:
    return random.choice([user_mail_info, SPARE_MAIL_INFO])
  return SPARE_MAIL_INFO


def _send_check_report(name, return_list, mail_info, driver, chara_data, device_cfg):
  """check_mail の結果を Gmail で通報。h_ch_ma_fm.py の挙動を踏襲。"""
  if not mail_info:
    return
  title = f"happy新着 {name}"
  text = ""
  img_path = None
  for m in return_list:
    text += m + ",\n"
    if "警告" in text or "NoImage" in text or "利用" in text:
      shot = _save_screenshot(driver, device_cfg, f"{name}_ban")
      if shot:
        try:
          img_path = func.compress_image(shot)
        except Exception:
          img_path = shot
      title = "メッセージ"
      text = (
        f"ハッピーメール {chara_data['name']}:"
        f"{chara_data['login_id']}:{chara_data['password']}: {text}"
      )
  try:
    func.send_mail(text, mail_info, title, img_path)
  except Exception:
    print(f"[{name}] 通報メール送信失敗")
    print(traceback.format_exc())


def _send_ban_report(name, ban_keyword, mail_info, driver, chara_data, device_cfg):
  """BAN/警告画面検出時の緊急通報メール送信 (1日1回までのスロットリング付き)."""
  if not mail_info:
    return
  title = f"【BAN警告】ハッピーメール {name}"
  text = (
    f"ハッピーメール {chara_data['name']}:{chara_data['login_id']}:{chara_data['password']}\n"
    f"BAN/警告画面を検出しました。検出キーワード: {ban_keyword}\n"
    f"添付スクショを確認のうえ、必要なら端末を確認してください。\n"
    f"検出時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
  )
  shot = _save_screenshot(driver, device_cfg, f"{name}_ban_alert")
  img_path = None
  if shot:
    try:
      img_path = func.compress_image(shot)
    except Exception:
      img_path = shot
  try:
    func.send_mail(text, mail_info, title, img_path)
    print(f"[{name}] BAN通報メール送信完了")
  except Exception:
    print(f"[{name}] BAN通報メール送信失敗")
    print(traceback.format_exc())


# ============================================================
# 1キャラの周回処理
# ============================================================
def _process_chara(chara_data, holder, mail_info, state, device_cfg):
  """1周分: check_mail (受動: 連続OK) + return_foot xor fst (能動: 1件)."""
  name = chara_data["name"]
  print(f"\n  ===== {name} ({datetime.now().strftime('%H:%M:%S')}) =====")

  # アプリを必ず前面化 (バックグラウンドに回されている可能性)
  try:
    holder["driver"].activate_app(APP_PACKAGE)
    time.sleep(2)
    happymail_android.dismiss_popups(holder["driver"])
  except WebDriverException as e:
    _handle_crash(holder, device_cfg, name, "activate_app", e)
    return

  # ── BAN/警告画面検出 (フェーズ3) ──
  # 検出時はその周の能動・受動操作を全てスキップ。1日1回まで通報メール。
  ban = happymail_android.detect_ban_screen(holder["driver"])
  if ban:
    print(f"  [{name}] BAN/警告画面検出: {ban!r}")
    if not state.get("ban_reported_today"):
      _send_ban_report(name, ban, mail_info, holder["driver"], chara_data, device_cfg)
      state["ban_reported_today"] = True
    else:
      print(f"  [{name}] 本日は既に通報済み — スクショのみ追加保存")
      _save_screenshot(holder["driver"], device_cfg, f"{name}_ban_repeat")
    return

  # ── 1. 能動送信タスクの抽選 (1ループ1通制約) ──
  active_candidates = []
  if state["daily_done"] < state["daily_limit"]:
    active_candidates.append("return_foot")
  elapsed_since_fst = (
    (datetime.now() - state["last_fst_sent"]).total_seconds()
    if state["last_fst_sent"] else float("inf")
  )
  fst_interval = random.randint(FST_INTERVAL_MIN_SEC, FST_INTERVAL_MAX_SEC)
  if (
    state["fst_daily_done"] < state["fst_daily_limit"]
    and elapsed_since_fst >= fst_interval
  ):
    active_candidates.append("fst")

  active_task = None
  if active_candidates and random.random() >= ACTIVE_SKIP_PROB:
    active_task = random.choice(active_candidates)
  print(f"  [{name}] 能動候補={active_candidates} 選択={active_task}")

  # ── 2. check_mail (受動: 連続OK) ──
  happymail_android.human_sleep(1.0, 3.0)
  try:
    return_list = happymail_android.check_mail(
      name=chara_data["name"],
      driver=holder["driver"],
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
    if return_list:
      _send_check_report(
        chara_data["name"], return_list, mail_info,
        holder["driver"], chara_data, device_cfg,
      )
  except WebDriverException as e:
    _handle_crash(holder, device_cfg, name, "check_mail", e)
    return
  except Exception:
    print(f"[{name}] check_mail 例外:")
    print(traceback.format_exc())

  # ── 3. 能動送信1件 (return_foot xor fst) ──
  if active_task is None:
    return
  happymail_android.human_sleep(1.5, 4.0)
  if active_task == "return_foot":
    _do_return_foot(chara_data, holder, state, device_cfg)
  elif active_task == "fst":
    _do_fst(chara_data, holder, state, device_cfg)


def _do_return_foot(chara_data, holder, state, device_cfg):
  """足跡返し1件を試みる。フェーズ2の return_footpoint 実装後に本物が動く。"""
  name = chara_data["name"]
  fn = getattr(happymail_android, "return_footpoint", None)
  if fn is None:
    print(f"  [{name}] return_foot: 未実装 (フェーズ2で実装予定) — ノーオペ")
    return
  try:
    sent = fn(holder["driver"], chara_data, send_cnt=1) or 0
    if sent:
      state["daily_done"] += int(sent)
      print(
        f"  [{name}] return_foot +{sent} → 累計"
        f" {state['daily_done']}/{state['daily_limit']}"
      )
    else:
      print(f"  [{name}] return_foot: 該当なし")
  except WebDriverException as e:
    _handle_crash(holder, device_cfg, name, "return_foot", e)
  except Exception:
    print(f"[{name}] return_foot 例外:")
    print(traceback.format_exc())


def _do_fst(chara_data, holder, state, device_cfg):
  """FST送信1件を試みる。フェーズ4の score_and_send_fst_message 実装後に本物が動く。"""
  name = chara_data["name"]
  fn = getattr(happymail_android, "score_and_send_fst_message", None)
  if fn is None:
    print(f"  [{name}] fst: 未実装 (フェーズ4で実装予定) — ノーオペ")
    return
  try:
    sent_to = fn(holder["driver"], chara_data)
    if sent_to:
      state["fst_daily_done"] += 1
      state["last_fst_sent"] = datetime.now()
      print(
        f"  [{name}] fst送信 → 累計"
        f" {state['fst_daily_done']}/{state['fst_daily_limit']}"
      )
    else:
      print(f"  [{name}] fst: 送信先なし")
  except WebDriverException as e:
    _handle_crash(holder, device_cfg, name, "fst", e)
  except Exception:
    print(f"[{name}] fst 例外:")
    print(traceback.format_exc())


# ============================================================
# 1日のループ
# ============================================================
def run_one_day(chara_data, holder, device_cfg, user_data):
  """7:00 〜 22:00 (±30分) の間、巡回ループを回す。"""
  now = datetime.now()
  start_offset = random.randint(-DAILY_OFFSET_MIN, DAILY_OFFSET_MIN)
  end_offset = random.randint(-DAILY_OFFSET_MIN, DAILY_OFFSET_MIN)
  today_start = now.replace(
    hour=DAILY_START_HOUR, minute=0, second=0, microsecond=0,
  ) + timedelta(minutes=start_offset)
  today_end = now.replace(
    hour=DAILY_END_HOUR, minute=0, second=0, microsecond=0,
  ) + timedelta(minutes=end_offset)

  if now < today_start:
    wait_sec = (today_start - now).total_seconds()
    print(f"開始時刻 ({today_start.strftime('%H:%M')}) まで {wait_sec/60:.0f}分待機")
    time.sleep(wait_sec)
    now = datetime.now()

  if now >= today_end:
    print(f"終了時刻 ({today_end.strftime('%H:%M')}) を過ぎているのでスキップ")
    return

  state = {
    "daily_limit": random.randint(*DAILY_LIMIT_RANGE),
    "daily_done": 0,
    "fst_daily_limit": random.randint(*FST_DAILY_LIMIT_RANGE),
    "fst_daily_done": 0,
    "last_fst_sent": None,
    "ban_reported_today": False,
  }
  user_mail_info = _build_user_mail_info(user_data)
  mail_info = _pick_mail_info(user_mail_info)

  print(f"\n{'='*50}")
  print(f"本日の処理開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
  print(f"  開始:{today_start.strftime('%H:%M')} 終了:{today_end.strftime('%H:%M')}")
  print(f"  daily_limit (return_foot): {state['daily_limit']}件")
  print(f"  fst_daily_limit:           {state['fst_daily_limit']}件")
  print(f"  通報メール宛先:            {mail_info[0] if mail_info else '(なし)'}")
  print(f"{'='*50}")

  round_cnt = 1
  while datetime.now() < today_end:
    round_start = datetime.now()
    print(f"\n--- {round_cnt}周目 ({round_start.strftime('%H:%M:%S')}) ---")

    if _should_take_break(round_cnt):
      break_min = random.randint(*BREAK_DURATION_MIN)
      print(f"  離席模倣: {break_min}分休憩")
      time.sleep(break_min * 60)
      if datetime.now() >= today_end:
        break

    try:
      _process_chara(chara_data, holder, mail_info, state, device_cfg)
    except Exception:
      print(traceback.format_exc())

    elapsed = (datetime.now() - round_start).total_seconds()
    print(
      f"  {round_cnt}周目完了 ({datetime.now().strftime('%H:%M:%S')}, 経過{elapsed:.0f}秒)"
      f" / 本日 RF={state['daily_done']}/{state['daily_limit']}"
      f" FST={state['fst_daily_done']}/{state['fst_daily_limit']}"
    )

    wait_sec = _human_round_interval() - elapsed
    if wait_sec > 0 and datetime.now() < today_end:
      print(f"  次の周まで {wait_sec/60:.1f}分待機...")
      time.sleep(wait_sec)
    round_cnt += 1

  print(f"\n本日の処理完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
  print(
    f"  最終: RF={state['daily_done']}/{state['daily_limit']}"
    f" FST={state['fst_daily_done']}/{state['fst_daily_limit']}"
    f" 周回={round_cnt - 1}"
  )


# ============================================================
# main
# ============================================================
def main():
  parser = argparse.ArgumentParser(
    description="ハッピーメールAndroidネイティブアプリ巡回ドライバ (フェーズ1)"
  )
  parser.add_argument("login_id", help="device_mapping.json に登録済みのlogin_id")
  args = parser.parse_args()

  device_cfg = load_device_mapping(args.login_id)
  print(
    f"[CONFIG] login_id={args.login_id} udid={device_cfg['udid']}"
    f" appium={device_cfg['appium_port']}"
    f" system_port={device_cfg['system_port']}"
  )

  os.makedirs(os.path.join(LOG_DIR, device_cfg["udid"]), exist_ok=True)

  user_data = func.get_user_data()
  if not user_data or user_data == 2:
    print("[ERROR] ユーザーデータ取得失敗")
    sys.exit(1)

  chara_data = next(
    (c for c in user_data.get("happymail", [])
     if c.get("login_id") == args.login_id),
    None,
  )
  if not chara_data:
    available = [c.get("login_id") for c in user_data.get("happymail", [])]
    print(f"[ERROR] login_id={args.login_id} が user_data の happymail に存在しない")
    print(f"  user_data 内: {available}")
    sys.exit(1)
  print(f"[CHARA] name={chara_data['name']} login_id={chara_data['login_id']}")

  # 端末の画面 ON 維持 (USB 接続前提。失敗してもログ出して継続)
  try:
    subprocess.run(
      ["adb", "-s", device_cfg["udid"], "shell", "svc", "power", "stayon", "true"],
      check=False, timeout=10,
    )
    print("[ADB] svc power stayon true 投入")
  except Exception as e:
    print(f"[ADB] stayon 失敗 (継続): {e}")

  appium_proc = start_appium_if_needed(device_cfg["appium_port"])
  holder = {"driver": None}
  run_today = True

  try:
    print("[Appium] driver 作成中…")
    holder["driver"] = create_driver(device_cfg)
    time.sleep(3)
    happymail_android.dismiss_popups(holder["driver"])

    while True:
      if run_today:
        try:
          # 毎日 user_data を再取得 (キャラ情報の変更に追随)
          fresh = func.get_user_data()
          if fresh and fresh != 2:
            user_data = fresh
            new_chara = next(
              (c for c in user_data.get("happymail", [])
               if c.get("login_id") == args.login_id),
              None,
            )
            if new_chara:
              chara_data = new_chara
          run_one_day(chara_data, holder, device_cfg, user_data)
        except Exception:
          print("[run_one_day] 例外:")
          print(traceback.format_exc())

      else:
        print(f"本日はスキップ日 ({datetime.now().strftime('%Y-%m-%d')})")

      if RUN_EVERY_OTHER_DAY:
        run_today = not run_today

      next_offset = random.randint(-DAILY_OFFSET_MIN, DAILY_OFFSET_MIN)
      next_start = (datetime.now() + timedelta(days=1)).replace(
        hour=DAILY_START_HOUR, minute=0, second=0, microsecond=0,
      ) + timedelta(minutes=next_offset)
      wait_sec = (next_start - datetime.now()).total_seconds()
      status = "実行" if run_today else "スキップ"
      print(
        f"翌日は【{status}】 次回:"
        f" {next_start.strftime('%Y-%m-%d %H:%M')}"
        f" ({wait_sec/3600:.1f}時間後)"
      )
      time.sleep(max(60, wait_sec))

  except KeyboardInterrupt:
    print("\nCtrl+C により中断")
  except Exception:
    print("[main] 例外:")
    print(traceback.format_exc())
  finally:
    if holder["driver"] is not None:
      try:
        holder["driver"].quit()
      except Exception:
        pass
      print("[Appium] driver 終了")
    if appium_proc is not None:
      appium_proc.terminate()
      try:
        appium_proc.wait(timeout=5)
      except Exception:
        appium_proc.kill()
      print("[Appium] サーバ終了")


if __name__ == "__main__":
  main()

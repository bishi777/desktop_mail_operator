import time
import sqlite3
import random
import os
import sys
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import traceback
from selenium.webdriver.common.by import By
from widget import pcmax
from selenium.webdriver.support.select import Select
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.common.exceptions import TimeoutException
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
import requests
import shutil
import unicodedata
import platform
from urllib3.exceptions import MaxRetryError
from webdriver_manager.core.driver_cache import DriverCacheManager
import tempfile
from stem import Signal
from stem.control import Controller
import psutil
import signal
from DrissionPage import ChromiumOptions
from DrissionPage import Chromium, ChromiumPage
from DrissionPage.errors import BrowserConnectError, PageDisconnectedError, ElementNotFoundError
from urllib3.exceptions import ReadTimeoutError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import formatdate
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
import difflib
from PIL import Image
import traceback
from datetime import datetime, date
import unicodedata
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, StaleElementReferenceException,
    ElementClickInterceptedException, ElementNotInteractableException,
    InvalidArgumentException, NoSuchElementException
)
from selenium.webdriver.common.action_chains import ActionChains
from google import genai
import settings
from google.genai.errors import ClientError
from google.genai.types import HttpOptions
import anthropic



def parse_arrival_datetime(text: str, now: datetime | None = None) -> datetime | None:
    if now is None:
        now = datetime.now()
    s = (text or "").strip()

    # 1) YYYY-MM-DD HH:MM[:SS]
    m = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?', s)
    if m:
        y, mo, d, hh, mm, ss = map(int, m.groups(default='0'))
        return datetime(y, mo, d, hh, mm, ss)

    # 2) MM-DD HH:MM[:SS]（年は今年で補完）
    m = re.search(r'(\d{1,2})[-/](\d{1,2})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?', s)
    if m:
        mo, d, hh, mm, ss = map(int, m.groups(default='0'))
        dt = datetime(now.year, mo, d, hh, mm, ss)
        # 稀に未来になる場合は前年扱い（年跨ぎ対策）
        if dt > now and (dt - now) > timedelta(days=1):
            dt = datetime(now.year - 1, mo, d, hh, mm, ss)
        return dt

    # 3) HH:MM[:SS]（今日扱い。未来になったら前日扱い）
    m = re.search(r'(\d{1,2}):(\d{2})(?::(\d{2}))?', s)
    if m:
        hh, mm, ss = map(int, m.groups(default='0'))
        dt = now.replace(hour=hh, minute=mm, second=ss, microsecond=0)
        if dt > now:
            dt -= timedelta(days=1)
        return dt

    # 4) 相対表記：「X分前」「X時間前」
    m = re.search(r'(\d+)\s*分前', s)
    if m:
        return now - timedelta(minutes=int(m.group(1)))
    m = re.search(r'(\d+)\s*時間前', s)
    if m:
        return now - timedelta(hours=int(m.group(1)))

    return None

def _format_check_date(v) -> str:
    """check_date を“分まで”で整形。None→'-'。dateは日付のみ。"""
    if v is None:
        return "-"
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M")
    if isinstance(v, date):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, int):
        # UNIX秒 or ミリ秒を想定
        try:
            if v > 10**11:  # ms
                return datetime.fromtimestamp(v / 1000).strftime("%Y-%m-%d %H:%M")
            if v >= 10**9:  # sec
                return datetime.fromtimestamp(v).strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass
        return str(v)
    if isinstance(v, str):
        s = v.strip()
        # 代表的な書式を試す（分までで揃える）
        for fmt in (
            "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S",
            "%Y-%m-%d %H:%M",    "%Y/%m/%d %H:%M",
            "%Y-%m-%d",          "%Y/%m/%d",
            "%m/%d %H:%M",
        ):
            try:
                dt = datetime.strptime(s, fmt)
                if fmt == "%m/%d %H:%M":
                    dt = dt.replace(year=datetime.now().year)
                return dt.strftime("%Y-%m-%d %H:%M" if "H" in fmt else "%Y-%m-%d")
            except Exception:
                continue
        # ISO 8601 っぽい文字列にも対応
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass
        return s
    return str(v)


def format_progress_mail(report_dict: dict, now: datetime) -> str:
    """
    report_dict 例:
      {
        'りな': {
          'fst': 8, 'rf': 0, 'check_first': 0, 'check_second': 2,
          'gmail_condition': 1, 'check_more': 0, 'check_date': None|datetime|date|int|str
        },
        ...
      }
    旧仕様（report_dict[name] が int）の場合は fst として扱う。
    """
    def get(d, k, default=0):
        if isinstance(d, dict):
            v = d.get(k, default)
            try:
                return int(v)
            except (TypeError, ValueError):
                return default
        # 旧仕様: report_dict[name] が int の時、fst とみなす
        return int(d) if (k == "fst" and isinstance(d, int)) else default

    keys = ["fst", "rf", "check_first", "check_second", "gmail_condition", "check_more"]
    labels = {
        "fst": "FST",
        "rf": "RF",
        "check_first": "1stChk",
        "check_second": "2ndChk",
        "gmail_condition": "Gmail条件",
        "check_more": "More",
        "check_date": "最終チェック",
    }

    # 合計（check_date は集計対象外）
    totals = {k: 0 for k in keys}
    for v in report_dict.values():
        for k in keys:
            totals[k] += get(v, k)

    lines = [
        # f"PCMAXの進捗報告",
        # "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "📊 概要（合計）",
        f"- {labels['fst']}: {totals['fst']} / {labels['rf']}: {totals['rf']}",
        f"- {labels['check_first']}: {totals['check_first']} / {labels['check_second']}: {totals['check_second']}",
        f"- {labels['gmail_condition']}: {totals['gmail_condition']} / {labels['check_more']}: {totals['check_more']}",
        "",
    ]

    def ja_key(s: str) -> str:
        s = unicodedata.normalize("NFKC", s or "")
        # カタカナ→ひらがな（簡易）
        t = []
        for ch in s:
            code = ord(ch)
            t.append(chr(code - 0x60) if 0x30A1 <= code <= 0x30F6 else ch)
        return "".join(t)

    lines.append("👤 キャラ別")
    for name in sorted(report_dict.keys(), key=ja_key):
        v = report_dict[name]
        fst   = get(v, "fst")
        rf    = get(v, "rf")
        c1    = get(v, "check_first")
        c2    = get(v, "check_second")
        gml   = get(v, "gmail_condition")
        more  = get(v, "check_more")
        cdate = _format_check_date(v.get("check_date") if isinstance(v, dict) else None)

        lines.append(
            f"・{name}  |  {labels['fst']} {fst} / {labels['rf']} {rf}  |  "
            f"{labels['check_first']} {c1} / {labels['check_second']} {c2}  |  "
            f"{labels['gmail_condition']} {gml} / {labels['check_more']} {more}  |  "
            f"{labels['check_date']} {cdate}"
        )

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


def get_driver(headless):
  options = Options()
  if headless:
    options.add_argument('--headless')
  options.add_argument("--no-first-run")
  options.add_argument("--disable-popup-blocking")
  options.add_argument("--disable-gpu") 
  options.add_argument("--disable-software-rasterizer")
  options.add_argument("--disable-dev-shm-usage")  # 共有メモリの使用を無効化（仮想環境で役立つ）
  options.add_argument("--incognito")
  options.add_argument('--enable-unsafe-swiftshader')
  options.add_argument('--log-level=3')  # これでエラーログが抑制されます
  options.add_argument('--disable-web-security')
  options.add_argument('--disable-extensions')
  options.add_argument("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1")
  options.add_argument("--no-sandbox")
  options.add_argument("--window-size=456,912")
  options.add_experimental_option("detach", True)
  options.add_argument("--disable-cache")
  options.add_argument("--disable-blink-features=AutomationControlled")  # 自動化検出回避のためのオプション
  # ChromeDriver のログを非表示
  service = Service(ChromeDriverManager().install(), log_output=os.devnull)
  
  # service = Service(executable_path=ChromeDriverManager().install())
  driver = webdriver.Chrome(options=options, service=service)
  wait = WebDriverWait(driver, 18)
  return driver, wait

def get_the_temporary_folder(temp_dir):
  # スクリプトのディレクトリを基準にディレクトリを作成
  script_dir = os.path.dirname(os.path.abspath(__file__)) 
  tmp_dir = os.path.join(script_dir, "tmp")  # tmpフォルダのパスを作成
  if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)
  # tmpフォルダ内に 引数で受け取った フォルダを作成
  dir = os.path.join(tmp_dir, temp_dir)  # h_footprintフォルダのパスを作成
  if not os.path.exists(dir):
    os.makedirs(dir)
  entries = os.listdir(dir)  # ディレクトリ内のエントリを取得
  if len(entries) >= 10:
    print("キャッシュが複数存在するため、クリアします。起動中のマクロは再起動してください。。。")
    for entry in entries:
      entry_path = os.path.join(dir, entry)
      try:
        # エントリがファイルの場合
        if os.path.isfile(entry_path) or os.path.islink(entry_path):
            os.remove(entry_path)
            # print(f"Deleted file: {entry_path}")
        # エントリがフォルダの場合
        elif os.path.isdir(entry_path):
            shutil.rmtree(entry_path)
            # print(f"Deleted folder: {entry_path}")
      except Exception as e:
          print(f"Failed to delete {entry_path}: {e}")
  return dir

def clear_webdriver_cache():
    os_name = platform.system()
    # スクリプトの実行ディレクトリを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 削除するキャッシュディレクトリ
    cache_dirs = []
    # macOS の場合
    if os_name == "Darwin":
        cache_dirs = [
            os.path.expanduser("~/.wdm/drivers"),  # WebDriverのキャッシュディレクトリ
            os.path.join(script_dir, "widget", "tmp", "h_footprint")  # スクリプトの実行ディレクトリに基づいたパス
        ]
    # Windows の場合
    elif os_name == "Windows":
        cache_dirs = [
            os.path.join(os.getenv('USERPROFILE'), '.wdm', 'drivers'),
            os.path.join(script_dir, "widget", "tmp", "h_footprint")
        ]
    else:
        return  # サポートしていないOSの場合は何もしない

    # キャッシュディレクトリの削除
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"Deleted: {cache_dir}")
            except Exception as e:
                print(f"Error clearing cache {cache_dir}: {e}")

def get_multi_driver(profile_path, headless_flag, user_agent="", max_retries=3):
  for attempt in range(max_retries):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(base_dir, profile_path)
    os.makedirs(profile_path, exist_ok=True)
    # Windows ではパスの `\` を適切に処理
    if platform.system() == "Windows":
        profile_path = profile_path.replace("/", "\\")
    try:
      options = Options()
      if headless_flag:
        options.add_argument('--headless')
      options.add_argument(f"--user-data-dir={profile_path}")  # 個別のユーザーデータ
      options.add_argument("--no-first-run")
      options.add_argument("--disable-popup-blocking")
      options.add_argument("--disable-gpu") 
      options.add_argument("--disable-software-rasterizer")
      options.add_argument("--disable-dev-shm-usage")  # 共有メモリの使用を無効化（仮想環境で役立つ）
      options.add_argument("--incognito")
      options.add_argument('--enable-unsafe-swiftshader')
      options.add_argument('--log-level=3')  # これでエラーログが抑制されます
      options.add_argument('--disable-web-security')
      options.add_argument('--disable-extensions')
      if user_agent:
        options.add_argument(f"--user-agent={user_agent}")
      options.add_argument("--no-sandbox")
      options.add_argument("--window-size=456,912")
      options.add_experimental_option("detach", True)
      options.add_argument("--disable-cache")
      options.add_argument("--disable-blink-features=AutomationControlled")  # 自動化検出回避のためのオプション

      # ログ抑制
      options.add_argument("--disable-logging")  # Chromeのログを抑制
      options.add_argument("--log-level=3")  # エラーレベルを最小限に
      options.add_argument("--output=/dev/null")  # ログの出力先を空に
      options.add_argument("--disable-background-networking")  # 不要なネットワーク通信を抑制
      options.add_argument("--mute-audio")  # 音声をミュート
      options.add_experimental_option("excludeSwitches", ["enable-logging"])  # DevToolsのログを抑制
      # ChromeDriver のログを非表示
      service = Service(ChromeDriverManager().install(), log_output=os.devnull)

      # service = Service(executable_path=ChromeDriverManager().install())
      driver = webdriver.Chrome(options=options, service=service)
      wait = WebDriverWait(driver, 18)
      return driver, wait
    except (WebDriverException, NoSuchElementException, MaxRetryError, ConnectionError) as e:
      print(f"WebDriverException発生: {e}")
      print(f"再試行します ({attempt + 1}/{max_retries})")
      clear_webdriver_cache()
      time.sleep(5)
      if attempt == max_retries - 1:
          raise
    except ConnectionError as e:
      print(f"⚠️ ネットワークエラーが発生しました: {e}")
      print("3分後に再接続します...")
      clear_webdriver_cache()
      time.sleep(180)
      if attempt == max_retries - 1:
          raise

def close_all_drivers(drivers_dict):
  for name, data in list(drivers_dict.items()):
    try:
      data["driver"].quit()
      # print(f"{name} のブラウザを正常に閉じました")
      pid = data["driver"].service.process.pid
      print(f"🔴 {name} の ChromeDriver を終了 (PID: {pid})...")
      
      if psutil.pid_exists(pid):
          print(f"💀 {name} の ChromeDriver プロセスがまだ生存しているため、強制終了します")
          os.kill(pid, signal.SIGTERM)
      # print(f"✅ {name} の ChromeDriver (PID: {pid}) を終了しました")
    except WebDriverException as e:
      print(f"{name} のブラウザを閉じる際にエラーが発生: {e}")
  drivers_dict.clear() 

def test_get_driver(tmp_dir, headless_flag, max_retries=3, profile_path="", user_agent=""):
    # os_name = platform.system()
    # print(tmp_dir)
    # tmpフォルダ内に一意のキャッシュディレクトリを作成
    if tmp_dir:
      temp_dir = os.path.join(tmp_dir, f"temp_cache_{os.getpid()}")  # 一意のディレクトリを生成（PIDベース）
      os.environ["WDM_CACHE"] = temp_dir
      if not os.path.exists(temp_dir):
          os.makedirs(temp_dir)  # キャッシュディレクトリが存在しない場合は作成
    # print(f"WDM_CACHE is set to: {os.environ['WDM_CACHE']}")
    for attempt in range(max_retries):
      try:
        options = Options()
        if headless_flag:
          options.add_argument('--headless')
        if profile_path:
          options.add_argument(f"--user-data-dir={profile_path}")
          options.add_argument("--profile-directory=Profile 74")
        else:
          options.add_argument("--incognito")
        if user_agent:
          options.add_argument(f"--user-agent={user_agent}")
        options.add_argument("--disable-gpu") 
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-dev-shm-usage")  # 共有メモリの使用を無効化（仮想環境で役立つ）
        options.add_argument('--enable-unsafe-swiftshader')
        options.add_argument('--log-level=3')  # これでエラーログが抑制されます
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-extensions')
        options.add_argument("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=456,912")
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-cache")
        options.add_argument("--disable-blink-features=AutomationControlled")  # 自動化検出回避のためのオプション
        service = Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(options=options, service=service)
        wait = WebDriverWait(driver, 18)
        return driver, wait
      except (WebDriverException, NoSuchElementException, MaxRetryError, ConnectionError) as e:
        print(f"WebDriverException発生: {e}")
        print(f"再試行します ({attempt + 1}/{max_retries})")
        clear_webdriver_cache()
        time.sleep(5)
        if attempt == max_retries - 1:
            raise
      except ConnectionError as e:
        print(f"⚠️ ネットワークエラーが発生しました: {e}")
        print("3分後に再接続します...")
        clear_webdriver_cache()
        time.sleep(180)
        if attempt == max_retries - 1:
            raise

def timer(fnc, seconds, h_cnt, p_cnt):  
  start_time = time.time() 
  fnc(h_cnt, p_cnt)
  while True:
    elapsed_time = time.time() - start_time  # 経過時間を計算する
    if elapsed_time >= seconds:
      start_time = time.time() 
      break
    else:
      time.sleep(10)
  return True

def send_conditional(user_name, user_address, mailaddress, password, text, site):
  subject = f'{site}でやり取りしてた{user_name}さんでしょうか？'
  text = text
  address_from = mailaddress
  address_to = user_address
  smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
  smtpobj.set_debuglevel(0)
  smtpobj.starttls()
  smtpobj.login(mailaddress, password)
  msg = MIMEText(text)
  msg['Subject'] = subject
  msg['From'] = address_from
  msg['To'] = address_to
  msg['Date'] = formatdate()
  smtpobj.send_message(msg)
  smtpobj.close()  

def send_error(chara, error_message, attachment_paths=None):
    """
    エラーメールを送信。画像・ファイル添付に対応
    :param chara:  キャラ名など
    :param error_message: 本文に載せるエラー文字列
    :param attachment_paths: 文字列 or 文字列のリスト（添付するファイルパス）
    """
    # ★本番は環境変数に置き換えるのを強く推奨
    mailaddress = 'kenta.bishi777@gmail.com'
    password = 'rjdzkswuhgfvslvd'   # アプリパスワード推奨（2段階認証ON）
    address_from = 'kenta.bishi777@gmail.com'
    address_to = "gifopeho@kmail.li"
    subject = "エラーメッセージ"

    # マルチパート（本文 + 添付）
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = address_from
    msg['To'] = address_to
    msg['Date'] = formatdate()

    # 本文（UTF-8）
    body = f"キャラ名: {chara}\n{error_message}"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 添付があれば追加（画像でもその他でもOK）
    if attachment_paths:
        if isinstance(attachment_paths, str):
            attachment_paths = [attachment_paths]
        for path in attachment_paths:
            if not path or not os.path.exists(path):
                continue
            ctype, encoding = mimetypes.guess_type(path)
            maintype, subtype = (ctype.split('/', 1) if ctype else ('application', 'octet-stream'))

            with open(path, 'rb') as f:
                if maintype == 'image':
                    part = MIMEImage(f.read(), _subtype=subtype, name=os.path.basename(path))
                else:
                    part = MIMEBase(maintype, subtype)
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition',
                                    f'attachment; filename="{os.path.basename(path)}"')
            # 画像の場合も Content-Disposition を付けておくと親切
            if maintype == 'image':
                part.add_header('Content-Disposition',
                                f'attachment; filename="{os.path.basename(path)}"')
            msg.attach(part)

    # 送信
    smtpobj = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
    try:
        # smtpobj.set_debuglevel(1)  # 必要ならオン
        smtpobj.starttls()
        smtpobj.login(mailaddress, password)
        smtpobj.send_message(msg)
    finally:
        smtpobj.close()
   
def send_mail(message, mail_info, title, image_paths=None):
  mailaddress = mail_info[1]
  password = mail_info[2]
  text = message
  subject = title
  address_from = mail_info[1]
  address_to = mail_info[0]

  # マルチパートメッセージを作成
  msg = MIMEMultipart()
  msg['Subject'] = subject
  msg['From'] = address_from
  msg['To'] = address_to
  msg['Date'] = formatdate()

  # 本文を追加
  msg.attach(MIMEText(text, 'plain', 'utf-8'))

  # 画像の添付処理（1枚でも複数枚でも対応）
  if image_paths:
      # もし文字列（1枚）ならリストに変換
      if isinstance(image_paths, str):
          paths = [image_paths]
      else:
          paths = image_paths

      for path in paths:
          if os.path.exists(path):
              with open(path, 'rb') as f:
                  img_data = f.read()
              image = MIMEImage(img_data, name=os.path.basename(path))
              msg.attach(image)
          else:
              print(f"⚠️ 添付失敗: ファイルが存在しません → {path}")
  # Gmail SMTP サーバへ接続
  smtpobj = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)  # 30秒でタイムアウト
  smtpobj.set_debuglevel(0)  # デバッグログオフ
  smtpobj.starttls()
  smtpobj.login(mailaddress, password)
  try:
    smtpobj.send_message(msg)
    print("通知メール送信完了")
  except Exception as e:
    print("❌ 通知メール送信エラー:", e)
    if "Daily user sending limit exceeded" in str(e):
      print("⚠️ Gmail送信上限に達しました。別アカウントを使うか翌日まで待機してください。")
    else:
      traceback.print_exc()
  finally:
    smtpobj.close()
  



def h_p_return_footprint(name, h_w, p_w, driver, return_foot_message, cnt, h_return_foot_img, p_return_foot_img):
  start_time = time.time() 
  wait = WebDriverWait(driver, 10)
  wait_time = random.uniform(1, 3)
  history_user_list = []
  p_w = ""
  # wait_time = 2
  # ハッピーメールの足跡リストまで
  driver.switch_to.window(h_w)
  driver.get("https://happymail.co.jp/sp/app/html/mbmenu.php")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  # マイページをクリック
  nav_list = driver.find_element(By.ID, value='ds_nav')
  mypage = nav_list.find_element(By.LINK_TEXT, "マイページ")
  mypage.click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  # 足あとをクリック
  return_footpoint = driver.find_element(By.CLASS_NAME, value="icon-ico_footprint")
  return_footpoint.click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  # 足跡ユーザーを取得
  happy_foot_user = driver.find_elements(By.CLASS_NAME, value="ds_post_head_main_info")
  while len(happy_foot_user) == 0:
      time.sleep(2)
      happy_foot_user = driver.find_elements(By.CLASS_NAME, value="ds_post_head_main_info")  
  mail_icon_cnt = 0
  name_field = happy_foot_user[0].find_element(By.CLASS_NAME, value="ds_like_list_name")
  user_name = name_field.text
  mail_icon = name_field.find_elements(By.TAG_NAME, value="img")
  mail_icon_cnt = 0
  if len(mail_icon):
    if not user_name in history_user_list:
        # print(history_user_list)
        mail_icon_cnt = 0
        history_user_list.append(user_name)
        happy_foot_user[0].click()
    else:
      # print('ハッピーメール：メールアイコンがあります')
      mail_icon_cnt += 1
      # print(f'メールアイコンカウント{mail_icon_cnt}')
      name_field = happy_foot_user[mail_icon_cnt].find_element(By.CLASS_NAME, value="ds_like_list_name")
      user_name = name_field.text
      mail_icon = name_field.find_elements(By.TAG_NAME, value="img")
      # # メールアイコンが7つ続いたら終了
      if mail_icon_cnt == 5:
        print("ハッピーメール：メールアイコンが5続きました")
      # ユーザークリック
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", happy_foot_user[mail_icon_cnt])
      time.sleep(1)
      happy_foot_user[mail_icon_cnt].click()
  else:
    happy_foot_user[0].click()

  # PCMAXの足跡リストまで
  if p_w:
    driver.switch_to.window(p_w)
    pcmax.login(driver, wait)
    # 新着メッセージの確認
    have_new_massage_users = []
    new_message = driver.find_element(By.CLASS_NAME, value="message")
    new_message.click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    user_info = driver.find_elements(By.CLASS_NAME, value="user_info")
    # 新着ありのユーザーをリストに追加
    for usr_info in user_info:
      unread = usr_info.find_elements(By.CLASS_NAME, value="unread1")
      if len(unread):
        new_mail_pcmax_name = usr_info.find_element(By.CLASS_NAME, value="name").text
        if len(new_mail_pcmax_name) > 7:
          new_mail_pcmax_name = new_mail_pcmax_name[:7] + "…"
        have_new_massage_users.append(new_mail_pcmax_name)
    print("新着メッセージリスト")
    print(have_new_massage_users)
    driver.get("https://pcmax.jp/pcm/index.php")
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    # 右下のキャラ画像をクリック
    chara_img = driver.find_elements(By.XPATH, value="//*[@id='sp_footer']/a[5]")
    if len(chara_img):
      chara_img[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
    else: #番号確認画面
      return
    # //*[@id="contents"]/div[2]/div[2]/ul/li[5]/a
    # 足あとをクリック
    footpoint = driver.find_element(By.XPATH, value="//*[@id='contents']/div[2]/div[2]/ul/li[5]/a")
    footpoint.click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    for i in range(3):
      # ページの最後までスクロール
      driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      # ページが完全に読み込まれるまで待機
      time.sleep(1)
    # ユーザーを取得
    user_list = driver.find_element(By.CLASS_NAME, value="list-content")
    div = user_list.find_elements(By.XPATH, value='./div')
    # ユーザーのlinkをリストに保存
    link_list = []
    user_cnt = 0
    # print(len(div))
    while user_cnt + 1 < len(div) - 1:
      # 新着リストの名前ならスキップ
      new_mail_name = div[user_cnt].find_element(By.CLASS_NAME, value="user-name")
      if new_mail_name.text in have_new_massage_users:
        user_cnt += 1
      else:
        a_tags = div[user_cnt].find_elements(By.TAG_NAME, value="a")
        # print("aタグの数：" + str(len(a_tags)))
        if len(a_tags) > 1:
          link = a_tags[1].get_attribute("href")
          # print(link)
          link_list.append(link)
        user_cnt += 1
  # メッセージを送信
  pcmax_return_message_cnt = 1
  pcmax_transmission_history = 0
  pcmax_send_flag = True
  foot_cnt = 0
  p_foot_cnt = 0
  p_send_cnt = 0
  while cnt > foot_cnt:
    # happymail
    driver.switch_to.window(h_w)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    happy_send_status = True
    m = driver.find_elements(By.XPATH, value="//*[@id='ds_main']/div/p")
    if len(m):
      print(m[0].text)
      if m[0].text == "プロフィール情報の取得に失敗しました": 
          continue
    # 自己紹介文に業者、通報が含まれているかチェック
    if len(driver.find_elements(By.CLASS_NAME, value="translate_body")):
      contains_violations = driver.find_element(By.CLASS_NAME, value="translate_body")
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", contains_violations)
      self_introduction_text = contains_violations.text.replace(" ", "").replace("\n", "")
      if '通報' in self_introduction_text or '業者' in self_introduction_text:
          print('ハッピーメール：自己紹介文に危険なワードが含まれていました')
          happy_send_status = False
    # メッセージ履歴があるかチェック
    mail_field = driver.find_element(By.ID, value="ds_nav")
    mail_history = mail_field.find_element(By.ID, value="mail-history")
    display_value = mail_history.value_of_css_property("display")
    if display_value != "none":
        print('ハッピーメール：メール履歴があります')
        # print(user_name)
        # user_name_list.append(user_name) 
        happy_send_status = False
        mail_icon_cnt += 1
    # メールするをクリック
    if happy_send_status:
      send_mail = mail_field.find_element(By.CLASS_NAME, value="ds_profile_target_btn")
      send_mail.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
      # 足跡返しを入力
      text_area = driver.find_element(By.ID, value="text-message")
      text_area.send_keys(return_foot_message)
      # 送信
      send_mail = driver.find_element(By.ID, value="submitButton")
      send_mail.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
      # 画像があれば送信
      if h_return_foot_img:
        img_conform = driver.find_element(By.ID, value="media-confirm")
        plus_icon = driver.find_element(By.CLASS_NAME, value="icon-message_plus")
        plus_icon.click()
        time.sleep(1)
        upload_file = driver.find_element(By.ID, "upload_file")
        upload_file.send_keys(h_return_foot_img)
        time.sleep(1)
        submit = driver.find_element(By.ID, value="submit_button")
        submit.click()
        while img_conform.is_displayed():
            time.sleep(1)
      foot_cnt += 1
      print(name + ':ハッピーメール：'  + str(foot_cnt) + "件送信")
      mail_icon_cnt = 0
      driver.get("https://happymail.co.jp/sp/app/html/ashiato.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      # https://happymail.co.jp/sp/app/html/ashiato.php
    else:
      driver.get("https://happymail.co.jp/sp/app/html/ashiato.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
    # 足跡ユーザーを取得
    time.sleep(1)
    happy_foot_user = driver.find_elements(By.CLASS_NAME, value="ds_post_head_main_info")
    while len(happy_foot_user) == 0:
        time.sleep(1)
        happy_foot_user = driver.find_elements(By.CLASS_NAME, value="ds_post_head_main_info")    
    name_field = happy_foot_user[0].find_element(By.CLASS_NAME, value="ds_like_list_name")
    user_name = name_field.text
    
    # print(user_name)
    # print(history_user_list)
    mail_icon = name_field.find_elements(By.TAG_NAME, value="img")
    if len(mail_icon):
      while len(mail_icon):
        if not user_name in history_user_list:
          
          mail_icon_cnt = 0
          history_user_list.append(user_name)
          happy_foot_user[0].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
          driver.get("https://happymail.co.jp/sp/app/html/ashiato.php")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(wait_time)
          happy_foot_user = driver.find_elements(By.CLASS_NAME, value="ds_post_head_main_info")
          name_field = happy_foot_user[0].find_element(By.CLASS_NAME, value="ds_like_list_name")
          mail_icon = name_field.find_elements(By.TAG_NAME, value="img")
        else:
          # print('ハッピーメール：メールアイコンがあります')
          mail_icon_cnt += 1
          # print(f'メールアイコンカウント{mail_icon_cnt}')
          name_field = happy_foot_user[mail_icon_cnt].find_element(By.CLASS_NAME, value="ds_like_list_name")
          user_name = name_field.text
          mail_icon = name_field.find_elements(By.TAG_NAME, value="img")
          # # メールアイコンが7つ続いたら終了
          if mail_icon_cnt == 5:
            print("ハッピーメール：メールアイコンが5続きました")
      # ユーザークリック
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", happy_foot_user[mail_icon_cnt])
      time.sleep(1)
      happy_foot_user[mail_icon_cnt].click()
    else:
      happy_foot_user[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(2)


    # pcmax
    if p_w and pcmax_send_flag:
      transmission_history = 0
      driver.switch_to.window(p_w)
      time.sleep(1)
      driver.get(link_list[p_foot_cnt])
      time.sleep(wait_time)
      # お相手のご都合により表示できませんはスキップ
      main = driver.find_elements(By.TAG_NAME, value="main")
      if not len(main):
        p_foot_cnt += 1
        continue

      # 送信履歴が連続で続くと終了
      sent = driver.find_elements(By.XPATH, value="//*[@id='profile-box']/div/div[2]/p/a/span")
      if len(sent):
        pcmax_transmission_history += 1
        if pcmax_transmission_history == 5:
          pcmax_send_flag = False
        print('pcmax:送信履歴があります')
        print(f"送信履歴カウント：{pcmax_transmission_history}" )
        p_foot_cnt += 1
        time.sleep(1)
        continue
      # 自己紹介文をチェック
      self_introduction = driver.find_elements(By.XPATH, value="/html/body/main/div[4]/div/p")
      if len(self_introduction):
        self_introduction = self_introduction[0].text.replace(" ", "").replace("\n", "")
        if '通報' in self_introduction or '業者' in self_introduction:
          print('pcmax:自己紹介文に危険なワードが含まれていました')
          p_foot_cnt += 1
          continue
      # 残ポイントチェック
      point = driver.find_elements(By.ID, value="point")
      if len(point):
        point = point[0].find_element(By.TAG_NAME, value="span").text
        pattern = r'\d+'
        match = re.findall(pattern, point)
        if int(match[0]) > 1:
          maji_soushin = True
        else:
          maji_soushin = False
      else:
        time.sleep(wait_time)
        print(' 相手の都合により表示できません')
        p_foot_cnt += 1
        continue
      # メッセージをクリック
      message = driver.find_elements(By.ID, value="message1")
      if len(message):
        message[0].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(3)
      else:
        continue
      # 画像があれば送付
      if p_return_foot_img:
        picture_icon = driver.find_elements(By.CLASS_NAME, value="mail-menu-title")
        picture_icon[0].click()
        time.sleep(1)
        picture_select = driver.find_element(By.ID, "my_photo")
        select = Select(picture_select)
        select.select_by_visible_text(p_return_foot_img)
      # メッセージを入力
      text_area = driver.find_element(By.ID, value="mdc")
      text_area.send_keys(return_foot_message)
      time.sleep(1)
      p_foot_cnt += 1
      p_send_cnt += 1
      print("pcmax:マジ送信 " + str(maji_soushin) + " ~" + str(p_send_cnt) + "~")
      # メッセージを送信
      if maji_soushin:
        send = driver.find_element(By.CLASS_NAME, value="maji_send")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", send)
        send.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        send_link = driver.find_element(By.ID, value="link_OK")
        send_link.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        # time.sleep(wait_time)
        pcmax_transmission_history = 0
      else:
        send = driver.find_element(By.ID, value="send_n")
        send.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        # time.sleep(wait_time)
        # mail_history = 0
  # timedeltaオブジェクトを作成してフォーマットする
  elapsed_time = time.time() - start_time  # 経過時間を計算する
  elapsed_timedelta = timedelta(seconds=elapsed_time)
  elapsed_time_formatted = str(elapsed_timedelta)
  print(f"<<<<<<<<<<<<<h_p_foot 経過時間 {elapsed_time_formatted}>>>>>>>>>>>>>>>>>>")
  print(f"pcmax足跡返し　{name}、{p_send_cnt}件")


def check_new_mail_gmail(driver, wait, name, mail_address):
  if not mail_address:
    return None
  return_list = []
  dbpath = 'firstdb.db'
  conn = sqlite3.connect(dbpath)
  cur = conn.cursor()
  cur.execute('SELECT window_Handle FROM gmail WHERE mail_address = ?', (mail_address,))
  w_h = ""
  for row in cur:
      w_h = row[0]
  if not w_h:
    return None
  cur.execute('SELECT login_id, passward FROM pcmax WHERE name = ?', (name,))
  login_id = ""
  passward = ""
  for row in cur:
    login_id = row[0]
    passward = row[1]
  try:
      driver.switch_to.window(w_h)
      time.sleep(2)
      driver.get("https://mail.google.com/mail/mu")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(2)  
  except TimeoutException as e:
      print("TimeoutException")
      driver.refresh()
  except Exception as e:
      print(f"<<<<<<<<<<エラー：{mail_address}>>>>>>>>>>>")
      print(traceback.format_exc())
      driver.quit()
  # メニューをクリック
  # カスタム属性の値を持つ要素をXPathで検索
  custom_value = "メニュー"
  xpath = f"//*[@aria-label='{custom_value}']"
  element = driver.find_elements(By.XPATH, value=xpath)
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(2) 
  element[0].click()
  time.sleep(1) 
  custom_value = "toggleaccountscallout+21"
  xpath = f"//*[@data-control-type='{custom_value}']"
  element = driver.find_elements(By.XPATH, value=xpath)
  if len(element):
      time.sleep(2)
      element = driver.find_elements(By.XPATH, value=xpath)
  address = element[0].text
  # メインボックスのチェック
  menuitem_element = driver.find_elements(By.XPATH, '//*[@role="menuitem"]')
  main_box = menuitem_element[0]
  main_box.click()
  time.sleep(1)
  emails = driver.find_elements(By.XPATH, value='//*[@role="listitem"]')
  for email in emails:
    new_email = email.find_elements(By.TAG_NAME, value="b")
    if len(new_email):
      child_elements = email.find_elements(By.CLASS_NAME, value="Rk")
      if child_elements[0].text:  # テキストが空でない場合
          # print(f"この子要素にテキストが含まれています: {child_elements[0].text}")
          return_list.append(f"{address},{login_id}:{passward}\n「{child_elements[0].text}」")
      email.click()
      time.sleep(2)
      driver.back()
      time.sleep(1)
    else:
      continue
      
  # 迷惑メールフォルダーをチェック
  custom_value = "メニュー"
  xpath = f"//*[@aria-label='{custom_value}']"
  element = driver.find_elements(By.XPATH, value=xpath)
  element[0].click()
  time.sleep(2) 
  menu_list = driver.find_elements(By.XPATH, value="//*[@role='menuitem']")
  spam = menu_list[-1]
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", spam)
  spam.click()
  time.sleep(1) 
  emails = driver.find_elements(By.XPATH, value='//*[@role="listitem"]')
  for email in emails:
    new_email = email.find_elements(By.TAG_NAME, value="b")
    if len(new_email):
      child_elements = email.find_elements(By.CLASS_NAME, value="Rk")
      if child_elements[0].text:  # テキストが空でない場合
          # print(f"この子要素にテキストが含まれています: {child_elements[0].text}")
          return_list.append(f"{address}:迷惑フォルダ,{login_id}:{passward}\n「{child_elements[0].text}」")
      email.click()
      time.sleep(2)
      driver.back()
      time.sleep(1)
    else:
      continue
  custom_value = "メニュー"
  xpath = f"//*[@aria-label='{custom_value}']"
  element = driver.find_elements(By.XPATH, value=xpath)
  element[0].click()
  # window_handles = driver.window_handles
  # for window_handle in window_handles:
  #   driver.switch_to.window(window_handle)
  #   current_url = driver.current_url
  #   if current_url.startswith("https://mail.google.com/mail/mu"):
  #       print("URLがhttps://mail.google.com/mail/muから始まります。")
  #   else:
  #       print("URLがhttps://mail.google.com/mail/muから始まりません。")
  if len(return_list):
    return return_list
  else:
    return None

def get_user_data_ken2():
  # APIエンドポイントURL
  api_url = "https://meruopetyan.com/api/user-data/"
  # DEBUG
  # api_url = "http://127.0.0.1:8000/api/user-data/"
  max_retries = 3
  retry_count = 0
  wait_time = 300  # 5分（300秒）

  # POSTリクエストのペイロード
  data = {
      'name': "ken2",
      'password': "7234"
  }
  while retry_count < max_retries:

    try:
      # POSTリクエストを送信してデータを取得
      response = requests.post(api_url, data=data)
      
      # レスポンスのステータスコードを確認
      if response.status_code == 200:
          # レスポンスのJSONデータを取得
          user_data = response.json()

          # Happymailデータを表示
          # print("Happymailのデータ:")
          # for data in user_data.get('userprofile', []):
          #     print(f"Name: {data['gmail_account']}, ")

          # # PCMaxデータを表示
          # print("PCMaxのデータ:")
          # for data in user_data.get('pcmax', []):
          #     print(f"Name: {data['name']}, ")
          return user_data
      elif response.status_code == 204:
        print(f"有効期限が切れている可能性があります。")
        return 0
      elif response.status_code == 404:
        print(f"ユーザー名が見つかりません。")
        return 0
      elif response.status_code == 400:
        print(f"パスワードが正しくありません。")
        return 0
      
      else:
        print(f"Error: {response.status_code}, データの取得に失敗しました。")
        return 0
    except requests.exceptions.ConnectionError as e:
      retry_count += 1
      print(f"接続エラーが発生しました。リトライ回数: {retry_count}/{max_retries}")
      if retry_count >= max_retries:
          print("最大リトライ回数に達しました。エラーを終了します。")
          raise e
      print(f"{wait_time}秒後にリトライします...")
      time.sleep(wait_time)  # 5分間待機
  # すべてのリトライが失敗した場合のエラーメッセージ
  raise Exception("サーバーへの接続に失敗しました。")

def get_user_data():
  # APIエンドポイントURL
  api_url = "https://meruopetyan.com/api/user-data/"
  # DEBUG
  # api_url = "http://127.0.0.1:8000/api/user-data/"
  max_retries = 3
  retry_count = 0
  wait_time = 300  # 5分（300秒）

  try:
    # ユーザーのnameとpasswordを設定
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    # 最新のユーザーデータを取得
    c.execute("SELECT user_name, password FROM users ORDER BY id DESC LIMIT 1")
    user_data = c.fetchone()
    conn.close()
  except sqlite3.OperationalError as e:
        print(f"ユーザーデータを登録してください。")
        return 2
  if not user_data[0] or not user_data[1]:
    print("ユーザーデータがありません")
    return 2
      
  user_name = user_data[0]
  password = user_data[1]
  # POSTリクエストのペイロード
  data = {
      'name': user_name,
      'password': password
  }

  while retry_count < max_retries:
    try:
      # POSTリクエストを送信してデータを取得
      response = requests.post(api_url, data=data)
      # レスポンスのステータスコードを確認
      if response.status_code == 200:
          # レスポンスのJSONデータを取得
          user_data = response.json()

          # Happymailデータを表示
          # print("Happymailのデータ:")
          # for data in user_data.get('userprofile', []):
          #     print(f"Name: {data['gmail_account']}, ")

          # # PCMaxデータを表示
          # print("PCMaxのデータ:")
          # for data in user_data.get('pcmax', []):
          #     print(f"Name: {data['name']}, ")
          return user_data
      elif response.status_code == 204:
        print(f"有効期限が切れている可能性があります。")
        return 0
      elif response.status_code == 404:
        print(f"ユーザー名が見つかりません。")
        return 0
      elif response.status_code == 400:
        print(f"パスワードが正しくありません。")
        return 0
      
      else:
        print(f"Error: {response.status_code}, データの取得に失敗しました。")
        return 0
    except requests.exceptions.ConnectionError as e:
      retry_count += 1
      print(f"接続エラーが発生しました。リトライ回数: {retry_count}/{max_retries}")
      if retry_count >= max_retries:
          print("最大リトライ回数に達しました。エラーを終了します。")
          raise e
      print(f"{wait_time}秒後にリトライします...")
      time.sleep(wait_time)  # 5分間待機
  # すべてのリトライが失敗した場合のエラーメッセージ
  raise Exception("サーバーへの接続に失敗しました。")

# 文字列を正規化する関数
def normalize_text(text, user_name=""):
    # if user_name:
    #   text.replace("〇〇", user_name)
    # Unicodeの互換正規化（NFKC）を使って、全角・半角や記号を統一
    return unicodedata.normalize('NFKC', text).replace("\n", "").replace("\r", "").replace(" ", "").replace("　", "").replace("〜", "~")

def change_tor_ip():
  with Controller.from_port(port=9051) as controller:
    controller.authenticate()  # デフォルト設定の場合は認証不要
    controller.signal(Signal.NEWNYM)
  time.sleep(5)  # 新しい回線が張られるのを待つ
  
def get_current_ip():
    session = requests.Session()

    # プロキシ設定
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }

    try:
        # プロキシ経由で試す
        return session.get("http://httpbin.org/ip", timeout=5).text
    except Exception as e:
        print("⚠️ プロキシ経由での接続に失敗:", e)
        print("➡️ 代わりに直アクセスします。")

        # プロキシを無効化して再チャレンジ
        session.proxies = {"http": None, "https": None}

        try:
            return session.get("http://httpbin.org/ip", timeout=5).text
        except Exception as e2:
            print("❌ 直アクセスも失敗:", e2)
            return "UNKNOWN"

def resolve_reCAPTCHA(login_url, site_key):
  API_KEY = "1bc4af1c018d3882d89bae813594befb"  
  PAGE_URL = login_url
  SITE_KEY = site_key  

  # 🔹 2Captcha にリクエストを送信
  print("🛠️ 2Captcha にリクエスト送信中...")
  response = requests.post("http://2captcha.com/in.php", {
      "key": API_KEY,
      "method": "userrecaptcha",
      "googlekey": SITE_KEY,
      "pageurl": PAGE_URL,
      "json": 1
  }).json()

  # 🔹 APIエラー処理
  if response["status"] != 1:
      print("❌ 2Captcha リクエスト失敗:", response)
      exit()

  # 🔹 reCAPTCHA の解決待ち
  captcha_id = response["request"]
  print("⏳ reCAPTCHA の解決中...")

  for i in range(30):  # 最大30秒待つ
      time.sleep(3)  # 5秒ごとにチェック
      result = requests.get(f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}&json=1").json()
      
      if result["status"] == 1:
          captcha_solution = result["request"]
          print("✅ reCAPTCHA 解決成功！")
          print(captcha_solution)

          return captcha_solution
  else:
      print("❌ reCAPTCHA の解決に失敗しました")
      exit()
      return False

def test_get_DrissionChromium(profile_dir=None, headless_flag=False, max_retries=3):
  for attempt in range(max_retries):
    try:
      port = random.randint(9100, 9200)  # 🔸 各ブラウザにランダムなポートを指定
      options = ChromiumOptions()
      if headless_flag:
          options.headless(True)
      options.set_argument("--disable-gpu")
      options.set_argument("--log-level=3")
      # 🔽 ここが重要：ユーザープロファイルのディレクトリを指定！
      if profile_dir:
          options.set_paths(local_port=port, user_data_path=profile_dir)
      chromium = Chromium(options)
      return chromium

    except BrowserConnectError as e:
      print(f"BrowserConnectError発生: {e}")
      print(f"再試行します ({attempt + 1}/{max_retries})")
      time.sleep(5)
      if attempt == max_retries - 1:
        raise
    except ConnectionError as e:
      print(f"⚠️ ネットワークエラーが発生しました: {e}")
      print("3分後に再接続します...")
      time.sleep(180)
      if attempt == max_retries - 1:
        raise

# 最大リトライ回数
MAX_RETRIES = 3
def safe_execute(driver, action, *args, **kwargs):
  """
  タイムアウトが発生した場合にリトライするラッパー関数
  """
  retries = 0
  while retries < MAX_RETRIES:
    try:
      print(f"[試行中] {action.__name__} (試行回数: {retries + 1})")
      result = action(*args, **kwargs)
      print(f"[成功] {action.__name__} が完了しました")
      print(driver.current_url)
      # スクショします
      driver.save_screenshot(f"{action.__name__}_{retries + 1}.png")
      return result
    except (ReadTimeoutError, TimeoutException) as e:
      retries += 1
      print(f"[警告] タイムアウト発生: {e}")
      print("[再試行] ページをリロードします")
      driver.refresh()
      time.sleep(5)  # 5秒待機して再試行
    except Exception as e:
      print(f"[エラー] {action.__name__} の実行中にエラーが発生しました: {e}")
      return None
  print(f"[エラー] 最大試行回数 ({MAX_RETRIES}) に達したためスキップします")
  return None

def compress_image(input_path, output_path=None, max_width=1280, quality=65):
    """
    PNGなどのスクショをJPEGへ変換しつつ圧縮。
    - max_width を超える場合はアスペクト比を保って縮小
    - quality は 50〜70 くらいが目安
    戻り値: 出力ファイルのパス
    """
    if output_path is None:
        base, _ = os.path.splitext(input_path)
        output_path = base + "_compressed.jpg"

    # 画像を開く
    with Image.open(input_path) as im:
        # JPEG用にRGBへ
        if im.mode != "RGB":
            im = im.convert("RGB")

        # リサイズ（横幅基準）
        w, h = im.size
        if w > max_width:
            new_h = int(h * (max_width / w))
            im = im.resize((max_width, new_h), Image.LANCZOS)

        # 圧縮保存（最小限のサイズにしたいなら optimize=True / progressive=True）
        im.save(output_path, format="JPEG", quality=quality, optimize=True, progressive=True)

    return output_path

def find_by_id(driver, element_id: str):
    """
    Android Chrome + Appium で By.ID が invalid locator になる問題を吸収するラッパー。
    1. まず By.ID を試す
    2. invalid locator の場合は CSSセレクタ #id で再トライ
    """
    try:
        return driver.find_element(By.ID, element_id)
    except InvalidArgumentException:
        # モバイル Chrome だと ID ロケータが invalid になる場合がある
        return driver.find_element(By.CSS_SELECTOR, f'#{element_id}')


def find_by_name(driver, name: str):
    """
    Android Chrome + Appium で By.NAME が invalid locator になる問題を吸収するラッパー。
    1. まず By.NAME を試す
    2. invalid locator の場合は CSSセレクタ [name="..."] で再トライ
    """
    try:
        return driver.find_element(By.NAME, name)
    except InvalidArgumentException:
        return driver.find_element(By.CSS_SELECTOR, f'[name="{name}"]')
    
def normalize_ai_text(text, name):
    text = text.removeprefix("アシスタント:")
    text = text.removeprefix(name + ":")  

    return text


def chat_ai_gemini(name, system_prompt, history, first_greeting, user_input=None, max_retry=3, ):
    client = genai.Client(
        api_key=settings.Gemini_API_KEY,
        http_options=HttpOptions(api_version="v1")
    )
    if not user_input or user_input.strip() == "":
        history.clear()
        history.append({"role": "assistant", "text": first_greeting})
        return first_greeting, history

    # ===== Gemini用：全文を1つのテキストにまとめる =====
    prompt_parts = []

    if system_prompt.strip():
        prompt_parts.append(f"【システム指示】\n{system_prompt}")

    for h in history:
        role = "ユーザー" if h["role"] == "user" else "アシスタント"
        prompt_parts.append(f"{role}: {h['text']}")

    prompt_parts.append(f"ユーザー: {user_input}")

    full_prompt = "\n\n".join(prompt_parts)
    # =================================================

    for attempt in range(1, max_retry + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite-001",

                contents=full_prompt,  # ← 文字列のみ
            )
            reply_text = response.text.strip()
            reply_text = normalize_ai_text(reply_text, name)

            history.append({"role": "user", "text": user_input})
            history.append({"role": "assistant", "text": reply_text})

            return reply_text, history

        except ClientError as e:
            if e.code == 429:
                print(f"⚠️ Gemini 429 (試行 {attempt}/{max_retry}) → 10秒待機")
                time.sleep(10)
                continue
            else:
                raise

    print("❌ Gemini 429 が続いたため今回はスキップ")
    return None, history


def chat_ai(name, system_prompt, history, first_greeting, user_input=None, max_retry=3):
    """Anthropic (Claude) 版の chat_ai。既存の chat_ai_gemini と同じシグネチャ。"""
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    if not user_input or user_input.strip() == "":
        history.clear()
        history.append({"role": "assistant", "text": first_greeting})
        return first_greeting, history

    # history を Anthropic 形式 (role: user/assistant, content: text) に変換
    # Gemini履歴では "model" が assistant 相当なので変換する
    messages = []
    for h in history:
        role = h.get("role", "user")
        if role not in ("user", "assistant"):
            role = "assistant" if role == "model" else "user"
        messages.append({"role": role, "content": h.get("text", "")})
    messages.append({"role": "user", "content": user_input})

    sys_text = (system_prompt or "").strip() if isinstance(system_prompt, str) else ""

    for attempt in range(1, max_retry + 1):
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=sys_text,
                messages=messages,
            )
            reply_text = response.content[0].text.strip()
            reply_text = normalize_ai_text(reply_text, name)

            history.append({"role": "user", "text": user_input})
            history.append({"role": "assistant", "text": reply_text})

            return reply_text, history

        except anthropic.RateLimitError:
            print(f"⚠️ Claude 429 (試行 {attempt}/{max_retry}) → 10秒待機")
            time.sleep(10)
            continue
        except anthropic.APIStatusError as e:
            status = getattr(e, "status_code", None)
            if status in (429, 529):
                print(f"⚠️ Claude {status} (試行 {attempt}/{max_retry}) → 10秒待機")
                time.sleep(10)
                continue
            raise

    print("❌ Claude リトライ上限到達のためスキップ")
    return None, history

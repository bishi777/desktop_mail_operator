from selenium.webdriver.support.ui import WebDriverWait
import random
import time
from selenium.webdriver.common.by import By
import os
from selenium.webdriver.support.select import Select
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from widget import func
import re
from selenium.common.exceptions import TimeoutException
import sqlite3
from datetime import datetime, timedelta
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import urllib3
import threading
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import shutil
from selenium.common.exceptions import NoSuchElementException
from DrissionPage import ChromiumPage
from DrissionPage.errors import BrowserConnectError, PageDisconnectedError, ElementNotFoundError


def login(name, login_id, login_pass, page):
  page.set.cookies.clear()
  tab = page.latest_tab  # アクティブなタブを取得
  # ログインページへアクセス
  tab.get("https://pcmax.jp/pcm/file.php?f=login_form")
  wait_time = random.uniform(1.5, 3)
  time.sleep(wait_time)
  # IDとパスワードを入力
  tab.ele("#login_id").input(login_id)
  tab.ele("#login_pw").input(login_pass)
  time.sleep(wait_time)
  # ログインボタンをクリック
  send_form = tab.ele('@name=login')
  try:
    send_form.click()
    time.sleep(wait_time)
  except Exception as e:
    print(f"エラー発生: {e}")
    print("🔄 ページをリロードして再試行します...")
    tab.refresh()
    time.sleep(2)

    # 再度IDとパスワードを入力
    tab.ele("#login_id").input(login_id)
    tab.ele("#login_pw").input(login_pass)
    time.sleep(1)
    tab.ele('@name=login').click()
  # 利用制限チェック
  if tab.eles('.suspend-title'):
    print(f"{name} pcmax利用制限中です")
    return f"{name} pcmax利用制限中です"
  print("✅ ログイン成功")
  return ""

def get_header_menu(page, menu):
  links = page.ele("#header_box").eles('tag:a')
  for link in links:
    if link.text == menu:
      link.click()
      # search1
      page.ele("#search1").click()

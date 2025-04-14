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

def catch_warning_pop(name, tab):
  warning = None
  if tab.eles('.log_dialog', timeout=0.5):
    tab.ele('.log_cancel').click()
  if tab.eles('.suspend-title', timeout=0.5):
    print(f"{name} pcmax利用制限中です")
    warning = f"{name} pcmax利用制限中です"
  if tab.eles('#dialog1', timeout=0.5):
    print("dialog1")
    tab.ele('#this_month').click()
    time.sleep(1)
    if tab.eles('#close1', timeout=0.5):
      tab.ele('#close1').click()
  if tab.eles('#ng_dialog', timeout=0.5):
    check1 = tab.ele('#check1')
    if check1:
      if not check1.states.is_checked:
        check1.click()
    ng_dialog_btn = tab.eles('.ng_dialog_btn', timeout=0.5)
    if ng_dialog_btn:
      ng_dialog_btn.click()
    
  return warning

def login(name, login_id, login_pass, tab):
  # ログインページへアクセス
  tab.get("https://pcmax.jp/pcm/file.php?f=login_form", interval=5,timeout=120)
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
  warning = catch_warning_pop(name, tab)
  if warning:
    print(warning)
    print("通知メール実装してね")
  print(f"{name}✅ ログイン成功")
  return ""

def get_header_menu(page, menu):
  links = page.ele("#header_box").eles('tag:a')
  for link in links:
    if link.text == menu:
      link.click()
      # # search1
      # page.ele("#search1").click()

def profile_search(tab):
  get_header_menu(tab, "プロフ検索")
  # 地域選択
  area_id_dict = {"静岡県":27, "新潟県":13, "山梨県":17, "長野県":18, "茨城県":19, "栃木県":20, "群馬県":21, "東京都":22, "神奈川県":23, "埼玉県":24, "千葉県":25}
  tokyo_checkbox = tab.ele('#22') 
  if not tokyo_checkbox.states.is_checked:
    tokyo_checkbox.click()
  time.sleep(1)
  # 年齢
  if tab.ele('#makerItem', timeout=0.1):
    oldest_age_select_box = tab.ele('#makerItem')
  else:
    oldest_age_select_box = tab.ele('#to_age')
  oldest_age_select_box.select('31歳')  
  # ~検索から外す項目~
  # 不倫・浮気
  if tab.ele('#10120', timeout=0.1):
    checkbox = tab.ele('#10120') 
  else:
    checkbox = tab.ele('#except12') 
  if not checkbox.states.is_checked:
    checkbox.click()
  time.sleep(1)
  # アブノーマル 
  if tab.ele('#10160', timeout=0.1):
    checkbox = tab.ele('#10160')
  else:
    checkbox = tab.ele('#except16')
  if not checkbox.states.is_checked:
    checkbox.click()
  time.sleep(1)
  # 同性愛
  if tab.ele('#10190', timeout=0.1):
    checkbox = tab.ele('#10190')
  else:
    checkbox = tab.ele('#except19')
  if not checkbox.states.is_checked:
    checkbox.click()
  time.sleep(1)
  # 写真・動画撮影
  if tab.ele('#10200', timeout=0.1):
    checkbox = tab.ele('#10200')
  else:
    checkbox = tab.ele('#except20')
  if not checkbox.states.is_checked:
    checkbox.click()
  time.sleep(1)
  # 検索ボタンを押す
  if tab.ele('#image_button', timeout=0.1):
    search = tab.ele('#image_button')
  else:
    search = tab.ele('#search1')
  search.click()

def set_fst_mail(name, chromium, tab, fst_message):
  random_wait = random.uniform(2, 4)
  ng_words = ["業者", "通報",]
  profile_search(tab)
  # ユーザーリスト結果表示その１
  elements = tab.eles('.text_left') 
  if elements:
    send_cnt = 0
    for i in elements:
      children = i.children()
      # print('----------------------------------')
      for child in children:
        # print(child.tag, child.text)
        # print(child.attr('href'))
        user_tab = chromium.new_tab(child.attr('href'))
        catch_warning_pop(name, tab)
        pr_area = user_tab.ele('.pr_area')
        if not pr_area:
          print('正常に開けません スキップします')
          user_tab.close()
          continue
        # マイルチェック　side_point_pcm_data
        # miles = user_tab.eles('.side_point_pcm_data')[0].text
        # pattern = r'\d+'
        # match = re.findall(pattern, miles.replace("M", ""))
        # if int(match[0]) > 1:
        #   maji_soushin = True
        # else:
        #   maji_soushin = False      
        # メニューを取得
        content_menu = user_tab.ele('#content_menu')
        children = content_menu.children()
        for child in children:
          # print(child.tag, child.text, child.attrs.get('class', ''))
          if child.text == "お断りリストに追加":
            okotowari = child
            # 自己PRチェック
            for ng_word in ng_words:
              if ng_word in pr_area.text:
                print('自己紹介文に危険なワードが含まれていました')
                # お断りリストに追加する 
                okotowari.click()
                okotowari_add_button = user_tab.ele('#image_button2')
                okotowari_add_button.click()
                time.sleep(5)
                user_tab.close()
          if 'memo_form' in child.attrs.get('id', ''):
            memo_children = child.children()
            for memo_child in memo_children:
              if 'memo_edit' in memo_child.attrs.get('class', ''): 
                memo_edit = memo_child
              if 'memo_open' in memo_child.attrs.get('class', ''):
                memo_edit_button = memo_child
        if "もふ" in memo_edit.text:
          user_tab.close()
        # fst_message送信
        else:
          memo_edit_button.click()
          memo_text_area = user_tab.ele('#memotxt')
          memo_text_area.input("もふ")
          user_tab.ele('#memo_send').click()
          user_tab.ele('#mdc').input(fst_message)
          time.sleep(1)
          # if maji_soushin:
          #   print(user_tab.ele('#maji_btn'))
          #   user_tab.ele('#maji_btn').click()
          #   time.sleep(4.5)
          #   user_tab.ele('#dialog_ok').click()
          # else:
          user_tab.ele('#send3').click()
          send_cnt += 1
          time.sleep(7)
          user_tab.close()
          time.sleep(random_wait)
          print(f"{name} fst_message {send_cnt}件")
          if send_cnt == 2:
            return
  # ユーザーリスト結果表示その２
  else:
    elements = tab.eles('.name') 
    print(len(elements))
    print(elements[0].text)
    elements[0].click()
    # じこPRチェック
    pr_area = tab.ele('.pr_area')
    if not pr_area:
      print('正常に開けません スキップします')
      tab.back()
    for ng_word in ng_words:
      if ng_word in pr_area.text:
        print('自己紹介文に危険なワードが含まれていました')
        # お断りリストに追加する 
        okotowari = tab.ele(".btn discline")
        okotowari.click()
        okotowari_add_button = tab.ele('#image_button2')
        okotowari_add_button.click()
        time.sleep(5)
        profile_search(tab)
    # メモ確認
    memo_edit = tab.ele('.side_memo memo_edit')
    print(memo_edit.text)
    
  


       
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

# log_dialog
def catch_warning_pop(name, tab):
  warning = None
  if tab.eles('.log_dialog'):
    tab.ele('.log_cancel').click()
  if tab.eles('.suspend-title'):
    print(f"{name} pcmax利用制限中です")
    warning = f"{name} pcmax利用制限中です"
  # dialog1
  if tab.eles('#dialog1'):
    print("dialog1")
  # ng_dialog
  if tab.eles('#ng_dialog'):
    check1 = tab.ele('#check1')
    if check1:
      if not check1.states.is_checked:
        check1.click()
    ng_dialog_btn = tab.eles('.ng_dialog_btn')
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
  print("✅ ログイン成功")
  return ""

def get_header_menu(page, menu):
  links = page.ele("#header_box").eles('tag:a')
  for link in links:
    if link.text == menu:
      link.click()
      # # search1
      # page.ele("#search1").click()

def set_fst_mail(name, chromium, tab, fst_message):
  get_header_menu(tab, "プロフ検索")
  # 地域選択
  area_id_dict = {"静岡県":27, "新潟県":13, "山梨県":17, "長野県":18, "茨城県":19, "栃木県":20, "群馬県":21, "東京都":22, "神奈川県":23, "埼玉県":24, "千葉県":25}
  tokyo_checkbox = tab.ele('#22') 
  if not tokyo_checkbox.states.is_checked:
    tokyo_checkbox.click()
  time.sleep(1)
  # 年齢
  oldest_age_select_box = tab.ele('#makerItem')  # idでセレクトを取得
  oldest_age_select_box.select('31歳')  

  # ~検索から外す項目~
  # 不倫・浮気
  checkbox = tab.ele('#10120') 
  if not checkbox.states.is_checked:
    checkbox.click()
  time.sleep(1)
  # アブノーマル
  checkbox = tab.ele('#10160') 
  if not checkbox.states.is_checked:
    checkbox.click()
  time.sleep(1)
  # 同性愛
  checkbox = tab.ele('#10190') 
  if not checkbox.states.is_checked:
    checkbox.click()
  time.sleep(1)
  # 写真・動画撮影
  checkbox = tab.ele('#10200') 
  if not checkbox.states.is_checked:
    checkbox.click()
  time.sleep(1)
  search = tab.ele('#image_button')
  search.click()

  # ユーザーリスト結果表示
  elements = tab.eles('.text_left') 
  for i in elements:
    children = i.children()
    print('----------------------------------')
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
      miles = user_tab.eles('.side_point_pcm_data')[0].text
      pattern = r'\d+'
      match = re.findall(pattern, miles.replace("M", ""))
      if int(match[0]) > 1:
        maji_soushin = True
      else:
        maji_soushin = False      
      content_menu = user_tab.ele('#content_menu')
      children = content_menu.children()
      for child in children:
        print(child.tag, child.text)
        if child.text == "お断りリストに追加":
          okotowari = child
        if "200文字まで入力できます" in child.text:
          memo_ele = child
      # 自己PRチェック
      ng_words = ["業者", "通報",]
      for ng_word in ng_words:
        if ng_word in pr_area.text:
          print('自己紹介文に危険なワードが含まれていました')
          # お断りリストに追加する 
          okotowari.click()
          okotowari_add_button = user_tab.ele('#image_button2')
          okotowari_add_button.click()
          print("tabを閉じます")
          time.sleep(5)
          user_tab.close()    
      # メモを確認
      if memo_ele:
        children = memo_ele.children()
        for child in children:
          # print(child.tag, child.text, child.attrs.get('class', ''))
          if 'memo_edit' in child.attrs.get('class', ''):
            memo_edit = child
          if 'memo_open' in child.attrs.get('class', ''):
            memo_edit_button = child
        if "もふ" in memo_edit.text:
          user_tab.close()
        # fst_message送信
        else:
          print("〜〜〜〜fst_message送信〜〜〜〜")
          print(maji_soushin)
          memo_edit_button.click()
          memo_text_area = user_tab.ele('#memotxt')
          memo_text_area.input("もふ")
          user_tab.ele('#memo_send').click()
          user_tab.ele('#mdc').input(fst_message)
          if maji_soushin:
            m = user_tab.ele('#maji_btn')
            print(m)
            user_tab.ele('#maji_btn').click()
            # user_tab.ele('#dialog_ok').click()
          else:
            user_tab.ele('#send3').click()
        


          


        

      return

       
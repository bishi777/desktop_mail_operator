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
    warning = f"{name} pcmax利用制限がかかっている可能性があります"
  if tab.eles('#dialog1', timeout=0.5):
    print("dialog1")
    if len(tab.eles('#this_month')):
      tab.ele('#this_month').click()
      time.sleep(1)
    if tab.eles('#close1', timeout=0.5):
      print(77777777)
      
      ele = tab.ele('#close1').click()
      tab.run_js('arguments[0].click();', ele)
  if tab.eles('#ng_dialog', timeout=0.5):
    check1 = tab.ele('#check1')
    if check1:
      if not check1.states.is_checked:
        check1.click()
    ng_dialog_btn = tab.eles('.ng_dialog_btn', timeout=0.5)
    if ng_dialog_btn:
      ng_dialog_btn[0].click()
  
  kiyaku_btn = tab.eles('.kiyaku-btn', timeout=0.5)
  if kiyaku_btn:
    kiyaku_btn[0].click()
    tab.get("https://pcmax.jp/pcm/member.php")

  return warning

def login(name, login_id, login_pass, tab):
  # ログインページへアクセス
  tab.get("https://pcmax.jp/pcm/file.php?f=login_form", interval=5,timeout=120)
  wait_time = random.uniform(1.5, 3)
  time.sleep(wait_time)
  # login
  tab.ele("#qOTkU1").ele("tag:input").click()
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
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
  if tab.url == "https://pcmax.jp/pcm/member.php":
    print(f"{name}✅ ログイン成功")
    return True
  else:
    print(f"{name} ログイン失敗")
    return False

def get_header_menu(page, menu):
  if "メッセージ" == menu:
    links = page.ele("#header_box_under").eles('tag:a')
  else:
    links = page.ele("#header_box").eles('tag:a')
  for link in links:
    if menu in link.text:
      if "メッセージ" == menu:
        new_message_badge = link.eles(".header_pcm_badge")
        if not len(new_message_badge):
          print(f"新着メールなし")
          return False
      link.click()
      return True

def profile_search(tab):
  get_header_menu(tab, "プロフ検索")
  # 地域選択
  area_id_dict = {
    # "新潟県":13, "山梨県":17,  "長野県":18, "茨城県":19, "埼玉県":24, 
    # "東京都":22, 
    "静岡県":27, 
    "栃木県":20, 
    "群馬県":21, 
    "神奈川県":23, 
    "千葉県":25
    }
  # チェックが入っていないか確認してリセット
  area_check_elements = tab.ele(".bbs_table-radio").eles("tag:input")
  for i in area_check_elements:
    if i.states.is_checked:
      i.click()
      time.sleep(0.5)
  if not tab.ele("#22").states.is_checked:
      tab.ele("#22").click()
      time.sleep(1)
  # ランダムに2つ選ぶ
  random_areas = dict(random.sample(list(area_id_dict.items()), 2))
  for area, area_id in random_areas.items():
    if not tab.ele(f"#{area_id}").states.is_checked:
      tab.ele(f"#{area_id}").click()
    time.sleep(1)
  # 年齢
  if tab.ele('#makerItem', timeout=0.1):
    oldest_age_select_box = tab.ele('#makerItem')
  else:
    oldest_age_select_box = tab.ele('#to_age')
  oldest_age_select_box.select('40歳')  
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

def set_fst_mail(name, chromium, tab, fst_message, send_cnt):
  catch_warning_pop(name, tab)
  random_wait = random.uniform(2, 4)
  ng_words = ["業者", "通報",]
  profile_search(tab)
  user_index = 0
  sent_cnt = 0
  while sent_cnt < send_cnt:
    catch_warning_pop(name, tab)
    elements = tab.eles('.list')   
    # ユーザーリスト結果表示その１
    if elements:
      print("ユーザーリスト結果表示その１")
      list_photo = tab.eles('.list_photo')[user_index]
      # print(len(tab.eles('.list_photo')))
      user_imgs = list_photo.eles("tag:img")
      send_flug = False
      while send_flug == False:
        send_flug = True
        for i in user_imgs:
          if "https://pcmax.jp/image/icon/16pix/emoji_206.png" in i.attr('src'):
            user_index += 1
            list_photo = tab.eles('.list_photo')[user_index]
            user_imgs = list_photo.eles("tag:img")
            send_flug = False
            if user_index > len(tab.eles('.list_photo')) - 2:
              print("~~~~~~~~~ユーザーリストを全て読み込みました~~~~~~~~~~~~~")
              send_flug = False
              return
            if user_index % 15 == 0:
              tab.scroll.to_bottom()
              time.sleep(4)
      link_elements = tab.eles('.text_left') 
      print(user_index)
      link = link_elements[user_index].ele("tag:a")
      user_tab = chromium.new_tab(link.attr('href'))
      catch_warning_pop(name, tab)
      pr_area = user_tab.ele('.pr_area')
      if not pr_area:
        print('正常に開けません スキップします')
        user_index += 1
        user_tab.close()
        continue
     
      # メニューを取得
      content_menu = user_tab.ele('#content_menu')
      children = content_menu.children()
      okorowari_flug = False
      for child in children:
        # print(child.tag, child.text, child.attrs.get('class', ''))
        if child.text == "お断りリストに追加":
          okotowari = child
          # 自己PRチェック
          for ng_word in ng_words:
            if ng_word in pr_area.text:
              okorowari_flug = True
              print('自己紹介文に危険なワードが含まれていました')
              # お断りリストに追加する 
              okotowari.click()
              okotowari_add_button = user_tab.ele('#image_button2')
              okotowari_add_button.click()
              time.sleep(5)
              user_tab.close()
              user_index += 1
      if okorowari_flug:
        continue         
      user_tab.ele('#mdc').input(fst_message)
      time.sleep(1)
     
      user_tab.ele('#send3').click()
      user_index += 1
      sent_cnt += 1
      now = datetime.now().strftime('%m-%d %H:%M:%S')
      print(f"{name} fst_message {sent_cnt}件 送信 {now}")
      time.sleep(6)
      user_tab.close()
      time.sleep(random_wait)
      
    # ユーザーリスト結果表示その２(制限なし)
    else:
      print("# ユーザーリスト結果表示その２")
      elements = tab.eles('.name') 
      print(len(elements))
      print(elements[0].text)
      elements[user_index].click()
      catch_warning_pop(name, tab)
      # じこPRチェック
      pr_area = tab.ele('.pr_area')
      if not pr_area:
        print('正常に開けません スキップします')
        tab.back()
        user_index += 1
        continue
      ng_word_flug = False
      for ng_word in ng_words:
        if ng_word in pr_area.text:
          print('自己紹介文に危険なワードが含まれていました')
          # お断りリストに追加する 
          okotowari = tab.ele(".btn discline")
          okotowari.click()
          okotowari_add_button = tab.ele('#image_button2')
          okotowari_add_button.click()
          time.sleep(2)
          user_index += 1
          profile_search(tab)
          ng_word_flug = True
      if ng_word_flug:
        continue
      # メモ確認
      memo_edit = tab.ele('.side_memo memo_edit')
      if "もふ" in memo_edit.text:
        time.sleep(random_wait)
        profile_search(tab)
        user_index += 1
      # fst_message送信
      else:
        tab.ele('.side_btn memo_open').click()
        tab.ele('#memotxt').input("もふ")
        tab.ele('#memo_send').click()
        tab.ele('#mail_com').input(fst_message)
        time.sleep(1)
        tab.ele('#send3').click()
        time.sleep(1)
        sent_cnt += 1
        now = datetime.now().strftime('%m-%d %H:%M:%S')
        print(f"{name} fst_message {sent_cnt}件　送信  {now}")
        user_index += 1
        catch_warning_pop(name, tab)
        profile_search(tab)
       
def check_mail(name, tab, login_id, login_pass, gmail_address, gmail_password, fst_message, second_message, condition_message, mailserver_address, mailserver_password):
  catch_warning_pop(name, tab)
  tab.ele("#header_logo").click()
  catch_warning_pop(name, tab)
  return_list = []
  new_message_flug = get_header_menu(tab, "メッセージ")
  if new_message_flug == False:
    print(f"新着メールなし")
    return 
  tab.ele(".not_yet").ele("tag:a").click()
  user_div_list = tab.eles(".mail_area clearfix")
  # 未読一覧のurl https://pcmax.jp/mobile/mail_recive_list.php?receipt_status=0
  while len(user_div_list):
    # print(user_div_list[0].ele("tag:a"))   
    user_div_list[0].ele("tag:a").click()
    tab.ele(".btn2").click()
    sent_by_me = tab.eles(".fukidasi right right_balloon")
    # 受信メッセージにメールアドレスが含まれているか
    received_mail_elem = tab.eles(".message-body fukidasi left left_balloon")
    if len(received_mail_elem):
      received_mail = received_mail_elem[-1].text
    else:
      received_mail = ""       
    # ＠を@に変換する
    # print(received_mail)
    if "＠" in received_mail:
      received_mail = received_mail.replace("＠", "@")
    if "あっとまーく" in received_mail:
      received_mail = received_mail.replace("あっとまーく", "@")
    if "アットマーク" in received_mail:
      received_mail = received_mail.replace("アットマーク", "@")

    # メールアドレスを抽出する正規表現
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    # email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    email_list = re.findall(email_pattern, received_mail)
    user_name = tab.ele(".title").ele("tag:a").text
    if email_list:
      # print("メールアドレスが含まれています")
      # icloudの場合
      if "icloud.com" in received_mail:
        print("icloud.comが含まれています")
        icloud_text = "メール送ったんですけど、ブロックされちゃって届かないのでこちらのアドレスにお名前添えて送ってもらえますか？"
        icloud_text = icloud_text + "\n" + gmail_address
        text_area = tab.eles("#mdc")
        text_area.input(icloud_text)
        time.sleep(4)
        tab.ele("#send_n").click()
        # 連続防止で失敗
        waiting = tab.eles(".banned-word")
        if len(waiting):
          # print("<<<<<<<<<<<<<<<<<<<連続防止で失敗>>>>>>>>>>>>>>>>>>>>")
          time.sleep(6)
          tab.ele("#send_n").click()   
        # tab.ele("#back2").click()  
        catch_warning_pop(name, tab)
        tab.back()   
        tab.back()
      else: 
        for user_address in email_list:
          site = "pcmax"
          try:
            func.send_conditional(user_name, user_address, gmail_address, gmail_password, condition_message, site)
            print("アドレス内1stメールを送信しました")
          except Exception:
            print(f"{name} アドレス内1stメールの送信に失敗しました")
            print(f"user_address:{user_address}  gmail_address:{gmail_address} gmail_password:{gmail_password}")
            print(condition_message)
        tab.back() 
        time.sleep(1) 
        # 見ちゃいや登録
        tab.ele(".icon no_look").parent().click()
        tab.ele("#image_button2").click()
    # メッセージ送信一件もなし
    elif len(sent_by_me) == 0:
      if len(tab.eles(".bluebtn_no")):
        if "送信はできません" in tab.eles(".bluebtn_no").text:
          print("ユーザーが退会している可能性があります")
      text_area = tab.ele("#mdc").input(fst_message)
      tab.ele("#send_n").click()
      # 連続防止で失敗
      waiting = tab.eles(".banned-word")
      if len(waiting):
        # print("<<<<<<<<<<<<<<<<<<<連続防止で失敗>>>>>>>>>>>>>>>>>>>>")
        time.sleep(6)
        tab.ele("#send_n").click()  
      catch_warning_pop(name, tab)
    # メッセージ送信一件以上
    elif len(sent_by_me) <= 1:
      if len(tab.eles(".bluebtn_no")):
        if "送信はできません" in tab.eles(".bluebtn_no").text:
          print("ユーザーが退会している可能性があります")
      no_history_second_mail = False
      sent_by_me_list = []
      if len(sent_by_me):
        for sent_list in sent_by_me:
          sent_by_me_list.append(sent_list)
      for send_my_text in sent_by_me_list:
        # second_mailを既に送っているか
        if func.normalize_text(second_message) == func.normalize_text(send_my_text.text):
          print('やり取り中')
          user_name = tab.eles(".user_name")[0].text
          received_mail_elem = tab.eles(".left_balloon")
          received_mail = received_mail_elem[-1].text
          return_message = f"{name}pcmax,{login_id}:{login_pass}\n{user_name}「{received_mail}」"
          site = "pcmax"
          try:
            func.send_conditional(user_name, user_address, mailserver_address, mailserver_password, return_message, site)
            print("通知メールを送信しました")
          except Exception:
            print(f"{name} 通知メールの送信に失敗しました")   
          return_list.append(return_message)
          no_history_second_mail = True
          # 見ちゃいや登録
          tab.ele(".icon no_look").parent().click()
          time.sleep(1)
          tab.ele("#image_button2").click() 
      # secondメッセージを入力
      if not no_history_second_mail:
        tab.ele("#mdc").input(second_message)
        time.sleep(2)
        tab.ele("#send_n").click()
        # 連続防止で失敗
        waiting = tab.eles(".banned-word")
        if len(waiting):
          # print("<<<<<<<<<<<<<<<<<<<連続防止で失敗>>>>>>>>>>>>>>>>>>>>")
          time.sleep(6)
          tab.ele("#send_n").click()
        catch_warning_pop(name, tab)  
    
    # 未読ユーザー一覧に戻る
    tab.get("https://pcmax.jp/mobile/mail_recive_list.php?receipt_status=0")
    user_div_list = tab.eles(".mail_area clearfix")

 


    
  


       
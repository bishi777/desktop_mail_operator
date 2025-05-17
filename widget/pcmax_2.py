from selenium.webdriver.support.ui import WebDriverWait
import random
import traceback
import time
from selenium.webdriver.common.by import By
import os
from selenium.webdriver.support.select import Select
import random
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


def catch_warning_pop(name, driver):
  warning = None
  wait = WebDriverWait(driver, 10)
  try:
    if driver.find_elements(By.CLASS_NAME, 'log_dialog'): 
      driver.find_element(By.CLASS_NAME, 'log_cancel').click()
  except Exception:
    driver.refresh()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
  try:
    if driver.find_elements(By.CLASS_NAME, 'suspend-title'):
      warning = f"{name} pcmax利用制限がかかっている可能性があります"
  except Exception:
    pass
  try:
    if driver.find_elements(By.ID, 'dialog1'):      
      this_month = driver.find_elements(By.ID, 'this_month')
      if len(this_month):
        time.sleep(1)
        driver.execute_script('arguments[0].click();', this_month[0])
        driver.find_element(By.ID, 'this_month').click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)     
        try:
          # close1 = driver.find_element(By.ID, 'close1')
          # print(77777777)
          # driver.execute_script('arguments[0].click();', close1)
          # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          # time.sleep(1)
          driver.find_element(By.ID, 'send3').click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
          
        except NoSuchElementException:
          pass
  except Exception:
    pass
  try:
    if driver.find_elements(By.ID, 'ng_dialog'):
      try:
        check1 = driver.find_element(By.ID, 'check1')
        if not check1.is_selected():
            check1.click()
      except NoSuchElementException:
        pass
      ng_dialog_btns = driver.find_elements(By.CLASS_NAME, 'ng_dialog_btn')
      if ng_dialog_btns:
        ng_dialog_btns[0].click()
  except Exception:
    pass
  try:
    kiyaku_btns = driver.find_elements(By.CLASS_NAME, 'kiyaku-btn')
    if kiyaku_btns:
      print("kiyaku_btns")

      print(kiyaku_btns[0].text)
      kiyaku_btns[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
  except Exception:
    pass
  try:
    tuto_pop = driver.find_elements(By.CLASS_NAME, 'tuto_screen')
    if tuto_pop:
      time.sleep(1)
      driver.find_elements(By.CLASS_NAME, 'tuto_dialog')[0].find_elements(By.TAG_NAME, 'span')[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
  except Exception:
    pass
  return warning

def get_header_menu(driver, menu, user_agent_type):
  wait = WebDriverWait(driver, 10)
  # iPhone版
  if user_agent_type == "iPhone":
    try:
      if menu == "メッセージ":
        link = driver.find_elements(By.CLASS_NAME, "sp-fl-message")
        new_message_badge = link[0].find_elements(By.CLASS_NAME, "badge1")
        if not new_message_badge:
          print("新着メールチェック完了")
          return False
        link[0].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1) 
        return True
      elif menu == "プロフ検索": 
        link = driver.find_elements(By.CLASS_NAME, "sp-fl-prof")
        link[0].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        return True
    except NoSuchElementException:
      pass
    return False
  # PC版
  if user_agent_type == "PC": 
    try:
      if menu == "メッセージ":
        header = driver.find_element(By.ID, "header_box_under")
      else:
        header = driver.find_element(By.ID, "header_box")
      links = header.find_elements(By.TAG_NAME, "a")
      for link in links:
        if menu in link.text:
          if menu == "メッセージ":
            try:
              new_message_badge = link.find_elements(By.CLASS_NAME, "header_pcm_badge")
              if not new_message_badge:
                print("新着メールチェック完了")
                return False
            except NoSuchElementException:
              pass
          link.click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)

          return True
    except NoSuchElementException:
      pass

    return False

def profile_search(driver, user_agent_type):
  wait = WebDriverWait(driver, 10)
  oldest_age = "34"
  youngest_age = "18"
  get_header_menu(driver, "プロフ検索", user_agent_type)
  if user_agent_type == "PC":
    area_id_dict = {
      "静岡県": 27,
      "栃木県": 20,
      "群馬県": 21,
      "神奈川県": 23,
      "千葉県": 25
    }
    # チェックが入っている項目をリセット
    try:
      area_check_elements = driver.find_element(By.CLASS_NAME, "bbs_table-radio").find_elements(By.TAG_NAME, "input")
      for el in area_check_elements:
        if el.is_selected():
          el.click()
          time.sleep(0.5)
    except NoSuchElementException:
      pass
    try:
      tokyo_checkbox = driver.find_element(By.ID, "22")
      if not tokyo_checkbox.is_selected():
        tokyo_checkbox.click()
        time.sleep(1)
    except NoSuchElementException:
      pass
    random_areas = dict(random.sample(list(area_id_dict.items()), 2))
    for area, area_id in random_areas.items():
      try:
        checkbox = driver.find_element(By.ID, str(area_id))
        if not checkbox.is_selected():
          checkbox.click()
          time.sleep(1)
      except NoSuchElementException:
        pass
    # 年齢設定
    try:
      time.sleep(2)
      oldest_age_select_box = driver.find_element(By.ID, "makerItem")
    except NoSuchElementException:
      oldest_age_select_box = driver.find_element(By.ID, "to_age")
    oldest_age_select_box.send_keys("34歳")

    # 除外カテゴリのチェック（不倫・浮気、アブノーマル、同性愛、写真・動画撮影）
    exclusion_ids = [
      ("10120", "except12"),
      ("10160", "except16"),
      ("10190", "except19"),
      ("10200", "except20"),
    ]

    for primary_id, fallback_id in exclusion_ids:
      try:
        checkbox = driver.find_element(By.ID, primary_id)
      except NoSuchElementException:
        checkbox = driver.find_element(By.ID, fallback_id)
      if not checkbox.is_selected():
        checkbox.click()
      time.sleep(1)

    # 検索ボタンを押す
    try:
      search_button = driver.find_element(By.ID, "image_button")
    except NoSuchElementException:
      search_button = driver.find_element(By.ID, "search1")
    search_button.click()

  elif user_agent_type == "iPhone":
    print(" iPhone版")

    driver.find_element(By.ID, "search1").click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1.5)
    search_elem = driver.find_elements(By.ID, value="search1")
    if not len(search_elem):
      print(f" プロフィール検索に利用制限あり")
      return
    select_area = driver.find_elements(By.CLASS_NAME, value="pref-select-link")    
    reset_area = driver.find_elements(By.CLASS_NAME, value="reference_btn")

    if not len(select_area) and not len(reset_area):
        # /////////////////////////利用制限あり
        print(f"利用制限あり")
       
    else:
      # /////////////////////////利用制限なし
      # 地域選択（3つまで選択可能）
      areas = [
        "東京都",
        "千葉県",
        "埼玉県",
        "神奈川県",
        # "静岡県",
        # "新潟県",
        # "山梨県",
        # "長野県",
        # "茨城県",
        "栃木県",
        # "群馬県",
      ]
      areas.remove("東京都")
      select_areas = random.sample(areas, 2)
      select_areas.append("東京都")
      
      # 地域選択
      if len(select_area):
        select_link = select_area[0].find_elements(By.TAG_NAME, value="a")
        select_link[0].click()
      else:
        # 都道府県の変更、リセット
        
        reset_area[0].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        reset_area_orange = driver.find_elements(By.CLASS_NAME, value="btn-orange")
        reset_area_orange[0].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        ok_button = driver.find_element(By.ID, value="link_OK")
        ok_button.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        select_area = driver.find_elements(By.CLASS_NAME, value="pref-select-link")
        # たまにエラー
        select_area_cnt = 0
        while not len(select_area):
          time.sleep(1)
          # print("select_areaが取得できません")
          select_area = driver.find_elements(By.CLASS_NAME, value="pref-select-link")
          select_area_cnt += 1
          if select_area_cnt == 10:
            break

        select_link = select_area[0].find_elements(By.TAG_NAME, value="a")
        select_link[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      area_id_dict = {"静岡県":27, "新潟県":13, "山梨県":17, "長野県":18, "茨城県":19, "栃木県":20, "群馬県":21, "東京都":22, "神奈川県":23, "埼玉県":24, "千葉県":25}
      area_ids = []
      for select_area in select_areas:
        if area_id_dict.get(select_area):
          area_ids.append(area_id_dict.get(select_area))
      for area_id in area_ids:
        if 19 <= area_id <= 25:
          region = driver.find_elements(By.CLASS_NAME, value="select-details-area")[1]
        elif 13 <= area_id <= 18:
          region = driver.find_elements(By.CLASS_NAME, value="select-details-area")[2]
        elif 26 <= area_id <= 29:
          region = driver.find_elements(By.CLASS_NAME, value="select-details-area")[4]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", region)
        check = region.find_elements(By.ID, value=int(area_id))
        time.sleep(1)
        driver.execute_script("arguments[0].click();", check[0])
      save_area = driver.find_elements(By.NAME, value="change")
      time.sleep(1)
      save_area[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      # 年齢
      if youngest_age:
        if 17 < int(youngest_age) < 59:
          str_youngest_age = youngest_age + "歳"
        elif 60 <= int(youngest_age):
          str_youngest_age = "60歳以上"
        from_age = driver.find_element(By.NAME, value="from_age")
        select_from_age = Select(from_age)
        select_from_age.select_by_visible_text(str_youngest_age)
        time.sleep(1)
      else:
        youngest_age = ""
      if oldest_age:
        if 17 < int(oldest_age) < 59:
          str_oldest_age = oldest_age + "歳"
        elif 60 <= int(oldest_age):
          str_oldest_age = "60歳以上" 
        to_age = driver.find_element(By.ID, "to_age")
        select = Select(to_age)
        select.select_by_visible_text(str_oldest_age)
        time.sleep(1)
      else:
        youngest_age = ""
      # ページの高さを取得
      last_height = driver.execute_script("return document.body.scrollHeight")
      while True:
        # ページの最後までスクロール
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # ページが完全に読み込まれるまで待機
        time.sleep(2)
        # 新しい高さを取得
        new_height = driver.execute_script("return document.body.scrollHeight")
        # ページの高さが変わらなければ、すべての要素が読み込まれたことを意味する
        if new_height == last_height:
            break
        last_height = new_height
      # 履歴あり、なしの設定
      mail_history = driver.find_elements(By.CLASS_NAME, value="thumbnail-c")
      check_flag = driver.find_element(By.ID, value="opt3") 
      is_checked = check_flag.is_selected()
      while not is_checked:
          mail_history[2].click()
          time.sleep(1)
          is_checked = check_flag.is_selected()

      enter_button = driver.find_elements(By.ID, value="search1")
      enter_button[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      

def set_fst_mail(name, driver, fst_message, send_cnt, user_agent_type):
  mail_img = None
  wait = WebDriverWait(driver, 10)
  catch_warning_pop(name, driver)
  random_wait = random.uniform(3, 5)
  ng_words = ["業者", "通報"]
  profile_search(driver, user_agent_type)
  user_index = 0
  sent_cnt = 0
  sent_user_list = []
  if user_agent_type == "iPhone":
    catch_warning_pop(name, driver)
    # ユーザーを取得
    user_list = driver.find_element(By.CLASS_NAME, value="content_inner")
    users = user_list.find_elements(By.XPATH, value='./div')
    # ユーザーのhrefを取得
    user_cnt = 1
    link_list = []
    for user_cnt in range(len(users)):
      user_id = users[user_cnt].get_attribute("id")
      if user_id == "loading":
        # print('id=loading')
        while user_id != "loading":
          time.sleep(2)
          user_id = users[user_cnt].get_attribute("id")
      link = "https://pcmax.jp/mobile/profile_detail.php?user_id=" + user_id + "&search=prof&condition=648ac5f23df62&page=1&sort=&stmp_counter=13&js=1"
      random_index = random.randint(0, len(link_list))
      link_list.insert(random_index, link)

    # print(f'リンクリストの数{len(link_list)}')
    # メール送信
    sent_cnt = 0
    for idx, link_url in enumerate(link_list, 1):
      send_status = True
      driver.get(link_url)
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      catch_warning_pop(name, driver)
      # 名前を取得
      user_name = driver.find_elements(By.CLASS_NAME, value="page_title")
      if len(user_name):
        user_name = user_name[0].text
      else:
        user_name = ""
      # 年齢,活動地域を取得
      profile_data = driver.find_elements(By.CLASS_NAME, value="data")
      span_cnt = 0
      while not len(profile_data):
        time.sleep(1)
        profile_data = driver.find_elements(By.CLASS_NAME, value="data")
        span_cnt += 1
        if span_cnt == 10:
          print("年齢と活動地域の取得に失敗しました")
          break
      if not len(profile_data):
        user_age = ""
        area_of_activity = ""
      else:
        span_elem = profile_data[0].find_elements(By.TAG_NAME, value="span")
        span_elem_list = []
        for span in span_elem:
          span_elem_list.append(span)
        for i in span_elem_list:
          if i.text == "送信歴あり":
            print(f"{user_name}:送信歴ありのためスキップ")
            send_status = False
            # send_cnt += 1
            break
        user_age = span_elem[0].text
        area_of_activity = span_elem[1].text
      # 自己紹介文をチェック
      self_introduction = driver.find_elements(By.XPATH, value="/html/body/main/div[4]/div/p")
      if len(self_introduction):
        self_introduction = self_introduction[0].text.replace(" ", "").replace("\n", "")
        for ng_word in ng_words:
          if ng_word in self_introduction:
            print('自己紹介文に危険なワードが含まれていました')
            time.sleep(1)
            send_status = False
            continue
          if send_status == False:
            break
      # メッセージを送信
      if send_status:
        # メッセージをクリック
        message = driver.find_elements(By.ID, value="message1")
        if len(message):
          message[0].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(3)
        else:
          continue
        # 画像があれば送付
        if mail_img:
          picture_icon = driver.find_elements(By.CLASS_NAME, value="mail-menu-title")
          picture_icon[0].click()
          time.sleep(1)
          picture_select = driver.find_element(By.ID, "my_photo")
          select = Select(picture_select)
          select.select_by_visible_text(mail_img)
        # メッセージを入力
        text_area = driver.find_element(By.ID, value="mdc")
        script = "arguments[0].value = arguments[1];"
        driver.execute_script(script, text_area, fst_message)
        time.sleep(4)   
        send = driver.find_element(By.ID, value="send_n")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", send)
        send.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2.5)
        sent_cnt += 1
        now = datetime.now().strftime('%m-%d %H:%M:%S')
        print(f"{name} fst_message   ユーザー名:{user_name}  {sent_cnt}件送信  {now}")
        if sent_cnt >= send_cnt:
          break
        

  while sent_cnt < send_cnt:
    catch_warning_pop(name, driver)
    elements = driver.find_elements(By.CLASS_NAME, 'list')
    # ユーザーリスト結果表示その１
    if elements:
      print(f"プロフ制限あり")
      break
    # ユーザーリスト結果表示その２
    else:
      # print("# ユーザーリスト結果表示その２")
      elements = driver.find_elements(By.CLASS_NAME, 'name')
      # print(len(elements))
      # print(elements[0].text)
      sent_user = elements[0].text
      while sent_user in sent_user_list:
        # print(f"{sent_user}はすでに送信済みです")
        user_index += 1
        sent_user = elements[user_index].text
      elements[user_index].click()
      catch_warning_pop(name, driver)
      try:
        pr_area = driver.find_element(By.CLASS_NAME, 'pr_area')
      except NoSuchElementException:
        print('正常に開けません スキップします')
        driver.back()
        user_index += 1
        continue
      ng_flag = False
      for ng_word in ng_words:
        if ng_word in pr_area.text:
          print('自己紹介文に危険なワードが含まれていました')
          try:
            driver.find_element(By.CLASS_NAME, 'btn.discline').click()
            driver.find_element(By.ID, 'image_button2').click()
            time.sleep(2)
          except NoSuchElementException:
            pass
          user_index += 1
          profile_search(driver, user_agent_type)
          ng_flag = True
          break
      if ng_flag:
        continue
      try:
        memo_edit = driver.find_element(By.CLASS_NAME, 'memo_edit')
        if "もふ" in memo_edit.text:
          time.sleep(random_wait)
          profile_search(driver, user_agent_type)
          user_index += 1
          sent_user_list.append(sent_user)
          continue
      except NoSuchElementException:
        pass
      driver.find_element(By.CLASS_NAME, 'memo_open').click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      driver.find_element(By.ID, 'memotxt').send_keys("もふ")
      driver.find_element(By.ID, 'memo_send').click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      text_area = driver.find_element(By.ID, value="mail_com")
      script = "arguments[0].value = arguments[1];"
      driver.execute_script(script, text_area, fst_message)
      time.sleep(1)
      # まじ送信　
      mile_point_text = driver.find_element(By.CLASS_NAME, value="side_point_pcm_data").text
      pattern = r'\d+'
      match = re.findall(pattern, mile_point_text)
      if int(match[0]) > 20:
        maji_soushin = True
      else:
        maji_soushin = False
      time.sleep(random_wait)
      now = datetime.now().strftime('%m-%d %H:%M:%S')
      if maji_soushin:
        maji =  driver.find_element(By.ID, value="majiBtn")
        maji.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        link_OK = driver.find_element(By.ID, value="link_OK")
        link_OK.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')   
      else:
        driver.find_element(By.ID, 'send3').click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(0.7)
      if len(driver.find_elements(By.ID, value="mailform_box")):
        if "連続防止" in driver.find_elements(By.ID, value="mailform_box")[0].text:
          print("連続防止　待機中...")
          time.sleep(6)
          if maji_soushin:
            maji =  driver.find_element(By.ID, value="majiBtn")
            maji.click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(1)
            link_OK = driver.find_element(By.ID, value="link_OK")
            link_OK.click()
          else:
            driver.find_element(By.ID, 'send3').click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(1)
      sent_cnt += 1   
      print(f"{name} fst_message マジ送信{maji_soushin}  ユーザー名:{sent_user}  {sent_cnt}件送信  {now}")
      user_index += 1
      catch_warning_pop(name, driver)
      sent_user_list.append(sent_user)
      back2 = driver.find_element(By.ID, value="back2")
      driver.execute_script("arguments[0].click();", back2)
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(random_wait)
     
def check_mail(name, driver, login_id, login_pass, gmail_address, gmail_password,
               fst_message, second_message, condition_message,
               mailserver_address, mailserver_password, user_agent_type):
  catch_warning_pop(name, driver)
  wait = WebDriverWait(driver, 10)
  return_list = []
  new_message_flag = get_header_menu(driver, "メッセージ", user_agent_type)
  if not new_message_flag:
    return
  driver.find_element(By.CLASS_NAME, "not_yet").find_element(By.TAG_NAME, "a").click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  while True:
    catch_warning_pop(name, driver)
    user_div_list = driver.find_elements(By.CSS_SELECTOR, ".mail_area.clearfix")
    if not user_div_list:
      break
    user_div_list[0].find_element(By.TAG_NAME, "a").click()
    driver.find_element(By.CLASS_NAME, "btn2").click()
    sent_by_me = driver.find_elements(By.CSS_SELECTOR, ".fukidasi.right.right_balloon")
    received_elems = driver.find_elements(By.CSS_SELECTOR, ".message-body.fukidasi.left.left_balloon")
    received_mail = received_elems[-1].text if received_elems else ""
    received_mail = received_mail.replace("＠", "@").replace("あっとまーく", "@").replace("アットマーク", "@")
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    email_list = re.findall(email_pattern, received_mail)
    user_name = driver.find_element(By.CLASS_NAME, "title").find_element(By.TAG_NAME, "a").text
    if email_list:
      if "icloud.com" in received_mail:
        print("icloud.comが含まれています")
        icloud_text = "メール送ったんですけど、ブロックされちゃって届かないのでこちらのアドレスにお名前添えて送ってもらえますか？\n" + gmail_address
        try:
          text_area = driver.find_element(By.ID, value="mdc")
          script = "arguments[0].value = arguments[1];"
          driver.execute_script(script, text_area, icloud_text)
          time.sleep(4)
          driver.find_element(By.ID, "send_n").click()
          if driver.find_elements(By.CLASS_NAME, "banned-word"):
            time.sleep(6)
            driver.find_element(By.ID, "send_n").click()
        except Exception:
          pass
        catch_warning_pop(name, driver)
        driver.back()
        driver.back()
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
        driver.back()
        time.sleep(1)
        try:
          driver.find_element(By.CSS_SELECTOR, ".icon.no_look").find_element(By.XPATH, "..").click()
          driver.find_element(By.ID, "image_button2").click()
        except Exception:
          pass
    elif not sent_by_me:
      try:
        if "送信はできません" in driver.find_element(By.CLASS_NAME, "bluebtn_no").text:
          print("ユーザーが退会している可能性があります")
      except Exception:
        pass
      text_area = driver.find_element(By.ID, value="mdc")
      script = "arguments[0].value = arguments[1];"
      driver.execute_script(script, text_area, fst_message)
      driver.find_element(By.ID, "send_n").click()
      if driver.find_elements(By.CLASS_NAME, "banned-word"):
        time.sleep(6)
        driver.find_element(By.ID, "send_n").click()
      catch_warning_pop(name, driver)

    elif len(sent_by_me) <= 1:
      try:
        if "送信はできません" in driver.find_element(By.CLASS_NAME, "bluebtn_no").text:
          print("ユーザーが退会している可能性があります")
      except Exception:
        pass
      no_history_second_mail = False
      sent_texts = [s.text for s in sent_by_me]
      for send_text in sent_texts:
        if func.normalize_text(second_message) == func.normalize_text(send_text):
          print("やり取り中")
          user_name = driver.find_element(By.CLASS_NAME, "user_name").text
          received_mail = driver.find_elements(By.CLASS_NAME, "left_balloon")[-1].text
          return_message = f"{name}pcmax,{login_id}:{login_pass}\n{user_name}「{received_mail}」"
          try:
            func.send_conditional(user_name, user_address, mailserver_address, mailserver_password, return_message, "pcmax")
            print("通知メールを送信しました")
          except Exception:
            print(f"{name} 通知メールの送信に失敗しました")
          return_list.append(return_message)
          no_history_second_mail = True
          try:
            driver.find_element(By.CSS_SELECTOR, ".icon.no_look").find_element(By.XPATH, "..").click()
            time.sleep(1)
            driver.find_element(By.ID, "image_button2").click()
          except Exception:
            pass
      if not no_history_second_mail:
        text_area = driver.find_element(By.ID, value="mdc")
        script = "arguments[0].value = arguments[1];"
        driver.execute_script(script, text_area, second_message)
        time.sleep(2)
        driver.find_element(By.ID, "send_n").click()
        if driver.find_elements(By.CLASS_NAME, "banned-word"):
          time.sleep(6)
          driver.find_element(By.ID, "send_n").click()
        catch_warning_pop(name, driver)
    driver.get("https://pcmax.jp/mobile/mail_recive_list.php?receipt_status=0")
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(0.5) 
from selenium.webdriver.support.ui import WebDriverWait
import random
import traceback
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
      print("dialog1")
      if driver.find_elements(By.ID, 'this_month'):
        driver.find_element(By.ID, 'this_month').click()
        time.sleep(1)
      try:
        close1 = driver.find_element(By.ID, 'close1')
        print(77777777)
        driver.execute_script('arguments[0].click();', close1)
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
      kiyaku_btns[0].click()
      driver.get("https://pcmax.jp/pcm/member.php")
  except Exception:
    pass
  return warning

def get_header_menu(driver, menu):
  wait = WebDriverWait(driver, 10)
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
              print("新着メールなし")
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

def profile_search(driver):
  get_header_menu(driver, "プロフ検索")
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
  oldest_age_select_box.send_keys("40歳")

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

def set_fst_mail(name, driver, fst_message, send_cnt):
  wait = WebDriverWait(driver, 10)
  catch_warning_pop(name, driver)
  random_wait = random.uniform(3, 5)
  ng_words = ["業者", "通報"]
  profile_search(driver)
  user_index = 0
  sent_cnt = 0
  sent_user_list = []
  while sent_cnt < send_cnt:
    catch_warning_pop(name, driver)
    elements = driver.find_elements(By.CLASS_NAME, 'list')
    # ユーザーリスト結果表示その１
    if elements:
      print("ユーザーリスト結果表示その１")
      list_photos = driver.find_elements(By.CLASS_NAME, 'list_photo')
      if user_index >= len(list_photos):
        print("~~~~~~~~~ユーザーリストを全て読み込みました~~~~~~~~~~~~~")
        return
      list_photo = list_photos[user_index]
      user_imgs = list_photo.find_elements(By.TAG_NAME, 'img')
      send_flag = False
      while not send_flag:
        send_flag = True
        for img in user_imgs:
          if "https://pcmax.jp/image/icon/16pix/emoji_206.png" in img.get_attribute('src'):
            user_index += 1
            if user_index >= len(list_photos) - 1:
              print("~~~~~~~~~ユーザーリストを全て読み込みました~~~~~~~~~~~~~")
              return
            list_photo = list_photos[user_index]
            user_imgs = list_photo.find_elements(By.TAG_NAME, 'img')
            send_flag = False
            if user_index % 15 == 0:
              driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
              time.sleep(4)
      link_elements = driver.find_elements(By.CLASS_NAME, 'text_left')
      link = link_elements[user_index].find_element(By.TAG_NAME, 'a')
      href = link.get_attribute('href')
      # 新しいタブを開いて https://example.com に移動
      driver.execute_script(f"window.open('{href}', '_blank');")
      # タブを切り替え
      driver.switch_to.window(driver.window_handles[-1])
      time.sleep(0.5)
      catch_warning_pop(name, driver)
      try:
        pr_area = driver.find_element(By.CLASS_NAME, 'pr_area')
      except NoSuchElementException:
        print('正常に開けません スキップします')
        user_index += 1
        # いまのタブを閉じる
        driver.close()
        # 残っているウィンドウの一覧を取得して、先頭のタブに切り替える
        driver.switch_to.window(driver.window_handles[0])         
        continue
      try:
        content_menu = driver.find_element(By.ID, 'content_menu')
        children = content_menu.find_elements(By.XPATH, "./*")
        okotowari_flag = False
        for child in children:
          if child.text == "お断りリストに追加":
            for ng_word in ng_words:
              if ng_word in pr_area.text:
                okotowari_flag = True
                print('自己紹介文に危険なワードが含まれていました')
                child.click()
                driver.find_element(By.ID, 'image_button2').click()
                time.sleep(5)
                # いまのタブを閉じる
                driver.close()
                # 残っているウィンドウの一覧を取得して、先頭のタブに切り替える
                driver.switch_to.window(driver.window_handles[0])
                user_index += 1
                break
        
      except NoSuchElementException:
        pass
      if okotowari_flag:
          continue
      text_area = driver.find_element(By.ID, value="mdc")
      script = "arguments[0].value = arguments[1];"
      driver.execute_script(script, text_area, fst_message)
      time.sleep(1)
      driver.find_element(By.ID, 'send3').click()
      user_index += 1
      sent_cnt += 1
      now = datetime.now().strftime('%m-%d %H:%M:%S')
      # # まじ
      # maji =  driver.find_element(By.ID, value="maji_btn")
      # maji.click()
      # print("まじ")
      # time.sleep(1)
      # # dialog_ok
      # dialog_ok = driver.find_element(By.ID, value="dialog_ok")
      # dialog_ok.click()
      # time.sleep(100)
      print(f"{name} fst_message {sent_cnt}件 送信 {now}")
      time.sleep(1)
      # いまのタブを閉じる
      driver.close()
      # 残っているウィンドウの一覧を取得して、先頭のタブに切り替える
      driver.switch_to.window(driver.window_handles[0])
      time.sleep(4)
      time.sleep(random_wait)

    # ユーザーリスト結果表示その２
    else:
      print("# ユーザーリスト結果表示その２")
      elements = driver.find_elements(By.CLASS_NAME, 'name')
      print(len(elements))
      print(elements[0].text)
      sent_user = elements[0].text
      while sent_user in sent_user_list:
        print(f"{sent_user}はすでに送信済みです")
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
          profile_search(driver)
          ng_flag = True
          break
      if ng_flag:
        continue
      try:
        memo_edit = driver.find_element(By.CLASS_NAME, 'memo_edit')
        if "もふ" in memo_edit.text:
          time.sleep(random_wait)
          profile_search(driver)
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
      if int(match[0]) > 1:
        maji_soushin = True
      else:
        maji_soushin = False
      now = datetime.now().strftime('%m-%d %H:%M:%S')
      if maji_soushin:
        maji =  driver.find_element(By.ID, value="majiBtn")
        maji.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        link_OK = driver.find_element(By.ID, value="link_OK")
        link_OK.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
      else:
        driver.find_element(By.ID, 'send3').click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
      if len(driver.find_elements(By.ID, value="mailform_box")):
        if "連続防止" in driver.find_elements(By.ID, value="mailform_box")[0].text:
          print("連続防止")
          time.sleep(7)
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
      back2.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(random_wait)
     
def check_mail(name, driver, login_id, login_pass, gmail_address, gmail_password,
               fst_message, second_message, condition_message,
               mailserver_address, mailserver_password):
  catch_warning_pop(name, driver)
  wait = WebDriverWait(driver, 10)
  driver.find_element(By.ID, "header_logo").click()
  catch_warning_pop(name, driver)
  return_list = []
  new_message_flag = get_header_menu(driver, "メッセージ")
  if not new_message_flag:
    return
  driver.find_element(By.CLASS_NAME, "not_yet").find_element(By.TAG_NAME, "a").click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  while True:
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
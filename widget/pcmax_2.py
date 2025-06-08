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
    if driver.find_elements(By.CLASS_NAME, 'suspend-title') or driver.find_elements(By.CLASS_NAME, 'setting-title'):
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
  # mail_screen
  try:
    mail_screen = driver.find_elements(By.ID, 'mail_screen')
    if mail_screen:
      time.sleep(1)
      driver.refresh()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
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


def set_fst_mail(name, driver, fst_message, send_cnt, mail_img):
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
      print(f"プロフ制限あり")
      break
    # ユーザーリスト結果表示その２
    else:
      # print("# ユーザーリスト結果表示その２")
      elements = driver.find_elements(By.CLASS_NAME, 'name')
      cnt = 0
      while not len(elements):
        driver.refresh()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
        elements = driver.find_elements(By.CLASS_NAME, 'name')
        cnt += 1
        if cnt == 2:
          return
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
      if int(match[0]) > 20:
        maji_soushin = True
      else:
        maji_soushin = False
      time.sleep(random_wait)
      # mail_imgがあれば送付
      if mail_img:
        my_photo_element = driver.find_element(By.ID, "my_photo")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", my_photo_element)
        select = Select(my_photo_element)
        for option in select.options:
          if mail_img in option.text:
            select.select_by_visible_text(option.text)
            time.sleep(0.4)
            break
        driver.find_element(By.NAME, "preview").click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(0.3)
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
               mailserver_address, mailserver_password, receiving_address):
  catch_warning_pop(name, driver)
  wait = WebDriverWait(driver, 10)
  return_list = []
  new_message_flag = get_header_menu(driver, "メッセージ")
  if not new_message_flag:
    return
  driver.find_element(By.CLASS_NAME, "not_yet").find_element(By.TAG_NAME, "a").click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  while True:
    catch_warning_pop(name, driver)
    user_div_list = driver.find_elements(By.CSS_SELECTOR, ".mail_area.clearfix")
    print(len(user_div_list))
    if not user_div_list:
      break
    # ４分経過しているか
    arrival_date = user_div_list[-1].find_elements(By.CLASS_NAME, value="time")
    date_numbers = re.findall(r'\d+', arrival_date[0].text)
    # datetime型を作成
    current_year = datetime.now().year
    arrival_datetime = datetime(current_year, int(date_numbers[0]), int(date_numbers[1]), int(date_numbers[2]), int(date_numbers[3]),)
    now = datetime.today()
    elapsed_time = now - arrival_datetime
    print(f"メール到着からの経過時間{elapsed_time}")
    # if True:
    if elapsed_time >= timedelta(minutes=4):
      print("4分以上経過しています。")
      user_name = user_div_list[-1].find_element(By.CLASS_NAME, value="user_info").text
      user_div_list[-1].find_element(By.TAG_NAME, "a").click()
      # user_div_list[0].find_element(By.TAG_NAME, "a").click()
      # user_name = user_div_list[0].find_element(By.CLASS_NAME, value="user_info").text 
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
          # print("icloud.comが含まれています")
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
          # みちゃいや
          catch_warning_pop(name, driver)
          driver.back()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(0.5) 
          driver.back()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(0.5) 
          icon_menu = driver.find_elements(By.ID, "icon_menu")
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", icon_menu[0])
          icon_menu[0].find_elements(By.TAG_NAME, "a")[-1].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(0.5) 
          image_button2 = driver.find_elements(By.ID, "image_button2")
          if len(image_button2):
            image_button2[0].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(0.5) 
        else:
          for user_address in email_list:
            site = "pcmax"
            try:
              func.normalize_text(condition_message)
              func.send_conditional(user_name, user_address, gmail_address, gmail_password, condition_message, site)
              print("アドレス内1stメールを送信しました")
            except Exception:
              print(f"{name} アドレス内1stメールの送信に失敗しました")
              print(f"user_address:{user_address}  gmail_address:{gmail_address} gmail_password:{gmail_password}")
              print(condition_message)
          # みちゃいや
          catch_warning_pop(name, driver)
          driver.back()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(0.5) 
          icon_menu = driver.find_elements(By.ID, "icon_menu")
          print(len(icon_menu))
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", icon_menu[0])
          icon_menu[0].find_elements(By.TAG_NAME, "a")[-1].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(0.5) 
          image_button2 = driver.find_elements(By.ID, "image_button2")
          if len(image_button2):
            image_button2[0].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(0.5) 
          time.sleep(1)
          try:
            driver.find_element(By.CSS_SELECTOR, ".icon.no_look").find_element(By.XPATH, "..").click()
            driver.find_element(By.ID, "image_button2").click()
          except Exception:
            pass
      elif not len(sent_by_me):
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

      elif len(sent_by_me) >= 1:
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
            received_mail = driver.find_elements(By.CLASS_NAME, "left_balloon")[-1].text
            return_message = f"{name}pcmax,{login_id}:{login_pass}\n{user_name}「{received_mail}」"
            try:
              func.send_mail(return_message, [receiving_address, mailserver_address, mailserver_password],  "pcmax新着")
              print("通知メールを送信しました")
            except Exception as e:
              print(f"{name} 通知メールの送信に失敗しました")
              traceback.print_exc()  
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
    else:
      print("４分経過していません")
      break


  
def return_footmessage(name, driver, return_foot_message, send_limit_cnt, mail_img):
  catch_warning_pop(name, driver)
  wait = WebDriverWait(driver, 10)
  ashiato_list_link = driver.find_element(By.ID, 'mydata_pcm').find_elements(By.TAG_NAME, "a")[2]
  # print(ashiato_list_link.text)
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", ashiato_list_link)
  time.sleep(0.5)
  ashiato_list_link.click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(0.5)
  rf_cnt = 0
  user_index = 0
  while rf_cnt < send_limit_cnt:
    foot_user_list = driver.find_elements(By.CLASS_NAME, 'list_box')
    bottom_scroll_cnt = 0
    if user_index >= len(foot_user_list):
      driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      bottom_scroll_cnt += 1
      if bottom_scroll_cnt == 1:
        print(f"user_index={user_index} が foot_user_list の長さ {len(foot_user_list)} を超えています。")
        break

    like = foot_user_list[user_index].find_elements(By.CLASS_NAME, 'type1')
    if not len(like):
      user_index += 1
    else:
      like[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(0.8)
      foot_user_list = driver.find_elements(By.CLASS_NAME, 'list_box')
      foot_user_link = foot_user_list[user_index].find_element(By.CLASS_NAME, "post_content").find_elements(By.TAG_NAME, 'a')[0]
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", foot_user_link)
      time.sleep(0.5)
      foot_user_link.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(0.5)
      try:
        memo_edit = driver.find_element(By.CLASS_NAME, 'memo_edit')
        if "もふ" in memo_edit.text:
          driver.back()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
          user_index += 1
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
      driver.execute_script(script, text_area, return_foot_message)
      time.sleep(1)  
      # まじ送信　
      mile_point_text = driver.find_element(By.CLASS_NAME, value="side_point_pcm_data").text
      pattern = r'\d+'
      match = re.findall(pattern, mile_point_text)
      if int(match[0]) > 20:
        maji_soushin = True
      else:
        maji_soushin = False
      time.sleep(4)
      if mail_img:
        my_photo_element = driver.find_element(By.ID, "my_photo")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", my_photo_element)
        select = Select(my_photo_element)
        for option in select.options:
          if mail_img in option.text:
            select.select_by_visible_text(option.text)
            time.sleep(0.4)
            break
        driver.find_element(By.NAME, "preview").click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(0.3)  
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
      rf_cnt += 1   
      print(f"{name} 足跡がえし マジ送信{maji_soushin}   {rf_cnt}件送信  {now}")
      user_index += 1
      catch_warning_pop(name, driver)
      back2 = driver.find_element(By.ID, value="back2")
      driver.execute_script("arguments[0].click();", back2)
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(3)




        
        

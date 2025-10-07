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
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


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
    kiyaku_btns = driver.find_elements(By.CLASS_NAME, 'kiyaku-btn')
    if kiyaku_btns:
      print("kiyaku_btns")
      print(kiyaku_btns[0].text)
      driver.execute_script("arguments[0].click();", kiyaku_btns[0])
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      if len(driver.find_elements(By.CLASS_NAME, 'kiyaku-btn')):
        driver.find_elements(By.CLASS_NAME, 'kiyaku-btn')[0].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
      warning = f"{name} 規約に同意しました"
  except Exception:
    pass
  try:
    suspend_title = driver.find_elements(By.CLASS_NAME, 'suspend-title')
    if suspend_title:
      if "相手"in suspend_title[0].text:
        warning = None
      elif "利用"in suspend_title[0].text:
        warning = f"{name} pcmax利用制限がかかっている可能性があります"
    setting_title = driver.find_elements(By.CLASS_NAME, 'setting-title')
    if setting_title:
      if "番号"in setting_title[0].text:
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
          # driver.execute_script('arguments[0].click();', close1)
          # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          # time.sleep(1)
          driver.find_element(By.ID, 'send3').click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)        
        except NoSuchElementException:
          pass
      btn_off = driver.find_elements(By.ID, 'btn_off')
      if len(btn_off):
        btn_off[0].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)      
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
    tuto_pop = driver.find_elements(By.CLASS_NAME, 'tuto_screen')
    if tuto_pop:
      time.sleep(1)
      driver.find_elements(By.CLASS_NAME, 'tuto_dialog')[0].find_elements(By.TAG_NAME, 'span')[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
  except Exception:
    pass
  try:
    mail_screen = driver.find_elements(By.ID, 'mail_screen')
    if mail_screen:
      time.sleep(1)
      driver.refresh()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
  except Exception:
    pass
  try:
    lin_dialog = driver.find_elements(By.CLASS_NAME, 'lin_dialog')
    if lin_dialog:
      time.sleep(1)
      lin_close = driver.find_elements(By.CLASS_NAME, 'lin_close')
      if lin_close:
        lin_close[0].click()
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
        print(f"✅ {menu} メニューをクリックします")
        link.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)

        return True
  except NoSuchElementException:
    pass
  return False

def imahima_on(driver,wait):
  get_header_menu(driver, "マイメニュー")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  imahima_icon = driver.find_element(By.ID, "ted")
  if 'ted-on' in imahima_icon.get_attribute("class").split():
    print("✅ いまヒマアイコンがオンになっています")
  else:
    print("❌ いまヒマアイコンがオフになっています")
    imahima_icon.click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    print("❌ いまヒマアイコンおんにしました")
  driver.back()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

def profile_search(driver):
  get_header_menu(driver, "プロフ検索")
  area_id_dict = {
    "静岡県": 27,
    "栃木県": 20,
    "群馬県": 21,
    "神奈川県": 23,
    "千葉県": 25
  }
  # print("✅ プロフ検索メニューのURLかチェック")
  # print(driver.current_url)
  wait = WebDriverWait(driver, 10)
  # https://linkleweb.jp/mobile/profile_reference.php
  # https://pcmax.jp/mobile/profile_reference.php
  if not "/mobile/profile_reference.php" in driver.current_url:
    if "pcmax.jp/mobile/profile_rest_reference.php" in driver.current_url:
      # print(f"❌ プロフ検索制限メニューのURLです") 
      driver.get("https://pcmax.jp/pcm/index.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
      if len(name_on_pcmax):
        print(f"{name_on_pcmax[0].text} プロフ検索制限がかかっている可能性があります")
      return
    else:
      time.sleep(2)
      get_header_menu(driver, "プロフ検索")
      time.sleep(2)
      # print("✅ プロフ検索メニューのURLかチェック その２")
      # print(driver.current_url)
      if not "/mobile/profile_reference.php" in driver.current_url:
        # print("❌ プロフ検索メニューのURLではありません")
        # print(driver.current_url)
        wait = WebDriverWait(driver, 10)
        if "pcmax" in driver.current_url:
          driver.get("https://pcmax.jp/pcm/index.php")
        elif "linkleweb" in driver.current_url:
          driver.get("https://linkleweb.jp/pcm/member.php")
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        name_on_pcmax = driver.find_elements(By.CLASS_NAME, 'mydata_name')
        print(f"✅ {name_on_pcmax[0].text}プロフ検索メニューのURLかチェック")
        
        if not "pcmax.jp/mobile/profile_reference.php" in driver.current_url:
          return
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
  # random_age = f"{random.randint(29, 38)}歳"
  old_age = "60歳以上"
  oldest_age_select_box.send_keys(old_age)

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
  # 身長設定
  try:
    time.sleep(2)
    max_height_select_box = driver.find_element(By.ID, "makerItem1")
  
    max_height = f"{random.randint(170, 175)}cm"
    max_height_select_box.send_keys(max_height)
  except NoSuchElementException:
    print("身長設定できません")
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
        # driver.find_element(By.NAME, "preview").click()
        # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
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

def check_top_image(name,driver):
  wait = WebDriverWait(driver, 10)
  driver.get("https://linkleweb.jp/pcm/member.php")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  catch_warning_pop(name, driver)
  profile_photo = driver.find_elements(By.CLASS_NAME, 'profile_photo')
  if len(profile_photo):
    top_image_back_ground = profile_photo[0].value_of_css_property("background-image")
    if "no-image" in top_image_back_ground:
      return True
  return False

def check_mail(name, driver, login_id, login_pass, gmail_address, gmail_password,
               fst_message, return_foot_message, mail_img, second_message, condition_message, confirmation_mail,
               mail_info):
  mailserver_address = mail_info[1]
  mailserver_password = mail_info[2]
  receiving_address = mail_info[0]
  catch_warning_pop(name, driver)
  wait = WebDriverWait(driver, 10)
  new_message_flag = get_header_menu(driver, "メッセージ")
  if not new_message_flag:
    return
  innner1_a_tags = driver.find_elements(By.CLASS_NAME, "inner")[0].find_elements(By.TAG_NAME, "a")
  for a_tag in innner1_a_tags:
    if "未読" in a_tag.text:
      a_tag.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      break
  
  while True:
    catch_warning_pop(name, driver)
    user_div_list = driver.find_elements(By.CSS_SELECTOR, ".mail_area.clearfix")
    # print(len(user_div_list))
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
    user_name = user_div_list[-1].find_element(By.CLASS_NAME, value="user_info").text

    # print(f"メール到着からの経過時間{elapsed_time}")
    # if True:
    if elapsed_time >= timedelta(minutes=4):
      print("4分以上経過しています。")
      print(f"{user_name}さんに返信します")
      user_div_list[-1].find_element(By.TAG_NAME, "a").click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      # user_div_list[0].find_element(By.TAG_NAME, "a").click()
      # user_name = user_div_list[0].find_element(By.CLASS_NAME, value="user_info").text 
      driver.find_element(By.CLASS_NAME, "btn2").click()
      sent_by_me = driver.find_elements(By.CSS_SELECTOR, ".fukidasi.right.right_balloon")
      received_elems = driver.find_elements(By.CSS_SELECTOR, ".message-body.fukidasi.left.left_balloon")
      received_mail = received_elems[-1].text if received_elems else ""
      received_mail = received_mail.replace("＠", "@").replace("あっとまーく", "@").replace("アットマーク", "@").replace("\n", "")
      email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
      email_list = re.findall(email_pattern, received_mail)
      user_name = driver.find_element(By.CLASS_NAME, "title").find_element(By.TAG_NAME, "a").text
      # print(len(sent_by_me))
      
      # DEBUG
      # if True:
      time.sleep(1)
      catch_warning_pop(name, driver)
      if email_list:
        # print(f"メールアドレスが見つかりました: {email_list}")
        if name == "つむぎ" or "icloud.com" in received_mail:
          # print("icloud.comが含まれています")
          icloud_text = "メール送ったんですけど、ブロックされちゃって届かないのでこちらのアドレスにお名前添えて送ってもらえますか？\n" + gmail_address
          try:
            text_area = driver.find_element(By.ID, value="mdc")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
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
            user_address = func.normalize_text(user_address)
            site = "リンクル(PCMAX)"
            try:
              func.normalize_text(condition_message)
              func.send_conditional(user_name, user_address, gmail_address, gmail_password, condition_message, site)
              print("アドレス内1stメールを送信しました")
            except Exception:
              print(f"{name} アドレス内1stメールの送信に失敗しました")
              error = traceback.format_exc()
              traceback.print_exc()
              print(f"user_address:{user_address}  gmail_address:{gmail_address} gmail_password:{gmail_password}")
              print(condition_message)
              func.send_error(name, f"アドレス内1stメールの送信に失敗しました\n{user_address}\n {gmail_address}\n {gmail_password}\n\n{error}",
                                    )
          if confirmation_mail:
            try:
              text_area = driver.find_element(By.ID, value="mdc")
              driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
              script = "arguments[0].value = arguments[1];"
              driver.execute_script(script, text_area, confirmation_mail)
              t_a_v_cnt = 0
              while not text_area_value:
                t_a_v_cnt += 1
                time.sleep(2)
                text_area_value = text_area.get_attribute("value")
                if t_a_v_cnt == 5:
                  print("テキストエリアにconfirmation_mail入力できません")
                  break
              driver.find_element(By.ID, "send_n").click()
              if driver.find_elements(By.CLASS_NAME, "banned-word"):
                time.sleep(6)
                driver.find_element(By.ID, "send_n").click()
              driver.back()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(1.5) 
            except Exception:
              pass
          # みちゃいや
          catch_warning_pop(name, driver)
          driver.back()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1.5) 
          icon_menu = driver.find_elements(By.ID, "icon_menu")
          print(len(icon_menu))
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", icon_menu[0])
          icon_menu[0].find_elements(By.TAG_NAME, "a")[-1].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(0.5) 
          image_button2 = driver.find_elements(By.ID, "image_button2")
          if len(image_button2):
            image_button2[0].click()
          else:
            print("みちゃいやできません")
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
        # print("1stメールを送信します")
        # print(len(sent_by_me))
        driver.find_element(By.CLASS_NAME, 'memo_open').click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        driver.find_element(By.ID, 'memotxt').send_keys("もふ")
        time.sleep(0.5)
        driver.find_element(By.ID, 'memo_send').click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        text_area = driver.find_element(By.ID, value="mdc")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
        script = "arguments[0].value = arguments[1];"
        driver.execute_script(script, text_area, fst_message)
        time.sleep(1)
        text_area_value = text_area.get_attribute("value")
        t_a_v_cnt = 0
        while not text_area_value:
          t_a_v_cnt += 1
          time.sleep(2)
          text_area_value = text_area.get_attribute("value")
          if t_a_v_cnt == 5:
            print("テキストエリアにfst_message入力できません")
            break
        if mail_img:
          my_photo_element = driver.find_element(By.ID, "my_photo")
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", my_photo_element)
          select = Select(my_photo_element)
          for option in select.options:
            if mail_img in option.text:
              select.select_by_visible_text(option.text)
              time.sleep(0.7)
              break
          # driver.find_element(By.NAME, "preview").click()
          # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          # time.sleep(0.3)  

        driver.find_element(By.ID, "send_n").click()
        if driver.find_elements(By.CLASS_NAME, "banned-word"):
          time.sleep(6)
          driver.find_element(By.ID, "send_n").click()
        catch_warning_pop(name, driver)
      elif len(sent_by_me) == 1:
        # print(777)
        # print(sent_by_me[-1].text)
        # print(func.normalize_text(fst_message) in func.normalize_text(sent_by_me[-1].text))
        # print(func.normalize_text(return_foot_message) in func.normalize_text(sent_by_me[-1].text))

        try:
          if "送信はできません" in driver.find_element(By.CLASS_NAME, "bluebtn_no").text:
            print("ユーザーが退会している可能性があります")
        except Exception:
          pass
        if func.normalize_text(fst_message) in func.normalize_text(sent_by_me[-1].text) or func.normalize_text(return_foot_message) in func.normalize_text(sent_by_me[-1].text):
          # print("2ndメールを送信します")
          # print(len(sent_by_me))
          text_area = driver.find_element(By.ID, value="mdc")
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
          time.sleep(1)
          script = "arguments[0].value = arguments[1];"
          driver.execute_script(script, text_area, second_message)
          t_a_v_cnt = 0
          while not text_area_value:
            t_a_v_cnt += 1
            time.sleep(2)
            text_area_value = text_area.get_attribute("value")
            if t_a_v_cnt == 5:
              print("テキストエリアにfst_message入力できません")
              break          
          driver.find_element(By.ID, "send_n").click()
          if driver.find_elements(By.CLASS_NAME, "banned-word"):
            time.sleep(6)
            driver.find_element(By.ID, "send_n").click()
          catch_warning_pop(name, driver)
        else:
          # print("やり取り中")
          received_mail = driver.find_elements(By.CSS_SELECTOR, ".left_balloon")[-1].text
          return_message = f"{name}pcmax,{login_id}:{login_pass}\n{user_name}「{received_mail}」"
          try:
            func.send_mail(return_message, [receiving_address, mailserver_address, mailserver_password],  f"pcmax新着{name}")
            print("通知メールを送信しました")
          except Exception as e:
            print(f"{name} 通知メールの送信に失敗しました")
            traceback.print_exc()  
          try:
            driver.find_element(By.CSS_SELECTOR, ".icon.no_look").find_element(By.XPATH, "..").click()
            time.sleep(1)
            driver.find_element(By.ID, "image_button2").click()
          except Exception:
            pass
      elif len(sent_by_me) > 1:
        # print(456456)
        # print(func.normalize_text(sent_by_me[-1].text))
        # print(func.normalize_text(fst_message) in func.normalize_text(sent_by_me[-1].text))
        # print(func.normalize_text(fst_message))
        # print("------------------------------")
        # print(func.normalize_text(return_foot_message) in func.normalize_text(sent_by_me[-1].text))
        # print(func.normalize_text(return_foot_message))
        if func.normalize_text(fst_message) in func.normalize_text(sent_by_me[-1].text) or func.normalize_text(return_foot_message) in func.normalize_text(sent_by_me[-1].text):
          # print("2ndメールを送信します")
          # print(len(sent_by_me))
          text_area = driver.find_element(By.ID, value="mdc")
          script = "arguments[0].value = arguments[1];"
          driver.execute_script(script, text_area, second_message)
          t_a_v_cnt = 0
          while not text_area_value:
            t_a_v_cnt += 1
            time.sleep(2)
            text_area_value = text_area.get_attribute("value")
            if t_a_v_cnt == 5:
              print("テキストエリアにsecond_message入力できません")
              break        
          driver.find_element(By.ID, "send_n").click()
          if driver.find_elements(By.CLASS_NAME, "banned-word"):
            time.sleep(6)
            driver.find_element(By.ID, "send_n").click()
          catch_warning_pop(name, driver)
        else:
          # print("やり取り中")
          received_mail = driver.find_elements(By.CSS_SELECTOR, ".left_balloon")[-1].text
          return_message = f"{name}pcmax,{login_id}:{login_pass}\n{user_name}「{received_mail}」"
          try:
            func.send_mail(return_message, [receiving_address, mailserver_address, mailserver_password],  f"pcmax新着{name}")
            print("通知メールを送信しました")
          except Exception as e:
            print(f"{name} 通知メールの送信に失敗しました")
            traceback.print_exc()  
            print(mail_info)
          try:
            driver.find_element(By.CSS_SELECTOR, ".icon.no_look").find_element(By.XPATH, "..").click()
            time.sleep(1)
            driver.find_element(By.ID, "image_button2").click()
          except Exception:
            pass
      if "pcmax" in driver.current_url:
        driver.get("https://pcmax.jp/mobile/mail_recive_list.php?receipt_status=0")
      elif "linkleweb" in driver.current_url:
        driver.get("https://linkleweb.jp/mobile/mail_recive_list.php?receipt_status=0")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(0.5) 

        
      #   sent_texts = [s.text for s in sent_by_me]
      #   for send_text in sent_texts:
      #     print(777)
      #     print(func.normalize_text(send_text))
      #     if func.normalize_text(second_message) == func.normalize_text(send_text) or len(sent_by_me) > 1:
      #       print("やり取り中")
      #       received_mail = driver.find_elements(By.CLASS_NAME, "left_balloon")[-1].text
      #       return_message = f"{name}pcmax,{login_id}:{login_pass}\n{user_name}「{received_mail}」"
      #       try:
      #         func.send_mail(return_message, [receiving_address, mailserver_address, mailserver_password],  "pcmax新着")
      #         print("通知メールを送信しました")
      #       except Exception as e:
      #         print(f"{name} 通知メールの送信に失敗しました")
      #         traceback.print_exc()  
      #       return_list.append(return_message)
      #       no_history_second_mail = True
      #       try:
      #         driver.find_element(By.CSS_SELECTOR, ".icon.no_look").find_element(By.XPATH, "..").click()
      #         time.sleep(1)
      #         driver.find_element(By.ID, "image_button2").click()
      #       except Exception:
      #         pass
      #       break
      #   if not no_history_second_mail:
      #     print("2ndメールを送信します")
      #     print(len(sent_by_me))
      #     print(no_history_second_mail)
      #     text_area = driver.find_element(By.ID, value="mdc")
      #     script = "arguments[0].value = arguments[1];"
      #     driver.execute_script(script, text_area, second_message)
      #     time.sleep(2)
      #     driver.find_element(By.ID, "send_n").click()
      #     if driver.find_elements(By.CLASS_NAME, "banned-word"):
      #       time.sleep(6)
      #       driver.find_element(By.ID, "send_n").click()
      #     catch_warning_pop(name, driver)
      # driver.get("https://pcmax.jp/mobile/mail_recive_list.php?receipt_status=0")
      # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      # time.sleep(0.5) 
    else:
      print("４分経過していません")
      return user_name
      break
  if "pcmax" in driver.current_url:
    driver.get("https://pcmax.jp/pcm/index.php")
  elif "linkleweb" in driver.current_url:
    driver.get("https://linkleweb.jp/pcm/member.php")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(0.5) 
  return None

def iikamo_list_return_message(name, driver, fst_message, send_cnt, mail_img, unread_user):
  catch_warning_pop(name, driver)
  wait = WebDriverWait(driver, 10)
  iikamo_list_link = driver.find_element(By.ID, 'mydata_pcm').find_elements(By.TAG_NAME, "a")[5]
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", iikamo_list_link)
  time.sleep(0.5)
  iikamo_list_link.click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(0.5)
  list_content = driver.find_element(By.CLASS_NAME, 'list-content')
  iikamo_users = list_content.find_elements(By.CLASS_NAME, 'list_box')
  #  i = 0の要素は除外
  for i in range(1, len(iikamo_users)):
    if not iikamo_users[i].is_displayed():
      continue
    print(iikamo_users[i].text)
    iikamo_users[i].find_element(By.CLASS_NAME, 'type4').click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1.5)
    if "good_recieve_list" in driver.current_url:
      # print("いいかもリストのページにいます")
      driver.find_elements(By.CLASS_NAME, 'tab')[2].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(0.5)
      match_users = driver.find_elements(By.CLASS_NAME, 'list_box')
      if len(match_users):
        print("いいかも返しを押しました")
        match_users[0].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
      else:
        return 0
    
    try:
      memo_edit = driver.find_element(By.CLASS_NAME, 'memo_edit')
      if "もふ" in memo_edit.text:
        return 0  
    except NoSuchElementException:
      print("ユーザー個別ページにアクセスしてない可能性があります")
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
      # driver.find_element(By.NAME, "preview").click()
      # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(0.3)  
    now = datetime.now().strftime('%m-%d %H:%M:%S')
    print(f"いいかも　まじ送信{maji_soushin}  {now}")
    if maji_soushin:
      print("いいかも返しまじ送信")
      maji =  driver.find_element(By.ID, value="majiBtn")
      maji.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      link_OK = driver.find_element(By.ID, value="link_OK")
      link_OK.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')   
    else:
      print("いいかも返しメッセージ送信")
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
      
    print(f"{name} マッチングがえし マジ送信{maji_soushin}   {1}件送信  {now}")
    return 1
    
      

def return_footmessage(name, driver, return_foot_message, send_limit_cnt, mail_img, unread_user):
  wait = WebDriverWait(driver, 10)
  if "pcmax" in driver.current_url:
    driver.get("https://pcmax.jp/pcm/member.php")
  elif "linkleweb" in driver.current_url:
    driver.get("https://linkleweb.jp/pcm/member.php")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  catch_warning_pop(name, driver)
  ashiato_list_link = driver.find_element(By.ID, 'mydata_pcm').find_elements(By.TAG_NAME, "a")[2]
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", ashiato_list_link)
  time.sleep(0.5)
  ashiato_list_link.click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(0.5)
  rf_cnt = 0
  user_index = 0
  bottom_scroll_flug = True
  bottom_scroll_cnt = 0
  while rf_cnt < send_limit_cnt:
    foot_user_list = driver.find_elements(By.CLASS_NAME, 'list_box')
    if bottom_scroll_flug:
      while user_index >= len(foot_user_list):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(3)
        bottom_scroll_cnt += 1
        foot_user_list = driver.find_elements(By.CLASS_NAME, 'list_box')
        if bottom_scroll_cnt == 2:
          bottom_scroll_flug = False
          break
    if user_index >= len(foot_user_list):
      return rf_cnt
    like = foot_user_list[user_index].find_elements(By.CLASS_NAME, 'type1')
    
    if not len(like):
      like = foot_user_list[user_index].find_elements(By.CLASS_NAME, 'type4')
    if not len(like):
      user_index += 1
    # DEBUG
    # if True:
    else:
      user_name = like[0].get_attribute("data-go2")
      # user_name = "あお"
      if unread_user and user_name in unread_user:
        print(f"{user_name} は未読リストにいるのでスキップします")
        user_index += 1
        continue
      like[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(0.8)
      # print(f"タイプしました　{user_name}")
      pressed_types = driver.find_elements(By.CLASS_NAME, 'ano')
      
      if not len(pressed_types):
        # print(f"pressed_typesが取得できません {user_name}")
        driver.refresh()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
        pressed_types = driver.find_elements(By.CLASS_NAME, 'ano')
        # print("*****************************")
        # print(len(pressed_types))
        # print("*****************************")
        
      for idx in range(len(pressed_types)):
        try:
          pressed_types = driver.find_elements(By.CLASS_NAME, 'ano')  # 毎回 fresh に再取得
          if not len(pressed_types):
            print("pressed_typesがない")
            time.sleep(2)
            continue
          pressed_type = pressed_types[idx]

          try:
            user_n = (pressed_type.get_dom_attribute("data-va5")
                    or pressed_type.get_dom_attribute("data-go2"))  
            # print("---888")
            # print(user_n)
            # print("---888")
          except StaleElementReferenceException:
            print("⚠️ stale なので再取得します123123")
            time.sleep(3)
            pressed_types = driver.find_elements(By.CLASS_NAME, 'ano')
            if idx < len(pressed_types):
              # print(123)
              pressed_type = pressed_types[idx]
              user_n = (pressed_type.get_dom_attribute("data-va5")
                  or pressed_type.get_dom_attribute("data-go2"))  
              # print(user_n)
          
          user_n = (pressed_type.get_dom_attribute("data-va5")
                    or pressed_type.get_dom_attribute("data-go2"))          
          if user_n and user_name in user_n: 
            # print(555) # Noneチェックを追加
            # print(user_n)
            # print(f"idx = {idx}")
            # print("---------------")
            # print(pressed_type)
            # print("---------------")
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", pressed_type)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(1.5)
            pressed_types = driver.find_elements(By.CLASS_NAME, 'ano')  # 毎回 fresh に再取得
            try:
              pressed_type_ele = pressed_type.get_attribute("outerHTML")
              # print(pressed_type_ele)
            except StaleElementReferenceException:
              print("⚠️ stale なので再取得します")
              time.sleep(3)
              pressed_types = driver.find_elements(By.CLASS_NAME, 'ano')
              if idx < len(pressed_types):
                  print(456)
                  pressed_type = pressed_types[idx]
                  print(pressed_type.get_attribute("outerHTML"))
            
            user_link = pressed_type.find_element(By.XPATH, "following-sibling::*[1]")
            href = user_link.get_attribute("href")
            # print("ユーザー　href")
            # print(href)
            if href:
              driver.get(href)
              wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
              time.sleep(0.2)
              # print("ユーザー詳細ページに来ました")
              # print(driver.current_url)
            break
        except Exception as e:
          print(f"⚠️ 要素処理エラー: {e}")
          print(traceback.format_exc())
          break
      try:
        memo_edit = driver.find_element(By.CLASS_NAME, 'memo_edit')
        if "もふ" in memo_edit.text:
          print(f"{user_n} もふあり")
          driver.back()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
          user_index += 1
          continue
      except NoSuchElementException as e:
        img_path = f"{name}_error.png"
        print(user_name)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(traceback.format_exc())
        
        driver.save_screenshot(img_path)
        func.send_error(
            chara=name,
            error_message=f"{user_name}\n{driver.current_url}\n{str(e)}",
            attachment_paths=img_path  # 複数なら ["a.png","b.log"] のようにリストで
        )
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
        # driver.find_element(By.NAME, "preview").click()
        # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
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
      time.sleep(1.2)
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
      elif len(driver.find_elements(By.CLASS_NAME, value='comp_title')):
        # print(77777777777)
        # print(driver.find_element(By.CLASS_NAME, value='comp_title').text)
        if "送信完了" in driver.find_element(By.CLASS_NAME, value='comp_title').text:
          rf_cnt += 1   
          print(f"{name} 足跡がえし マジ送信{maji_soushin} {user_n}  {rf_cnt}件送信  {now}")
          user_index += 1
          catch_warning_pop(name, driver)
          back2 = driver.find_element(By.ID, value="back2")
          driver.execute_script("arguments[0].click();", back2)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(3)
      else:
        img_path = f"{name}_returnfoot_error.png"
        print(user_name)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(traceback.format_exc())
        
        driver.save_screenshot(img_path)
        func.send_error(
            chara=name,
            error_message=f"{user_name}\n{str(e)}",
            attachment_paths=img_path  # 複数なら ["a.png","b.log"] のようにリストで
        )
        
  return rf_cnt

def re_post(driver,wait, post_title, post_content):
  post_area_tokyo = ["千代田区",  "文京区", 
                   "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", 
                   "杉並区", "豊島区",  "荒川区", "板橋区", "練馬区",
                    "武蔵野市",  "西東京市", "三鷹市", "調布市", "小金井市", "小平市",
                    "立川市", "八王子市",  "府中市", 
                   ]
  get_header_menu(driver, "掲示板投稿")
  driver.find_element(By.CLASS_NAME, "text_right").find_elements(By.TAG_NAME, "a")[0].click()
  examination_wait = driver.find_elements(By.CLASS_NAME, "wait")
  if len(examination_wait):
    print("掲示板投稿の審査中です")
    return
  list_photo = driver.find_elements(By.CLASS_NAME, "list_photo")
  if not len(list_photo):
    print("投稿がありません。新規投稿します")
    candidate_add_post_links = driver.find_element(By.CLASS_NAME, "instructions").find_elements(By.TAG_NAME, "a")
    for candidate_add_post_link in candidate_add_post_links:
      if "掲示板でお相手を募集する" in candidate_add_post_link.text:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", candidate_add_post_link)
        time.sleep(0.5)
        candidate_add_post_link.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        break
    driver.find_element(By.ID, "2").click()
    detail_area = driver.find_element(By.ID, "citych")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", detail_area)
    time.sleep(0.5)
    select = Select(detail_area)
    select.select_by_visible_text(random.choice(post_area_tokyo))
    max_reception_count = driver.find_element(By.NAME, "max_reception_count")
    select = Select(max_reception_count)
    select.select_by_visible_text("5通")
    driver.find_element(By.ID, "bty_4").click()
    driver.find_element(By.ID, "bty_16").click()
    driver.find_element(By.ID, "bty_5").click()
    driver.find_element(By.ID, "bty_6").click()
    driver.find_element(By.ID, "bty_7").click()
    driver.find_element(By.ID, "bty_8").click()
    
    bbs_title = driver.find_element(By.NAME, "bbs_title")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", detail_area)
    time.sleep(0.5)
    script = "arguments[0].value = arguments[1];"
    driver.execute_script(script, bbs_title, post_title)
    time.sleep(0.5)
    driver.execute_script(script, driver.find_element(By.ID, "bbs_comment1"), post_content)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", driver.find_element(By.ID, "wri"))
    time.sleep(1)
    driver.find_element(By.ID, "wri").click()
    return
  elif len(list_photo) == 1:
    # 30分経過しているか
    posted_date = driver.find_elements(By.CLASS_NAME, value="font_size")
    date_numbers = re.findall(r'\d+', posted_date[0].text)
    # datetime型を作成
    current_year = datetime.now().year
    arrival_datetime = datetime(current_year, int(date_numbers[0]), int(date_numbers[1]), int(date_numbers[2]), int(date_numbers[3]),)
    now = datetime.today()
    elapsed_time = now - arrival_datetime
    print(f"前回の投稿からの経過時間{elapsed_time}")
    if elapsed_time >= timedelta(minutes=1):
      print("地域を変更して再投稿します")
      line_bottoms = driver.find_elements(By.CLASS_NAME, "line_bottom")
      for line_bottom in line_bottoms:
        if "地域を変えてコピー" in line_bottom.text:
          line_bottom.click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          detail_area = driver.find_element(By.ID, "citych")
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", detail_area)
          time.sleep(1)
          select = Select(detail_area)
          select.select_by_visible_text(random.choice(post_area_tokyo))
          max_reception_count = driver.find_element(By.NAME, "max_reception_count")
          select = Select(max_reception_count)
          select.select_by_visible_text("5通")
          time.sleep(1)
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", driver.find_element(By.ID, "wri"))
          time.sleep(10)
          driver.find_element(By.ID, "wri").click()
          break
    else:
      print("30分経過していません")
      return

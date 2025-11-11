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
import re


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
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)      
      except NoSuchElementException:
        pass
      ng_dialog_btns = driver.find_elements(By.CLASS_NAME, 'ng_dialog_btn')
      if ng_dialog_btns:
        ng_dialog_btns[0].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)      
  except Exception:
    pass
  
  try:
    tuto_pop = driver.find_elements(By.CLASS_NAME, 'tuto_screen')
    if tuto_pop:
      time.sleep(1)
      driver.find_elements(By.CLASS_NAME, 'tuto_dialog')[0].find_elements(By.TAG_NAME, 'span')[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(2)
  except Exception:
    pass
  try:
    mail_screen = driver.find_elements(By.ID, 'mail_screen')
    if mail_screen:
      time.sleep(1)
      driver.refresh()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(2)
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
        time.sleep(2)
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
              # print("新着メールチェック完了")
              return False
          except NoSuchElementException:
            pass
        # print(f"✅ {menu} メニューをクリックします")
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
  if "pcmax" in driver.current_url:
    imahima_icon = driver.find_element(By.ID, "ted")
    if 'ted-on' in imahima_icon.get_attribute("class").split():
      print("✅ いまヒマアイコンがオンになっています")
    else:
      print("❌ いまヒマアイコンがオフになっています")
      imahima_icon.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(2)
      print("❌ いまヒマアイコンおんにしました")
  elif "linkleweb" in driver.current_url:
    imahima_icon = driver.find_element(By.ID, "my_today_free")
    if 'free_off' in imahima_icon.get_attribute("style"):
      print("❌ いまヒマアイコンがオフになっています")
      imahima_icon.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(2)
      print("❌ いまヒマアイコンおんにしました")
  driver.back()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

def profile_search(driver, search_edit):
  get_header_menu(driver, "プロフ検索")
  area_id_dict = {
    "静岡県": 27,
    "栃木県": 20,
    "群馬県": 21,
    "神奈川県": 23,
    "千葉県": 25,
    "埼玉県": 24,
  }
  wait = WebDriverWait(driver, 10)
  if not "/mobile/profile_reference.php" in driver.current_url:
    if "/mobile/profile_rest_reference.php" in driver.current_url:
      print(f"❌ プロフ検索制限メニューのURLです") 
      return False
    else:
      time.sleep(2)
      get_header_menu(driver, "プロフ検索")
      time.sleep(2)
      if not "/mobile/profile_reference.php" in driver.current_url:
        print("❌ プロフ検索メニューのURLではありません")
        print(driver.current_url)
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
  r = random.randint(0, 99)
  # 地域設定（ランダムで１つ選択）
  if search_edit["area_flug"] == 1:
    if r < 50:
      area, area_id = random.choice(list(area_id_dict.items()))
      try:
        checkbox = driver.find_element(By.ID, str(area_id))
        if not checkbox.is_selected():
            checkbox.click()
            time.sleep(1)
      except NoSuchElementException:
        pass
  # 地域設定（ランダムで２つ選択）
  if search_edit["area_flug"] == 2:
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
  youngest_age_select_box = driver.find_element(By.NAME, "from_age")
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", youngest_age_select_box)
  old_value = random.choice(search_edit["o_age"])
  old_age = f"{old_value}歳"
  young_value = random.choice(search_edit["y_age"])
  young_age = f"{young_value}歳"
  # print(f"{young_age} 〜 {old_age} で検索します")
  youngest_age_select_box.send_keys(young_age)
  time.sleep(0.5)
  oldest_age_select_box.send_keys(old_age)
  time.sleep(0.5)
  # 検索対象
  # チェックが入っている項目をリセット
  try:
    check_elements = driver.find_elements(By.CLASS_NAME, "bbs_table_td-in2")[2].find_elements(By.TAG_NAME, "input")
    for el in check_elements:
      if el.is_selected():
        el.click()
        time.sleep(0.5)
  except NoSuchElementException:
    pass
  labels = driver.find_elements(By.CLASS_NAME, "bbs_table_td-in2")[2].find_elements(By.TAG_NAME, "label")
  for label in labels:
    if label.text.replace(" ", "") in search_edit["search_target"]:
      checkbox = label.find_element(By.TAG_NAME, "input")
      if not checkbox.is_selected():
        checkbox.click()
      time.sleep(0.5)
  # 検索する項目
  # try:
  #   purpose_id13 = driver.find_element(By.ID, "purpose_id13")
  # except NoSuchElementException:
  #   print("セックスフレンドのチェックボックスが見つかりません")
  # if purpose_id13.is_selected():
  #   purpose_id13.click()
  # time.sleep(0.5)

  # 検索から外す項目
  exclusion_ids = [
    ("10120", "except12"),
    ("", "except14"),
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
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", max_height_select_box)
    value = random.choice(search_edit["m_height"])
    if value == 180:
      max_height = "180cm以上"
    else:
      max_height = f"{value}cm"
    max_height_select_box.send_keys(max_height)
  except NoSuchElementException:
    print("身長設定できません")
  time.sleep(0.5)
  # 体型
  body_type_labels = driver.find_elements(By.CLASS_NAME, "bbs_table_td-in2")[6].find_elements(By.TAG_NAME, "label")
  for label in body_type_labels:
    if label.text.replace(" ", "") in search_edit["search_body_type"]:
      checkbox = label.find_element(By.TAG_NAME, "input")
      if not checkbox.is_selected():
        checkbox.click()
      time.sleep(0.5)
  # 年収
  annual_income_select_box = driver.find_element(By.ID, "sa1")
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", annual_income_select_box)
  value = random.choice(search_edit["annual_income"])
  annual_income_select_box.send_keys(value)
  time.sleep(0.5)
  # 検索ボタンを押す
  try:
    search_button = driver.find_element(By.ID, "image_button")
  except NoSuchElementException:
    search_button = driver.find_element(By.ID, "search1")
  search_button.click()
  return True
def set_fst_mail(name, driver, fst_message, send_cnt, mail_img, iikamo_cnt, two_messages_flug, mail_info):
  wait = WebDriverWait(driver, 10)
  catch_warning_pop(name, driver)
  random_wait = random.uniform(3, 5)
  ng_words = ["業者", "通報"]
  search_edit = {
    "y_age": [18],
    "o_age": [28,29,30],
    "m_height": [165,170,175],
    "area_flug": 1,
    "search_target": ["プロフィール写真あり", "送信歴無し"],
    "exclude_words": ["セックスフレンド", "不倫・浮気", "エロトーク・TELH", "SMパートナー", "写真・動画撮影", "同性愛", "アブノーマル"],
    "search_body_type": [ "スリム", "やや細め", "普通", "ふくよか", "太め" ],
    "annual_income":["200万円未満", "200万円以上〜400万円未満", ]
  }
  if not profile_search(driver, search_edit):
    return 0
  sent_cnt = 0
  iikamo_cnted = 0
  user_row_cnt = 0
  no_pr_area_cnt = 0
  # two_message_users = ["もんちー", "あつき"]
  two_message_users = []
  fm_user_list_scroll_cnt = 0
  try:
    while (sent_cnt < send_cnt) or (iikamo_cnted < iikamo_cnt):
      catch_warning_pop(name, driver)
      elements = driver.find_elements(By.CLASS_NAME, 'list')
      # ユーザーリスト結果表示その１
      if elements:
        print(f"プロフ制限あり")
        break
      # ユーザーリスト結果表示その２
      else:
        # print("# ユーザーリスト結果表示その２")
        elements = driver.find_elements(By.CLASS_NAME, 'profile_card')
        # user_name = driver.find_elements(By.CLASS_NAME, 'name')
        reload_cnt = 0
        while not len(elements):
          driver.refresh()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(3)
          elements = driver.find_elements(By.CLASS_NAME, 'name')
          reload_cnt += 1
          if reload_cnt == 2:
            return sent_cnt
        # https://pcmax.jp/mobile/profile_list.php?condition=690345149ea3c
        user_profile_list_url = driver.current_url
        while user_row_cnt >= len(elements):
          print("下までスクロールする")
          print(user_row_cnt)
          print(len(elements))
          driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(3)
          elements = driver.find_elements(By.CLASS_NAME, 'name')
          fm_user_list_scroll_cnt += 1
          if fm_user_list_scroll_cnt > 3:
            return sent_cnt
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", elements[user_row_cnt])
        exchange = elements[user_row_cnt].find_elements(By.CLASS_NAME, value="exchange")
        user_name_ele = elements[user_row_cnt].find_elements(By.CLASS_NAME, value="name")
        if len(user_name_ele):
          user_name = user_name_ele[0].text
        else:
          user_name = None
        while len(exchange):
          # print(f"やり取り有り　{user_name}")
          user_row_cnt += 1 
          if user_row_cnt >= len(elements):
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
            elements = driver.find_elements(By.CLASS_NAME, 'profile_card')
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", elements[user_row_cnt])
          exchange = elements[user_row_cnt].find_elements(By.CLASS_NAME, value="exchange")    
          user_name_ele = elements[user_row_cnt].find_elements(By.CLASS_NAME, value="name")
          if len(user_name_ele):
            user_name = user_name_ele[0].text
          else:
            user_name = None
        if "linkleweb" in driver.current_url:
          user_info = elements[user_row_cnt].find_elements(By.CLASS_NAME, value="user_info")[0].text
        elif "pcmax" in driver.current_url:
          user_info = user_name
        user_area = elements[user_row_cnt].find_elements(By.CLASS_NAME, value="conf")[0].text.replace("登録地域", "")
        elements[user_row_cnt].find_element(By.CLASS_NAME, value="profile_link_btn").click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        catch_warning_pop(name, driver)
        # print(f"~~~~~ユーザー名:{user_info}  確認中...~~~~~~")
        if user_name is None:
          print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>ユーザー名取得できずスキップします<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
          func.send_mail(f"{name} ユーザー名取得できずスキップします")
          return sent_cnt
        try:
          pr_area = driver.find_element(By.CLASS_NAME, 'pr_area')
        except NoSuchElementException:
          print('正常に開けません スキップします')
          print(driver.current_url)
          print(f"user_row_cnt {user_row_cnt}  len(elements) {len(elements)}")
          driver.back()
          user_row_cnt += 1
          no_pr_area_cnt += 1
          if no_pr_area_cnt > 4:
            break
          continue
        ng_flag = False
        for ng_word in ng_words:
          if ng_word in pr_area.text:
            print(f'{user_name} 自己紹介文にNGワードが含まれていました')
            try:
              driver.find_element(By.CLASS_NAME, 'btn.discline').click()
              driver.find_element(By.ID, 'image_button2').click()
              time.sleep(2)
            except NoSuchElementException:
              pass
            user_row_cnt += 1
            profile_search(driver, search_edit)
            ng_flag = True
            break
        if ng_flag:
          continue
        time.sleep(1)
        if not (sent_cnt < send_cnt):
          # type1 いいかも
          # type4 いいかもありがとう
          # type5 いいかもありがとう済み
          arleady_iikamo = driver.find_elements(By.CLASS_NAME, 'type5')
          iikamo = driver.find_elements(By.CLASS_NAME, 'type1')
          iikamo_arigatou = driver.find_elements(By.CLASS_NAME, 'type4')
          iikamo_text = ""
          if len(arleady_iikamo):
            iikamo_text = f"いいかも済み"
            # print(f"いいかも済み  ユーザー名:{user_info} {user_area} ")
            user_row_cnt += 1
            driver.back()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(0.7)
            continue
          elif len(iikamo):
            iikamo[0].click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(0.7)
            iikamo_cnted += 1
            user_row_cnt += 1
            iikamo_text = f"いいかも"
            # print(f"いいかも  ユーザー名:{user_info} {user_area} {iikamo_cnted}件  ")
          elif len(iikamo_arigatou):
            iikamo_arigatou[0].click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(0.7)
            iikamo_cnted += 1
            user_row_cnt += 1
            iikamo_text = f"いいかもありがとう"
            # print(f"いいかもありがとう  ユーザー名:{user_info} {user_area} {iikamo_cnted}件  ")
          driver.back()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
          driver.back()
        else:  
          try:
            memo_edit = driver.find_element(By.CLASS_NAME, 'memo_edit')
            if "もふ" in memo_edit.text:
              time.sleep(random_wait)
              profile_search(driver, search_edit)

              user_row_cnt += 1
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
          prof_ditail_user_name = driver.find_element(By.CLASS_NAME, value="li_content")
          if user_name not in prof_ditail_user_name.text:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>ユーザー名不一致のためスキップします<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            print(f"期待:{user_name}  取得:{prof_ditail_user_name.text}")
            func.send_mail(f"{name} ユーザー名不一致のためスキップします\n期待:{user_name}\n取得:{prof_ditail_user_name.text}")
            driver.back()
            user_row_cnt += 1
            continue
          text_area = driver.find_element(By.ID, value="mail_com")
          script = "arguments[0].value = arguments[1];"
          driver.execute_script(script, text_area, fst_message.format(name=user_name))
          time.sleep(1)
          # まじ送信　
          mile_point_text = driver.find_elements(By.CLASS_NAME, value="side_point_pcm_data")
          if len(mile_point_text):
            pattern = r'\d+'
            match = re.findall(pattern, mile_point_text[0].text)
            if int(match[0]) > 20:
              maji_soushin = True
            else:
              maji_soushin = False
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
          now = datetime.now().strftime('%H:%M:%S')
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
          catch_warning_pop(name, driver)
          if two_messages_flug:
            two_message_users.append(user_name)
          back2 = driver.find_element(By.ID, value="back2")
          driver.execute_script("arguments[0].click();", back2)
          sent_cnt += 1
          print(f"マジ送信{maji_soushin} {iikamo_text} ユーザー名:{user_info} {user_area} {sent_cnt}件送信  {now}")
          user_row_cnt += 1  
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(random_wait)
        driver.get(user_profile_list_url)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
    if two_messages_flug:
      header = driver.find_element(By.ID, "header_box_under")
      links = header.find_elements(By.TAG_NAME, "a")
      for link in links:
        if "メッセージ" in link.text:
          link.click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
          break
      inner = driver.find_elements(By.CLASS_NAME, "inner")
      a_btns = inner[0].find_elements(By.TAG_NAME, "a")
      for a_btn in a_btns:
        if "送信" in a_btn.text:
          a_btn.click() 
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
          break
      for two_message_user in two_message_users:
        mail_details = driver.find_elements(By.CLASS_NAME, "mail_area")
        for mail_detail in mail_details:
          user_info = mail_detail.find_element(By.CLASS_NAME, "user_info")
          # print(f"~~~~~two_message_user:{two_message_user}~~~~~~")
          # print(f"user_info.text:{user_info.text}~~~~~~")
          # print(two_message_user in user_info.text)
          if two_message_user in user_info.text:
            # driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", user_info)
            mail_detail.find_element(By.TAG_NAME, "a").click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(1)
            # print(f"two_message_user 1stメールを送信します")
            # print(f"~~~~~ユーザー名:{two_message_user}  確認中...~~~~~~")
            # print(fst_message.format(name=two_message_user))
            user_name = two_message_user
            if user_name is None:
              print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<ユーザーネームが取得できていません {user_name}>>>>>>>>>>>>>>>>>>>>>>>")
              func.send_error(name, f"ユーザーネームが取得できていません {user_name}\n",                            )
              return user_name, check_first, check_second, check_more, gmail_condition, check_date
            if "name" in fst_message.format(name=user_name):
              print(f"ユーザー名が正しく反映されていません\n{user_name}\{fst_message.format(name=user_name)}")
              func.send_error(name, f"ユーザー名が正しく反映されていません\n{user_name}\{fst_message.format(name=user_name)}")          
              return user_name, check_first, check_second, check_more, gmail_condition, check_date
            text_area = driver.find_element(By.ID, value="mdc")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
            script = "arguments[0].value = arguments[1];"
            driver.execute_script(script, text_area, fst_message.format(name=user_name))
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
            driver.find_element(By.ID, "send_n").click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(1)
            mailform_box = driver.find_elements(By.ID, value="mailform_box")
            if len(mailform_box):
              if "連続防止" in mailform_box[0].text:
                print("連続防止　待機中...")
                time.sleep(7)
                text_area = driver.find_element(By.ID, value="mdc")
                driver.execute_script(script, text_area, fst_message.format(name=user_name))
                time.sleep(1)
                if mail_img:
                  my_photo_element = driver.find_element(By.ID, "my_photo")
                  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", my_photo_element)
                  select = Select(my_photo_element)
                  for option in select.options:
                    if mail_img in option.text:
                      select.select_by_visible_text(option.text)
                      time.sleep(0.7)
                      break
                driver.find_element(By.ID, "send_n").click()
                time.sleep(1)
            if driver.find_elements(By.CLASS_NAME, "banned-word"):
              time.sleep(6)
              driver.find_element(By.ID, "send_n").click()
            print(f"{user_name}にtwo_m用の1stメールを送信しました")
            catch_warning_pop(name, driver)
            if "pcmax" in driver.current_url: 
              driver.get("https://pcmax.jp/mobile/mail_recive_send_list.php")
            elif "linkleweb" in driver.current_url:
              driver.get("https://linkleweb.jp/mobile/mail_recive_send_list.php")
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(1)
            mail_details = driver.find_elements(By.CLASS_NAME, "mail_area")  
            break       
  except: 
    print("fst送信のエラー")
    traceback.print_exc()
  finally:
    return sent_cnt
  
def check_top_image(name,driver):
  wait = WebDriverWait(driver, 10)
  if "pcmax" in driver.current_url:
    driver.get("https://pcmax.jp/pcm/member.php")
  elif "linkleweb" in driver.current_url:
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
  check_date = None
  catch_warning_pop(name, driver)
  wait = WebDriverWait(driver, 10)
  new_message_flag = get_header_menu(driver, "メッセージ")
  if not new_message_flag:
    # header_box_under = driver.find_element(By.ID, "header_box_under")
    # header_box_under.find_element(By.TAG_NAME, "a").click()
    # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    return [],0,0,0,0, None
  check_first = 0
  check_second = 0
  check_more = 0
  gmail_condition = 0
  user_name = None
  innner1_a_tags = driver.find_elements(By.CLASS_NAME, "inner")[0].find_elements(By.TAG_NAME, "a")
  if "linkleweb" in driver.current_url:
    for a_tag in innner1_a_tags:
      if "未読" in a_tag.text:
        # print("✅ 未読リストをクリックしますlinkleweb")
        a_tag.click()
        break
  elif "pcmax" in driver.current_url:
    # print("✅ 未読リストをクリックしますpcmax")
    not_yet = driver.find_element(By.CLASS_NAME, "not_yet").find_element(By.TAG_NAME, "a")
    not_yet.click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
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
    check_date = arrival_datetime
    now = datetime.today()
    elapsed_time = now - arrival_datetime
    user_name = user_div_list[-1].find_element(By.CLASS_NAME, value="user_info").text

    print(f"メール到着からの経過時間{elapsed_time}")
    # if True:
    if elapsed_time >= timedelta(minutes=4):
      print("4分以上経過しています。")
      print(f"{user_name}さんに返信します")
      user_div_list[-1].find_element(By.TAG_NAME, "a").click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      if "/mobile/mail_recive_list.php" in driver.current_url:
        print("受信箱URLです")
        user_div_list = driver.find_elements(By.CSS_SELECTOR, ".mail_area.clearfix")
        print(len(user_div_list))
        user_div_list[-1].find_element(By.TAG_NAME, "a").click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
      if "pcmax" in driver.current_url:
        try:
          # やり取りを全てみるボタンをクリック
          btn2 = driver.find_element(By.CLASS_NAME, "btn2")
          btn2.click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(0.5)
        except NoSuchElementException:
          img_path = None
          img_path = f"{name}_btn2_none.png"
          driver.save_screenshot(img_path)
          title = "btn2が見つかりません"
          text = f"{driver.current_url}"   
          # メール送信
          if mail_info:
            func.send_mail(text, mail_info, title, img_path)
          print("btn2が見つかりません")
          return [user_name], check_first, check_second, check_more, gmail_condition, check_date
      try:
        # user_name = driver.find_element(By.CLASS_NAME, "user_name").text
        user_name = driver.find_element(By.CLASS_NAME, "title").find_element(By.TAG_NAME, "a").text
      except Exception as e:
        print(f"{name}: 新着チェック　　ユーザー名取得できません\n {e}")
        func.send_error(f"{name} ユーザー名取得できません\n{traceback.format_exc()}")
        return [user_name], check_first, check_second, check_more, gmail_condition, check_date
      sent_by_me = driver.find_elements(By.CSS_SELECTOR, ".fukidasi.right.right_balloon")
      received_elems = driver.find_elements(By.CSS_SELECTOR, ".message-body.fukidasi.left.left_balloon")
      received_mail = received_elems[-1].text if received_elems else ""
      received_mail = received_mail.replace("＠", "@").replace("あっとまーく", "@").replace("アットマーク", "@").replace("\n", "")
      email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
      email_list = re.findall(email_pattern, received_mail)
      # print(f"~sent_by_me~ {len(sent_by_me)}")
      # DEBUG
      # if True:
      time.sleep(1)
      catch_warning_pop(name, driver)
      if email_list:
        # 見ちゃいや
        if "linkleweb" in driver.current_url:
          add_btns = driver.find_elements(By.CLASS_NAME, "add_btn")
          for add_btn in add_btns:
            if "見ちゃいや" in add_btn.text:
              add_btn.click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(1)
              image_button2 = driver.find_elements(By.ID, "image_button2")
              if len(image_button2):
                image_button2[0].click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(1)
              driver.back()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(1)
              driver.back()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(1)
              break
        # print(f"メールアドレスが見つかりました: {email_list}")
        if "icloud" in received_mail:
          # print("icloudが含まれています")
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
            check_more += 1
            print(f"{user_name}にicloud.com返信メールを送信しました")
          except Exception:
            pass
        else:
          for user_address in email_list:
            user_address = func.normalize_text(user_address)
            site = "リンクル"
            try:
              send_text =condition_message.format(name=user_name)
              func.send_conditional(user_name, user_address, gmail_address, gmail_password, send_text, site)
              print(f"{user_name}にアドレス内1stメールを送信しました")
              gmail_condition += 1
            except Exception:
              print(f"{name} アドレス内1stメールの送信に失敗しました")
              error = traceback.format_exc()
              traceback.print_exc()
              print(f"user_address:{user_address}  gmail_address:{gmail_address} gmail_password:{gmail_password}")
              print(condition_message.format(name=user_name))
              func.send_error(name, f"アドレス内1stメールの送信に失敗しました\n{user_address}\n {gmail_address}\n {gmail_password}\n\n{error}",
                                    )
          if confirmation_mail:
            try:
              text_area = driver.find_element(By.ID, value="mdc")
              driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
              script = "arguments[0].value = arguments[1];"
              driver.execute_script(script, text_area, confirmation_mail)
              text_area_value = text_area.get_attribute("value")
              t_a_v_cnt = 0
              # print(text_area_value)
              while not text_area_value:
                t_a_v_cnt += 1
                time.sleep(2)
                text_area_value = text_area.get_attribute("value")
                if t_a_v_cnt == 5:
                  print("テキストエリアにconfirmation_mail入力できません")
                  break
              time.sleep(3)
              driver.find_element(By.ID, "send_n").click()
              time.sleep(7)
              if driver.find_elements(By.CLASS_NAME, "banned-word"):
                time.sleep(6)
                driver.find_element(By.ID, "send_n").click()
              driver.back()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(1.5) 
            except Exception:
              pass
          catch_warning_pop(name, driver)
          # みちゃいや
          if "pcmax" in driver.current_url:
            driver.back()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(0.5) 
            icon_menu = driver.find_elements(By.ID, "icon_menu")
            if not len(icon_menu):
              print("icon_menuが見つかりません")
              screenshot_path = f"{name}_icon_menu_none.png"
              driver.save_screenshot(screenshot_path)
              title = "icon_menuが見つかりません"
              text = f"{driver.current_url}"   
              # メール送信  
              if mail_info:
                func.send_mail(text, mail_info, title, screenshot_path)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", icon_menu[0])
            icon_menu[0].find_elements(By.TAG_NAME, "a")[-1].click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(0.5) 
            image_button2 = driver.find_elements(By.ID, "image_button2")
            if len(image_button2):
              image_button2[0].click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(0.5) 
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(1.5) 
            catch_warning_pop(name, driver)
            
      elif not len(sent_by_me):
        try:
          if "送信はできません" in driver.find_element(By.CLASS_NAME, "bluebtn_no").text:
            print("ユーザーが退会している可能性があります")
        except Exception:
          pass
        # print('1stメールをユーザー名:{user_name}に送信します')
        # print(fst_message.format(name=user_name))
        if user_name is None:
          print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<ユーザーネームが取得できていません {user_name}>>>>>>>>>>>>>>>>>>>>>>>")
          func.send_error(name, f"ユーザーネームが取得できていません {user_name}\n",                            )
          return [user_name], check_first, check_second, check_more, gmail_condition, check_date
        if "name" in fst_message.format(name=user_name):
          print(f"ユーザー名が正しく反映されていません\n{user_name}\{fst_message.format(name=user_name)}")
          func.send_error(name, f"ユーザー名が正しく反映されていません\n{user_name}\{fst_message.format(name=user_name)}")          
          return [user_name], check_first, check_second, check_more, gmail_condition, check_date
        
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
        
        driver.execute_script(script, text_area, fst_message.format(name=user_name))
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
        driver.find_element(By.ID, "send_n").click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        mailform_box = driver.find_elements(By.ID, value="mailform_box")
        if len(mailform_box):
          if "連続防止" in mailform_box[0].text:
            print("連続防止　待機中...")
            time.sleep(7)
            text_area = driver.find_element(By.ID, value="mdc")
            driver.execute_script(script, text_area, fst_message.format(name=user_name))
            time.sleep(1)
            if mail_img:
              my_photo_element = driver.find_element(By.ID, "my_photo")
              driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", my_photo_element)
              select = Select(my_photo_element)
              for option in select.options:
                if mail_img in option.text:
                  select.select_by_visible_text(option.text)
                  time.sleep(0.7)
                  break
            driver.find_element(By.ID, "send_n").click()
            time.sleep(1)
        if driver.find_elements(By.CLASS_NAME, "banned-word"):
          time.sleep(6)
          driver.find_element(By.ID, "send_n").click()
        check_first += 1
        print(f"{user_name}に1stメールを送信しました")
        catch_warning_pop(name, driver)
      elif len(sent_by_me) == 1:
        try:
          if "送信はできません" in driver.find_element(By.CLASS_NAME, "bluebtn_no").text:
            print("ユーザーが退会している可能性があります")
        except Exception:
          pass
        # print("~~~~~~~~~受信メールを送信チェック中~~~~~~~~~")
        # print(func.normalize_text(sent_by_me[-1].text))
        # print(func.normalize_text(fst_message.format(name=user_name)) in func.normalize_text(sent_by_me[-1].text))
        if "いいかも！ありがとう" in func.normalize_text(sent_by_me[-1].text):
          send_message = fst_message.format(name=user_name)
        elif func.normalize_text(fst_message.format(name=user_name)) in func.normalize_text(sent_by_me[-1].text) or func.normalize_text(return_foot_message.format(name=user_name)) in func.normalize_text(sent_by_me[-1].text):
          send_message = second_message
          text_area = driver.find_element(By.ID, value="mdc")
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
          time.sleep(1)
          script = "arguments[0].value = arguments[1];"
          driver.execute_script(script, text_area, send_message)
          t_a_v_cnt = 0
          text_area_value = text_area.get_attribute("value")
          while not text_area_value:
            t_a_v_cnt += 1
            time.sleep(2)
            text_area_value = text_area.get_attribute("value")
            if t_a_v_cnt == 5:
              print("テキストエリアにsend_message入力できません")
              break          
          driver.find_element(By.ID, "send_n").click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
          if driver.find_elements(By.CLASS_NAME, "banned-word"):
            time.sleep(6)
            driver.find_element(By.ID, "send_n").click()
          catch_warning_pop(name, driver)
          mailform_box = driver.find_elements(By.ID, value="mailform_box")
          if len(mailform_box):
            if "連続防止" in mailform_box[0].text:
              print("連続防止　待機中...")
              time.sleep(7)
              text_area = driver.find_element(By.ID, value="mdc")
              driver.execute_script(script, text_area, send_message)
              time.sleep(1)
              driver.find_element(By.ID, "send_n").click()
              time.sleep(1)
          print(f"{user_name}に2ndメールを送信しました")
          check_second += 1
        else:
          # print("やり取り中")
          received_mail = driver.find_elements(By.CSS_SELECTOR, ".left_balloon")[-1].text
          return_message = f"{name}pcmax,{login_id}:{login_pass}\n{user_name}「{received_mail}」"
          try:
            func.send_mail(return_message, [receiving_address, mailserver_address, mailserver_password],  f"pcmax新着{name}")
            print("通知メールを送信しました")
            check_more += 1
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
        if func.normalize_text(fst_message.format(name=user_name)) in func.normalize_text(sent_by_me[-1].text) or func.normalize_text(return_foot_message.format(name=user_name)) in func.normalize_text(sent_by_me[-1].text):
          # print(len(sent_by_me))
          text_area = driver.find_element(By.ID, value="mdc")
          script = "arguments[0].value = arguments[1];"
          driver.execute_script(script, text_area, second_message)
          t_a_v_cnt = 0
          text_area_value = text_area.get_attribute("value")
          while not text_area_value:
            t_a_v_cnt += 1
            time.sleep(2)
            text_area_value = text_area.get_attribute("value")
            if t_a_v_cnt == 5:
              print("テキストエリアにsecond_message入力できません")
              break        
          driver.find_element(By.ID, "send_n").click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
          if driver.find_elements(By.CLASS_NAME, "banned-word"):
            time.sleep(6)
            driver.find_element(By.ID, "send_n").click()
          catch_warning_pop(name, driver)
          mailform_box = driver.find_elements(By.ID, value="mailform_box")
          if len(mailform_box):
            if "連続防止" in mailform_box[0].text:
              print("連続防止　待機中...")
              time.sleep(7)
              text_area = driver.find_element(By.ID, value="mdc")
              driver.execute_script(script, text_area, second_message)
              time.sleep(1)
              driver.find_element(By.ID, "send_n").click()
              time.sleep(1)
          print(f"{user_name}に2ndメールを送信しました")
          check_second += 1
        else:
          # print("やり取り中")
          received_mail = driver.find_elements(By.CSS_SELECTOR, ".left_balloon")[-1].text
          return_message = f"{name}pcmax,{login_id}:{login_pass}\n{user_name}「{received_mail}」"
          try:
            func.send_mail(return_message, [receiving_address, mailserver_address, mailserver_password],  f"pcmax新着{name}")
            print("通知メールを送信しました")
            check_more += 1
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
    else:
      print("４分経過していません")
      return [user_name], check_first, check_second, check_more, gmail_condition, check_date
      break
  if "pcmax" in driver.current_url:
    driver.get("https://pcmax.jp/pcm/index.php")
  elif "linkleweb" in driver.current_url:
    driver.get("https://linkleweb.jp/pcm/member.php")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(0.5) 
  return [user_name], check_first, check_second, check_more, gmail_condition, check_date

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
    
      

def return_footmessage(name, driver, return_foot_message, send_limit_cnt, mail_img, unread_user, two_messages_flug):
  two_message_users = []
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
  user_row_cnt = 0
  bottom_scroll_cnt = 0
  while rf_cnt < send_limit_cnt:
    foot_user_list = driver.find_elements(By.CLASS_NAME, 'list_box')
    user_list_url = driver.current_url
    while user_row_cnt >= len(foot_user_list):
      driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(3)
      bottom_scroll_cnt += 1
      foot_user_list = driver.find_elements(By.CLASS_NAME, 'list_box')
      if bottom_scroll_cnt == 2:
        return rf_cnt
    # めもありか確認　memo_tab
    memo_tab = foot_user_list[user_row_cnt].find_elements(By.CLASS_NAME, 'memo_tab')
    if len(memo_tab):
      user_row_cnt += 1
      continue
    user_name = foot_user_list[user_row_cnt].find_element(By.CLASS_NAME,"user-name").text
    if unread_user and user_name in unread_user:
      print(f"{user_name} は未読リストにいるのでスキップします")
      user_row_cnt += 1
      continue
    while user_row_cnt >= len(foot_user_list):
      driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(3)
      bottom_scroll_cnt += 1
      foot_user_list = driver.find_elements(By.CLASS_NAME, 'list_box')
      if bottom_scroll_cnt == 3:
        return rf_cnt
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", foot_user_list[user_row_cnt])
    time.sleep(0.7)
    # foot_user_list[user_row_cnt]がクリックできる状態か確認したい
    foot_user_list_rtry_cnt = 0
    while (not foot_user_list[user_row_cnt].is_displayed() or not foot_user_list[user_row_cnt].is_enabled()):
      foot_user_list_rtry_cnt += 1
      for i, elem in enumerate(driver.find_elements(By.CLASS_NAME, "list_box")):
        print(i, elem.is_displayed(), elem.location)
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", foot_user_list[user_row_cnt])
      time.sleep(3)
      foot_user_list = driver.find_elements(By.CLASS_NAME, 'list_box')
      if foot_user_list_rtry_cnt == 5:
        print(f"{user_name} のリストがクリックできる状態になりません")
        print(driver.current_url)
        user_name = foot_user_list[user_row_cnt].find_element(By.CLASS_NAME,"user-name").text

        driver.save_screenshot(f"{user_name}_click_debug.png")
        elem = foot_user_list[user_row_cnt]
        print(f"クリック対象: {user_name}")
        print(f"  displayed={elem.is_displayed()}, enabled={elem.is_enabled()}, location={elem.location}, size={elem.size}")
        driver.save_screenshot(f"{user_name}_before_click.png")    
        func.send_error(
            chara=name,
            error_message=f"{user_name} のリストがクリックできる状態になりません\n{driver.current_url}\ndisplayed={elem.is_displayed()}, enabled={elem.is_enabled()}, location={elem.location}, size={elem.size}",
            attachment_paths=f"{user_name}_click_debug.png"
        )
        break
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", foot_user_list[user_row_cnt])
    time.sleep(0.7)
    foot_user_list[user_row_cnt].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1.5)
    catch_warning_pop(name, driver)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "overview"))
    )
    ditail_page_user_name = driver.find_element(By.ID, 'overview').find_element(By.TAG_NAME, 'p').text
    if user_name[:6] not in ditail_page_user_name[:6]:
      print(f"ユーザー名が一致しません user_name:{user_name}  ditail_page_user_name:{ditail_page_user_name}")
      func.send_error(name, f"ユーザー名が一致しません user_name:{user_name}  ditail_page_user_name:{ditail_page_user_name}\n",                            )
      driver.back()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      user_row_cnt += 1
      continue
    if two_messages_flug:
      two_message_users.append(ditail_page_user_name)
    arleady_iikamo = driver.find_elements(By.CLASS_NAME, 'type5')
    iikamo = driver.find_elements(By.CLASS_NAME, 'type1')
    iikamo_arigatou = driver.find_elements(By.CLASS_NAME, 'type4')
    iikamo_text = ""
    if len(arleady_iikamo):
      iikamo_text = f"いいかも済み"
      # print(f"いいかも済み  ユーザー名:{ditail_page_user_name}  ")
    elif len(iikamo):
      WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'type1')))
      iikamo[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(0.7)
      iikamo_text = f"いいかも"
      # print(f"いいかも  ユーザー名:{ditail_page_user_name} ")
    elif len(iikamo_arigatou):
      # iikamo_arigatou[0].click()
      # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      # time.sleep(0.7)
      iikamo_text = f"いいかもありがとう"
      # print(f"いいかもありがとう  ユーザー名:{ditail_page_user_name} ")
    try:
      catch_warning_pop(name, driver)
      memo_edit = driver.find_element(By.CLASS_NAME, 'memo_edit')
      if "もふ" in memo_edit.text:
        print(f"{user_name} もふあり")
        driver.back()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
        user_row_cnt += 1
        continue
    except NoSuchElementException as e:
      img_path = f"{name}_error.png"
      print(ditail_page_user_name)
      print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
      print(traceback.format_exc())
      
      driver.save_screenshot(img_path)
      func.send_error(
          chara=name,
          error_message=f"{ditail_page_user_name}\n{driver.current_url}\n{str(e)}",
          attachment_paths=img_path  # 複数なら ["a.png","b.log"] のようにリストで
      )
      pass
    memo_ele = driver.find_elements(By.CSS_SELECTOR, '.side_btn.memo_open')
    memo_ele[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    driver.find_element(By.ID, 'memotxt').send_keys("もふ")
    driver.find_element(By.ID, 'memo_send').click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    if "pcmax" in driver.current_url:
      text_area = driver.find_elements(By.ID, value="mail_com")
    elif "linkleweb" in driver.current_url:
      text_area = driver.find_elements(By.ID, value="comme")
    script = "arguments[0].value = arguments[1];"
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area[0])
    time.sleep(0.5)
    driver.execute_script(script, text_area[0], return_foot_message.format(name=ditail_page_user_name))
    time.sleep(0.5)  
    # まじ送信　
    if "pcmax" in driver.current_url:
      mile_point_text = driver.find_element(By.CLASS_NAME, value="side_point_pcm_data").text
    elif "linkleweb" in driver.current_url:
      mile_point_text = driver.find_element(By.CLASS_NAME, value="side_mile_pcm_data").text
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
    now = datetime.now().strftime('%d %H:%M:%S')
    if maji_soushin:
      if "pcmax" in driver.current_url:
        maji =  driver.find_element(By.ID, value="majiBtn")
      elif "linkleweb" in driver.current_url:
        maji =  driver.find_element(By.CLASS_NAME, value="maji_btn_send")
      maji.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      if "pcmax" in driver.current_url:
        link_OK = driver.find_element(By.ID, value="link_OK")
      elif "linkleweb" in driver.current_url:
        link_OK = driver.find_element(By.CSS_SELECTOR, ".majibt.yes")
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
    elif "pcmax" in driver.current_url:
      if len(driver.find_elements(By.CLASS_NAME, value='comp_title')):
        # print(driver.find_element(By.CLASS_NAME, value='comp_title').text)
        if "送信完了" in driver.find_element(By.CLASS_NAME, value='comp_title').text:
          rf_cnt += 1   
          print(f"{rf_cnt}件送信　ユーザー名:{ditail_page_user_name} {iikamo_text} マジ送信{maji_soushin}  {now}")
          user_row_cnt = 0
          unread_user.append(user_name)
          catch_warning_pop(name, driver)
          back2 = driver.find_element(By.ID, value="back2")
          driver.execute_script("arguments[0].click();", back2)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(3)
    elif "linkleweb" in driver.current_url:
      time.sleep(1)
      rf_cnt += 1   
      print(f"{rf_cnt}件送信 ユーザー名:{ditail_page_user_name} {iikamo_text} マジ送信{maji_soushin}  {now}")
      user_row_cnt += 1
      driver.get(user_list_url)
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(3)
    else:
      img_path = f"{name}_returnfoot_error.png"
      print(ditail_page_user_name)
      print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
      print(traceback.format_exc())
      
      driver.save_screenshot(img_path)
      func.send_error(
          chara=name,
          error_message=f"{ditail_page_user_name}\n送信が完了しませんでした",
          attachment_paths=img_path  # 複数なら ["a.png","b.log"] のようにリストで
      )
  if two_messages_flug:
    header = driver.find_element(By.ID, "header_box_under")
    links = header.find_elements(By.TAG_NAME, "a")
    for link in links:
      if "メッセージ" in link.text:
        link.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        break
    inner = driver.find_elements(By.CLASS_NAME, "inner")
    a_btns = inner[0].find_elements(By.TAG_NAME, "a")
    for a_btn in a_btns:
      if "送信" in a_btn.text:
        a_btn.click() 
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        break
    for two_message_user in two_message_users:
      mail_details = driver.find_elements(By.CLASS_NAME, "mail_area")
      for mail_detail in mail_details:
        user_info = mail_detail.find_element(By.CLASS_NAME, "user_info")
        # print(f"~~~~~two_message_user:{two_message_user}~~~~~~")
        # print(f"user_info.text:{user_info.text}~~~~~~")
        # print(two_message_user in user_info.text)
        if two_message_user in user_info.text:
          # driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", user_info)
          mail_detail.find_element(By.TAG_NAME, "a").click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
          # print(f"two_message_user 1stメールを送信します")
          # print(f"~~~~~ユーザー名:{two_message_user}  確認中...~~~~~~")
          # print(fst_message.format(name=two_message_user))
          user_name = two_message_user
          if user_name is None:
            print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<ユーザーネームが取得できていません {user_name}>>>>>>>>>>>>>>>>>>>>>>>")
            func.send_error(name, f"ユーザーネームが取得できていません {user_name}\n",                            )
            return rf_cnt
          if "name" in return_foot_message.format(name=user_name):
            print(f"ユーザー名が正しく反映されていません\n{user_name}\{return_foot_message.format(name=user_name)}")
            func.send_error(name, f"ユーザー名が正しく反映されていません\n{user_name}\{return_foot_message.format(name=user_name)}")          
            return rf_cnt
          text_area = driver.find_element(By.ID, value="mdc")
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
          script = "arguments[0].value = arguments[1];"
          driver.execute_script(script, text_area, return_foot_message.format(name=user_name))
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
          driver.find_element(By.ID, "send_n").click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
          mailform_box = driver.find_elements(By.ID, value="mailform_box")
          if len(mailform_box):
            if "連続防止" in mailform_box[0].text:
              print("連続防止　待機中...")
              time.sleep(7)
              text_area = driver.find_element(By.ID, value="mdc")
              driver.execute_script(script, text_area, return_foot_message.format(name=user_name))
              time.sleep(1)
              if mail_img:
                my_photo_element = driver.find_element(By.ID, "my_photo")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", my_photo_element)
                select = Select(my_photo_element)
                for option in select.options:
                  if mail_img in option.text:
                    select.select_by_visible_text(option.text)
                    time.sleep(0.7)
                    break
              driver.find_element(By.ID, "send_n").click()
              time.sleep(1)
          if driver.find_elements(By.CLASS_NAME, "banned-word"):
            time.sleep(6)
            driver.find_element(By.ID, "send_n").click()
          print(f"{user_name}にtwo_m用の1stメールを送信しました")
          catch_warning_pop(name, driver)
          if "pcmax" in driver.current_url: 
            driver.get("https://pcmax.jp/mobile/mail_recive_send_list.php")
          elif "linkleweb" in driver.current_url:
            driver.get("https://linkleweb.jp/mobile/mail_recive_send_list.php")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
          mail_details = driver.find_elements(By.CLASS_NAME, "mail_area")  
          break         
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

def make_footprint(name, driver, footprint_count, iikamo_count):
  current_step = 0
  wait = WebDriverWait(driver, 10)
  random_wait = random.uniform(0.1, 3.4)
  search_edit = {
    "y_age": [18],
    "o_age": [28,29,30],
    "m_height": [165,170,175],
    "area_flug": 2,
    "search_target": ["送信歴無し"],
    "exclude_words": ["不倫・浮気", "エロトーク・TELH", "SMパートナー", "写真・動画撮影", "同性愛", "アブノーマル"],
    "search_body_type": ["スリム", "やや細め", "普通", "ふくよか", "太め" ],
    "annual_income":["200万円未満", "200万円以上〜400万円未満", "指定なし"]
  }
  if not profile_search(driver, search_edit):
    return
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  user_list = driver.find_elements(By.CLASS_NAME, 'profile_card')
  user_list_url = driver.current_url
  ft_cnt = 0
  # やり取りあるか確認
  while ft_cnt < footprint_count:
    if current_step < len(user_list):
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", user_list[current_step])
      time.sleep(0.4)
      exchange = user_list[current_step].find_elements(By.CLASS_NAME, value="exchange")
      user_name = user_list[current_step].find_elements(By.CLASS_NAME, value="name")[0].text
      if len(exchange):
        print(f"やり取り有り　{user_name}")
        current_step += 1
        continue   
      if "linkleweb" in driver.current_url:
        user_info = user_list[current_step].find_elements(By.CLASS_NAME, value="user_info")[0].text
      elif "pcmax" in driver.current_url:
        user_info = user_name
      user_area = user_list[current_step].find_elements(By.CLASS_NAME, value="conf")[0].text.replace("登録地域", "")    
      user_list[current_step].find_element(By.CLASS_NAME, "profile_link_btn").click()   
      catch_warning_pop(name, driver)
      iikamo_text = ""
      if iikamo_count > 0:
        # type1 いいかも
        # type4 いいかもありがとう
        # type5 いいかもありがとう済み
        arleady_iikamo = driver.find_elements(By.CLASS_NAME, 'type5')
        iikamo = driver.find_elements(By.CLASS_NAME, 'type1')
        iikamo_arigatou = driver.find_elements(By.CLASS_NAME, 'type4')  
        if len(arleady_iikamo):
          iikamo_text = f"いいかも済み"
          # print(f"いいかも済み  ユーザー名:{user_name} {user_area} ")
        elif len(iikamo):
          iikamo[0].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(0.7)
          iikamo_count -= 1
          iikamo_text = f"いいかも"
          # print(f"いいかも  ユーザー名:{user_info} {user_area} ")
        elif len(iikamo_arigatou):
          iikamo_arigatou[0].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(0.7)
          iikamo_count -= 1
          iikamo_text = "いいかもありがとう"
          # print(f"いいかもありがとう  ユーザー名:{user_info} {user_area}")
      footprint_now = datetime.now().strftime('%d %H:%M:%S')
      current_step += 1  
      ft_cnt += 1
      print(f"{ft_cnt}件 {iikamo_text} ユーザー名:{user_info} {user_area} {footprint_now}")  
      time.sleep(random_wait) 
    else:
      # print("足跡付けのユーザーがいません")
      # print(current_step)
      # print(len(user_list))
      driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(4)
      user_list = driver.find_elements(By.CLASS_NAME, 'profile_card')
      # print("スクロールした")
      # print(current_step)
      # print(len(user_list))
      if current_step >= len(user_list):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(4)
        # print("もう一回スクロールした")
        # print(current_step)
        # print(len(user_list))
        if current_step > len(user_list):
          # print("スクロールしてもユーザーがいなかった")
          print(driver.current_url)
          profile_search(driver, search_edit)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          user_list_url = driver.current_url
        else:
          user_list[current_step].find_element(By.CLASS_NAME, "profile_link_btn").click()   
          footprint_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
          print(f"2スクロールしてから足跡付け {current_step}件 {footprint_now}")    
          time.sleep(0.6)
      else:
        continue
    if not user_list_url in driver.current_url:
      driver.get(user_list_url)
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    user_list = driver.find_elements(By.CLASS_NAME, 'profile_card')


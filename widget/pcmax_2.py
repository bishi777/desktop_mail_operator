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
    if tuto_pop:
      time.sleep(1)
      driver.refresh()
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

  try:
    apn_dialog = driver.find_elements(By.CLASS_NAME, 'apn_dialog')
    if apn_dialog:
      time.sleep(1)
      apn_close = apn_dialog[0].find_elements(By.CLASS_NAME, 'apn_btn')
      if apn_close:
        apn_close[0].click()
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
  if old_value == 60:
    old_age = "60歳以上"
  else:
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
    ("10130", "except13"),
    ("", "except14"),
    ("10150", "except15"),
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
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", checkbox)
      time.sleep(0.5)
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

  # 検索順を 最新ログイン順 → 登録順 → 最新ログイン順 と切替えてリフレッシュを強制
  # （デフォルト最新ログイン順のままだと並び替えが反映されない事があるため）
  try:
    sort_select = driver.find_element(By.ID, "so1")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", sort_select)
    Select(sort_select).select_by_value("3")  # 最新ログイン順
    print("検索順 → 最新ログイン順")
    time.sleep(random.uniform(1.0, 2.0))
    sort_select = driver.find_element(By.ID, "so1")
    Select(sort_select).select_by_value("2")  # 登録順
    print("検索順 → 登録順")
    time.sleep(random.uniform(1.0, 2.0))
    sort_select = driver.find_element(By.ID, "so1")
    Select(sort_select).select_by_value("3")  # 最新ログイン順に戻す（最終状態）
    print("検索順 → 最新ログイン順（最終）")
    time.sleep(0.5)
  except NoSuchElementException:
    print("検索順の設定ができません")

  # 検索ボタンを押す
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(0.5)
  driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(0.5)
  try:
    search_button = driver.find_element(By.ID, "image_button")
  except NoSuchElementException:
    search_button = driver.find_element(By.ID, "search1")
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", search_button)
  time.sleep(0.5)
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
        iikamo_text = ""
        if not (sent_cnt < send_cnt):
          # type1 いいかも
          # type4 いいかもありがとう
          # type5 いいかもありがとう済み
          arleady_iikamo = driver.find_elements(By.CLASS_NAME, 'type5')
          iikamo = driver.find_elements(By.CLASS_NAME, 'type1')
          iikamo_arigatou = driver.find_elements(By.CLASS_NAME, 'type4')
          
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
               mail_info, chara_prompt):
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
      # 年齢チェック
      match = re.search(r'(\d+)歳', user_name)
      if match:
        age = int(match.group(1))
        print(age)
        if age < 18 or age > 40:
          chat_ai_flug = True
        else:
          chat_ai_flug = False
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
      email_list = None
      email_pattern = r'[a-zA-Z0-9_.+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-.]+'
      received_mail = ""
      for received_mail in received_elems:
        received_mail = received_mail.text 
        received_mail = received_mail.replace("＠", "@").replace("あっとまーく", "@").replace("アットマーク", "@")
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
        elif "pcmax" in driver.current_url:
          # やり取り全表示画面には #icon_menu が無いので、一度メール詳細画面に戻る
          driver.back()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
          nolook_a = driver.find_elements(By.CSS_SELECTOR, "#icon_menu a[href*='nolook_add.php']")
          if nolook_a:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", nolook_a[0])
            nolook_a[0].click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(1)
            image_button2 = driver.find_elements(By.ID, "image_button2")
            if len(image_button2):
              image_button2[0].click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(1)
            print(f"{user_name}を見ちゃいや登録")
          driver.get("https://pcmax.jp/mobile/mail_recive_list.php?receipt_status=0")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
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
            site = "リンクル(PCMAX)"
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
      elif chat_ai_flug:
        if False:
        # if chara_prompt:
          history = []
          male_history = []
          # right_balloon キャラ
          # left_baloon ユーザー
          message__blocks = driver.find_elements(By.CLASS_NAME, value="bggray")
          for message__block in message__blocks:
            femail_flug = message__block.find_elements(By.CLASS_NAME, value="right_balloon") 
            if len(femail_flug):
              history.append({"role": "model", "text": femail_flug[0].text})
            mail_flug = message__block.find_elements(By.CLASS_NAME, value="left_balloon") 
            if len(mail_flug):
              history.append({"role": "user", "text": mail_flug[0].text})
              male_history.append(mail_flug[0].text)
          if not male_history:
            user_input = None
          else:
            user_input = male_history[-1]
          print("AIチャット返信処理を開始します")
          ai_response, all_history = func.chat_ai(name, chara_prompt, history, fst_message, user_input) 
          if ai_response is None:
            print("Gemini制限中のため返信しません")
            return
          text_area = driver.find_element(By.ID, value="mdc")
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
          script = "arguments[0].value = arguments[1];"
          driver.execute_script(script, text_area, ai_response)
          time.sleep(1)
          text_area_value = text_area.get_attribute("value")
          t_a_v_cnt = 0
          while not text_area_value:
            t_a_v_cnt += 1
            time.sleep(2)
            text_area_value = text_area.get_attribute("value")
            if t_a_v_cnt == 5:
              print("テキストエリアに入力できません")
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
          print(f"{user_name}にチャットAIを送信しました")
          catch_warning_pop(name, driver)
          formatted_history = []
          formatted_history.append("==================================")
          formatted_history.append(f"   {user_name} (相手) との履歴")
          formatted_history.append("==================================")
          seen_messages = set() # To prevent exact duplicates if likely
          for h in all_history:
              role = h["role"]
              text = h["text"].strip()
              # Deduplication check (simple)
              signature = f"{role}:{text}"
              if signature in seen_messages:
                    continue
              seen_messages.add(signature)
              if role == "user":
                  header = f"▼ {user_name} (相手)"
              else:  # assistant / model
                  header = f"▲ {name} (自分/AI)"
              
              formatted_history.append(f"\n{header}")
              formatted_history.append("-" * 20)
              formatted_history.append(text)    
          mail_text = "\n".join(formatted_history)
          return_message = f"{name}pcmax,{login_id}:{login_pass}\n{user_name}「{mail_text}」"
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
        # print("~~~~~~~~~こちらから送信したメッセージチェック中~~~~~~~~~")
        # print(func.normalize_text(sent_by_me[-1].text))
        # いいかも!ありがとう♪よろしくお願いします。
        # print(func.normalize_text(fst_message.format(name=user_name)) in func.normalize_text(sent_by_me[-1].text))
        if "いいかも!ありがとう" in func.normalize_text(sent_by_me[-1].text):
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
          print("やり取り中")

          messages = driver.find_element(By.CLASS_NAME, "bggray").text
          return_message = f"{name}pcmax,{login_id}:{login_pass}\n{messages}」"
          # received_mail = driver.find_elements(By.CSS_SELECTOR, ".left_balloon")[-1].text
          # return_message = f"{name}pcmax,{login_id}:{login_pass}\n{user_name}「{received_mail}」"

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
  ashiato_list_link_ = driver.find_element(By.ID, 'mydata_pcm').find_elements(By.TAG_NAME, "a")
  for link in ashiato_list_link_:
    if "あしあと" in link.text:
      ashiato_list_link = link
      break
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", ashiato_list_link)
  time.sleep(0.5)
  ashiato_list_link.click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(0.5)
  rf_cnt = 0
  user_row_cnt = 0
  now_hour = datetime.now().hour
  # 午前6時〜8時の間は7、それ以外は2
  if 6 <= now_hour < 8:
    bottom_scroll_cnt = 6
  else:
    bottom_scroll_cnt = 2
  bottom_roll_cnt = 0

  while rf_cnt < send_limit_cnt:
    foot_user_list = driver.find_elements(By.CLASS_NAME, 'list_box')
    while user_row_cnt >= len(foot_user_list):
      driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(3)
      bottom_roll_cnt += 1
      foot_user_list = driver.find_elements(By.CLASS_NAME, 'list_box')
      if bottom_roll_cnt == bottom_scroll_cnt:
        return rf_cnt
    foot_user_list = driver.find_elements(By.CLASS_NAME, 'list_box')
    user_list_url = driver.current_url
    # 女性はスキップ
    woman = foot_user_list[user_row_cnt].find_elements(By.CLASS_NAME, 'woman')
    if len(woman):
      user_row_cnt += 1
      continue

    # いいかも済みはスキップ
    if foot_user_list[user_row_cnt].find_elements(By.CLASS_NAME, 'type5'):
      user_row_cnt += 1
      continue
    # マッチングもスキップ
    if foot_user_list[user_row_cnt].find_elements(By.CLASS_NAME, 'type6'):
      user_row_cnt += 1
      continue

    # 年齢確認
    user_age = foot_user_list[user_row_cnt].find_element(By.CLASS_NAME, 'user-age').text
    match = re.search(r'(\d+)歳', user_age)
    if name == "ひろみ":
      print(f"特殊設定　{name}  年齢確認 {user_age}")
    elif match:
      age = int(match.group(1))
      if 18 <= age <= 69:
        print(f"年齢確認OK{age}")
      else:
        user_row_cnt += 1
        continue
    user_name = foot_user_list[user_row_cnt].find_element(By.TAG_NAME,"a").get_attribute('data-va5')
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
    user_name = foot_user_list[user_row_cnt].find_element(By.TAG_NAME,"a").get_attribute('data-va5')
    if foot_user_list[user_row_cnt].is_displayed() is False:
      # print("クリックできません")
      user_row_cnt += 1
      continue
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
    if user_name.replace(" ", "").replace("　", "") not in ditail_page_user_name.replace(" ", "").replace("　", ""):
      print(f"ユーザー名が一致しません user_name:{user_name}  ditail_page_user_name:{ditail_page_user_name}")
      func.send_error(name, f"ユーザー名が一致しません user_name:{user_name}  ditail_page_user_name:{ditail_page_user_name}\n",                            )
      driver.back()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      user_row_cnt += 1
      continue
    if two_messages_flug:
      two_message_users.append(ditail_page_user_name)
    iikamo = driver.find_elements(By.CLASS_NAME, 'type1')
    iikamo_arigatou = driver.find_elements(By.CLASS_NAME, 'type4')
    iikamo_text = ""
    if len(iikamo_arigatou):
      iikamo_arigatou[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(0.7)
      iikamo_text = f"いいかもありがとう"
    elif len(iikamo):
      WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'type1')))
      iikamo[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(0.7)
      iikamo_text = f"いいかも"
    
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
          user_row_cnt += 1
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
      unread_user.append(user_name)
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

def _post_new_with_area(driver, wait, post_title, post_content, pref_name, city_name):
  """新規投稿として指定地域に掲示板を投稿する（審査中でコピーリンクがない場合のフォールバック）"""
  get_header_menu(driver, "掲示板投稿")
  if "/mobile/bbs_write.php" not in driver.current_url:
    driver.get("https://pcmax.jp/mobile/bbs_write.php")
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
  # 掲示板を書くリンクをクリック
  links = driver.find_elements(By.TAG_NAME, "a")
  for link in links:
    if "掲示板でお相手を募集する" in link.text:
      link.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      break
  driver.find_element(By.ID, "2").click()
  # 都道府県を変更
  pref_select = driver.find_element(By.ID, "prech")
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", pref_select)
  time.sleep(0.5)
  Select(pref_select).select_by_visible_text(pref_name)
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  detail_area = driver.find_element(By.ID, "citych")
  Select(detail_area).select_by_visible_text(city_name)
  time.sleep(0.5)
  max_reception_count = driver.find_element(By.NAME, "max_reception_count")
  Select(max_reception_count).select_by_visible_text("5通")
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
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  print(f"掲示板新規投稿完了（{pref_name} {city_name}）")
  return True

def _post_copy_with_area(driver, wait, pref_name, city_name):
  """「過去の書込のコピー・削除」ページから「地域を変えてコピー」で指定地域に投稿する"""
  line_bottoms = driver.find_elements(By.CLASS_NAME, "line_bottom")
  for line_bottom in line_bottoms:
    if "地域を変えてコピー" in line_bottom.text:
      line_bottom.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      # 都道府県を変更
      pref_select = driver.find_element(By.ID, "prech")
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", pref_select)
      time.sleep(0.5)
      Select(pref_select).select_by_visible_text(pref_name)
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      # 市区町村を選択
      detail_area = driver.find_element(By.ID, "citych")
      Select(detail_area).select_by_visible_text(city_name)
      time.sleep(0.5)
      max_reception_count = driver.find_element(By.NAME, "max_reception_count")
      Select(max_reception_count).select_by_visible_text("5通")
      time.sleep(1)
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", driver.find_element(By.ID, "wri"))
      time.sleep(10)
      driver.find_element(By.ID, "wri").click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      print(f"掲示板投稿完了（{pref_name} {city_name}）")
      return True
  print("「地域を変えてコピー」リンクが見つかりません")
  return False

def _post_multi_nearby(driver, wait, post_title, post_content, prefs, count):
  """nearby_prefs から count 件サンプリングして地域違いで投稿する（コピー失敗時は新規投稿）"""
  chosen = random.sample(prefs, count)
  for chosen_pref in chosen:
    if _go_to_post_list(driver, wait):
      if not _post_copy_with_area(driver, wait, chosen_pref, "全域"):
        _post_new_with_area(driver, wait, post_title, post_content, chosen_pref, "全域")
    else:
      _post_new_with_area(driver, wait, post_title, post_content, chosen_pref, "全域")

def _go_to_post_list(driver, wait):
  """過去の書込のコピー・削除ページへ遷移する"""
  if not get_header_menu(driver, "掲示板投稿"):
    driver.get("https://pcmax.jp/mobile/bbs_write.php")
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
  text_right = driver.find_elements(By.CLASS_NAME, "text_right")
  if text_right:
    copy_links = text_right[0].find_elements(By.TAG_NAME, "a")
    if copy_links:
      copy_links[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      return True
  print("過去の書込リンクが見つかりません")
  return False

def _delete_all_posts(driver, wait):
  """掲示板一覧画面で既存投稿を全削除する。事前に _go_to_post_list で一覧画面に遷移済みであること。"""
  count = 0
  while True:
    line_bottoms = driver.find_elements(By.CLASS_NAME, "line_bottom")
    delete_url = None
    for lb in line_bottoms:
      for a in lb.find_elements(By.TAG_NAME, "a"):
        href = a.get_attribute("href") or ""
        m = re.search(r'dispMenu\((\d+),(\d+),(\d+)\)', href)
        if m:
          sfid_match = re.search(r'sfid=([a-f0-9]+)', driver.current_url)
          sfid = sfid_match.group(1) if sfid_match else ""
          delete_url = f"https://pcmax.jp/mobile/bbs_write.php?delete=1&pref_no={m.group(1)}&bbs_category={m.group(2)}&bbs_id={m.group(3)}&page=1&sfid={sfid}"
          break
      if delete_url:
        break
    if not delete_url:
      break
    driver.get(delete_url)
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    count += 1
    if not _go_to_post_list(driver, wait):
      break
  return count

def re_post(driver, wait, post_title, post_content):
  post_area_tokyo = ["千代田区",  "文京区",
                   "品川区", "目黒区", "大田区", "世田谷区", "渋谷区",
                   "杉並区", "豊島区",  "荒川区", "板橋区", "練馬区",
                    "武蔵野市",  "西東京市", "三鷹市", "調布市", "小金井市", "小平市",
                    "立川市", "八王子市",  "府中市",
                   ]
  nearby_prefs = ["神奈川県", "埼玉県", "千葉県", "群馬県", "栃木県"]
  if not _go_to_post_list(driver, wait):
    print("re_post: 掲示板一覧へ遷移失敗")
    return
  list_photo = driver.find_elements(By.CLASS_NAME, "list_photo")
  print(f"re_post: 既存投稿数 = {len(list_photo)}")

  if len(list_photo) >= 1:
    posted_date_elems = driver.find_elements(By.CLASS_NAME, "font_size")
    if posted_date_elems:
      try:
        date_numbers = re.findall(r'\d+', posted_date_elems[0].text)
        current_year = datetime.now().year
        last_post = datetime(current_year, int(date_numbers[0]), int(date_numbers[1]), int(date_numbers[2]), int(date_numbers[3]))
        elapsed = datetime.today() - last_post
        print(f"前回の投稿からの経過時間: {elapsed}")
        if elapsed < timedelta(hours=2):
          print("前回投稿から2時間未満のため再投稿しません")
          return
      except (ValueError, IndexError) as e:
        print(f"⚠️ 投稿日時パース失敗、続行: {e}")
    deleted = _delete_all_posts(driver, wait)
    print(f"既存投稿{deleted}件を削除しました")

  chosen_city = random.choice(post_area_tokyo)
  print(f"新規投稿します（東京都 {chosen_city}）")
  _post_new_with_area(driver, wait, post_title, post_content, "東京都", chosen_city)
  print("東京投稿完了 → 近隣県に2件追加投稿します（合計3件）")
  _post_multi_nearby(driver, wait, post_title, post_content, nearby_prefs, 2)

def make_footprint(name, driver, footprint_count, iikamo_count):
  import urllib.parse
  current_step = 0
  wait = WebDriverWait(driver, 10)
  random_wait = random.uniform(3.4, 6.4)
  search_edit = {
    "y_age": [18],
    "o_age": [29,30,34],
    "m_height": [165,170,175],
    "area_flug": 2,
    "search_target": ["送信歴無し"],
    "exclude_words": ["不倫・浮気", "エロトーク・TELH", "SMパートナー", "写真・動画撮影", "同性愛", "アブノーマル"],
    "search_body_type": ["スリム", "やや細め", "普通", "ふくよか", "太め" ],
    "annual_income":["200万円未満", "200万円以上〜400万円未満", "指定なし"]
  }
  if name == "ひろみ":
    search_edit["o_age"] = [34, 60]
    print(f"特殊設定　{name}　年齢{search_edit['y_age']}~{search_edit['o_age']}")
  catch_warning_pop(name, driver)
  if not profile_search(driver, search_edit):
    return
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # # 地域セレクト: 東京都50%、栃木/静岡/群馬/埼玉/千葉/神奈川 各約8%
  # _area_pool    = ["東京都", "栃木県", "静岡県", "群馬県", "埼玉県", "千葉県", "神奈川県"]
  # _area_weights = [28, 12, 12, 12, 12, 12, 12]
  # chosen_area = random.choices(_area_pool, weights=_area_weights)[0]
  # try:
  #   from urllib.parse import urljoin
  #   base_url = driver.current_url
  #   area_url = driver.execute_script("""
  #     var sel = document.querySelectorAll('select')[0];
  #     if (!sel) return null;
  #     for (var i = 0; i < sel.options.length; i++) {
  #       if (sel.options[i].text.trim() === arguments[0]) {
  #         return sel.options[i].value;
  #       }
  #     }
  #     // デバッグ用: 全オプションを表示
  #     var opts = [];
  #     for (var j = 0; j < sel.options.length; j++) { opts.push(sel.options[j].text.trim()); }
  #     return '__OPTIONS__:' + opts.join(',');
  #   """, chosen_area)
  #   if area_url and not str(area_url).startswith('__OPTIONS__:'):
  #     driver.get(urljoin(base_url, area_url))
  #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  #     time.sleep(1)
  #     # 地域選択できたか確認
  #     selected_area = driver.execute_script("""
  #       var sel = document.querySelectorAll('select')[0];
  #       if (!sel) return null;
  #       return sel.options[sel.selectedIndex].text.trim();
  #     """)
  #     if selected_area != chosen_area:
  #       print(f"{name} 地域選択NG（期待:{chosen_area} 実際:{selected_area}）→ 再試行")
  #       area_url2 = driver.execute_script("""
  #         var sel = document.querySelectorAll('select')[0];
  #         if (!sel) return null;
  #         for (var i = 0; i < sel.options.length; i++) {
  #           if (sel.options[i].text.trim() === arguments[0]) {
  #             return sel.options[i].value;
  #           }
  #         }
  #         return null;
  #       """, chosen_area)
  #       if area_url2:
  #         driver.get(urljoin(base_url, area_url2))
  #         wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  #         time.sleep(1)
  #         selected_area = driver.execute_script("""
  #           var sel = document.querySelectorAll('select')[0];
  #           if (!sel) return null;
  #           return sel.options[sel.selectedIndex].text.trim();
  #         """)
  #         print(f"{name} 再試行後の地域: {selected_area}")
  #       else:
  #         print(f"{name} 再試行用URLが取得できませんでした")
  #     if selected_area != chosen_area:
  #       print(f"{name} ⚠️ 地域選択最終NG（期待:{chosen_area} 実際:{selected_area}）→ そのまま続行")
  #     else:
  #       print(f"{name} ✅ 検索地域: {selected_area}")
  #   elif area_url and str(area_url).startswith('__OPTIONS__:'):
  #     opts = area_url.replace('__OPTIONS__:', '')
  #     print(f"{name} ⚠️ 地域オプションに '{chosen_area}' が見つかりません。利用可能: {opts}")
  #   else:
  #     print(f"{name} ⚠️ セレクト要素が見つかりません（指定無しで続行）")
  # except Exception as e:
  #   print(f"{name} 地域セレクトエラー: {e}")
  #   traceback.print_exc()
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
      user_age =  user_list[current_step].find_elements(By.CLASS_NAME, value="age")[0].text
      user_area = user_list[current_step].find_elements(By.CLASS_NAME, value="conf")[0].text.replace("登録地域", "")
      age_num_m = re.search(r'(\d+)', user_age)
      if age_num_m and int(age_num_m.group(1)) > 34:
        print(f"年齢スキップ {user_name} {user_age}")
        current_step += 1
        continue
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
      # メモ登録（地域セレクト） ※地域セレクト無効化中のためスキップ
      # try:
      #   uid_m = re.search(r'user_id=(\d+)', driver.current_url)
      #   if uid_m:
      #     area_short = re.sub(r'[都道府県]$', '', chosen_area)
      #     encoded_memo = urllib.parse.quote(f"地域セレクト{area_short}", encoding='shift_jis')
      #     driver.execute_script(
      #       f"$.get('https://pcmax.jp/mobile/memo_reg.php?memo_user_id={uid_m.group(1)}&memo={encoded_memo}&regist=1');"
      #     )
      #     time.sleep(0.3)
      # except Exception as e:
      #   print(f"{name} メモ登録エラー: {e}")
      footprint_now = datetime.now().strftime('%m/%d %H:%M:%S')
      current_step += 1  
      ft_cnt += 1
      print(f"{ft_cnt}件 {iikamo_text} {user_info}{user_age} {user_area} {footprint_now}")  
      time.sleep(random_wait) 
    else:
      print("足跡付けのユーザーがいません")
      print(current_step)
      print(len(user_list))
      driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(4)
      user_list = driver.find_elements(By.CLASS_NAME, 'profile_card')
      print("スクロールした")
      print(current_step)
      print(len(user_list))
      if current_step >= len(user_list):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(4)
        print("もう一回スクロールした")
        print(current_step)
        print(len(user_list))
        if current_step > len(user_list):
          print("スクロールしてもユーザーがいなかった")
          print(driver.current_url)
          profile_search(driver, search_edit)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          user_list_url = driver.current_url
          current_step = 0
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


def make_footprint_shinjin(name, driver, footprint_count=5, iikamo_count=0):
  """新人プロフィール検索から足跡をつける。東京→他地域を2回繰り返す"""
  wait = WebDriverWait(driver, 10)
  _area_pool = ["栃木県", "静岡県", "群馬県", "埼玉県", "千葉県", "神奈川県"]
  areas = ["東京都"] + random.sample(_area_pool, 2)
  catch_warning_pop(name, driver)

  for area in areas:
    # TOPページに移動して新人プロフィール検索をクリック
    if "pcmax" in driver.current_url:
      driver.get("https://pcmax.jp/pcm/index.php")
    elif "linkleweb" in driver.current_url:
      driver.get("https://linkleweb.jp/pcm/member.php")
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    # 新人プロフィール検索リンクをクリック
    links = driver.find_elements(By.TAG_NAME, "a")
    clicked = False
    for link in links:
      if "新人プロフィール検索" in link.text:
        link.click()
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        clicked = True
        break
    if not clicked:
      print(f"{name} 新人プロフィール検索リンクが見つかりません")
      return

    # 地域を変更（selectの最初の要素で地域URLを選択）
    if area != "東京都":
      try:
        area_select = driver.find_elements(By.TAG_NAME, "select")[0]
        options = area_select.find_elements(By.TAG_NAME, "option")
        for opt in options:
          if opt.text.strip() == area:
            area_url = opt.get_attribute("value")
            from urllib.parse import urljoin
            driver.get(urljoin(driver.current_url, area_url))
            wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
            time.sleep(1)
            break
      except Exception as e:
        print(f"{name} 地域変更エラー({area}): {e}")
        continue

    print(f"{name} 新人足跡付け開始: {area}")
    user_list_url = driver.current_url
    user_list = driver.find_elements(By.CLASS_NAME, "profile_card")
    ft_cnt = 0
    current_step = 0
    area_iikamo_count = iikamo_count  # 地域ごとにリセット
    random_wait = random.uniform(0.1, 3.4)

    while ft_cnt < footprint_count:
      if current_step >= len(user_list):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(3)
        user_list = driver.find_elements(By.CLASS_NAME, "profile_card")
        if current_step >= len(user_list):
          print(f"{name} {area} これ以上ユーザーがいません({ft_cnt}件)")
          break

      card = user_list[current_step]
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", card)
      time.sleep(0.4)

      # やり取りありスキップ
      exchange = card.find_elements(By.CLASS_NAME, "exchange")
      if exchange:
        current_step += 1
        continue

      # 年齢チェック
      try:
        user_name = card.find_elements(By.CLASS_NAME, "name")[0].text
        user_age = card.find_elements(By.CLASS_NAME, "age")[0].text
        age_m = re.search(r'(\d+)', user_age)
        if age_m and int(age_m.group(1)) > 34:
          current_step += 1
          continue
      except Exception:
        current_step += 1
        continue

      # プロフィールを見る
      try:
        card.find_element(By.CLASS_NAME, "profile_link_btn").click()
        catch_warning_pop(name, driver)
      except Exception:
        current_step += 1
        continue

      # いいかも処理
      iikamo_text = ""
      if area_iikamo_count > 0:
        arleady_iikamo = driver.find_elements(By.CLASS_NAME, 'type5')
        iikamo = driver.find_elements(By.CLASS_NAME, 'type1')
        iikamo_arigatou = driver.find_elements(By.CLASS_NAME, 'type4')
        if len(arleady_iikamo):
          iikamo_text = "いいかも済み"
        elif len(iikamo):
          iikamo[0].click()
          wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
          time.sleep(0.7)
          area_iikamo_count -= 1
          iikamo_text = "いいかも"
        elif len(iikamo_arigatou):
          iikamo_arigatou[0].click()
          wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
          time.sleep(0.7)
          area_iikamo_count -= 1
          iikamo_text = "いいかもありがとう"

      footprint_now = datetime.now().strftime('%m/%d %H:%M:%S')
      ft_cnt += 1
      current_step += 1
      user_area = ""
      try:
        user_area = card.find_elements(By.CLASS_NAME, "conf")[0].text.replace("登録地域", "")
      except Exception:
        pass
      print(f"  {ft_cnt}件 {iikamo_text} {user_name}{user_age} {user_area} {footprint_now}")
      time.sleep(random_wait)

      # 検索結果ページに戻る
      if user_list_url not in driver.current_url:
        driver.get(user_list_url)
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        user_list = driver.find_elements(By.CLASS_NAME, "profile_card")

    print(f"{name} 新人足跡付け完了: {area} {ft_cnt}件")


def make_footprint_keyword(name, driver, footprint_count=5, iikamo_count=0):
  """プロフィール検索フォームで キーワード + 都道府県(東京+近隣からランダム3県=計4県)
  + 年齢(18〜34) + 送信歴無し を設定し、「この条件で検索する」で検索。
  結果に順に足跡付け（+いいかも）する。※サイト側の仕様で都道府県は最大4つ。"""
  wait = WebDriverWait(driver, 10)
  KEYWORDS = ["童貞", "未経験", "女性慣れ"]
  # 近隣県の pref[] value: 神奈川23, 埼玉24, 千葉25, 茨城19, 栃木20, 群馬21
  _NEARBY_PAIRS = [("23", "神奈川県"), ("24", "埼玉県"), ("25", "千葉県"),
                   ("19", "茨城県"), ("20", "栃木県"), ("21", "群馬県")]
  nearby_pick = random.sample(_NEARBY_PAIRS, 3)
  TARGET_PREF_VALUES = {"22"} | {v for v, _ in nearby_pick}
  TARGET_AREAS = {"東京都"} | {n for _, n in nearby_pick}
  AGE_MIN, AGE_MAX = 18, 34
  random_wait = random.uniform(3.4, 6.4)
  keyword = random.choice(KEYWORDS)
  print(f"{name} 対象地域: {sorted(TARGET_AREAS)} キーワード: {keyword}")

  catch_warning_pop(name, driver)

  # プロフィール検索フォームへ直接遷移
  if "linkleweb" in driver.current_url:
    driver.get("https://linkleweb.jp/mobile/profile_reference.php")
  else:
    driver.get("https://pcmax.jp/mobile/profile_reference.php")
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(1)

  # 都道府県チェック（東京+近隣6県のみ）
  for cb in driver.find_elements(By.CSS_SELECTOR, "input[name='pref[]']"):
    v = cb.get_attribute("value")
    want = v in TARGET_PREF_VALUES
    if cb.is_selected() != want:
      driver.execute_script("arguments[0].click();", cb)

  # 送信歴無しをチェック
  nt = driver.find_elements(By.CSS_SELECTOR, "input[name='no_transmit']")
  if nt and not nt[0].is_selected():
    driver.execute_script("arguments[0].click();", nt[0])

  # 年齢範囲
  try:
    Select(driver.find_element(By.NAME, "from_age")).select_by_visible_text(f"{AGE_MIN}歳")
    Select(driver.find_element(By.NAME, "to_age")).select_by_visible_text(f"{AGE_MAX}歳")
  except Exception as e:
    print(f"{name} 年齢設定エラー: {e}")

  # キーワードを phrase 入力欄に入力
  try:
    phrase = driver.find_element(By.CSS_SELECTOR, "input[name='phrase']")
    phrase.clear()
    phrase.send_keys(keyword)
  except Exception as e:
    print(f"{name} キーワード入力エラー: {e}")

  # 「この条件 で 検索 する」ボタンをクリック
  clicked = False
  for btn in driver.find_elements(By.TAG_NAME, "button"):
    if "条件" in btn.text and "検索" in btn.text:
      driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
      time.sleep(0.4)
      btn.click()
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(1.5)
      clicked = True
      break
  if not clicked:
    print(f"{name} ❌ 「この条件で検索する」ボタンが見つかりません")
    return

  user_list_url = driver.current_url
  user_list = driver.find_elements(By.CLASS_NAME, 'profile_card')
  if not user_list:
    print(f"{name} 検索結果が0件")
    return

  ft_cnt = 0
  current_step = 0

  while ft_cnt < footprint_count:
    if current_step >= len(user_list):
      driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(3)
      user_list = driver.find_elements(By.CLASS_NAME, 'profile_card')
      if current_step >= len(user_list):
        print(f"{name} 検索結果終端: 付け数={ft_cnt}")
        return
      continue

    card = user_list[current_step]
    try:
      driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
      time.sleep(0.4)

      if card.find_elements(By.CLASS_NAME, "exchange"):
        nm_els = card.find_elements(By.CLASS_NAME, "name")
        print(f"やり取り有り {nm_els[0].text if nm_els else ''}")
        current_step += 1
        continue

      name_els = card.find_elements(By.CLASS_NAME, "name")
      age_els = card.find_elements(By.CLASS_NAME, "age")
      conf_els = card.find_elements(By.CLASS_NAME, "conf")
      if not (name_els and age_els and conf_els):
        current_step += 1
        continue
      user_name = name_els[0].text
      user_age_text = age_els[0].text
      user_area_text = conf_els[0].text.replace("登録地域", "").strip()

      age_m = re.search(r'(\d+)', user_age_text)
      if age_m:
        age_n = int(age_m.group(1))
        if age_n < AGE_MIN or age_n > AGE_MAX:
          print(f"年齢スキップ {user_name} {user_age_text}")
          current_step += 1
          continue

      matched_area = next((a for a in TARGET_AREAS if a in user_area_text), None)
      if matched_area is None:
        print(f"地域スキップ {user_name} {user_area_text}")
        current_step += 1
        continue

      card.find_element(By.CLASS_NAME, "profile_link_btn").click()
      catch_warning_pop(name, driver)

      iikamo_text = ""
      if iikamo_count > 0:
        arleady_iikamo = driver.find_elements(By.CLASS_NAME, 'type5')
        iikamo = driver.find_elements(By.CLASS_NAME, 'type1')
        iikamo_arigatou = driver.find_elements(By.CLASS_NAME, 'type4')
        if arleady_iikamo:
          iikamo_text = "いいかも済み"
        elif iikamo:
          iikamo[0].click()
          wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
          time.sleep(0.7)
          iikamo_count -= 1
          iikamo_text = "いいかも"
        elif iikamo_arigatou:
          iikamo_arigatou[0].click()
          wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
          time.sleep(0.7)
          iikamo_count -= 1
          iikamo_text = "いいかもありがとう"

      now_str = datetime.now().strftime('%m/%d %H:%M:%S')
      current_step += 1
      ft_cnt += 1
      print(f"{ft_cnt}件 {iikamo_text} {user_name}{user_age_text} {user_area_text} {now_str}")
      time.sleep(random_wait)

      if user_list_url not in driver.current_url:
        driver.get(user_list_url)
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
      user_list = driver.find_elements(By.CLASS_NAME, 'profile_card')
    except Exception as e:
      print(f"{name} カード処理エラー: {e}")
      current_step += 1
      continue


def make_footprint_imahima(name, driver, footprint_count, iikamo_count=0):
  """いまヒマリストページで34歳以下のユーザーに足跡をつける"""
  import urllib.parse
  wait = WebDriverWait(driver, 15)

  def _go_to_city_page(pref_name):
    """basic_info_change → profile_reg?city=1 へ遷移"""
    driver.get("https://pcmax.jp/mobile/basic_info_change.php?area=1")
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    wait.until(EC.presence_of_element_located((By.NAME, "area_pref_no")))
    time.sleep(1)
    Select(driver.find_element(By.NAME, "area_pref_no")).select_by_visible_text(pref_name)
    time.sleep(0.5)
    driver.find_element(By.ID, "image_button2").click()
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    wait.until(EC.presence_of_element_located((By.ID, "prech")))
    time.sleep(2)

  def _select_city(city_sel_id, city_text):
    """都道府県変更後に詳細地域を選択（選択して下さいの場合はスキップ）"""
    if city_text == "選択して下さい":
      return
    try:
      city_sel = Select(driver.find_element(By.ID, city_sel_id))
      city_sel.select_by_visible_text(city_text)
      time.sleep(0.3)
    except Exception:
      pass

  def _read_activity_areas():
    """現在の活動地域3つを読み取って返す"""
    driver.get("https://pcmax.jp/mobile/basic_info_change.php?area=1")
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    wait.until(EC.presence_of_element_located((By.NAME, "area_pref_no")))
    time.sleep(1)
    pref1 = Select(driver.find_element(By.NAME, "area_pref_no")).first_selected_option.text
    _go_to_city_page(pref1)
    areas = {}
    for i, (pref_id, city_id) in enumerate([("prech","city_id_1"),("prech2","city_id_2"),("prech3","city_id_3")], 1):
      areas[f"pref{i}"] = Select(driver.find_element(By.ID, pref_id)).first_selected_option.text
      areas[f"city{i}"] = Select(driver.find_element(By.ID, city_id)).first_selected_option.text
    return areas

  def _set_activity_areas(areas):
    """保存したエリアデータで3つすべてを設定して送信"""
    _go_to_city_page(areas["pref1"])
    wait.until(EC.presence_of_element_located((By.ID, "prech")))
    # エリア1
    Select(driver.find_element(By.ID, "prech")).select_by_visible_text(areas["pref1"])
    time.sleep(1)
    _select_city("city_id_1", areas["city1"])
    # エリア2
    wait.until(EC.presence_of_element_located((By.ID, "prech2")))
    Select(driver.find_element(By.ID, "prech2")).select_by_visible_text(areas["pref2"])
    time.sleep(1)
    _select_city("city_id_2", areas["city2"])
    # エリア3
    wait.until(EC.presence_of_element_located((By.ID, "prech3")))
    Select(driver.find_element(By.ID, "prech3")).select_by_visible_text(areas["pref3"])
    time.sleep(1)
    _select_city("city_id_3", areas["city3"])
    driver.find_element(By.ID, "p_reg_btn").click()
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1)

  # 現在の活動地域を保存
  original_areas = None
  _area_pool    = ["東京都", "栃木県", "静岡県", "群馬県", "埼玉県", "千葉県", "神奈川県"]
  _area_weights = [28, 12, 12, 12, 12, 12, 12]
  chosen_area = random.choices(_area_pool, weights=_area_weights)[0]
  try:
    driver.get("https://pcmax.jp/mobile/basic_info_change.php?area=1")
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    original_areas = _read_activity_areas()
    print(f"{name} 活動地域保存: {original_areas}")
    # 新しい地域に変更（エリア1のみ、詳細なし）
    _go_to_city_page(chosen_area)
    Select(driver.find_element(By.ID, "prech")).select_by_visible_text(chosen_area)
    time.sleep(1)
    driver.find_element(By.ID, "p_reg_btn").click()
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    print(f"{name} 活動地域変更: {chosen_area}")
  except Exception as e:
    print(f"{name} 活動地域変更エラー: {e}")

  # 活動地域が正しく変更されたか確認
  try:
    current_areas = _read_activity_areas()
    current_pref = current_areas.get("pref1", "")
    if current_pref != chosen_area:
      print(f"{name} 活動地域変更が反映されていません: 期待={chosen_area}, 実際={current_pref} → 再設定")
      _go_to_city_page(chosen_area)
      Select(driver.find_element(By.ID, "prech")).select_by_visible_text(chosen_area)
      time.sleep(1)
      driver.find_element(By.ID, "p_reg_btn").click()
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
    else:
      print(f"{name} 活動地域確認OK: {current_pref}")
  except Exception as e:
    print(f"{name} 活動地域確認エラー: {e}")

  # TOPページへ移動してリンクを取得
  top_url = "https://pcmax.jp/pcm/index.php" if "pcmax" in driver.current_url else "https://linkleweb.jp/pcm/index.php"
  driver.get(top_url)
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  try:
    link = driver.find_element(By.CSS_SELECTOR, "a[href*='profile_reference.php?direct2=1&sort=3']")
    link.click()
  except Exception as e:
    print(f"{name} いまヒマリンクエラー: {e}")
    # 活動地域を復元してからreturn
    if original_areas:
      try:
        _set_activity_areas(original_areas)
        print(f"{name} 活動地域復元: {original_areas}")
      except Exception as e2:
        print(f"{name} 活動地域復元エラー: {e2}")
    return 0
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(1)

  list_url = driver.current_url
  visited_ids = set()
  ft_cnt = 0
  encoded_memo = urllib.parse.quote("いまヒマリスト", encoding='shift_jis')

  while ft_cnt < footprint_count:
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='profile_detail']")
    targets = []
    for lnk in links:
      href = lnk.get_attribute("href") or ""
      uid_m = re.search(r'user_id=(\d+)', href)
      if not uid_m:
        continue
      uid = uid_m.group(1)
      if uid in visited_ids:
        continue
      link_text = lnk.text
      age_m = re.search(r'(\d+)歳', link_text)
      if not age_m:
        continue
      age = int(age_m.group(1))
      if age > 34:
        visited_ids.add(uid)
        continue
      targets.append((uid, href, age, link_text))

    if not targets:
      # 次ページボタン（▶三角）をクリック
      driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
      time.sleep(1)
      # 現在のページ番号を取得して次ページリンクを探す
      import re as _re
      current_page_m = _re.search(r'[?&]page=(\d+)', driver.current_url)
      current_page = int(current_page_m.group(1)) if current_page_m else 1
      next_page = current_page + 1
      next_btn = driver.find_elements(By.CSS_SELECTOR, f"a[href*='page={next_page}']")
      if next_btn:
        print(f"{name} 次ページへ移動 (page {next_page})")
        next_btn[0].click()
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        list_url = driver.current_url
        continue
      print(f"{name} いまヒマ足跡付け終了（対象ユーザーなし・次ページなし） {ft_cnt}件")
      break

    for uid, href, age, link_text in targets:
      if ft_cnt >= footprint_count:
        break
      visited_ids.add(uid)
      driver.get(href)
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(random.uniform(0.8, 2.0))
      # いいかも処理
      iikamo_text = ""
      if iikamo_count > 0:
        arleady_iikamo = driver.find_elements(By.CLASS_NAME, 'type5')
        iikamo = driver.find_elements(By.CLASS_NAME, 'type1')
        iikamo_arigatou = driver.find_elements(By.CLASS_NAME, 'type4')
        if arleady_iikamo:
          iikamo_text = "いいかも済み"
        elif iikamo:
          iikamo[0].click()
          wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
          time.sleep(0.7)
          iikamo_count -= 1
          iikamo_text = "いいかも"
        elif iikamo_arigatou:
          iikamo_arigatou[0].click()
          wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
          time.sleep(0.7)
          iikamo_count -= 1
          iikamo_text = "いいかもありがとう"
      # メモ確認：いまヒマリスト済みならスキップ
      try:
        memo_edit = driver.find_elements(By.CLASS_NAME, 'memo_edit')
        if memo_edit and "いまヒマリスト" in memo_edit[0].text:
          display_name = re.sub(r'\s*\d+歳.*', '', link_text.split('\n')[0])[:12]
          print(f"{name} スキップ（いまヒマリスト済み） {display_name} {age}歳")
          driver.get(list_url)
          wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
          continue
      except Exception as e:
        print(f"{name} メモ確認エラー: {e}")
      # メモ登録
      try:
        driver.execute_script(
          f"$.get('https://pcmax.jp/mobile/memo_reg.php?memo_user_id={uid}&memo={encoded_memo}&regist=1');"
        )
        time.sleep(0.5)
      except Exception as e:
        print(f"{name} メモ登録エラー: {e}")
      ft_cnt += 1
      display_name = re.sub(r'\s*\d+歳.*', '', link_text.split('\n')[0])[:12]
      print(f"{name} いまヒマ足跡 {ft_cnt}件 {display_name} {age}歳 {datetime.now().strftime('%m/%d %H:%M:%S')}")
      driver.get(list_url)
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(1)

  # 活動地域を元に戻す
  if original_areas:
    try:
      _set_activity_areas(original_areas)
      print(f"{name} 活動地域復元: {original_areas}")
      # 復元後に確認
      restored = _read_activity_areas()
      if restored.get("pref1") != original_areas.get("pref1"):
        print(f"{name} 活動地域復元失敗: 期待={original_areas.get('pref1')}, 実際={restored.get('pref1')} → 再試行")
        _set_activity_areas(original_areas)
        print(f"{name} 活動地域再復元完了")
      else:
        print(f"{name} 活動地域復元確認OK: {restored.get('pref1')}")
      original_areas = None
    except Exception as e:
      print(f"{name} 活動地域復元エラー: {e}")

  return ft_cnt


def pcmax_profile_edit(chara_data, driver, wait):
  """
  PCMAXのプロフィールを編集する関数
  1. profile_reg.php でプロフィール情報を入力して送信
  2. basic_info_change.php?name=1 でニックネームを修正
  3. basic_info_change.php?work=1 で職業を修正
  """
  name = chara_data['name']

  def set_select_by_name(field_name, value):
    try:
      el = driver.find_element(By.NAME, field_name)
      sel = Select(el)
      sel.select_by_visible_text(str(value))
      print(f'  {field_name} = {value} ✓')
    except Exception as e:
      print(f'  {field_name} = {value} ✗ ({e})')

  # 1. プロフィール編集ページへ移動
  driver.get('https://pcmax.jp/mobile/profile_reg.php')
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(2)

  # 2. フォームに入力
  set_select_by_name('height', chara_data['height'])
  set_select_by_name('body_type', chara_data['body_shape'])
  set_select_by_name('taste', chara_data['car_ownership'])
  set_select_by_name('smoke', chara_data['smoking'])
  set_select_by_name('spare_time', chara_data['freetime'])
  set_select_by_name('dirty_minded', chara_data['ecchiness_level'])
  set_select_by_name('drinking', chara_data['sake'])
  set_select_by_name('dating_process', chara_data['process_before_meeting'])
  set_select_by_name('dating_payment', chara_data['first_date_cost'])
  set_select_by_name('dating_travel', chara_data['travel'])
  set_select_by_name('birth_pref_no', chara_data['birth_place'])
  set_select_by_name('academic_background', chara_data['education'])
  set_select_by_name('housemate', chara_data['roommate'])
  set_select_by_name('marriage', chara_data['marry'])
  set_select_by_name('children', chara_data['child'])
  set_select_by_name('housework', chara_data['housework'])
  set_select_by_name('sociality', chara_data['sociability'])

  # 自己PR（絵文字などBMP外文字対応のためJSで直接set）
  try:
    el = driver.find_element(By.NAME, 'self_pr')
    driver.execute_script(
      "arguments[0].value = '';"
      "arguments[0].value = arguments[1];"
      "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
      "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
      el, chara_data['self_promotion']
    )
    print('  self_pr 入力完了 ✓')
  except Exception as e:
    print(f'  self_pr ✗ ({e})')

  # 活動エリア（都道府県）→ 活動エリア詳細（市区町村）
  # name属性なしのselectが活動エリア・活動エリア詳細
  try:
    selects = driver.find_elements(By.TAG_NAME, 'select')
    nameless = [s for s in selects if not (s.get_attribute('name') or '').strip()]
    if chara_data.get('activity_area') and len(nameless) >= 1:
      Select(nameless[0]).select_by_visible_text(chara_data['activity_area'])
      time.sleep(1)
      # 詳細selectの中身がAjaxで更新される可能性があるため取り直し
      selects = driver.find_elements(By.TAG_NAME, 'select')
      nameless = [s for s in selects if not (s.get_attribute('name') or '').strip()]
      print(f'  活動エリア = {chara_data["activity_area"]} ✓')
    if chara_data.get('detail_activity_area') and len(nameless) >= 2:
      Select(nameless[1]).select_by_visible_text(chara_data['detail_activity_area'])
      print(f'  活動エリア詳細 = {chara_data["detail_activity_area"]} ✓')
  except Exception as e:
    print(f'  活動エリア詳細 ✗ ({e})')

  time.sleep(1)

  # 3. 次へボタンをクリックして送信
  btn = driver.find_element(By.XPATH, "//*[contains(text(), '次へ')]")
  btn.click()
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  print(f'プロフィール編集送信完了: {driver.current_url}')

  # 4. ニックネームを修正
  driver.get('https://pcmax.jp/mobile/basic_info_change.php?name=1')
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  for inp in driver.find_elements(By.TAG_NAME, 'input'):
    if inp.get_attribute('type') in ('text', '') and inp.is_displayed():
      inp.clear()
      inp.send_keys(name)
      print(f'  ニックネーム = {name} ✓')
      break
  driver.execute_script("arguments[0].click()", driver.find_element(By.ID, 'image_button2'))
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  print(f'ニックネーム変更完了: {driver.current_url}')

  # 5. 職業を修正
  driver.get('https://pcmax.jp/mobile/basic_info_change.php?work=1')
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  try:
    sel_el = driver.find_element(By.XPATH, "//select[@name='occupation']")
    Select(sel_el).select_by_visible_text(chara_data['profession'])
    print(f'  職業 = {chara_data["profession"]} ✓')
  except Exception as e:
    print(f'  職業 ✗ ({e})')
  time.sleep(1)
  driver.execute_script("arguments[0].click()", driver.find_element(By.ID, 'image_button2'))
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  print(f'職業変更完了: {driver.current_url}')

  # 6. 血液型を修正
  driver.get('https://pcmax.jp/mobile/basic_info_change.php?blood=1')
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  try:
    sel_el = driver.find_element(By.XPATH, "//select[@name='blood_type']")
    Select(sel_el).select_by_visible_text(chara_data['blood_type'])
    print(f'  血液型 = {chara_data["blood_type"]} ✓')
  except Exception as e:
    print(f'  血液型 ✗ ({e})')
  time.sleep(1)
  driver.execute_script("arguments[0].click()", driver.find_element(By.ID, 'image_button2'))
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  print(f'血液型変更完了: {driver.current_url}')

  print(f'\n{name} のプロフィール編集がすべて完了しました')


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




genre_dic = {0:"スグ会いたい", 1:"スグじゃないけど"}
post_area_tokyo = ["千代田区", "中央区", "港区", "新宿区", "文京区", "台東区",
                   "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区",
                   "杉並区", "豊島区", "北区", "荒川区", "板橋区", "練馬区",
                    "武蔵野市",  
                   ]
post_area_kanagawa = ["横浜市鶴見区", "横浜市神奈川区", "横浜市西区", "横浜市中区", "横浜市南区", "横浜市保土ｹ谷区", 
                      "横浜市磯子区", "横浜市金沢区", "横浜市港北区", "横浜市戸塚区", "横浜市港南区", "横浜市旭区",
                      "横浜市緑区", "横浜市瀬谷区", "横浜市栄区", "横浜市泉区", "横浜市青葉区", "横浜市都筑区", 
                      "川崎市川崎区", "川崎市幸区", "川崎市中原区", "川崎市高津区", "川崎市多摩区", "川崎市宮前区", 
                      "川崎市麻生区",]
post_area_saitama = ["さいたま市西区", "さいたま市北区", "さいたま市大宮区", "さいたま市見沼区", "さいたま市中央区",
                      "さいたま市桜区", "さいたま市浦和区", "さいたま市南区", "さいたま市緑区", "さいたま市岩槻区",
                      "川口市", "戸田市", "和光市",]
post_area_chiba = ["千葉市中央区", "千葉市花見川区", "千葉市稲毛区", "千葉市若葉区",
                    "千葉市緑区", "千葉市美浜区", "市川市", "船橋市",]

post_area_dic = {"東京都":post_area_tokyo, "神奈川県":post_area_kanagawa, "埼玉県":post_area_saitama, "千葉県":post_area_chiba}
# detail_post_area_list = [post_area_tokyo, post_area_kanagawa, post_area_saitama, post_area_chiba]

def catch_warning_pop(name, driver, wait):
  warning = driver.find_elements(By.CLASS_NAME, value="caution-title")
  warning2 = driver.find_elements(By.CLASS_NAME, value="suspend-title")
  warning3 = driver.find_elements(By.CLASS_NAME, value="mail-setting-title")
  number_lock = driver.find_elements(By.ID, value="content_header2")
  if len(warning) or len(warning2) or len(warning3) or len(number_lock):
    kiyaku_btn = driver.find_elements(By.CLASS_NAME, value="kiyaku-btn")
    if len(kiyaku_btn):
      kiyaku_btn_text = kiyaku_btn[0].text    
      if kiyaku_btn_text == "上記を了承する":
        driver.execute_script("arguments[0].click();", kiyaku_btn[0])
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(3)
        # 番号ロック確認　setting-title mail-setting-title
        number_lock_elem = driver.find_elements(By.CLASS_NAME, value="setting-title")
        number_lock_elem2 = driver.find_elements(By.CLASS_NAME, value="mail-setting-title")
        if len(number_lock_elem):
          print(number_lock_elem[0].text)
          if "電話番号確認" in number_lock_elem[0].text:
            print(f"{name}に番号ロック画面が出ている可能性があります")
            return f"{name}に番号ロック画面が出ている可能性があります"
        if len(number_lock_elem2):
          print(number_lock_elem2[0].text)
          if "電話番号確認" in number_lock_elem2[0].text:
            print(f"{name}に番号ロック画面が出ている可能性があります")
            return f"{name}に番号ロック画面が出ている可能性があります"
        return None
    else:
      print(f"{name}に警告画面が出ている可能性があります")
      return f"{name}に警告画面が出ている可能性があります"


def login(name, login_id, login_pass, driver, wait):
  driver.delete_all_cookies()
  driver.get("https://pcmax.jp/pcm/file.php?f=login_form")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  wait_time = random.uniform(2, 5)
  time.sleep(2)
  id_form = driver.find_element(By.ID, value="login_id")
  id_form.send_keys(login_id)
  pass_form = driver.find_element(By.ID, value="login_pw")
  pass_form.send_keys(login_pass)
  time.sleep(1)
  send_form = driver.find_element(By.NAME, value="login")
  try:
    send_form.click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
  except TimeoutException as e:
    print("TimeoutException")
    driver.refresh()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    id_form = driver.find_element(By.ID, value="login_id")
    id_form.send_keys(login_id)
    pass_form = driver.find_element(By.ID, value="login_pw")
    pass_form.send_keys(login_pass)
    time.sleep(1)
    send_form = driver.find_element(By.NAME, value="login")
    send_form.click()
  # 利用制限中
  suspend = driver.find_elements(By.CLASS_NAME, value="suspend-title")
  if len(suspend):
    print(f"{name}pcmax利用制限中です")
    return False
  return True
  
def nav_item_click(name, nav_item, driver, wait):
  nav_list = driver.find_elements(By.ID, value='sp-floating')
  if not len(nav_list):
    nav_list = driver.find_elements(By.ID, value='sp_footer')
    if not len(nav_list):
      print(f"{name}ナビゲーターリストが見つかりません")
      return
  nav_text_elems = nav_list[0].find_elements(By.TAG_NAME, value='a')
  for nav_text_elem in nav_text_elems:
    if nav_item in nav_text_elem.text:
      if nav_item == "メッセージ":
        new_icon = nav_text_elem.find_elements(By.CLASS_NAME, value="badge1")
        if len(new_icon):
          driver.execute_script("arguments[0].click();", nav_text_elem)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
          
          return "new_message"
      driver.execute_script("arguments[0].click();", nav_text_elem)
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      return None

def re_login(driver, wait):
  login = None  # login変数の初期化
  try:
    try:
      driver.refresh()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
    except TimeoutException as e:
      print("<<<<<<<リロード>>>>>>>>>>")
      driver.refresh()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
    url = driver.current_url
    if url != "https://pcmax.jp/pcm/index.php":
      driver.get("https://pcmax.jp/pcm/index.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    # 利用制限中
    suspend = driver.find_elements(By.CLASS_NAME, value="suspend-title")
    if len(suspend):
      print('利用制限中です')
      return 
    login = driver.find_elements(By.CLASS_NAME, value="login")
    if len(login):    
      login[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      submit = driver.find_element(By.NAME, value="login")
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", submit)
      submit.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
  except TimeoutException as e:
    print("TimeoutException")
    driver.refresh()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    return re_login(driver, wait)
  
    
def re_post(pcmax_chara_dict, driver, wait, detail_area_flug):
  name = pcmax_chara_dict["name"]
  login_id = pcmax_chara_dict["login_id"]
  login_pass = pcmax_chara_dict["password"]
  post_title = pcmax_chara_dict["post_title"]
  post_contents = pcmax_chara_dict["post_content"]
  driver.delete_all_cookies()
  driver.get("https://pcmax.jp/pcm/file.php?f=login_form")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  wait_time = random.uniform(3, 6)
  time.sleep(2)
  id_form = driver.find_element(By.ID, value="login_id")
  id_form.send_keys(login_id)
  pass_form = driver.find_element(By.ID, value="login_pw")
  pass_form.send_keys(login_pass)
  time.sleep(1)
  send_form = driver.find_element(By.NAME, value="login")
  try:
    send_form.click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
  except TimeoutException as e:
    print("TimeoutException")
    driver.refresh()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    id_form = driver.find_element(By.ID, value="login_id")
    id_form.send_keys(login_id)
    pass_form = driver.find_element(By.ID, value="login_pw")
    pass_form.send_keys(login_pass)
    time.sleep(1)
    send_form = driver.find_element(By.NAME, value="login")
    send_form.click()
  # 利用制限中
  suspend = driver.find_elements(By.CLASS_NAME, value="suspend-title")
  if len(suspend):
    print(f"{pcmax_chara_dict['name']}pcmax利用制限中です")
    return  
  wait_time = random.uniform(3, 4)
  re_login(driver, wait)
  # MENUをクリック
  # menu = driver.find_elements(By.ID, value='sp_nav')
  # if not len(menu):
  menu = driver.find_elements(By.ID, value='nav-open')
  menu[0].click()
  time.sleep(wait_time)
  # 掲示板履歴をクリック　
  bulletin_board_history = driver.find_element(By.CLASS_NAME, value="nav-content-list")
  bulletin_board_history = bulletin_board_history.find_elements(By.TAG_NAME, value="dd")
  
  for i in bulletin_board_history:
    if i.text == "投稿履歴・編集":
      bulletin_board_history = i.find_element(By.TAG_NAME, value="a")
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", bulletin_board_history)
      bulletin_board_history.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
      break
  # 掲示板履歴なし
  no_post = driver.find_elements(By.CLASS_NAME, value="write_text")
  if len(no_post):
    if no_post[0].text == "まだ掲示板への投稿はありません。":
      print(f"{name} まだ掲示板への投稿はありません。")
      return
      # print(no_post[0].text)
      # add_post = driver.find_elements(By.CLASS_NAME, value="white_last")
      # add_post_button = add_post[0].find_elements(By.TAG_NAME, value="a")
      # add_post_button[0].click()
      # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      # time.sleep(wait_time)
      # if genre_flag == 0:
      #     choices = driver.find_elements(By.CLASS_NAME, value="choice")
      #     for choice in choices:
      #       candidate_choice = choice.get_attribute('href')
      #       if candidate_choice is not None:
      #           if choice.text == "スグ会いたい":
      #             add_post_link = candidate_choice
      #       else:
      #           continue
      # driver.get(add_post_link)
      # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      # time.sleep(wait_time) 
      # for kanto_region, kanto_area in post_area_dic.items():
      #   # # アダルトを選択
      #   adult = driver.find_element(By.ID, value="genre2")
      #   adult.click()
      #   title = driver.find_element(By.ID, value="title1") 
      #   title.send_keys(post_title)
      #   time.sleep(1)
      #   post_text = driver.find_element(By.ID, value="textarea1") 
      #   post_text.send_keys(post_contents)
      #   time.sleep(1)
      #   # 投稿地域を選択
      #   area = driver.find_element(By.ID, "prech")
      #   driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", area)
      #   time.sleep(1)
      #   select = Select(area)
      #   select.select_by_visible_text(kanto_region)
      #   time.sleep(1)
      #   # 詳細地域を選択
      #   detailed_area = driver.find_element(By.NAME, value="city_id")
      #   select = Select(detailed_area)
      #   detail_area = random.choice(kanto_area)
      #   print('今回の詳細地域 ~' + str(detail_area) + "~")
      #   select.select_by_visible_text(detail_area)
      #   time.sleep(1)
      #   # メール受付数を変更
      #   mail_reception = driver.find_element(By.NAME, "max_reception_count")
      #   select = Select(mail_reception)
      #   select.select_by_visible_text("5通")
      #   time.sleep(1)
      #   # チェック項目にチェック
      #   today_check = driver.find_element(By.ID, value="bty_4")
      #   today_check.click()
      #   ask_date = driver.find_element(By.ID, value="bty_5")
      #   ask_date.click()
      #   check3 = driver.find_element(By.ID, value="bty_6")
      #   check3.click()
      #   check4 = driver.find_element(By.ID, value="bty_7")
      #   check4.click()
      #   check5 = driver.find_element(By.ID, value="bty_8")
      #   check5.click()
      #   check6 = driver.find_element(By.ID, value="bty_9")
      #   check6.click()
      #   # 掲示板に書く 
      #   write_bulletin_board = driver.find_element(By.ID, value="bbs_write_btn")
      #   driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", write_bulletin_board)
      #   write_bulletin_board.click()
      #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      #   time.sleep(wait_time)
      #   # 利用制限チェック
      #   usage_limit = driver.find_elements(By.CLASS_NAME, value="white_box")
      #   if len(usage_limit):
      #     print(f"{name}pcmax利用制限画面が出ました")
      #     break
      #   # https://pcmax.jp/pcm/index.php
      #   driver.get("https://pcmax.jp/pcm/index.php")
        # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        # time.sleep(wait_time)
        
        # # MENUをクリック
        # menu = driver.find_element(By.ID, value='sp_nav')
        # menu.click()
        # time.sleep(wait_time)
        # # 掲示板書き込みをクリック　
        # bulletin_board_history = driver.find_element(By.CLASS_NAME, value="nav-content-list")
        # bulletin_board_history = bulletin_board_history.find_elements(By.TAG_NAME, value="dd")
        # for i in bulletin_board_history:
        #   if i.text == "掲示板書込み":
        #     bulletin_board_history = i.find_element(By.TAG_NAME, value="a")
        #     driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", bulletin_board_history)
        #     bulletin_board_history.click()
        #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        #     time.sleep(wait_time)
        #     break
      
  #掲示板4つ再投稿
  link_list = []
  posts = driver.find_elements(By.CLASS_NAME, value="bbs_posted_wrap")
  
  if not len(posts):
    return
  skip_cnt = 0
  repost_cnt = 0
  while len(posts):
    if skip_cnt >= len(posts):
      break
    reposted_time_element = posts[skip_cnt].find_elements(By.CLASS_NAME, value="posted-time")
    reposted_time = reposted_time_element[0].text
    reposted_time_obj = datetime.strptime(reposted_time, "%Y/%m/%d %H:%M")
    now = datetime.now()
    # 2時間後と比較
    if now >= reposted_time_obj + timedelta(minutes=10):
      print("10分以上経過しています。")
      copy_button = posts[skip_cnt].find_elements(By.TAG_NAME, value="button")
      copy_button[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
      detail_selected = driver.find_elements(By.CLASS_NAME, value="back_in_box")
      detail_selected = detail_selected[2].find_element(By.CLASS_NAME, value="item_r")
      detail_selected = detail_selected.text.replace(' ', '')
      
      # 前回の都道府県を取得
      last_area = driver.find_elements(By.CLASS_NAME, value="back_in_box")
      last_area = last_area[1].find_element(By.CLASS_NAME, value="item_r")
      last_area = last_area.text.replace(' ', '')
      print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
      print(last_area)
      print("前回の詳細地域 ~" + str(detail_selected) + "~" )
      # 編集するをクリック 
      edit_post = driver.find_element(By.ID, value="alink")
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", edit_post)
      time.sleep(1)
      edit_post.click()
      wait = WebDriverWait(driver, 15)
      time.sleep(wait_time)
      # ジャンルを選択
      # select_genre = driver.find_element(By.ID, value="selectb")
      # select = Select(select_genre)
      # select.select_by_visible_text(genre_dic[genre_flag])
      time.sleep(1)

      # 投稿地域を選択
      area = driver.find_element(By.ID, "prech")
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", area)
      time.sleep(1)
      select = Select(area)
      select.select_by_visible_text(last_area)
      time.sleep(1)
      print(detail_area_flug)
      if detail_area_flug == "same":
        # 詳細地域を選択
        detailed_area = driver.find_element(By.NAME, value="city_id")
        select = Select(detailed_area)
        
        print('今回の詳細地域 ~' + str(detail_selected) + "~")
        select.select_by_visible_text(detail_selected)
        time.sleep(1)
      else:
        # 詳細地域を選択
        detailed_area = driver.find_element(By.NAME, value="city_id")
        select = Select(detailed_area)
        if last_area in post_area_dic:
          try:
            post_area_dic[last_area].remove(detail_selected)
          except Exception:
            pass
          print(f"🔍 last_area: {last_area}")  # 追加: `last_area` を確認
          print(f"📌 post_area_dic keys: {list(post_area_dic.keys())}")  # 追加: `post_area_dic` のキーを確認
          detail_area = random.choice(post_area_dic[last_area])
        else:
          detail_area = str(detail_selected)
        print('今回の詳細地域 ~' + str(detail_area) + "~")
        select.select_by_visible_text(detail_area)
        time.sleep(1)
      # メール受付数を変更
      mail_reception = driver.find_element(By.NAME, "max_reception_count")
      select = Select(mail_reception)
      select.select_by_visible_text("5通")
      time.sleep(1)
      # 掲示板に書く 
      write_bulletin_board = driver.find_element(By.ID, value="bbs_write_btn")
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", write_bulletin_board)
      write_bulletin_board.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)

      # 利用制限チェック
      usage_limit = driver.find_elements(By.CLASS_NAME, value="white_box")
      if len(usage_limit):
        print(f"{name}pcmax利用制限画面が出ました")
        top_logo = driver.find_elements(By.ID, value="top")
        a = top_logo[0].find_element(By.TAG_NAME, value="a")
        a.click()
        time.sleep(wait_time)
        # MENUをクリック
        menu = driver.find_element(By.ID, value='sp_nav')
        menu.click()
        time.sleep(wait_time)
        # 掲示板履歴をクリック　
        bulletin_board_history = driver.find_element(By.CLASS_NAME, value="nav-content-list")
        bulletin_board_history = bulletin_board_history.find_elements(By.TAG_NAME, value="dd")
        for i in bulletin_board_history:
          if i.text == "投稿履歴・編集":
            bulletin_board_history = i.find_element(By.TAG_NAME, value="a")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", bulletin_board_history)
            bulletin_board_history.click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(wait_time)
            break
        #掲示板4つ再投稿
        link_list = []
        posts = driver.find_elements(By.CLASS_NAME, value="copy_title")
        if not len(posts):
          return
        for i in range(len(posts)):
          copy = posts[i].find_elements(By.TAG_NAME, value="a")
          for a_element in copy:
            link_text = a_element.text
            if link_text == "コピーする":
              link = a_element.get_attribute("href")
              link_list.append(link)
        
        for i in link_list:
          try:
            driver.get(i)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(wait_time)
          except TimeoutException as e:
            print("TimeoutException")
            driver.refresh()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(wait_time)
          submit = driver.find_element(By.CLASS_NAME, value="write_btn")
          submit.click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(wait_time)   
          repost_cnt += 1
        return
      else:
        repost_cnt += 1
      now = datetime.now().strftime('%m-%d %H:%M:%S')
      print(f"{name} 再投稿{repost_cnt}件 {last_area}:{detail_area}  time:{now}")
        
      # 掲示板投稿履歴をクリック
      bulletin_board_history = driver.find_element(By.XPATH, value="//*[@id='wrap']/div[2]/table/tbody/tr/td[3]/a")
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", bulletin_board_history)
      bulletin_board_history.click()
      time.sleep(1)
      posts = driver.find_elements(By.CLASS_NAME, value="bbs_posted_wrap")
      
    else:
        print("まだ10分経過していません。")
        skip_cnt += 1
        if skip_cnt > 3:
          break
    
  driver.get("https://pcmax.jp/pcm/index.php")
  
def return_footpoint(name, pcmax_windowhandle, driver, return_foot_message, cnt, return_foot_img):
  if cnt == 0:
    return
  wait = WebDriverWait(driver, 15)
  driver.switch_to.window(pcmax_windowhandle)
  wait_time = random.uniform(2, 3)
  time.sleep(1)
  re_login(driver, wait)
  # 新着メッセージの確認
  have_new_massage_users = []
  new_message = driver.find_element(By.CLASS_NAME, value="message")
  new_message.click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  user_info = driver.find_elements(By.CLASS_NAME, value="user_info")
  print(len(user_info))
  # 新着ありのユーザーをリストに追加
  for usr_info in user_info:
    unread = usr_info.find_elements(By.CLASS_NAME, value="unread1")
    if len(unread):
      name = usr_info.find_element(By.CLASS_NAME, value="name").text
      if len(name) > 7:
        name = name[:7] + "…"
      have_new_massage_users.append(name)
  print("新着メッセージリスト")
  print(have_new_massage_users)
  driver.get("https://pcmax.jp/pcm/index.php")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  # 右下のキャラ画像をクリック
  chara_img = driver.find_element(By.XPATH, value="//*[@id='sp_footer']/a[5]")
  chara_img.click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  # //*[@id="contents"]/div[2]/div[2]/ul/li[5]/a
  # 足あとをクリック
  footpoint = driver.find_element(By.XPATH, value="//*[@id='contents']/div[2]/div[2]/ul/li[5]/a")
  footpoint.click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  # ページの高さを取得
  last_height = driver.execute_script("return document.body.scrollHeight")
  while True:
    # ページの最後までスクロール
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # ページが完全に読み込まれるまで待機
    time.sleep(1)
    # 新しい高さを取得
    new_height = driver.execute_script("return document.body.scrollHeight")
    # ページの高さが変わらなければ、すべての要素が読み込まれたことを意味する
    if new_height == last_height:
        break
    last_height = new_height
  # ユーザーを取得
  user_list = driver.find_element(By.CLASS_NAME, value="list-content")
  div = user_list.find_elements(By.XPATH, value='./div')
  # リンクを取得
  user_cnt = 1
  mail_history = 0
  send_count = 0
  link_list = []
  while user_cnt <= 40:
    # 新着リストの名前ならスキップ
    name = div[user_cnt].find_element(By.CLASS_NAME, value="user-name")
    if name.text in have_new_massage_users:
      user_cnt += 1
    else:
      a_tags = div[user_cnt].find_elements(By.TAG_NAME, value="a")
      # print("aタグの数：" + str(len(a_tags)))
      if len(a_tags) > 1:
        link = a_tags[1].get_attribute("href")
        # print(link)
        link_list.append(link)
      user_cnt += 1
  for i in link_list:
    if mail_history == 7:
      break
    driver.get(i)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

    # タイプありがとう
    like_return = driver.find_elements(By.CLASS_NAME, value="tbtn2")
    if len(like_return):
      like_return[0].click()
      time.sleep(2)
    sent = driver.find_elements(By.XPATH, value="//*[@id='profile-box']/div/div[2]/p/a/span")
    if len(sent):
      print('送信履歴があります')
      time.sleep(2)
      mail_history += 1
      continue  
    # 自己紹介文をチェック
    self_introduction = driver.find_elements(By.XPATH, value="/html/body/main/div[4]/div/p")
    if len(self_introduction):
      self_introduction = self_introduction[0].text.replace(" ", "").replace("\n", "")
      if '通報' in self_introduction or '業者' in self_introduction:
        print('自己紹介文に危険なワードが含まれていました')
        refusal_elems = driver.find_elements(By.CLASS_NAME, value="flex_btn_container")
        for candidate_elem in refusal_elems:
          if "お断り" in candidate_elem.text:
            refusal_elem = candidate_elem
            refusal_elem.click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(wait_time)
        continue
    # 残ポイントチェック
    point = driver.find_elements(By.ID, value="point")
    if len(point):
      point = point[0].find_element(By.TAG_NAME, value="span").text
      pattern = r'\d+'
      match = re.findall(pattern, point)
      if int(match[0]) > 1:
        maji_soushin = True
      else:
        maji_soushin = False
    else:
      time.sleep(wait_time)
      continue
    time.sleep(1)
    # メッセージをクリック
    message = driver.find_elements(By.ID, value="message1")
    if len(message):
      message[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(3)
    else:
      continue
    # 画像があれば送付
    if return_foot_img:
      picture_icon = driver.find_elements(By.CLASS_NAME, value="mail-menu-title")
      picture_icon[0].click()
      time.sleep(1)
      picture_select = driver.find_element(By.ID, "my_photo")
      select = Select(picture_select)
      select.select_by_visible_text(return_foot_img)
      
    # メッセージを入力
    text_area = driver.find_element(By.ID, value="mdc")
    text_area.send_keys(return_foot_message)
    time.sleep(4)
    print("マジ送信 " + str(maji_soushin) + " ~" + str(send_count + 1) + "~")
    # メッセージを送信
    if maji_soushin:
      send = driver.find_element(By.CLASS_NAME, value="maji_send")
      send.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      send_link = driver.find_element(By.ID, value="link_OK")
      send_link.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
      send_count += 1
      mail_history = 0
      
    else:
      send = driver.find_element(By.ID, value="send_n")
      send.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
      send_count += 1
      mail_history = 0

    if send_count == cnt:
      break
  driver.get("https://pcmax.jp/pcm/index.php")

def make_footprints(chara_data, driver, wait, select_areas, youngest_age, oldest_age, foot_cnt):
  name = chara_data["name"]
  login_id = chara_data["login_id"]
  login_pass = chara_data["password"]
  wait_time = random.uniform(3, 6)
  login_flug = login(name, login_id, login_pass, driver, wait)
  if not login_flug:
    return
  warning_flug = catch_warning_pop(name, driver, wait)
  if warning_flug:
    return
  nav_item_click(name, "プロフ検索", driver, wait)
  # 検索条件を設定
  search_elem = driver.find_element(By.ID, value="search1")
  search_elem.click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  # /////////////////////////詳細検索画面/////////////////////////
  select_area = driver.find_elements(By.CLASS_NAME, value="pref-select-link")
  reset_area = driver.find_elements(By.CLASS_NAME, value="reference_btn")
  user_sort_list = [
    "ログイン順",
    # "登録順", 
    # "自己PR更新順"
  ]
  if not len(select_area) and not len(reset_area):
    print(f"{chara_data['name']}利用制限あり")
    
    # # 地域選択
    # if len(select_areas) == 1:
    #   select_area = driver.find_elements(By.NAME, value="pref_no")
    #   select = Select(select_area[0])
    #   select.select_by_visible_text(select_areas[0])
    # elif len(select_areas) > 1:
    #   # 選択確率の重みを設定
    #   weights = [0.2, 0.2, 0.6]  # 東京都は60%、千葉県と埼玉県は20%ずつの確率
    #   selected_area = random.choices(select_areas, weights=weights)[0]
    #   print(f"決定地域:{selected_area}")
    #   select_area = driver.find_elements(By.NAME, value="pref_no")
    #   select = Select(select_area[0])
    #   select.select_by_visible_text(selected_area)
    #   time.sleep(1)
    # # 年齢
    # oldest_age_element = driver.find_elements(By.ID, value="makerItem")
    # select = Select(oldest_age_element[0])
    # oldest = str(oldest_age) + "歳"
    # print(oldest)
    # select.select_by_visible_text(oldest)
    # time.sleep(1)
    # # 上記の条件で検索するボタン送信
    # filtered_send = driver.find_elements(By.NAME, value="send")
    # filtered_send[0].click()
    # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    # time.sleep(wait_time) 
  else:
    print(f"{chara_data['name']}利用制限なし")
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
        str_youngest_age = str(youngest_age) + "歳"
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
        str_oldest_age = str(oldest_age) + "歳"
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
    # ユーザーリスト並び替え設定
    user_sort = driver.find_element(By.ID, "sort2")
    if user_sort.tag_name == "select":
      select = Select(user_sort)
      select.select_by_visible_text(user_sort_list[0])
    if user_sort.tag_name == "div":
      sort_login = driver.find_elements(By.ID, "sort-login")
      sort_login[0].click()

  time.sleep(1)
  # ユーザーを取得
  user_list = driver.find_element(By.CLASS_NAME, value="content_inner")
  users = user_list.find_elements(By.XPATH, value='./div')
  # ページの高さを取得
  last_height = driver.execute_script("return document.body.scrollHeight")
  while True:
    # ページの最後までスクロール
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # ページが完全に読み込まれるまで待機
    time.sleep(2)
    user_list = driver.find_element(By.CLASS_NAME, value="content_inner")
    users = user_list.find_elements(By.XPATH, value='./div')
    # print(len(users))
    if len(users) > 50:
      print('ユーザー件数50　OVER')
      break
    # 新しい高さを取得
    new_height = driver.execute_script("return document.body.scrollHeight")
    # ページの高さが変わらなければ、すべての要素が読み込まれたことを意味する
    if new_height == last_height:
        break
    last_height = new_height
  # ユーザーのhrefを取得
  user_cnt = 1
  link_list = []
  for user_cnt in range(len(users)):
    # 実行確率（80%の場合）
    execution_probability = 0.99
    # ランダムな数値を生成し、実行確率と比較
    if random.random() < execution_probability:
      user_id = users[user_cnt].get_attribute("id")
      if user_id == "loading":
        # print('id=loading')
        while user_id != "loading":
          time.sleep(2)
          user_id = users[user_cnt].get_attribute("id")
      link = "https://pcmax.jp/mobile/profile_detail.php?user_id=" + user_id + "&search=prof&condition=648ac5f23df62&page=1&sort=&stmp_counter=13&js=1"
      random_index = random.randint(0, len(link_list))
      link_list.insert(random_index, link)

  print(f'リンクリストの数{len(link_list)}')
  for idx, link_url in enumerate(link_list, 1):
    driver.get(link_url)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    now = datetime.now().strftime('%m-%d %H:%M:%S')
    print(f"{chara_data['name']} 足跡　{idx}件  {now}")
    if int(idx) == int(foot_cnt):
      break

def check_new_mail(pcmax_info, driver, wait):
  return_list = []
  login_id = pcmax_info["login_id"]
  login_pass = pcmax_info["password"]
  fst_message = pcmax_info["fst_mail"]
  mail_img = pcmax_info["mail_img"]
  second_message = pcmax_info["second_message"]
  return_foot_message = pcmax_info["return_foot_message"]
  condition_message = pcmax_info["condition_message"]
  mail_address = pcmax_info["mail_address"]
  gmail_password = pcmax_info["gmail_password"]
  name = pcmax_info["name"]
  # DEBUG
  # if name != "りな":
  #   return
  if login_id == None or login_id == "":
    print(f"{name}のpcmaxキャラ情報を取得できませんでした")
    return 1, 0
  login_flug = login(name, login_id, login_pass, driver, wait)
  if not login_flug:
    return 1, 0
  warning_flug = catch_warning_pop(name, driver, wait)
  if warning_flug:
    warning_text = f"PCMAX {login_id}:{login_pass} {warning_flug}"
    return_list.append(warning_text)
    return return_list, 0    
  print(f"{name}のメールチェック開始")
  # トップ画像の確認
  top_img_elem = driver.find_elements(By.CLASS_NAME, value="p_img")
  if len(top_img_elem):
    top_img_style = top_img_elem[0].get_attribute("style")
    if "no-image" in top_img_style:
      print(f"{name}のトップ画像がNOIMAGEになっている可能性があります。")
  # 新着があるかチェック
  nav_flug = nav_item_click(name,"メッセージ", driver, wait)
  print(nav_flug == "new_message")
  if nav_flug == "new_message":
      print('新着があります')
      # 未読だけを表示
      new_message_display = driver.find_elements(By.CLASS_NAME, value="msg-display_change")
      new_message_display[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(2)
      message_list = driver.find_elements(By.CLASS_NAME, value="receive_user")
      unread = message_list[0].find_elements(By.CLASS_NAME, value="unread1")
      # メッセージ一覧を取得   
      while len(unread):
        try:
            message_list = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "receive_user")))   
        except TimeoutException:
            print("タイムアウトしました")
            break
        arrival_date = message_list[-1].find_elements(By.CLASS_NAME, value="date")
        date_numbers = re.findall(r'\d+', arrival_date[0].text)
        # datetime型を作成
        arrival_datetime = datetime(int(date_numbers[0]), int(date_numbers[1]), int(date_numbers[2]), int(date_numbers[3]), int(date_numbers[4])) 
        now = datetime.today()
        elapsed_time = now - arrival_datetime
        # print(f"メール到着からの経過時間{elapsed_time}")
        if elapsed_time >= timedelta(minutes=4):
          # print("4分以上経過しています。")
          taikai = False
          # dev
          # user_photo = message_list[5].find_element(By.CLASS_NAME, value="user_photo")
          try:
            element = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "receive_user")))
          except TimeoutException:
              print("要素が見つかりませんでした。")
          user_photo = element[-1].find_element(By.CLASS_NAME, value="user_photo")
          # 退会してるか判定
          out = element[-1].find_elements(By.CLASS_NAME, value="out")
          
          if len(out):
            next_element = element[-1].find_elements(By.XPATH, value='following-sibling::*')
            script_code = next_element[0].get_attribute("innerHTML")
            # 取得したJavaScriptコードを表示
            # 正規表現パターン
            pattern = r"mail_recive_detail\.php\?mail_id=(.*?);"
            match = re.search(pattern, script_code)
            result = match.group(1)
            print(result)
            
            taikai_user_url = f"https://pcmax.jp/mobile/mail_recive_detail.php?mail_id={result}"
            driver.get(taikai_user_url)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
            driver.get("https://pcmax.jp/mobile/mail_recive_list.php?receipt_status=0")
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
            continue
          user_link = user_photo.find_element(By.TAG_NAME, value="a").get_attribute("href")
          start_index = user_link.find("user_id=")
          # print(start_index)
          if start_index != -1:
              user_id = user_link[start_index + len("user_id="):]
              # print("取得した文字列:", user_id)
          elif "void" in str(start_index):
            user_page = user_photo.find_element(By.TAG_NAME, value="a")
            if user_page.is_enabled():
              driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", user_page)
              user_page.click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
              driver.back()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
              # 未読だけを表示
              new_message_display = driver.find_elements(By.CLASS_NAME, value="msg-display_change")
              new_message_display[0].click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
              # メッセージ一覧を取得
              message_list = driver.find_elements(By.CLASS_NAME, value="receive_user")
              continue
          else:
              # user info にIDが載ってる　i1167384264
              # https://pcmax.jp/mobile/mail_recive_detail.php?mail_id=1167384264&user_id=16164934
              print("user_idが見つかりませんでした。")
              if len(element):
                user_photo = element[-1].find_element(By.CLASS_NAME, value="user_photo")
                user_link = user_photo.find_element(By.TAG_NAME, value="a").get_attribute("href")
                start_index = user_link.find("user_id=")
                print(type(start_index))
                # print(start_index)
                if start_index != -1:
                  user_id = user_link[start_index + len("user_id="):]
                  # print("取得した文字列:", user_id)
                  taikai = False
                else:
                  taikai = True
          try:
            message_list = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "receive_user")))   
          except TimeoutException:
              print("要素が見つかりませんでした。")
              break
          #dev # mail_id = message_list[5].find_element(By.TAG_NAME, value="input").get_attribute("value")
          mail_id = message_list[-1].find_element(By.TAG_NAME, value="input").get_attribute("value")
          new_mail_link = "https://pcmax.jp/mobile/mail_recive_detail.php?mail_id=" + str(mail_id) + "&user_id=" + str(user_id)
          driver.get(new_mail_link)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(3)
          all_mail = driver.find_elements(By.ID, value="all_mail")
          if len(all_mail):
            all_mail[0].click()
            time.sleep(1)
            sent_by_me = driver.find_elements(By.CLASS_NAME, value="right_balloon_w")
            sent_by_me_maji = driver.find_elements(By.CLASS_NAME, value="right_balloon-maji")
          else:
            sent_by_me = driver.find_elements(By.CLASS_NAME, value="right_balloon_w")
            sent_by_me_maji = driver.find_elements(By.CLASS_NAME, value="right_balloon-maji")
          no_history_second_mail = True
          # 受信メッセージにメールアドレスが含まれているか
          received_mail_elem = driver.find_elements(By.CLASS_NAME, value="left_balloon_m")
          if len(received_mail_elem):
            received_mail = received_mail_elem[-1].text
          else:
            received_mail = ""       
          # ＠を@に変換する
          if "＠" in received_mail:
            received_mail = received_mail.replace("＠", "@")
          # メールアドレスを抽出する正規表現
          email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
          # email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
          email_list = re.findall(email_pattern, received_mail)
          if email_list:
            # print("メールアドレスが含まれています")
            # print(email_list)
            # print(name)
            # icloudの場合
            if "icloud.com" in received_mail:
              print("icloud.comが含まれています")
              icloud_text = "メール送ったんですけど、ブロックされちゃって届かないのでこちらのアドレスにお名前添えて送ってもらえますか？"
              icloud_text = icloud_text + "\n" + mail_address
              text_area = driver.find_elements(By.ID, value="mdc")
              if len(text_area):
                script = "arguments[0].value = arguments[1];"
                driver.execute_script(script, text_area[0], icloud_text)
                # text_area[0].send_keys(icloud_text)
                time.sleep(4)
                send = driver.find_element(By.ID, value="send_n")
                send.click()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(2)
                # 連続防止で失敗
                waiting = driver.find_elements(By.CLASS_NAME, value="banned-word")
                if len(waiting):
                  print("<<<<<<<<<<<<<<<<<<<連続防止で失敗>>>>>>>>>>>>>>>>>>>>")
                  time.sleep(6)
                  send = driver.find_element(By.ID, value="send_n")
                  send.click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(2)
              # 戻って見ちゃいや登録
              back = driver.find_element(By.ID, value="back3")
              back.click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
            else:
              name_elem = driver.find_elements(By.CLASS_NAME, value="content_header_center")
              user_name = name_elem[0].text
              for user_address in email_list:
                site = "pcmax"
                try:
                  func.send_conditional(user_name, user_address, mail_address, gmail_password, condition_message, site)
                  print("アドレス内1stメールを送信しました")
                except Exception:
                  print(f"{name} アドレス内1stメールの送信に失敗しました")
                  
            # 見ちゃいや登録
            latest_mail = driver.find_element(By.ID, value="dlink")
            latest_mail.click()
            time.sleep(2)
            dont_look_elems= driver.find_elements(By.CLASS_NAME, value="line-menu-inbox")
            dont_look = None
            for dont_look_elem in dont_look_elems:
              if "見ちゃいや" in dont_look_elem.text:
                dont_look = dont_look_elem
            if dont_look:
              driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", dont_look)
              time.sleep(1)
              dont_look.click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(1)
            dont_look_registration = driver.find_elements(By.CLASS_NAME, value="del")
            if len(dont_look_registration):
              dont_look_registration[0].click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
            driver.get("https://pcmax.jp/mobile/mail_recive_list.php?receipt_status=0")
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
            
            continue

            # received_mail_elem = driver.find_elements(By.CLASS_NAME, value="left_balloon_m")
            # received_mail = received_mail_elem[-1].text
            # return_message = f"{name}pcmax,{user_name}:{received_mail}"
            # print(return_message)
            # return_list.append(return_message)
            # no_history_second_mail = False
          
          # メッセージ送信一件もなし
          elif len(sent_by_me) == 0 and len(sent_by_me_maji) == 0:
            text_area = driver.find_elements(By.ID, value="mdc")
            if len(text_area):
              script = "arguments[0].value = arguments[1];"
              driver.execute_script(script, text_area[0], fst_message)
              # text_area[0].send_keys(fst_message)
              time.sleep(6)
              send = driver.find_element(By.ID, value="send_n")
              send.click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
              # 連続防止で失敗
              waiting = driver.find_elements(By.CLASS_NAME, value="banned-word")
              if len(waiting):
                print("<<<<<<<<<<<<<<<<<<<連続防止で失敗>>>>>>>>>>>>>>>>>>>>")
                time.sleep(6)
                send = driver.find_element(By.ID, value="send_n")
                send.click()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(2)
          # メッセージ送信一件だけ
          elif len(sent_by_me) == 1 or len(sent_by_me_maji) == 1:
            sent_by_me_list = []
            if len(sent_by_me):
              for sent_list in sent_by_me:
                sent_by_me_list.append(sent_list)
            elif len(sent_by_me_maji):
              for sent_list in sent_by_me_maji:
                sent_by_me_list.append(sent_list)
            for send_my_text in sent_by_me_list:
              # second_mailを既に送っているか
              if send_my_text.text == second_message:
                # print("second_mail履歴あり")
                name_elem = driver.find_elements(By.CLASS_NAME, value="content_header_center")
                user_name = name_elem[0].text
                received_mail_elem = driver.find_elements(By.CLASS_NAME, value="left_balloon_m")
                received_mail = received_mail_elem[-1].text
                return_message = f"{name}pcmax,{login_id}:{login_pass}\n{user_name}「{received_mail}」"
                return_list.append(return_message)
                no_history_second_mail = False
            # secondメッセージを入力
            if no_history_second_mail:
              if second_message:
                text_area = driver.find_elements(By.ID, value="mdc")
                if len(text_area):
                  script = "arguments[0].value = arguments[1];"
                  driver.execute_script(script, text_area[0], second_message)
                  # text_area[0].send_keys(second_message)
                  time.sleep(6)
                  send = driver.find_element(By.ID, value="send_n")
                  send.click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(2)
                  # 連続防止で失敗
                  waiting = driver.find_elements(By.CLASS_NAME, value="banned-word")
                  if len(waiting):
                    print("<<<<<<<<<<<<<<<<<<<連続防止で失敗>>>>>>>>>>>>>>>>>>>>")
                    time.sleep(6)
                    send = driver.find_element(By.ID, value="send_n")
                    send.click()
                    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                    time.sleep(2)
              else:
                print('やり取り中')
                name_elem = driver.find_elements(By.CLASS_NAME, value="content_header_center")
                user_name = name_elem[0].text
                # print(user_name)
                # print(received_mail)
                return_message = f"{name}pcmax,{login_id}:{login_pass}\n{user_name}「{received_mail}」"
                return_list.append(return_message)

          elif func.normalize_text(second_message) == func.normalize_text(sent_by_me[-1].text):
            # 受信メールにアドレスがあるか
            print('やり取り中')
            print(sent_by_me[-1].text)
            name_elem = driver.find_elements(By.CLASS_NAME, value="content_header_center")
            user_name = name_elem[0].text
            # print(user_name)
            # print(received_mail)
            return_message = f"{name}pcmax,{login_id}:{login_pass}\n{user_name}「{received_mail}」"
            return_list.append(return_message)
       
          # https://pcmax.jp/mobile/mail_recive_list.php?receipt_status=0
          driver.get("https://pcmax.jp/mobile/mail_recive_list.php?receipt_status=0")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
          # メッセージ一覧を取得
          message_list = driver.find_elements(By.CLASS_NAME, value="receive_user")
          if len(message_list):
            unread = message_list[0].find_elements(By.CLASS_NAME, value="unread1")
          else:
            break
        else:
          break
  # # 足跡返し
  # try:
  #   driver.get("https://pcmax.jp/pcm/index.php")
  #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # except TimeoutException as e:
  #   print("TimeoutException")
  #   driver.refresh()
  # time.sleep(2)
  # warning = driver.find_elements(By.CLASS_NAME, value="caution-title")
  # warning2 = driver.find_elements(By.CLASS_NAME, value="suspend-title")
  # warning3 = driver.find_elements(By.CLASS_NAME, value="setting-title")
  # if len(warning) or len(warning2) or len(warning3):
  #   print(f"{name}pcmaxに警告画面が出ている可能性があります")
  #   # return_list.append(f"{name}pcmaxに警告画面が出ている可能性があります")
  #   if len(return_list):
  #     return return_list, 0
  #   else:
  #     return 1, 0
  # # 右下のキャラ画像をクリック
  # chara_img = driver.find_elements(By.XPATH, value="//*[@id='sp_footer']/a[5]")
  # reload_cnt = 1
  # while not len(chara_img):
  #   time.sleep(5)
  #   # print("右下のキャラ画像が見つかりません")
  #   chara_img = driver.find_elements(By.XPATH, value="//*[@id='sp_footer']/a[5]")
  #   reload_cnt += 1
  #   if reload_cnt == 5:
  #     break
  # if not len(chara_img):
  #   return
  # chara_img[0].click()
  # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(2)
  # # //*[@id="contents"]/div[2]/div[2]/ul/li[5]/a
  # # 足あとをクリック
  # footpoint = driver.find_element(By.CLASS_NAME, value="visit1")
  # # footpoint = driver.find_element(By.XPATH, value="//*[@id='contents']/div[2]/div[2]/ul/li[5]/a")
  # footpoint.click()
  # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(2)
  # # ページの高さを取得
  # last_height = driver.execute_script("return document.body.scrollHeight")
  # while True:
  #   # ページの最後までスクロール
  #   driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
  #   # ページが完全に読み込まれるまで待機
  #   time.sleep(1)
    
  #   # ユーザーを取得
  #   user_list = driver.find_element(By.CLASS_NAME, value="list-content")
  #   div = user_list.find_elements(By.XPATH, value='./div')
  #   if len(div) > 40:
  #     # print(len(div))
  #     break
  #   # 新しい高さを取得
  #   new_height = driver.execute_script("return document.body.scrollHeight")
  #   # ページの高さが変わらなければ、すべての要素が読み込まれたことを意味する
  #   if new_height == last_height:
  #     break
  #   last_height = new_height
  # # リンクを取得
  # user_cnt = 1
  # mail_history = 0
  # send_count = 0
  # link_list = []
  # while user_cnt < len(div):
  #   # 新着リストの名前ならスキップ
  #   span= div[user_cnt].find_elements(By.TAG_NAME, value="span")
  #   user_name = ""
  #   for i in span:
  #     if i.get_attribute("class") == "user-name":
  #       user_name = i.text    
  #   like = div[user_cnt].find_elements(By.CLASS_NAME, value="type1")
  #   # name = div[user_cnt].find_element(By.CLASS_NAME, value="user-name")
  #   # print(1111111111111111)
  #   # print(user_name)
  #   if user_name in have_new_massage_users:
  #     # print('新着リストのユーザーです')
  #     user_cnt += 1
  #   elif not len(like):
  #     user_cnt += 1
  #   else:
  #     a_tags = div[user_cnt].find_elements(By.TAG_NAME, value="a")
  #     # print("aタグの数：" + str(len(a_tags)))
  #     if len(a_tags) > 1:
  #       link = a_tags[1].get_attribute("href")
  #       # print(link)
  #       link_list.append(link)
  #     user_cnt += 1
  # # print(len(link_list))
  # for i in link_list:
  #   # if mail_history == 7:
  #   #   break
  #   driver.get(i)
  #   # //*[@id="profile-box"]/div/div[2]/p/a/span
  #   sent = driver.find_elements(By.XPATH, value="//*[@id='profile-box']/div/div[2]/p/a/span")
  #   if len(sent):
  #     # print('送信履歴があります')
  #     # いいねする
  #     with_like = driver.find_elements(By.CLASS_NAME, value="type1")
  #     if len(with_like):
  #       with_like[0].click()
  #       wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  #       time.sleep(1)
  #     time.sleep(2)
  #     mail_history += 1
  #     continue  
  #   # 自己紹介文をチェック
  #   self_introduction = driver.find_elements(By.XPATH, value="/html/body/main/div[4]/div/p")
  #   if len(self_introduction):
  #     self_introduction = self_introduction[0].text.replace(" ", "").replace("\n", "")
  #     if '通報' in self_introduction or '業者' in self_introduction:
  #       print('自己紹介文に危険なワードが含まれていました')
  #       # お断り登録
  #       refusal_elems = driver.find_elements(By.CLASS_NAME, value="flex_btn_container")
  #       refusal_elems = refusal_elems[0].find_elements(By.TAG_NAME, value="a")
  #       refusal_elem = ""
  #       for candidate_elem in refusal_elems:
  #         if "お断り" in candidate_elem.text:
  #           refusal_elem = candidate_elem
  #       if refusal_elem:
  #         driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", refusal_elem)
  #         time.sleep(1)
  #         refusal_elem.click()
  #         wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  #         time.sleep(2)
  #         refusal_registration = driver.find_elements(By.CLASS_NAME, value="del")
  #         refusal_registration[0].click()
  #         wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  #         time.sleep(2)
  #       continue
  #   # 残ポイントチェック
  #   point = driver.find_elements(By.ID, value="point")
  #   if len(point):
  #     point = point[0].find_element(By.TAG_NAME, value="span").text
  #     pattern = r'\d+'
  #     match = re.findall(pattern, point)
  #     if int(match[0]) > 1:
  #       maji_soushin = True
  #     else:
  #       maji_soushin = False
  #   else:
  #     time.sleep(4)
  #     continue
  #   time.sleep(1)
  #   # いいねする
  #   with_like = driver.find_elements(By.CLASS_NAME, value="type1")
  #   if len(with_like):
  #     time.sleep(1)
  #     with_like[0].click()
  #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  #     time.sleep(1)
  #   # メッセージをクリック
  #   message = driver.find_elements(By.ID, value="message1")
  #   if len(message):
  #     message[0].click()
  #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  #     time.sleep(3)
  #   else:
  #     continue
  #   # 画像があれば送付
  #   if mail_img:
  #     picture_icon = driver.find_elements(By.CLASS_NAME, value="mail-menu-title")
  #     picture_icon[0].click()
  #     time.sleep(1)
  #     picture_select = driver.find_element(By.ID, "my_photo")
  #     select = Select(picture_select)
  #     select.select_by_visible_text(mail_img)
      
  #   # メッセージを入力
  #   text_area = driver.find_element(By.ID, value="mdc")
  #   script = "arguments[0].value = arguments[1];"
  #   driver.execute_script(script, text_area, return_foot_message)
  #   # text_area.send_keys(return_foot_message)
  #   time.sleep(6)
  #   # print("マジ送信 " + str(maji_soushin) + " ~" + str(send_count + 1) + "~")
  #   print(f"{name}pcmax 足跡返し マジ送信:{maji_soushin} {send_count + 1}件送信")

  #   # メッセージを送信
  #   if maji_soushin:
  #     send = driver.find_element(By.CLASS_NAME, value="maji_send")
  #     driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", send)
  #     # send.click()
  #     driver.execute_script("arguments[0].click();", send)
  #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  #     time.sleep(2)
  #     send_link = driver.find_elements(By.ID, value="link_OK")
  #     driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", send_link[0])
  #     send_link[0].click()
  #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  #     time.sleep(2)
  #     send_count += 1
  #     mail_history = 0
      
  #   else:
  #     send = driver.find_element(By.ID, value="send_n")
  #     send.click()
  #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  #     time.sleep(2)
  #     send_count += 1
  #     mail_history = 0
  # # if send_count:
  # #   return_list.append(f'{name}pcmax 足跡返し{send_count}件')

  # if len(return_list):
  #   return return_list, send_count
  # else:
  #   return 1, send_count
  if len(return_list):
    return return_list, 0
  else:
    return 1, 0

  
def re_registration(chara_data, driver, wait):
  # print(chara_data)
  name = chara_data["name"]
  login_id = chara_data["login_id"]
  login_pass = chara_data["password"]
  date_of_birth = chara_data["date_of_birth"]
  self_promotion = chara_data["self_promotion"]
  height = chara_data["height"]
  body_shape = chara_data["body_shape"]
  blood_type = chara_data["blood_type"]
  activity_area = chara_data["activity_area"]
  detail_activity_area = chara_data["detail_activity_area"]
  profession = chara_data["profession"]
  freetime = chara_data["freetime"]
  car_ownership = chara_data["car_ownership"]
  smoking = chara_data["smoking"]
  ecchiness_level = chara_data["ecchiness_level"]
  sake = chara_data["sake"]
  process_before_meeting = chara_data["process_before_meeting"]
  first_date_cost = chara_data["first_date_cost"]

  driver.delete_all_cookies()
  driver.get("https://pcmax.jp/pcm/file.php?f=login_form")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  wait_time = random.uniform(4, 6)
  time.sleep(2)
  id_form = driver.find_element(By.ID, value="login_id")
  id_form.send_keys(login_id)
  pass_form = driver.find_element(By.ID, value="login_pw")
  pass_form.send_keys(login_pass)
  time.sleep(1)
  send_form = driver.find_element(By.NAME, value="login")
  try:
    send_form.click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
  except TimeoutException as e:
    print("TimeoutException")
    driver.refresh()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    id_form = driver.find_element(By.ID, value="login_id")
    id_form.send_keys(login_id)
    pass_form = driver.find_element(By.ID, value="login_pw")
    pass_form.send_keys(login_pass)
    time.sleep(1)
    send_form = driver.find_element(By.NAME, value="login")
    send_form.click()
  # 利用制限中
  suspend = driver.find_elements(By.CLASS_NAME, value="suspend-title")
  if len(suspend):
    print(f'{name}pcmax利用制限中です')
    return  
  wait_time = random.uniform(4,5)
  re_login(driver, wait)
  # MENUをクリック
  menu = driver.find_element(By.ID, value='sp_nav')
  menu.click()
  time.sleep(wait_time)
  # プロフィール編集をクリック　
  bulletin_board_history = driver.find_element(By.CLASS_NAME, value="nav-content-list")
  bulletin_board_history = bulletin_board_history.find_elements(By.TAG_NAME, value="dd")
  for i in bulletin_board_history:
    if i.text == "プロフィール編集":
      edit_profile = i.find_element(By.TAG_NAME, value="a")
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", edit_profile)
      edit_profile.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
      break
  # 名前を変更
  # info_change = driver.find_elements(By.CLASS_NAME, value="info_change")
  # name_change = info_change[0].find_elements(By.TAG_NAME, value="a")[0]
  # name_change.click()
  # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(wait_time)
  # nick_name = driver.find_elements(By.CLASS_NAME, value="textbox")
  # nick_name[0].clear()
  # nick_name[0].send_keys(chara_data["name"])
  # time.sleep(2)
  # set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
  # set_button[0].click()
  # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(wait_time)

  # 生年月日を変更
  # info_change = driver.find_elements(By.CLASS_NAME, value="info_change")
  # birthdate_change = info_change[0].find_elements(By.TAG_NAME, value="a")[1]
  # birthdate_change.click()
  # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(wait_time)
  # birth_date = driver.find_elements(By.CLASS_NAME, value="textbox")
  # birth_date[0].clear()
  # birth_date[0].send_keys(date_of_birth)
  # time.sleep(2)
  # set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
  # set_button[0].click()
  # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(wait_time)

  # 自己PR
  if self_promotion:
    # setting_btn
    promotion_change_button = driver.find_elements(By.CLASS_NAME, value="setting_btn")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", promotion_change_button[0])
    time.sleep(1)
    promotion_change_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    clear_btn = driver.find_elements(By.ID, value="clear_btn")
    clear_btn[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    text_area = driver.find_elements(By.ID, value="comment")
    script = "arguments[0].value = arguments[1];"
    driver.execute_script(script, text_area[0], self_promotion)
    # text_area[0].send_keys(self_promotion)
    time.sleep(2)
    set_button = driver.find_elements(By.ID, value="p_reg_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  
  # 体型
  if body_shape:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    body_shape_link = prof_list[1].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", body_shape_link[0])
    time.sleep(1)
    body_shape_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    body_shape_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    if not len(body_shape_select):
      time.sleep(3)
      print(len(body_shape_select))
    select = Select(body_shape_select[0])
    select.select_by_visible_text(body_shape)
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # 身長
  prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
  height_link = prof_list[0].find_elements(By.TAG_NAME, value="a")
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", height_link[0])
  time.sleep(1)
  height_link[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  height_select = driver.find_elements(By.CLASS_NAME, value="s_select")
  height_select_cnt = 0
  
  while len(height_select) == 0:
    time.sleep(5)
    height_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    height_select_cnt += 1
    if height_select_cnt == 4:
      print("エラーが起きました、時間をおいて試してください。")
      break

  select = Select(height_select[0])
  select.select_by_value(str(height))
  time.sleep(1)
  set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
  set_button[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  # 血液型
  # if blood_type:
  #   prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
  #   blood_type_link = prof_list[2].find_elements(By.TAG_NAME, value="a")
  #   driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", blood_type_link[0])
  #   time.sleep(1)
  #   blood_type_link[0].click()
  #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  #   time.sleep(wait_time)
  #   blood_type_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
  #   select = Select(blood_type_link_select[0])
  #   select.select_by_visible_text(blood_type)
  #   time.sleep(1)
  #   set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
  #   set_button[0].click()
  #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  #   time.sleep(wait_time)

  # 活動エリア
  # prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
  # activity_area_link = prof_list[5].find_elements(By.TAG_NAME, value="a")
  # driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", activity_area_link[0])
  # time.sleep(1)
  # activity_area_link[0].click()
  # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(wait_time)
  # activity_area_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
  # select = Select(activity_area_link_select[0])
  # select.select_by_visible_text(activity_area)
  # time.sleep(1)
  # set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
  # set_button[0].click()
  # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(wait_time)
  # 活動詳細エリア
  # if detail_activity_area:
  #   # prech
  #   activity_area_link_select = driver.find_elements(By.ID, value="prech")
  #   select = Select(activity_area_link_select[0])
  #   select.select_by_visible_text(activity_area)
  #   time.sleep(2)
  #   detail_activity_area_link_select = driver.find_elements(By.ID, value="city_id_1")
  #   select = Select(detail_activity_area_link_select[0])
  #   select.select_by_visible_text(detail_activity_area)
  # time.sleep(1)
  # set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
  # set_button[0].click()
  # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(wait_time)

  # 職業
  # if profession:
  #   prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
  #   profession_link = prof_list[6].find_elements(By.TAG_NAME, value="a")
  #   driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", profession_link[0])
  #   time.sleep(1)
  #   profession_link[0].click()
  #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  #   time.sleep(wait_time)
  #   profession_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
  #   select = Select(profession_link_select[0])
  #   select.select_by_visible_text(profession)
  #   time.sleep(1)
  #   set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
  #   set_button[0].click()
  #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  #   time.sleep(wait_time)

  # ヒマな時間帯
  if freetime:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    freetime_link = prof_list[9].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", freetime_link[0])
    time.sleep(1)
    freetime_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    freetime_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(freetime_link_select[0])
    select.select_by_visible_text(freetime)
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # 車の所有
  if car_ownership:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    car_ownership_link = prof_list[10].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", car_ownership_link[0])
    time.sleep(1)
    car_ownership_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    car_ownership_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(car_ownership_link_select[0])
    select.select_by_visible_text(car_ownership)
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # 喫煙
  if smoking:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    smoking_link = prof_list[11].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", smoking_link[0])
    time.sleep(1)
    smoking_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    smoking_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(smoking_link_select[0])
    select.select_by_visible_text(smoking)
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # エッチ度
  if ecchiness_level:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    ecchiness_level_link = prof_list[12].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", ecchiness_level_link[0])
    time.sleep(1)
    ecchiness_level_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    ecchiness_level_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(ecchiness_level_link_select[0])
    select.select_by_visible_text(ecchiness_level)
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # お酒
  if sake:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    sake_link = prof_list[13].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", sake_link[0])
    time.sleep(1)
    sake_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    sake_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(sake_link_select[0])
    select.select_by_visible_text(sake)
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # 会うまでのプロセス
  if process_before_meeting:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    process_before_meeting_link = prof_list[14].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", process_before_meeting_link[0])
    time.sleep(1)
    process_before_meeting_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    process_before_meeting_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(process_before_meeting_link_select[0])
    select.select_by_visible_text(process_before_meeting)
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # 初回デート費用
  if first_date_cost:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    first_date_cost_link = prof_list[15].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", first_date_cost_link[0])
    time.sleep(1)
    first_date_cost_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    first_date_cost_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(first_date_cost_link_select[0])
    select.select_by_visible_text(first_date_cost)
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # 旅行・宿泊
  if chara_data["travel"]:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    travel_link = prof_list[16].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", travel_link[0])
    time.sleep(1)
    travel_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    travel_link_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(travel_link_link_select[0])
    select.select_by_visible_text(chara_data["travel"])
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # 出身地
  if chara_data["birth_place"]:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    birth_place_link = prof_list[17].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", birth_place_link[0])
    time.sleep(1)
    birth_place_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    birth_place_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(birth_place_link_select[0])
    select.select_by_visible_text(chara_data["birth_place"])
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # 学歴
  if chara_data["education"]:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    education_link = prof_list[18].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", education_link[0])
    time.sleep(1)
    education_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    education_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(education_link_select[0])
    select.select_by_visible_text(chara_data["education"])
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # 年収
  if chara_data["annual_income"]:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    annual_income_link = prof_list[19].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", annual_income_link[0])
    time.sleep(1)
    annual_income_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    annual_income_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(annual_income_link_select[0])
    select.select_by_visible_text(chara_data["annual_income"])
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # 同居人
  if chara_data["roommate"]:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    roommate_link = prof_list[20].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", roommate_link[0])
    time.sleep(1)
    roommate_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    roommate_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(roommate_link_select[0])
    select.select_by_visible_text(chara_data["roommate"])
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # 結婚
  if chara_data["marry"]:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    marry_link = prof_list[21].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", marry_link[0])
    time.sleep(1)
    marry_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    marry_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(marry_link_select[0])
    select.select_by_visible_text(chara_data["marry"])
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # 子供
  if chara_data["child"]:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    child_link = prof_list[22].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", child_link[0])
    time.sleep(1)
    child_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    child_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(child_link_select[0])
    select.select_by_visible_text(chara_data["child"])
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # 家事・育児
  if chara_data["housework"]:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    housework_link = prof_list[23].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", housework_link[0])
    time.sleep(1)
    housework_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    housework_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(housework_link_select[0])
    select.select_by_visible_text(chara_data["housework"])
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
  # 社交性
  if chara_data["sociability"]:
    prof_list = driver.find_elements(By.CLASS_NAME, value="prof_lst")
    sociability_link = prof_list[24].find_elements(By.TAG_NAME, value="a")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", sociability_link[0])
    time.sleep(1)
    sociability_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    sociability_link_select = driver.find_elements(By.CLASS_NAME, value="s_select")
    select = Select(sociability_link_select[0])
    select.select_by_visible_text(chara_data["sociability"])
    time.sleep(1)
    set_button = driver.find_elements(By.CLASS_NAME, value="basic_btn")
    set_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)

  registration_button = driver.find_elements(By.CLASS_NAME, value="btn")
  registration_button[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)

def send_fst_mail(pcmax_chara, maji_soushin, select_areas, youngest_age, oldest_age, ng_words, limit_send_cnt, user_sort_list, driver, wait):
  try:
    driver.delete_all_cookies()
    driver.get("https://pcmax.jp/pcm/file.php?f=login_form")
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  except TimeoutException as e:
    print("TimeoutException")
    driver.refresh()
  wait_time = random.uniform(6, 8)
  time.sleep(2)
  id_form = driver.find_element(By.ID, value="login_id")
  id_form.send_keys(pcmax_chara["login_id"])
  pass_form = driver.find_element(By.ID, value="login_pw")
  pass_form.send_keys(pcmax_chara["password"])
  time.sleep(1)
  send_form = driver.find_element(By.NAME, value="login")
  send_form.click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(3)
  send_complete = False
  try:
    send_cnt = 1
    while True:
      # 利用制限中
      suspend = driver.find_elements(By.CLASS_NAME, value="suspend-title")
      if len(suspend):
        print(f'{pcmax_chara["name"]}利用制限中です')  
        driver.quit()
        return
      #プロフ検索をクリック
      footer_icons = driver.find_element(By.ID, value="sp_footer")
      search_profile = footer_icons.find_element(By.XPATH, value="./*[1]")
      search_profile.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(3)
      # 検索条件を設定
      search_elem = driver.find_element(By.ID, value="search1")
      search_elem.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      # /////////////////////////詳細検索画面/////////////////////////
      
      select_area = driver.find_elements(By.CLASS_NAME, value="pref-select-link")
      reset_area = driver.find_elements(By.CLASS_NAME, value="reference_btn")
      
      if not len(select_area) and not len(reset_area):
        # /////////////////////////利用制限あり
        print(f"{pcmax_chara['name']}利用制限あり")
        try:
          func.send_error(pcmax_chara['name'], "pcmaxプロフ制限あり")
        except Exception:
          print("エラー送信失敗しました")
        # 地域選択
        if len(select_areas) == 1:
          select_area = driver.find_elements(By.NAME, value="pref_no")
          select = Select(select_area[0])
          select.select_by_visible_text(select_areas[0])
        elif len(select_areas) > 1:
          # 選択確率の重みを設定
          weights = [0.2, 0.2, 0.6]  # 東京都は60%、千葉県と埼玉県は20%ずつの確率
          selected_area = random.choices(select_areas, weights=weights)[0]
          print(f"決定地域:{selected_area}")
          select_area = driver.find_elements(By.NAME, value="pref_no")
          select = Select(select_area[0])
          select.select_by_visible_text(selected_area)
          time.sleep(1)
        # 年齢
        oldest_age = driver.find_elements(By.ID, value="makerItem")
        select = Select(oldest_age[0])
        select.select_by_visible_text("29歳")
        time.sleep(1)
        # 上記の条件で検索するボタン送信
        filtered_send = driver.find_elements(By.NAME, value="send")
        filtered_send[0].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(wait_time)
      else:
        # /////////////////////////利用制限なし
        print(f"{pcmax_chara['name']}利用制限なし")
        
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
        # ユーザーリスト並び替え設定
        user_sort = driver.find_element(By.ID, "sort2")
        if user_sort.tag_name == "select":
          select = Select(user_sort)
          select.select_by_visible_text(user_sort_list[0])
        if user_sort.tag_name == "div":
          sort_login = driver.find_elements(By.ID, "sort-login")
          sort_login[0].click()
        time.sleep(1)

      # ユーザーを取得
      user_list = driver.find_element(By.CLASS_NAME, value="content_inner")
      users = user_list.find_elements(By.XPATH, value='./div')
      # ページの高さを取得
      last_height = driver.execute_script("return document.body.scrollHeight")
      while True:
        # ページの最後までスクロール
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # ページが完全に読み込まれるまで待機
        time.sleep(2)
        user_list = driver.find_element(By.CLASS_NAME, value="content_inner")
        users = user_list.find_elements(By.XPATH, value='./div')
        # print(len(users))
        if len(users) > 200:
          print('ユーザー件数200　OVER')
          break
        # 新しい高さを取得
        new_height = driver.execute_script("return document.body.scrollHeight")
        # ページの高さが変わらなければ、すべての要素が読み込まれたことを意味する
        if new_height == last_height:
            break
        last_height = new_height
      # ユーザーのhrefを取得
      user_cnt = 1
      link_list = []
      for user_cnt in range(len(users)):
        # 実行確率（80%の場合）
        execution_probability = 0.99
        # ランダムな数値を生成し、実行確率と比較
        if random.random() < execution_probability:
          user_id = users[user_cnt].get_attribute("id")
          if user_id == "loading":
            # print('id=loading')
            while user_id != "loading":
              time.sleep(2)
              user_id = users[user_cnt].get_attribute("id")
          link = "https://pcmax.jp/mobile/profile_detail.php?user_id=" + user_id + "&search=prof&condition=648ac5f23df62&page=1&sort=&stmp_counter=13&js=1"
          random_index = random.randint(0, len(link_list))
          link_list.insert(random_index, link)

      print(f'リンクリストの数{len(link_list)}')
      # メール送信
      for idx, link_url in enumerate(link_list, 1):
        send_status = True
        driver.get(link_url)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
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
              time.sleep(wait_time)
              send_status = False
              continue
            if send_status == False:
              break
        # 残ポイントチェック
        if maji_soushin:
          point = driver.find_elements(By.ID, value="point")
          if len(point):
            point = point[0].find_element(By.TAG_NAME, value="span").text
            pattern = r'\d+'
            match = re.findall(pattern, point)
            if int(match[0]) > 1:
              maji_soushin = True
            else:
              maji_soushin = False
          else:
            time.sleep(wait_time)
            continue
          time.sleep(1)
        
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
          if pcmax_chara["mail_img"]:
            picture_icon = driver.find_elements(By.CLASS_NAME, value="mail-menu-title")
            picture_icon[0].click()
            time.sleep(1)
            picture_select = driver.find_element(By.ID, "my_photo")
            select = Select(picture_select)
            select.select_by_visible_text(pcmax_chara["mail_img"])
          # メッセージを入力
          text_area = driver.find_element(By.ID, value="mdc")
          script = "arguments[0].value = arguments[1];"
          driver.execute_script(script, text_area, pcmax_chara["fst_mail"])
          # text_area.send_keys(fst_message)
          time.sleep(4)
        
          if maji_soushin:
            send = driver.find_elements(By.CLASS_NAME, value="maji_send")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", send[0])
            send[0].click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(1)
            send_link = driver.find_element(By.ID, value="link_OK")
            send_link.click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(wait_time)
          else:
            send = driver.find_element(By.ID, value="send_n")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", send)
            send.click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(wait_time)
          time.sleep(wait_time)
          print(str(pcmax_chara["name"]) + ": pcmax、マジ送信 " + str(maji_soushin) + " ~" + str(send_cnt) + "~ " + str(user_age) + " " + str(area_of_activity) + " " + str(user_name))
          send_cnt += 1
        # if send_cnt == limit_send_cnt + 1:
        #   driver.quit()
        #   print(f"<<<<<<<<<<<{pcmax_chara['name']}、送信数{send_cnt - 1}件:上限に達しました>>>>>>>>>>>>>>")
        #   send_complete = True
        #   break
      break
      try:
        driver.get("https://pcmax.jp/pcm/index.php")
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(wait_time)
      except TimeoutException as e:
        print("TimeoutException")
        driver.refresh()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
      
  # 何らかの処理
  except KeyboardInterrupt:
    print("Ctl + c")
    driver.quit()  
  except Exception:
    if send_complete:
      driver.quit()  
    else:
      print("エラー")
      print(traceback.format_exc())


def repost_one_rap(sorted_pcmax, headless, detail_area_flug):
  def timer(sec, functions):
    start_time = time.time() 
    for func in functions:
      try:
        return_func = func()
      except Exception as e:
        print(e)
        return_func = 0
    elapsed_time = time.time() - start_time  # 経過時間を計算する
    while elapsed_time < sec:
      # make_footprints_repost_later()
      time.sleep(30)
      elapsed_time = time.time() - start_time  # 経過時間を計算する
      # print(f"待機中~~ {elapsed_time} ")
    
    return return_func
  
  wait_cnt = 7200 / len(sorted_pcmax)

  start_one_rap_time = time.time() 
  driver,wait = func.get_driver(headless)

  for pcmax_chara in sorted_pcmax:
    
    print(len(sorted_pcmax))
    print(pcmax_chara["name"])
    try:
      return_func = timer(wait_cnt, [lambda: re_post(pcmax_chara, driver, wait, detail_area_flug)])
      
    except Exception as e:
      print(f"エラー{pcmax_chara['name']}")
      print(traceback.format_exc())
      # func.send_error(chara, traceback.format_exc())
  elapsed_time = time.time() - start_one_rap_time  
  elapsed_timedelta = timedelta(seconds=elapsed_time)
  elapsed_time_formatted = str(elapsed_timedelta)
  driver.quit()
  

  



def repost_scheduler(schedule_data, sorted_pcmax, headless, detail_area_flug,):
  def background_task():
    # while True:
    #     # 必要な処理をここに記述
    #     # print("バックグラウンドタスクを実行中...")
    #     # make_footprints(driver, wait, select_areas, youngest_age, oldest_age,)
    #     # time.sleep(5) 
    print("待機中...")
  
  # スケジューラのジョブリスナー
  def job_listener(event):
      if event.exception:
          print(f"ジョブでエラーが発生しました: {event.job_id}")
      else:
          print(f"ジョブが正常に完了しました: {event.job_id}")

  #メインのスケジューラ関数
  def start_scheduler(schedule_data, sorted_pcmax, headless, detail_area_flug,):
      scheduler = BlockingScheduler()
      for r_time in schedule_data:
        hour, minute, = r_time
        # print(f"{hour}   {minute}")
        scheduler.add_job(
            repost_one_rap, 
            'cron', 
            hour=int(hour), 
            minute=int(minute), 
            args=[sorted_pcmax, headless, detail_area_flug,], 
            max_instances=2, 
            misfire_grace_time=60*60
        )
        print(f"掲示板スケジュール設定: {hour}時{minute}分, ")
      # イベントリスナーを追加
      scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

      # バックグラウンドタスクのスレッドを起動
      threading.Thread(target=background_task, daemon=True).start()

      try:
          # スケジューラの開始
          scheduler.start()
      except (KeyboardInterrupt, SystemExit):
          print("スケジューラを停止します。")
          scheduler.shutdown()
  
  # スケジューラを開始
  start_scheduler(schedule_data, sorted_pcmax, headless, detail_area_flug,)

def returnfoot_fst(sorted_pcmax, driver, wait,send_limit, ):
  name = sorted_pcmax["name"]
  login_id = sorted_pcmax["login_id"]
  login_pass = sorted_pcmax["password"]
  return_foot_message = sorted_pcmax["return_foot_message"]
  fst_message = sorted_pcmax["fst_mail"]
  mail_img = sorted_pcmax["mail_img"]
  login_flug = login(name, login_id, login_pass, driver, wait)
  if not login_flug:
    return
  wait_time = random.uniform(3, 4)
  re_login(driver, wait)
  time.sleep(2)
  # 新着があるかチェック
  nav_flug = nav_item_click(name, "メッセージ", driver, wait)
  have_new_massage_users = []
  if nav_flug == "new_message":
    print('新着があります')
    # 未読だけを表示
    new_message_display = driver.find_elements(By.CLASS_NAME, value="msg-display_change")
    new_message_display[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    message_list = driver.find_elements(By.CLASS_NAME, value="receive_user")
    if len(message_list):
      # 新着ありのユーザーをリストに追加
      for usr_info in message_list:
        unread = usr_info.find_elements(By.CLASS_NAME, value="unread1")
        if len(unread):
          new_mail_user = usr_info.find_element(By.CLASS_NAME, value="name").text
          if len(new_mail_user) > 7:
            new_mail_user = new_mail_user[:7] + "…"
          have_new_massage_users.append(new_mail_user)
      print(f"新着メッセージ数 {len(message_list)}")
  else:
    driver.get("https://pcmax.jp/pcm/member.php")
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)  
  # 足跡返し
  nav_item_click(name, "マイメニュー", driver, wait)
  visit = driver.find_elements(By.CLASS_NAME, value="visit1")
  visit[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  # ページの高さを取得
  last_height = driver.execute_script("return document.body.scrollHeight")
  while True:
    # ページの最後までスクロール
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # ページが完全に読み込まれるまで待機
    time.sleep(1)
    # ユーザーを取得
    user_list = driver.find_element(By.CLASS_NAME, value="list-content")
    div = user_list.find_elements(By.XPATH, value='./div')
    if len(div) > 40:
      # print(len(div))
      break
    # 新しい高さを取得
    new_height = driver.execute_script("return document.body.scrollHeight")
    # ページの高さが変わらなければ、すべての要素が読み込まれたことを意味する
    if new_height == last_height:
      break
    last_height = new_height
  # リンクを取得
  user_cnt = 1
  mail_history = 0
  send_count = 0
  link_list = []
  while user_cnt < len(div):
    # 新着リストの名前ならスキップ
    span= div[user_cnt].find_elements(By.TAG_NAME, value="span")
    user_name = ""
    for i in span:
      if i.get_attribute("class") == "user-name":
        user_name = i.text    
    like = div[user_cnt].find_elements(By.CLASS_NAME, value="type1")
    # name = div[user_cnt].find_element(By.CLASS_NAME, value="user-name")
    if user_name in have_new_massage_users:
      print('新着リストのユーザーです')
      user_cnt += 1
    elif not len(like):
      user_cnt += 1
    else:
      a_tags = div[user_cnt].find_elements(By.TAG_NAME, value="a")
      # print("aタグの数：" + str(len(a_tags)))
      if len(a_tags) > 1:
        link = a_tags[1].get_attribute("href")
        # print(link)
        link_list.append(link)
      user_cnt += 1
  for i in link_list:
    if send_count >= send_limit:
      print("〜〜〜〜送信上限に達しました〜〜〜〜")
      return send_count
    # if mail_history == 7:
    #   break
    driver.get(i)
    ng_pop = driver.find_elements(By.ID, value="ng_dialog")
    if len(ng_pop):
      next_no_pop = ng_pop[0].find_elements(By.ID, value="check1")
      next_no_pop[0].click()
      time.sleep(1)
      understand_button = ng_pop[0].find_elements(By.CLASS_NAME, value="ng_dialog_btn")
      understand_button[0].click()
      time.sleep(2)
    # //*[@id="profile-box"]/div/div[2]/p/a/span
    sent = driver.find_elements(By.XPATH, value="//*[@id='profile-box']/div/div[2]/p/a/span")
    if len(sent):
      # print('送信履歴があります')
      # いいねする
      with_like = driver.find_elements(By.CLASS_NAME, value="type1")
      if len(with_like):
        with_like[0].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
      time.sleep(2)
      mail_history += 1
      continue  
    # 自己紹介文をチェック
    self_introduction = driver.find_elements(By.XPATH, value="/html/body/main/div[4]/div/p")
    if len(self_introduction):
      self_introduction = self_introduction[0].text.replace(" ", "").replace("\n", "")
      if '通報' in self_introduction or '業者' in self_introduction:
        print('自己紹介文に危険なワードが含まれていました')
        # お断り登録
        refusal_elems = driver.find_elements(By.CLASS_NAME, value="flex_btn_container")
        refusal_elems = refusal_elems[0].find_elements(By.TAG_NAME, value="a")
        refusal_elem = ""
        for candidate_elem in refusal_elems:
          if "お断り" in candidate_elem.text:
            refusal_elem = candidate_elem
        if refusal_elem:
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", refusal_elem)
          time.sleep(1)
          refusal_elem.click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
          refusal_registration = driver.find_elements(By.CLASS_NAME, value="del")
          refusal_registration[0].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
        continue
    # 残ポイントチェック
    # point = driver.find_elements(By.ID, value="point")
    # if len(point):
    #   point = point[0].find_element(By.TAG_NAME, value="span").text
    #   pattern = r'\d+'
    #   match = re.findall(pattern, point)
    #   if int(match[0]) > 1:
    #     maji_soushin = True
    #   else:
    #     maji_soushin = False
    # else:
    #   print(999)
    #   time.sleep(4)
    #   maji_soushin = False
    #   # continue
    # time.sleep(1)
    # いいねする
    with_like = driver.find_elements(By.CLASS_NAME, value="type1")
    if len(with_like):
      time.sleep(1)
      with_like[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
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
    driver.execute_script(script, text_area, return_foot_message)
    # text_area.send_keys(return_foot_message)
    time.sleep(5)
    # メッセージを送信
    # if maji_soushin:
    #   send = driver.find_element(By.CLASS_NAME, value="maji_send")
    #   driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", send)
    #   # send.click()
    #   driver.execute_script("arguments[0].click();", send)
    #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    #   time.sleep(2)
    #   send_link = driver.find_elements(By.ID, value="link_OK")
    #   driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", send_link[0])
    #   send_link[0].click()
    #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    #   time.sleep(2)
    #   send_count += 1
    #   mail_history = 0
    #   print(f"{name}pcmax 足跡返し マジ送信:{maji_soushin} {send_count }件送信") 
    # else:
    send = driver.find_element(By.ID, value="send_n")
    send.click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    send_count += 1
    mail_history = 0
    now = datetime.now().strftime('%m-%d %H:%M:%S')
    # print(f"{name}pcmax 足跡返し マジ送信:{maji_soushin} {send_count }件送信")
    print(f"{name}pcmax 足跡返し  {send_count }件送信  {now}")

  
  # ////////////fst////////////////////////////
  # send_count = 0# DEBUG
  returnfoot_cnt = send_count
  
  if send_count <= send_limit:
    re_login(driver, wait)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    #プロフ検索をクリック
    nav_item_click("プロフ検索", driver, wait)
    # 検索条件を設定
    
    search_elem = driver.find_elements(By.ID, value="search1")
    if not len(search_elem):
      print(f"{name} プロフィール検索に利用制限あり")
      return
    search_elem[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    # /////////////////////////詳細検索画面/////////////////////////
    
    select_area = driver.find_elements(By.CLASS_NAME, value="pref-select-link")
    reset_area = driver.find_elements(By.CLASS_NAME, value="reference_btn")
    select_areas = ["東京都",]
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
    youngest_age = "19"
    oldest_age = "33"
    user_sort_list = [
      "ログイン順",
      # "登録順", 
      # "自己PR更新順"
    ]
    if not len(select_area) and not len(reset_area):
      # /////////////////////////利用制限あり
      print(f"{name}利用制限あり")
      return
      # 地域選択
      if len(select_areas) == 1:
        select_area = driver.find_elements(By.NAME, value="pref_no")
        select = Select(select_area[0])
        select.select_by_visible_text(select_areas[0])
      elif len(select_areas) > 1:
        # 選択確率の重みを設定
        weights = [0.2, 0.2, 0.6]  # 東京都は60%、千葉県と埼玉県は20%ずつの確率
        selected_area = random.choices(select_areas, weights=weights)[0]
        print(f"決定地域:{selected_area}")
        select_area = driver.find_elements(By.NAME, value="pref_no")
        select = Select(select_area[0])
        select.select_by_visible_text(selected_area)
        time.sleep(1)
      # 年齢
      oldest_age = driver.find_elements(By.ID, value="makerItem")
      select = Select(oldest_age[0])
      select.select_by_visible_text("29歳")
      time.sleep(1)
      # 上記の条件で検索するボタン送信
      filtered_send = driver.find_elements(By.NAME, value="send")
      filtered_send[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
    else:
      # /////////////////////////利用制限なし
      print(f"{name}利用制限なし")
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
      # ユーザーリスト並び替え設定
      user_sort = driver.find_element(By.ID, "sort2")
      if user_sort.tag_name == "select":
        select = Select(user_sort)
        select.select_by_visible_text(user_sort_list[0])
      if user_sort.tag_name == "div":
        sort_login = driver.find_elements(By.ID, "sort-login")
        sort_login[0].click()
      time.sleep(1)
    # ユーザーを取得
    user_list = driver.find_element(By.CLASS_NAME, value="content_inner")
    users = user_list.find_elements(By.XPATH, value='./div')
    # ページの高さを取得
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
      # ページの最後までスクロール
      driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      # ページが完全に読み込まれるまで待機
      time.sleep(2)
      user_list = driver.find_element(By.CLASS_NAME, value="content_inner")
      users = user_list.find_elements(By.XPATH, value='./div')
      # print(len(users))
      if len(users) > 200:
        # print('ユーザー件数200　OVER')
        break
      # 新しい高さを取得
      new_height = driver.execute_script("return document.body.scrollHeight")
      # ページの高さが変わらなければ、すべての要素が読み込まれたことを意味する
      if new_height == last_height:
          break
      last_height = new_height
    # ユーザーのhrefを取得
    user_cnt = 1
    link_list = []
    for user_cnt in range(len(users)):
      # 実行確率（80%の場合）
      execution_probability = 0.80
      # ランダムな数値を生成し、実行確率と比較
      if random.random() < execution_probability:
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
    for idx, link_url in enumerate(link_list, 1):
      send_status = True
      driver.get(link_url)
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
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
            print(f"{name}:送信歴ありのためスキップ")
            send_status = False
            # send_cnt += 1
            break
        user_age = span_elem[0].text
        area_of_activity = span_elem[1].text
      # 自己紹介文をチェック
      ng_words = [
        "通報",
        "業者",
        # "食事",
        # "お茶",
        # "円",
        # "パパ",
        # "援",
        # "援交",
        # "お金のやり取り",
      ]
      self_introduction = driver.find_elements(By.XPATH, value="/html/body/main/div[4]/div/p")
      if len(self_introduction):
        self_introduction = self_introduction[0].text.replace(" ", "").replace("\n", "")
        for ng_word in ng_words:
          if ng_word in self_introduction:
            print('自己紹介文に危険なワードが含まれていました')
            time.sleep(wait_time)
            send_status = False
            continue
          if send_status == False:
            break
      # # 残ポイントチェック
      # point = driver.find_elements(By.ID, value="point")
      # if len(point):
      #   point = point[0].find_element(By.TAG_NAME, value="span").text
      #   pattern = r'\d+'
      #   match = re.findall(pattern, point)
      #   if int(match[0]) > 1:
      #     maji_soushin = True
      #   else:
      #     maji_soushin = False
      # else:
      #   time.sleep(4)
      #   maji_soushin = False
      #   continue
      # time.sleep(1)
      maji_soushin = False
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
          try:
            select.select_by_visible_text(mail_img)
          except NoSuchElementException:
            print("送付画像のタイトルが一致しません")
        # メッセージを入力
        text_area = driver.find_element(By.ID, value="mdc")
        script = "arguments[0].value = arguments[1];"
        driver.execute_script(script, text_area, fst_message)
        # text_area.send_keys(fst_message)
        time.sleep(4)
      
        if maji_soushin:
          send = driver.find_elements(By.CLASS_NAME, value="maji_send")
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", send[0])
          send[0].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
          send_link = driver.find_element(By.ID, value="link_OK")
          send_link.click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(wait_time)
        else:
          send = driver.find_element(By.ID, value="send_n")
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", send)
          send.click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(wait_time)
        time.sleep(wait_time)
        send_count += 1
        now = datetime.now().strftime('%m-%d %H:%M:%S')
        print(str(name) + ": pcmax、fst_mail マジ送信 " + str(maji_soushin) + " ~" + str(send_count) + "~ " + str(user_age) + " " + str(area_of_activity) + " " + str(user_name) + str(now))
        if send_count > send_limit:
          print("送信上限に達しました")
          return returnfoot_cnt
        
      
    try:
      driver.get("https://pcmax.jp/pcm/index.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
    except TimeoutException as e:
      print("TimeoutException")
      driver.refresh()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(2)
    return returnfoot_cnt


  # if send_count:
  #   return_list.append(f'{name}pcmax 足跡返し{send_count}件')

  # if len(return_list):
  #   return return_list, send_count
  # else:
  #   return 1, send_count
  
def returnfoot_fst_one_rap(sorted_pcmax, headless, send_limit, one_four_flug, mail_info):
  if one_four_flug:
    print("1時間後に実行します")
    time.sleep(3600)
  def timer(sec, functions):
    start_time = time.time() 
    for func in functions:
      try:
        return_func = func()
      except Exception as e:
        print(traceback.format_exc())
        return_func = 0
    elapsed_time = time.time() - start_time  # 経過時間を計算する
    while elapsed_time < sec:
      # make_footprints_repost_later()
      time.sleep(30)
      elapsed_time = time.time() - start_time  # 経過時間を計算する
      # print(f"待機中~~ {elapsed_time} ")
    
    return return_func
  
  wait_cnt = 3600 / len(sorted_pcmax)
  start_one_rap_time = time.time() 
  
  while True:
    try:
      temp_dir = func.get_the_temporary_folder("p_returnfoot_fst")
      driver,wait = func.test_get_driver(temp_dir, headless)
      send_cnt_list = []
      print("~~キャラリスト数~~~~~")
      print(len(sorted_pcmax))
      for pcmax_chara in sorted_pcmax:
        # if pcmax_chara['name'] != "ハル":
        #   continue
        func.change_tor_ip()
        try:
          return_func = timer(wait_cnt, [lambda: returnfoot_fst(pcmax_chara, driver, wait, send_limit)])
          send_cnt_list.append(f"{pcmax_chara['name']}: {return_func}")
        except Exception as e:
          print(f"エラー{pcmax_chara['name']}")
          print(traceback.format_exc())
          # func.send_error(chara, traceback.format_exc())
      if len(mail_info) and mail_info[0] != "" and mail_info[1] != "" and mail_info[2] != "":
        str_return_cnt_list = ",\n".join(send_cnt_list)
        title = "PCMAX足跡件数"
        func.send_mail(str_return_cnt_list, mail_info, title)
      # elapsed_time = time.time() - start_one_rap_time  
      # elapsed_timedelta = timedelta(seconds=elapsed_time)
      # elapsed_time_formatted = str(elapsed_timedelta)
      driver.quit()
      shutil.rmtree(temp_dir)
      time.sleep(2)
    except Exception as e:
      print(traceback.format_exc())
      driver.quit()
      shutil.rmtree(temp_dir)
      time.sleep(2)
    
def repost_30minute(schedule_data, sorted_pcmax, headless, detail_area_flug):
  def timer(sec, functions):
    start_time = time.time() 
    for func in functions:
      try:
        return_func = func()
      except Exception as e:
        print(traceback.format_exc())
        return_func = 0
    elapsed_time = time.time() - start_time  # 経過時間を計算する
    while elapsed_time < sec:
      # make_footprints_repost_later()
      time.sleep(30)
      elapsed_time = time.time() - start_time  # 経過時間を計算する
      # print(f"待機中~~ {elapsed_time} ")
    
    return return_func
  # 2時間で１周
  wait_cnt = 6000 / len(sorted_pcmax)

  start_one_rap_time = time.time() 
  
  while True:
    # 現在の時刻を取得
    now = datetime.now()

    # 午前6時から午後8時の間だけ実行
    if 6 <= now.hour < 20:
      temp_dir = func.get_the_temporary_folder("p_repost")
      driver,wait = func.test_get_driver(temp_dir, headless)
      for pcmax_chara in sorted_pcmax:
          func.change_tor_ip()
          # print(len(sorted_pcmax))
          # print(pcmax_chara["name"])
          # if pcmax_chara["name"] != "ハル":
          #   print(666)
          #   continue
          try:
              # ループ内で処理を実行
              return_func = timer(wait_cnt, [lambda: re_post(pcmax_chara, driver, wait, detail_area_flug)])
          except Exception as e:
              print(f"エラー{pcmax_chara['name']}")
              print(traceback.format_exc())
              # func.send_error(pcmax_chara, traceback.format_exc())
      driver.quit()
      shutil.rmtree(temp_dir)
      time.sleep(1)
    else:
        print("現在の時間帯は処理時間外です。午前6時から午後8時まで実行されます。")
    # 1分ごとに再チェック（処理負荷を下げるため）
    time.sleep(60)
  

  

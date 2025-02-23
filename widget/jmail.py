from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import random
import time
from selenium.webdriver.common.by import By
import os
import sys
import traceback
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from widget import func
from selenium.webdriver.support.select import Select
import sqlite3
import re
from datetime import datetime, timedelta
import difflib
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import base64
import requests

def login_jmail(driver, wait, login_id, login_pass):
  driver.delete_all_cookies()
  # https://mintj.com/msm/login/?adv=___36h1tmot02r12l8kxdtxx0b3z
  driver.get("https://mintj.com/msm/login/")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  wait_time = random.uniform(3, 6)
  time.sleep(2)
  id_form = driver.find_element(By.ID, value="loginid")
  id_form.send_keys(login_id)
  pass_form = driver.find_element(By.ID, value="pwd")
  pass_form.send_keys(login_pass)
  time.sleep(1)
  send_form = driver.find_element(By.ID, value="B1login")
  try:
    send_form.click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    error_msg = driver.find_elements(By.CLASS_NAME, value="errormsg")
    if len(error_msg):
      return False
    else:
      return True
  except TimeoutException as e:
    print("TimeoutException")
    driver.refresh()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    id_form = driver.find_element(By.ID, value="loginid")
    id_form.send_keys(login_id)
    pass_form = driver.find_element(By.ID, value="pwd")
    pass_form.send_keys(login_pass)
    time.sleep(1)
    send_form = driver.find_element(By.ID, value="B1login")
    send_form.click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    error_msg = driver.find_elements(By.CLASS_NAME, value="errormsg")
    if len(error_msg):
      return False
    else:
      return True
  

def re_post(driver, name):
  try:
    wait = WebDriverWait(driver, 15)
    dbpath = 'firstdb.db'
    conn = sqlite3.connect(dbpath)
    # SQLiteを操作するためのカーソルを作成
    cur = conn.cursor()
    # 順番
    # データ検索  
    cur.execute('SELECT * FROM jmail WHERE name = ?', (name,))
    for row in cur:
        # print(6666)
        # print(row)
        login_id = row[2]
        login_pass = row[3]
        post_title = row[4]
        post_content = row[5]
    login_jmail(driver, wait, login_id, login_pass)
    # メニューをクリック
    menu_icon = driver.find_elements(By.CLASS_NAME, value="menu-off")
    menu_icon[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    #  アダルト掲示板をクリック
    menu = driver.find_elements(By.CLASS_NAME, value="iconMenu")
    adult_post_menus = menu[0].find_elements(By.TAG_NAME, value="p")
    adult_post_menu = adult_post_menus[0].find_elements(By.XPATH, "//*[contains(text(), 'アダルト掲示板')]")
    adult_post_menu_link = adult_post_menu[0].find_element(By.XPATH, "./.")
    #  adult_post_menu_link.click()
    driver.get(adult_post_menu_link.get_attribute("href"))
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    #  投稿をクリック　color_variations_03
    post_icon = driver.find_elements(By.CLASS_NAME, value="color_variations_03")
    post_icon[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    #  コーナーを選択
    corner_select = driver.find_elements(By.NAME, value="CornerId")
    select = Select(corner_select[0])
    select.select_by_visible_text("今すぐあそぼっ")
    time.sleep(1)
    #  件名を入力
    post_title_input = driver.find_elements(By.NAME, value="Subj")
    post_title_input[0].clear()
    post_title_input[0].send_keys(post_title)
    time.sleep(1)
    #  メッセージを入力
    post_content_input = driver.find_elements(By.NAME, value="Comment")
    post_content_input[0].clear()
    post_content_input[0].send_keys(post_content)
    time.sleep(1)
    #  メール受信数を選択　Number of emails received
    select_recieve_number = driver.find_elements(By.NAME, value="ResMaxCount")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", select_recieve_number[0])
    time.sleep(1)
    select = Select(select_recieve_number[0])
    select.select_by_visible_text("5件")
    time.sleep(1)
    #  書き込む
    write_button = driver.find_elements(By.NAME, value="Bw")
    write_button[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)

    return True
  except Exception as e:
    print(f"掲示板再投稿エラー{name}")    
    return False


import sqlite3

def check_new_mail(driver, wait, jmail_info, try_cnt):
  name = jmail_info['name']
  login_id = jmail_info['login_id']
  password = jmail_info['password']
  mail_img = jmail_info['chara_image']
  # 画像データを取得してBase64にエンコード
  if mail_img:
    image_response = requests.get(f"https://meruopetyan.com/{mail_img}")
    image_base64 = base64.b64encode(image_response.content).decode('utf-8')
    # ローカルに一時的に画像ファイルとして保存
    image_filename = f"{name}_image.png"
    with open(image_filename, 'wb') as f:
        f.write(base64.b64decode(image_base64))
    # 画像の保存パスを取得
    image_path = os.path.abspath(image_filename)
    print(image_path)
  else:
    image_path = ""
    image_filename = None 
  # データベース接続とテーブル作成
  conn = sqlite3.connect('user_data.db')
  c = conn.cursor()
  # テーブル作成時に login_id と password を NULL を許容する
  c.execute('''
      CREATE TABLE IF NOT EXISTS jmail (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          login_id TEXT,
          password TEXT,
          send_list TEXT
      )
  ''')
  c.execute('SELECT * FROM jmail WHERE name = ? AND login_id = ? AND password = ?', (name, login_id, password))
  sqlite_jmail_result = c.fetchone()  
  if sqlite_jmail_result is None:
      # print("ローカルに合致するギャラデータなし")
      c.execute('SELECT * FROM jmail WHERE name = ?', (name,))
      conn.commit()
      sqlite_jmail_result = c.fetchone()
      # 名前で検索結果なし
      if sqlite_jmail_result is None:
        # print("ローカルに名前も合致するギャラデータなし")
        c.execute("INSERT INTO jmail (name, login_id, password, send_list) VALUES (?,?,?,?)", (name, login_id, password, ""))
        conn.commit()  
      else:
        # print("ローカルに名前だけ合致するギャラデータあり")
        c.execute("UPDATE jmail SET login_id = ?, password = ?, send_list = ? WHERE name = ?", (login_id, password, "", name))
        conn.commit()  
      submitted_users = []
  else:
    # print("ローカルに合致するギャラデータあり")
    submitted_users = sqlite_jmail_result[4] 
  conn.close()
  # print(f"送信履歴ありリスト")
  # print(submitted_users)
  fst_message = jmail_info['fst_message']
  return_foot_message = jmail_info['return_foot_message']
  second_message = jmail_info['conditions_message']
  if login_id == None or login_id == "":
    print(f"{name}のjmailキャラ情報を取得できませんでした")
    return ""
  login_flug = login_jmail(driver, wait, login_id, password)
  if not login_flug:
    print(f"jmail:{name}に警告画面が出ている可能性があります")
    return ""
  # メールアイコンをクリック
  mail_icon = driver.find_elements(By.CLASS_NAME, value="mail-off")
  link = mail_icon[0].find_element(By.XPATH, "./..")
  driver.get(link.get_attribute("href"))
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  if submitted_users is not None and submitted_users != [] :
    interacting_user_list = submitted_users.split()
  else:
    interacting_user_list = []
 
  interacting_users = driver.find_elements(By.CLASS_NAME, value="icon_sex_m")
  # 未読メールをチェック
  sended_mail = False
  return_list = []
  for interacting_user_cnt in range(len(interacting_users)):
    # interacting_userリストを取得
    interacting_user_name = interacting_users[interacting_user_cnt].text
    if "未読" in interacting_user_name:
      interacting_user_name = interacting_user_name.replace("未読", "")
    if "退会" in interacting_user_name:
      interacting_user_name = interacting_user_name.replace("退会", "")
    if " " in interacting_user_name:
      interacting_user_name = interacting_user_name.replace(" ", "")
    if "　" in interacting_user_name:
      interacting_user_name = interacting_user_name.replace("　", "")
    # 未読、退会以外でNEWのアイコンも存在してそう

    # NEWアイコンがあるかチェック
    new_icon = interacting_users[interacting_user_cnt].find_elements(By.TAG_NAME, value="img")
    if "未読" in interacting_users[interacting_user_cnt].text or len(new_icon):
    # deug
    # if "やん" in interacting_users[interacting_user_cnt].text:
      # 時間を取得　align_right
      parent_usr_info = interacting_users[interacting_user_cnt].find_element(By.XPATH, "./..")
      parent_usr_info = parent_usr_info.find_element(By.XPATH, "./..")
      next_element = parent_usr_info.find_element(By.XPATH, value="following-sibling::*[1]")
      current_year = datetime.now().year
      date_string = f"{current_year} {next_element.text}"
      date_format = "%Y %m/%d %H:%M" 
      date_object = datetime.strptime(date_string, date_format)
      now = datetime.today()
      elapsed_time = now - date_object
      print(interacting_users[interacting_user_cnt].text)
      print(f"メール到着からの経過時間{elapsed_time}")
      print(interacting_user_name)
      if elapsed_time >= timedelta(minutes=4):
        print("4分以上経過しています。")
        if interacting_user_name not in interacting_user_list:
          interacting_user_name = " " + interacting_user_name
          interacting_user_list.append(interacting_user_name)
        send_message = ""
        # リンクを取得
        link_element = interacting_users[interacting_user_cnt].find_element(By.XPATH, "./..")
        driver.get(link_element.get_attribute("href"))
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
        send_by_user = driver.find_elements(By.CLASS_NAME, value="balloon_left")
        send_by_user_message = send_by_user[0].find_elements(By.CLASS_NAME, value="balloon")[0].text
        # 相手からのメッセージが何通目か確認する
        if not sended_mail:
          send_by_me = driver.find_elements(By.CLASS_NAME, value="balloon_right")
          # print(888)
          # print(len(send_by_me))
          if len(send_by_me) == 0:
            send_message = fst_message
          elif len(send_by_me) == 1:
            send_message = second_message
          elif len(send_by_me) == 2:
            print("捨てメアドに通知")
            print(f"{name}   {login_id}  {password} : {interacting_user_name}  ;;;;{send_by_user_message}")
            return_message = f"{name}jmail,{login_id}:{password}\n{interacting_user_name}「{send_by_user_message}」"
            return_list.append(return_message)  
            print("捨てメアドに、送信しました")
        if send_message:
          # 返信するをクリック
          res_do = driver.find_elements(By.CLASS_NAME, value="color_variations_05")
          res_do[1].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
          # メッセージを入力　name=comment
          text_area = driver.find_elements(By.NAME, value="comment")
          # text_area[0].send_keys(send_message)
          script = "arguments[0].value = arguments[1];"
          driver.execute_script(script, text_area[0], send_message)
          time.sleep(4)
          # 画像があれば送信
          if send_message == fst_message and image_path:
            img_input = driver.find_elements(By.NAME, value="image1")
            img_input[0].send_keys(image_path)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
          send_button = driver.find_elements(By.NAME, value="sendbutton")
          send_button[0].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
        # メール一覧に戻る　message_back
        back_parent = driver.find_elements(By.CLASS_NAME, value="message_back")
        back = back_parent[0].find_elements(By.TAG_NAME, value="a")
        back[0].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
        interacting_users = driver.find_elements(By.CLASS_NAME, value="icon_sex_m")  
  pager = driver.find_elements(By.CLASS_NAME, value="pager")
  if len(pager):
    pager_link = pager[0].find_elements(By.TAG_NAME, value="a")
   
    for i in range(len(pager_link)):
      next_pager = pager_link[i]
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", next_pager)
      next_pager.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(2)
      interacting_users = driver.find_elements(By.CLASS_NAME, value="icon_sex_m")
      for interacting_user_cnt in range(len(interacting_users)):
      # interacting_userリストを取得
        interacting_user_name = interacting_users[interacting_user_cnt].text
        if "未読" in interacting_user_name:
          interacting_user_name = interacting_user_name.replace("未読", "")
        if "退会" in interacting_user_name:
          interacting_user_name = interacting_user_name.replace("退会", "")
        if " " in interacting_user_name:
          interacting_user_name = interacting_user_name.replace(" ", "")
        if "　" in interacting_user_name:
          interacting_user_name = interacting_user_name.replace("　", "")
        # 未読、退会以外でNEWのアイコンも存在してそう
        # NEWアイコンがあるかチェック
        new_icon = interacting_users[interacting_user_cnt].find_elements(By.TAG_NAME, value="img")
        if "未読" in interacting_users[interacting_user_cnt].text or len(new_icon):          
          # 時間を取得　align_right
          parent_usr_info = interacting_users[interacting_user_cnt].find_element(By.XPATH, "./..")
          parent_usr_info = parent_usr_info.find_element(By.XPATH, "./..")
          next_element = parent_usr_info.find_element(By.XPATH, value="following-sibling::*[1]")
          current_year = datetime.now().year
          date_string = f"{current_year} {next_element.text}"
          date_format = "%Y %m/%d %H:%M" 
          date_object = datetime.strptime(date_string, date_format)
          now = datetime.today()   
          elapsed_time = now - date_object
          print(interacting_users[interacting_user_cnt].text)
          print(f"メール到着からの経過時間{elapsed_time}")
          if elapsed_time >= timedelta(minutes=4):
            print("4分以上経過しています。")
            # ユーザー名を保存
            if interacting_user_name not in interacting_user_list:
              interacting_user_name = " " + interacting_user_name
              interacting_user_list.append(interacting_user_name)
            send_message = ""
            # リンクを取得
            link_element = interacting_users[interacting_user_cnt].find_element(By.XPATH, "./..")
            driver.get(link_element.get_attribute("href"))
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
            send_by_user = driver.find_elements(By.CLASS_NAME, value="balloon_left")
            send_by_user_message = send_by_user[0].find_elements(By.CLASS_NAME, value="balloon")[0].text
            # 相手からのメッセージが何通目か確認する
            if not sended_mail:
              send_by_me = driver.find_elements(By.CLASS_NAME, value="balloon_right")
              if len(send_by_me) == 0:
                send_message = fst_message
                interacting_user_list.append(user_name)
              elif len(send_by_me) == 1:
                send_message = second_message
              elif second_message in send_by_me[0].text:
                print("捨てメアドに通知")
                print(f"{name}   {login_id}  {password} : {interacting_user_name}  ;;;;{send_by_user_message}")
                return_message = f"{name}jmail,{login_id}:{password}\n{interacting_user_name}「{send_by_user_message}」"
                return_list.append(return_message)  
                print("捨てメアドに、送信しました")
            if send_message:
              # 返信するをクリック
              res_do = driver.find_elements(By.CLASS_NAME, value="color_variations_05")
              res_do[1].click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
              # メッセージを入力　name=comment
              text_area = driver.find_elements(By.NAME, value="comment")
              # text_area[0].send_keys(send_message)
              script = "arguments[0].value = arguments[1];"
              driver.execute_script(script, text_area[0], send_message)
              time.sleep(4)
              # 画像があれば送信
              if send_message == fst_message and image_path:              
                img_input = driver.find_elements(By.NAME, value="image1")
                img_input[0].send_keys(image_path)
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(2)
              
            # メール一覧に戻る　message_back
            back_parent = driver.find_elements(By.CLASS_NAME, value="message_back")
            back = back_parent[0].find_elements(By.TAG_NAME, value="a")
            back[0].click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
        pager = driver.find_elements(By.CLASS_NAME, value="pager")
        if len(pager):
          pager_link = pager[0].find_elements(By.TAG_NAME, value="a")
  # ///////////////初めまして送信///////////////////////////////////////////////
  fst_send_limit = 1
  returnfoot_send_limit = 1
  
  if try_cnt % 12 == 0:
    #メニューをクリック
    menu_icon = driver.find_elements(By.CLASS_NAME, value="menu-off")
    menu_icon[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    menu = driver.find_elements(By.CLASS_NAME, value="iconMenu")
    #プロフ検索をクリック
    foot_menus = menu[0].find_elements(By.TAG_NAME, value="p")
    foot_menu = foot_menus[0].find_elements(By.XPATH, "//*[contains(text(), 'プロフ検索')]")
    foot_menu_link = foot_menu[0].find_element(By.XPATH, "./..")
    driver.get(foot_menu_link.get_attribute("href"))
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    users_elem = driver.find_elements(By.CLASS_NAME, value="search_list_col")
    fst_mail_cnt = 0
    for i in range(len(users_elem)):
      user_name = users_elem[i].find_element(By.CLASS_NAME, value="prof_name").text
      # 送信済かチェック
      if user_name not in interacting_user_list:
        interacting_user_list.append(user_name)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", users_elem[i])
        users_elem[i].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
        # 自己紹介文チェック
        profile = driver.find_elements(By.CLASS_NAME, value="prof_pr")
        if len(profile):
          profile = profile[0].text.replace(" ", "").replace("\n", "")
          if '通報' in profile or '業者' in profile:
            print('自己紹介文に危険なワードが含まれていました')
            interacting_user_list.append(user_name)
            driver.back()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
            continue
        text_area = driver.find_elements(By.ID, value="textarea")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area[0])
        time.sleep(1)
        script = "arguments[0].value = arguments[1];"
        driver.execute_script(script, text_area[0], fst_message)
        time.sleep(4)
        # 画像があれば送付
        if image_path:
          upload_file = driver.find_element(By.ID, "upload_file")
          # upload_file.send_keys("/Users/yamamotokenta/Desktop/myprojects/mail_operator/widget/picture/chara_img01.jpg")
          upload_file.send_keys(image_path)
          # file_icon
          file_label = driver.find_element(By.ID, "file_icon")
          class_attribute = file_label.get_attribute("class")
          while not "file_img" in class_attribute.split():
            time.sleep(1)
            class_attribute = file_label.get_attribute("class")
        send_btn = driver.find_elements(By.ID, value="message_send")
        driver.execute_script("arguments[0].click();", send_btn[0])
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
        send_complete_element = driver.find_elements(By.ID, value="modal_title")
        send_complete = send_complete_element[0].text
        wait_cnt = 0
        send_status = True
        while send_complete != "送信完了しました":
          time.sleep(4)
          print(send_complete)
          wait_cnt += 1
          if wait_cnt > 3:
            print("ロード時間が15秒以上かかっています")
            print("送信失敗しました")
            send_status = False
            break
          send_complete = send_complete_element[0].text
        if send_status:
          fst_mail_cnt += 1
          print(f"jmail 1st_mail {name} : {fst_mail_cnt}件送信")
        if fst_mail_cnt == fst_send_limit:
          print("送信上限に達しました")
          break
        driver.back()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
        users_elem = driver.find_elements(By.CLASS_NAME, value="search_list_col")

    # /////////////////////////あしあと返し
    # #メニューをクリック
    # menu_icon = driver.find_elements(By.CLASS_NAME, value="menu-off")
    # driver.execute_script("arguments[0].click();", menu_icon[0])
    # # menu_icon[0].click()
    # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    # time.sleep(2)
    # menu = driver.find_elements(By.CLASS_NAME, value="iconMenu")
    # #足跡をクリック
    # foot_menus = menu[0].find_elements(By.TAG_NAME, value="p")
    # foot_menu = foot_menus[0].find_elements(By.XPATH, "//*[contains(text(), 'あしあと')]")
    # foot_menu_link = foot_menu[0].find_element(By.XPATH, "./..")
    # driver.get(foot_menu_link.get_attribute("href"))
    # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    # time.sleep(2)
    # name_element = driver.find_elements(By.CLASS_NAME, value="icon_sex_m")
    # print(111111111)
    # print(len(name_element))
    # for foot_return_cnt in range(len(name_element)):
    #   # 年齢を取得
    #   next_to_element = name_element[foot_return_cnt].find_element(By.XPATH, "following-sibling::*[1]")
    #   user_age = next_to_element.text
    #   # print(next_to_element.text)
    #   age_list = ["18~21", "22~25", "26~29", "30~34", ]
    #   if any(age in user_age.replace("～", "~") for age in age_list):
    #     # print("age_list の中の文字列が string に含まれています。")
    #     # 地域を判定
    #     next_to_next_element = name_element[foot_return_cnt].find_element(By.XPATH, "following-sibling::*[2]")
    #     if "大阪" in next_to_next_element.text or "兵庫" in next_to_next_element.text or "石川" in next_to_next_element.text:
    #       continue
    #     foot_user_name = name_element[foot_return_cnt].text
    #     if "未読" in foot_user_name:
    #         foot_user_name = foot_user_name.replace("未読", "")
    #     if "退会" in foot_user_name:
    #       foot_user_name = foot_user_name.replace("退会", "")
    #     if " " in foot_user_name:
    #       foot_user_name = foot_user_name.replace(" ", "")
    #     if "　" in foot_user_name:
    #       foot_user_name = foot_user_name.replace("　", "")
    #     # 送信済かチェック
    #     # if foot_user_name not in interacting_user_list:
    #     if True:#DEBUG 
    #       send_status = True
    #       # print(f"{foot_user_name}はメールリストになかった")
    #       foot_user_link = name_element[foot_return_cnt].find_element(By.XPATH, "./..")
    #       driver.get(foot_user_link.get_attribute("href"))
    #       wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    #       time.sleep(2)
    #       # 自己紹介文チェック
    #       profile = driver.find_elements(By.CLASS_NAME, value="prof_pr")
    #       if len(profile):
    #         profile = profile[0].text.replace(" ", "").replace("\n", "")
    #         if '通報' in profile or '業者' in profile:
    #           print('自己紹介文に危険なワードが含まれていました')
    #           interacting_user_list.append(foot_user_name)
    #           send_status = False
    #       if send_status:
    #         text_area = driver.find_elements(By.ID, value="textarea")
    #         driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area[0])
    #         time.sleep(1)
    #         # text_area[0].send_keys(return_foot_message)
    #         script = "arguments[0].value = arguments[1];"
    #         driver.execute_script(script, text_area[0], return_foot_message)
    #         time.sleep(4)
    #         # 画像があれば送付
    #         if image_path:
    #           img_input = driver.find_elements(By.ID, value="upload_file")
    #           img_input[0].send_keys(image_path)
    #           wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    #           time.sleep(2)
    #         send_btn = driver.find_elements(By.ID, value="message_send")
    #         driver.execute_script("arguments[0].click();", send_btn[0])
    #         wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    #         time.sleep(2)
    #         send_complete_element = driver.find_elements(By.ID, value="modal_title")
    #         send_complete = send_complete_element[0].text
    #         # print(888)
    #         # print(send_complete)
    #         wait_cnt = 0
    #         while send_complete != "送信完了しました":
    #           time.sleep(4)
    #           # print(send_complete)
    #           wait_cnt += 1
    #           if wait_cnt > 4:
    #             print("ロード時間が15秒以上かかっています")
    #             print("送信失敗しました")
    #             send_status = False
    #             break
    #           send_complete = send_complete_element[0].text
    #         if send_status:
    #           # ユーザー名を保存
    #           interacting_user_list.append(foot_user_name)
    #           returnfoot_send_limit += 1
    #           print(f"jmail足跡返し {name} {user_age}: {returnfoot_send_limit}件送信")
    #           if fst_mail_cnt == returnfoot_send_limit:
    #             print(f"足跡返し送信上限に達しました")
    #             break
    #         # あしあとリストに戻る
    #         driver.back()
    #         wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    #         time.sleep(2)
    #         name_element = driver.find_elements(By.CLASS_NAME, value="icon_sex_m")
  
  # interacting_user_listを保存
  print(f"送信済ユーザーリスト {len(interacting_user_list)}人")
  print(interacting_user_list)
  send_list_string = " ".join(interacting_user_list)
  conn = sqlite3.connect('user_data.db')
  c = conn.cursor()
  c.execute("UPDATE jmail SET send_list = ? WHERE name = ?", (send_list_string, name))
  conn.commit()
  conn.close()
  if image_filename:
    if os.path.exists(image_filename):
        os.remove(image_filename)
  if len(return_list):
    return return_list
  else:
    return ""

def make_footprints(name, jmail_id, jmail_pass, driver, wait):
  login_jmail(driver, wait, jmail_id, jmail_pass)
  #メニューをクリック
  menu_icon = driver.find_elements(By.CLASS_NAME, value="menu-off")
  menu_icon[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  menu = driver.find_elements(By.CLASS_NAME, value="iconMenu")
  #プロフ検索をクリック
  foot_menus = menu[0].find_elements(By.TAG_NAME, value="p")
  foot_menu = foot_menus[0].find_elements(By.XPATH, "//*[contains(text(), 'プロフ検索')]")
  foot_menu_link = foot_menu[0].find_element(By.XPATH, "./..")
  driver.get(foot_menu_link.get_attribute("href"))
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  # 詳しく検索
  detail_query = driver.find_elements(By.ID, value="ac2h2")
  detail_query[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  # 年齢を選択
  age18_21 = driver.find_elements(By.XPATH, '//label[@for="CheckAge1"]')
  age18_21[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(1)
  age22_25 = driver.find_elements(By.XPATH, '//label[@for="CheckAge2"]')
  age22_25[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(1)
  age26_29 = driver.find_elements(By.XPATH, '//label[@for="CheckAge3"]')
  age26_29[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(1)
  age30_34 = driver.find_elements(By.XPATH, '//label[@for="CheckAge4"]')
  age30_34[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(1)
  # 身長を選択
  height150 = driver.find_elements(By.XPATH, '//label[@for="CheckHeight1"]')
  height150[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(1)
  height154 = driver.find_elements(By.XPATH, '//label[@for="CheckHeight2"]')
  height154[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(1)
  height159 = driver.find_elements(By.XPATH, '//label[@for="CheckHeight3"]')
  height159[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(1)
  height164 = driver.find_elements(By.XPATH, '//label[@for="CheckHeight4"]')
  height164[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(1)
  height169 = driver.find_elements(By.XPATH, '//label[@for="CheckHeight5"]')
  height169[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(1)

  # 地域を選択
  tokyo_state = selected_state = driver.find_elements(By.XPATH, '//label[@for="CheckState-9"]')
  tokyo_state[0].click()
  area_id_dict = {"東京都":"CheckState-8", "神奈川県":"CheckState-9",}
  random_selected = random.choice(list(area_id_dict.values()))
  xpath = f'//label[@for="{random_selected}"]'
  selected_state = driver.find_elements(By.XPATH, xpath)
  background_color = selected_state[0].value_of_css_property('background-color')
  
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", selected_state[0])
  if background_color == "rgba(0, 0, 0, 0)":
    selected_state[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
  # 検索する
  query_submit = driver.find_elements(By.ID, value="button")
  query_submit[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(100)
  

   
   

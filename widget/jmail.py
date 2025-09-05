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
import shutil
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import uuid
from PIL import Image

def catch_warning(driver, wait):
  loader = driver.find_elements(By.ID, value="loader")
  if len(loader):
    driver.refresh() 
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
  # 警告画面が表示されているか確認
  warning_element = driver.find_elements(By.CLASS_NAME, value="karte-widget__container")
  if len(warning_element):
    print("広告が表示されています。")
    driver.refresh()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    return True
  
  errormsg = driver.find_elements(By.CLASS_NAME, value="errormsg")
  if len(errormsg):
    print("警告画面が表示されています。")
    print(errormsg[0].text)
    if "電話番号・会員IDを正しく入力してください。" in errormsg[0].text:
      print("ログアウトしています")
      return False
    return True
  
def encode_img(name, mail_img):
  # 画像データを取得してBase64にエンコード
  if mail_img:
    image_response = requests.get(f"https://meruopetyan.com/{mail_img}")
    # image_response = requests.get(f"http://127.0.0.1:8000/{mail_img}")
    image_base64 = base64.b64encode(image_response.content).decode('utf-8')
    # ローカルに一時的に画像ファイルとして保存
    image_filename = f"{name}_image.png"
    with open(image_filename, 'wb') as f:
        f.write(base64.b64decode(image_base64))
    # 画像の保存パスを取得
    image_path = os.path.abspath(image_filename)
  else:
    image_path = ""
    image_filename = None 
  return image_filename, image_path

def login_jmail(driver, wait, login_id, login_pass):
  driver.delete_all_cookies()
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
  

def start_jmail_drivers(jmail_list, headless, base_path):
  drivers = {}
  try:
    for i in jmail_list:
      name = i["name"]
      if name != "えりか":
        continue
      profile_path = os.path.join(base_path, f"{i['name']}_{uuid.uuid4().hex}")

      # profile_path = os.path.join(base_path, i["name"])
      if os.path.exists(profile_path):
        shutil.rmtree(profile_path)  # フォルダごと削除
        os.makedirs(profile_path, exist_ok=True)  
      # iPhone14
      user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/537.36"
      driver,wait = func.get_multi_driver(profile_path, headless, user_agent)
      
      login_flug = login_jmail(driver, wait, i["login_id"], i["password"])
      drivers[i["name"]] = {"name":i["name"], "login_id":i["login_id"], "password":i["password"], "post_title":i["post_title"], "post_contents":i["post_contents"],"driver": driver, "wait": wait, "fst_message": i["fst_message"], "return_foot_message":i["return_foot_message"], "conditions_message":i["second_message"], "mail_img":i["chara_image"], "submitted_users":i["submitted_users"],"second_message":i["second_message"], "chara_image":i["chara_image"], "mail_address_image":i["mail_address_image"], "submitted_users":i["submitted_users"], "mail_address":i["mail_address"]}
    return drivers
  except KeyboardInterrupt:
    # Ctrl+C が押された場合
    print("ログイン中にプログラムが Ctrl+C により中断qされました。")
    func.close_all_drivers(drivers)
  except Exception as e:
    # 予期しないエラーが発生した場合
    print("ログイン中〜〜〜〜〜〜〜〜〜〜〜〜〜〜")
    func.close_all_drivers(drivers)
    print("エラーが発生しました:", e)
    traceback.print_exc()


def check_mail(name, jmail_info, driver, wait, mail_info):
  login_id = jmail_info['login_id']
  password = jmail_info['password']
  fst_message = jmail_info['fst_message']
  second_message = jmail_info['second_message']
  submitted_users = jmail_info['submitted_users']
  mail_img = jmail_info['chara_image']
  mail_address_image = jmail_info['mail_address_image']
  submitted_users = jmail_info['submitted_users']
  gmail_address = jmail_info['mail_address']
  gmail_password = jmail_info['gmail_password']
  from_mypost = False
  # login_flug = login_jmail(driver, wait, login_id, password)
  # if not login_flug:
  #   print(f"jmail:{name}に警告画面が出ている可能性があります")
  #   return ""
  if fst_message == "":
    print(f"{name}のjmailキャラ情報に1stメッセージが設定されていません")
    return submitted_users
  driver.get("https://mintj.com/msm/mainmenu/?sid=")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(0.7)
  warning_flug = catch_warning(driver, wait)
  if warning_flug is False:
    print(f"jmail:{name}に警告画面が出ている可能性があります")
    return submitted_users
  # メールアイコンをクリック
  mail_icon = driver.find_elements(By.CLASS_NAME, value="mail-off")
  link = mail_icon[0].find_element(By.XPATH, "./..")
  driver.get(link.get_attribute("href"))
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  message_tab = driver.find_element(By.CLASS_NAME, value="message_tab")
  link_message_tabs = message_tab.find_elements(By.TAG_NAME, value="a")
  for link_message_tab in link_message_tabs:
    if "未読" in link_message_tab.text:
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", link_message_tab)
      link_message_tab.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(2)
      break
  interacting_users = driver.find_elements(By.CLASS_NAME, value="icon_sex_m")
  # 未読メールをチェック
  sended_mail = False
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
    if "テラ" in interacting_users[interacting_user_cnt].text or len(new_icon):
      submitted_users.append(interacting_user_name)
    if "未読" in interacting_users[interacting_user_cnt].text or len(new_icon):
    # deug
    # if True:
      # 時間を取得　
      parent_usr_info = interacting_users[interacting_user_cnt].find_element(By.XPATH, "./..")
      parent_usr_info = parent_usr_info.find_element(By.XPATH, "./..")
      next_element = parent_usr_info.find_element(By.XPATH, value="following-sibling::*[1]")
      current_year = datetime.now().year
      date_string = f"{current_year} {next_element.text}"
      date_format = "%Y %m/%d %H:%M" 
      date_object = datetime.strptime(date_string, date_format)
      now = datetime.today()
      elapsed_time = now - date_object
      # print(interacting_users[interacting_user_cnt].text)
      # print(f"メール到着からの経過時間{elapsed_time}")
      # print(interacting_user_name)

      # 年齢を取得
      age_element = driver.find_elements(By.CLASS_NAME, value="list_subtext")[interacting_user_cnt]
      match = re.search(r"\d+～\d+", age_element.text)
      if match:
        age_range = match.group()
        # 「～」で分割して数値に変換
        min_age, max_age = map(int, age_range.split("～"))
        if max_age <= 30:
          print("30歳以下です")
          young_flag = True
        else:
          print("31歳以上です")
          young_flag = False
      # if True:
      if elapsed_time >= timedelta(minutes=4):
        print("4分以上経過しています。")
        if interacting_user_name not in submitted_users:
          submitted_users.append(interacting_user_name)
        send_message = ""
        ojisan_flag = False
        # リンクを取得
        link_element = interacting_users[interacting_user_cnt].find_element(By.XPATH, "./..")
        driver.get(link_element.get_attribute("href"))
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
        send_by_user = driver.find_elements(By.CLASS_NAME, value="balloon_left")
        send_by_user_message = send_by_user[0].find_elements(By.CLASS_NAME, value="balloon")[0].text
        # メールアドレスがあるか確認
        received_mail = send_by_user_message.replace("＠", "@").replace("あっとまーく", "@").replace("アットマーク", "@").replace("\n", "")
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        email_list = re.findall(email_pattern, received_mail)
        if email_list:
          print(f"メールアドレスが見つかりました: {email_list}")
          if name == "つむぎ" or "icloud.com" in received_mail:
            # print("icloud.comが含まれています")
            icloud_text = "メール送ったんですけど、ブロックされちゃって届かないのでこちらのアドレスにお名前添えて送ってもらえますか？\n" + gmail_address
            try:
              # 返信するをクリック
              res_do = driver.find_elements(By.CLASS_NAME, value="color_variations_05")
              res_do[1].click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
              # メッセージを入力　name=comment
              text_area = driver.find_elements(By.NAME, value="comment")
              script = "arguments[0].value = arguments[1];"
              driver.execute_script(script, text_area[0], send_message)
              time.sleep(4)
              
              send_button = driver.find_elements(By.NAME, value="sendbutton")
              send_button[0].click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
            except Exception:
              pass
        else:
          # 掲示板からきたか判定
          color_variations_03 = driver.find_elements(By.CLASS_NAME, value="color_variations_03")
          if len(color_variations_03):
            for i in color_variations_03:
              if "元の投稿を見る" in i.text:
                print(f"{interacting_user_name}さんは掲示板から来た")
                from_mypost = True
                break
        # 相手からのメッセージが何通目か確認する
        if not sended_mail:
          send_by_me = driver.find_elements(By.CLASS_NAME, value="balloon_right")
          my_length = len(send_by_me)
          if my_length == 0:
            if young_flag:
              send_message = fst_message
              if from_mypost:
                send_message = second_message
              if mail_img:
                image_filename, image_path = encode_img(name, mail_img)
              else:
                image_filename, image_path = "", ""
            else:
              ojisan_flag = True
              print("おじさん処理")     
          elif my_length == 1:
            if  not from_mypost:
              send_message = second_message
              if mail_address_image:
                image_filename, image_path = encode_img(name, mail_address_image)
              else:
                image_filename, image_path = "", ""
            else:
              print("捨てメアドに通知")
              print(f"{name}   {login_id}  {password} : {interacting_user_name}  ;;;;{send_by_user_message}")
              return_message = f"{name}jmail,{login_id}:{password}\n{interacting_user_name}「{send_by_user_message}」"
              func.send_mail(
                f"{name}jmail",
                mail_info, 
                return_message, 
                )
              print("捨てメアドに、送信しました")
              image_path = ""
              image_filename = ""
          elif my_length >= 2:
            print("捨てメアドに通知")
            print(f"{name}   {login_id}  {password} : {interacting_user_name}  ;;;;{send_by_user_message}")
            return_message = f"{name}jmail,{login_id}:{password}\n{interacting_user_name}「{send_by_user_message}」"
            func.send_mail(
              f"{name}jmail",
              mail_info, 
              return_message, 
              )
            print("捨てメアドに、送信しました")
            image_path = ""
            image_filename = ""
        
        if send_message:
          # 返信するをクリック
          res_do = driver.find_elements(By.CLASS_NAME, value="color_variations_05")
          res_do[1].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
          # メッセージを入力　name=comment
          text_area = driver.find_elements(By.NAME, value="comment")
          script = "arguments[0].value = arguments[1];"
          driver.execute_script(script, text_area[0], send_message)
          time.sleep(4)
          # 画像があれば送信 
          if image_path:
            img_input = driver.find_elements(By.NAME, value="image1")
            img_input[0].send_keys(image_path)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
          send_button = driver.find_elements(By.NAME, value="sendbutton")
          send_button[0].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
          # ローディングが終わるのを一定時間待って、待機後リロードしてメッセージが遅れたか確認
        if ojisan_flag:
          user_links = driver.find_elements(By.CLASS_NAME, value="icon_sex_m")
          for user_link in user_links:
            if name != user_link.text:
              user_link.find_element(By.TAG_NAME, value="a").click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
              catch_warning(driver, wait)
              # スクショして送信
              driver.save_screenshot("screenshot.png")
              # 圧縮（JPEG化＋リサイズ＋品質調整）
              compressed_path = func.compress_image("screenshot.png")  # 例: screenshot2_compressed.jpg ができる
              title = f"{name}jmail おじさんメッセージ"
              text = send_by_user_message   
              # メール送信
              if mail_info:
                func.send_mail(text, mail_info, title,  compressed_path)
              for p in ["screenshot.png", compressed_path]:
                try:
                  if os.path.exists(p):
                    os.remove(p)
                except Exception as e:
                  print(f"⚠️ 後処理で削除失敗: {p} -> {e}")
              break
              
          driver.back()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
        # メール一覧に戻る
        try:
          catch_warning(driver, wait)
          back_parent = driver.find_elements(By.CLASS_NAME, value="message_back")
          back = back_parent[0].find_elements(By.TAG_NAME, value="a")
          back[0].click()
        except StaleElementReferenceException:
          print("⚠️ back要素がstaleでした。再取得します...")
          time.sleep(1)
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
      catch_warning(driver, wait)
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
          # 年齢を取得
          age_element = driver.find_elements(By.CLASS_NAME, value="list_subtext")[interacting_user_cnt]
          match = re.search(r"\d+～\d+", age_element.text)
          if match:
            age_range = match.group()
            # 「～」で分割して数値に変換
            min_age, max_age = map(int, age_range.split("～"))
            if max_age <= 30:
              print("30歳以下です")
              young_flag = True
            else:
              print("31歳以上です")
              young_flag = False
          # print(interacting_users[interacting_user_cnt].text)
          # print(f"メール到着からの経過時間{elapsed_time}")
          if elapsed_time >= timedelta(minutes=4):
            print("4分以上経過しています。")
            # ユーザー名を保存
            if interacting_user_name not in submitted_users:
              submitted_users.append(interacting_user_name)
            send_message = ""
            # リンクを取得
            link_element = interacting_users[interacting_user_cnt].find_element(By.XPATH, "./..")
            driver.get(link_element.get_attribute("href"))
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
            send_by_user = driver.find_elements(By.CLASS_NAME, value="balloon_left")
            send_by_user_message = send_by_user[0].find_elements(By.CLASS_NAME, value="balloon")[0].text
            # メールアドレスがあるか確認
            received_mail = send_by_user_message.replace("＠", "@").replace("あっとまーく", "@").replace("アットマーク", "@").replace("\n", "")
            email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
            email_list = re.findall(email_pattern, received_mail)
            if email_list:
              print(f"メールアドレスが見つかりました: {email_list}")
              if name == "つむぎ" or "icloud.com" in received_mail:
                # print("icloud.comが含まれています")
                icloud_text = "メール送ったんですけど、ブロックされちゃって届かないのでこちらのアドレスにお名前添えて送ってもらえますか？\n" + gmail_address
                try:
                  # 返信するをクリック
                  res_do = driver.find_elements(By.CLASS_NAME, value="color_variations_05")
                  res_do[1].click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(2)
                  # メッセージを入力　name=comment
                  text_area = driver.find_elements(By.NAME, value="comment")
                  script = "arguments[0].value = arguments[1];"
                  driver.execute_script(script, text_area[0], send_message)
                  time.sleep(4)
                  
                  send_button = driver.find_elements(By.NAME, value="sendbutton")
                  send_button[0].click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(2)
                except Exception:
                  pass
            else:
              # 掲示板からきたか判定
              color_variations_03 = driver.find_elements(By.CLASS_NAME, value="color_variations_03")
              if len(color_variations_03):
                for i in color_variations_03:
                  if "元の投稿を見る" in i.text:
                    print(f"{interacting_user_name}さんは掲示板から来た")
                    from_mypost = True
                    break
            # 相手からのメッセージが何通目か確認する
            if not sended_mail:
              send_by_me = driver.find_elements(By.CLASS_NAME, value="balloon_right")
              if from_mypost:
                my_length = len(send_by_me) + 1
              else:
                my_length = len(send_by_me)
              if my_length == 0:
                if young_flag:
                  send_message = fst_message
                  if mail_img:
                    image_filename, image_path = encode_img(name, mail_img)
                  else:
                    image_filename, image_path = "", ""
                else:
                  send_message = ""
                  print("おじさん処理")
                  
              elif my_length == 1:
                send_message = second_message
                if mail_address_image:
                  image_filename, image_path = encode_img(name, mail_address_image)
                else:
                  image_filename, image_path = "", ""
              elif my_length >= 2:
                print("捨てメアドに通知")
                print(f"{name}   {login_id}  {password} : {interacting_user_name}  ;;;;{send_by_user_message}")
                return_message = f"{name}jmail,{login_id}:{password}\n{interacting_user_name}「{send_by_user_message}」"
                func.send_mail(
                  f"{name}jmail",
                  mail_info, 
                  return_message, 
                  )
                print("捨てメアドに、送信しました")
                image_path = ""
                image_filename = ""
            
            if send_message:
              # 返信するをクリック
              res_do = driver.find_elements(By.CLASS_NAME, value="color_variations_05")
              res_do[1].click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
              # メッセージを入力　name=comment
              text_area = driver.find_elements(By.NAME, value="comment")
              script = "arguments[0].value = arguments[1];"
              driver.execute_script(script, text_area[0], send_message)
              time.sleep(4)
              # 画像があれば送信 
              if image_path:
                img_input = driver.find_elements(By.NAME, value="image1")
                img_input[0].send_keys(image_path)
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(2)
              send_button = driver.find_elements(By.NAME, value="sendbutton")
              send_button[0].click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
              # ローディングが終わるのを一定時間待って、待機後リロードしてメッセージが遅れたか確認
            else:
              user_links = driver.find_elements(By.CLASS_NAME, value="icon_sex_m")
              for user_link in user_links:
                if name != user_link.text:
                  user_link.find_element(By.TAG_NAME, value="a").click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(2)
                  catch_warning(driver, wait)
                  # スクショして送信
                  driver.save_screenshot("screenshot.png")
                  # 圧縮（JPEG化＋リサイズ＋品質調整）
                  compressed_path = func.compress_image("screenshot.png")  # 例: screenshot2_compressed.jpg ができる
                  title = f"{name}jmail おじさんメッセージ"
                  text = send_by_user_message   
                  # メール送信
                  if mail_info:
                    func.send_mail(text, mail_info, title,  compressed_path)
                  for p in ["screenshot.png", compressed_path]:
                    try:
                      if os.path.exists(p):
                        os.remove(p)
                    except Exception as e:
                      print(f"⚠️ 後処理で削除失敗: {p} -> {e}")
                  break
            # メール一覧に戻る　message_back
            back_parent = driver.find_elements(By.CLASS_NAME, value="message_back")
            back = back_parent[0].find_elements(By.TAG_NAME, value="a")
            back[0].click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
        pager = driver.find_elements(By.CLASS_NAME, value="pager")
        if len(pager):
          pager_link = pager[0].find_elements(By.TAG_NAME, value="a")
  return submitted_users      
  

# # sqlite version
# def check_new_mail(driver, wait, jmail_info, try_cnt):
#   name = jmail_info['name']
#   login_id = jmail_info['login_id']
#   password = jmail_info['password']
#   mail_img = jmail_info['chara_image']
#   if mail_img:
#     image_path = encode_img(name, mail_img)
 
#   sqlite_jmail_result = c.fetchone()  
#   if sqlite_jmail_result is None:
#       # print("ローカルに合致するギャラデータなし")
#       c.execute('SELECT * FROM jmail WHERE name = ?', (name,))
#       conn.commit()
#       sqlite_jmail_result = c.fetchone()
#       # 名前で検索結果なし
#       if sqlite_jmail_result is None:
#         # print("ローカルに名前も合致するギャラデータなし")
#         c.execute("INSERT INTO jmail (name, login_id, password, send_list) VALUES (?,?,?,?)", (name, login_id, password, ""))
#         conn.commit()  
#       else:
#         # print("ローカルに名前だけ合致するギャラデータあり")
#         c.execute("UPDATE jmail SET login_id = ?, password = ?, send_list = ? WHERE name = ?", (login_id, password, "", name))
#         conn.commit()  
#       submitted_users = []
#   else:
#     # print("ローカルに合致するギャラデータあり")
#     submitted_users = sqlite_jmail_result[4] 
#   conn.close()
#   # print(f"送信履歴ありリスト")
#   # print(submitted_users)
#   fst_message = jmail_info['fst_message']
#   return_foot_message = jmail_info['return_foot_message']
#   second_message = jmail_info['conditions_message']
#   if login_id == None or login_id == "":
#     print(f"{name}のjmailキャラ情報を取得できませんでした")
#     return ""
#   login_flug = login_jmail(driver, wait, login_id, password)
#   if not login_flug:
#     print(f"jmail:{name}に警告画面が出ている可能性があります")
#     return ""
#   # メールアイコンをクリック
#   mail_icon = driver.find_elements(By.CLASS_NAME, value="mail-off")
#   link = mail_icon[0].find_element(By.XPATH, "./..")
#   driver.get(link.get_attribute("href"))
#   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#   time.sleep(2)
#   if submitted_users is not None and submitted_users != [] :
#     interacting_user_list = submitted_users.split()
#   else:
#     interacting_user_list = []
 
#   interacting_users = driver.find_elements(By.CLASS_NAME, value="icon_sex_m")
#   # 未読メールをチェック
#   sended_mail = False
#   return_list = []
#   for interacting_user_cnt in range(len(interacting_users)):
#     # interacting_userリストを取得
#     interacting_user_name = interacting_users[interacting_user_cnt].text
#     if "未読" in interacting_user_name:
#       interacting_user_name = interacting_user_name.replace("未読", "")
#     if "退会" in interacting_user_name:
#       interacting_user_name = interacting_user_name.replace("退会", "")
#     if " " in interacting_user_name:
#       interacting_user_name = interacting_user_name.replace(" ", "")
#     if "　" in interacting_user_name:
#       interacting_user_name = interacting_user_name.replace("　", "")
#     # 未読、退会以外でNEWのアイコンも存在してそう

#     # NEWアイコンがあるかチェック
#     new_icon = interacting_users[interacting_user_cnt].find_elements(By.TAG_NAME, value="img")
#     if "未読" in interacting_users[interacting_user_cnt].text or len(new_icon):
#     # deug
#     # if "やん" in interacting_users[interacting_user_cnt].text:
#       # 時間を取得　align_right
#       parent_usr_info = interacting_users[interacting_user_cnt].find_element(By.XPATH, "./..")
#       parent_usr_info = parent_usr_info.find_element(By.XPATH, "./..")
#       next_element = parent_usr_info.find_element(By.XPATH, value="following-sibling::*[1]")
#       current_year = datetime.now().year
#       date_string = f"{current_year} {next_element.text}"
#       date_format = "%Y %m/%d %H:%M" 
#       date_object = datetime.strptime(date_string, date_format)
#       now = datetime.today()
#       elapsed_time = now - date_object
#       print(interacting_users[interacting_user_cnt].text)
#       print(f"メール到着からの経過時間{elapsed_time}")
#       print(interacting_user_name)
#       if elapsed_time >= timedelta(minutes=4):
#         print("4分以上経過しています。")
#         if interacting_user_name not in interacting_user_list:
#           interacting_user_name = " " + interacting_user_name
#           interacting_user_list.append(interacting_user_name)
#         send_message = ""
#         # リンクを取得
#         link_element = interacting_users[interacting_user_cnt].find_element(By.XPATH, "./..")
#         driver.get(link_element.get_attribute("href"))
#         wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#         time.sleep(2)
#         send_by_user = driver.find_elements(By.CLASS_NAME, value="balloon_left")
#         send_by_user_message = send_by_user[0].find_elements(By.CLASS_NAME, value="balloon")[0].text
#         # 相手からのメッセージが何通目か確認する
#         if not sended_mail:
#           send_by_me = driver.find_elements(By.CLASS_NAME, value="balloon_right")
#           # print(888)
#           # print(len(send_by_me))
#           if len(send_by_me) == 0:
#             send_message = fst_message
#           elif len(send_by_me) == 1:
#             send_message = second_message
#           elif len(send_by_me) == 2:
#             print("捨てメアドに通知")
#             print(f"{name}   {login_id}  {password} : {interacting_user_name}  ;;;;{send_by_user_message}")
#             return_message = f"{name}jmail,{login_id}:{password}\n{interacting_user_name}「{send_by_user_message}」"
#             return_list.append(return_message)  
#             print("捨てメアドに、送信しました")
#         if send_message:
#           # 返信するをクリック
#           res_do = driver.find_elements(By.CLASS_NAME, value="color_variations_05")
#           res_do[1].click()
#           wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#           time.sleep(2)
#           # メッセージを入力　name=comment
#           text_area = driver.find_elements(By.NAME, value="comment")
#           # text_area[0].send_keys(send_message)
#           script = "arguments[0].value = arguments[1];"
#           driver.execute_script(script, text_area[0], send_message)
#           time.sleep(4)
#           # 画像があれば送信
#           if send_message == fst_message and image_path:
#             img_input = driver.find_elements(By.NAME, value="image1")
#             img_input[0].send_keys(image_path)
#             wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#             time.sleep(2)
#           send_button = driver.find_elements(By.NAME, value="sendbutton")
#           send_button[0].click()
#           wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#           time.sleep(2)
#         # メール一覧に戻る　message_back
#         back_parent = driver.find_elements(By.CLASS_NAME, value="message_back")
#         back = back_parent[0].find_elements(By.TAG_NAME, value="a")
#         back[0].click()
#         wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#         time.sleep(2)
#         interacting_users = driver.find_elements(By.CLASS_NAME, value="icon_sex_m")  
#   pager = driver.find_elements(By.CLASS_NAME, value="pager")
#   if len(pager):
#     pager_link = pager[0].find_elements(By.TAG_NAME, value="a")
   
#     for i in range(len(pager_link)):
#       next_pager = pager_link[i]
#       driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", next_pager)
#       next_pager.click()
#       wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#       time.sleep(2)
#       interacting_users = driver.find_elements(By.CLASS_NAME, value="icon_sex_m")
#       for interacting_user_cnt in range(len(interacting_users)):
#       # interacting_userリストを取得
#         interacting_user_name = interacting_users[interacting_user_cnt].text
#         if "未読" in interacting_user_name:
#           interacting_user_name = interacting_user_name.replace("未読", "")
#         if "退会" in interacting_user_name:
#           interacting_user_name = interacting_user_name.replace("退会", "")
#         if " " in interacting_user_name:
#           interacting_user_name = interacting_user_name.replace(" ", "")
#         if "　" in interacting_user_name:
#           interacting_user_name = interacting_user_name.replace("　", "")
#         # 未読、退会以外でNEWのアイコンも存在してそう
#         # NEWアイコンがあるかチェック
#         new_icon = interacting_users[interacting_user_cnt].find_elements(By.TAG_NAME, value="img")
#         if "未読" in interacting_users[interacting_user_cnt].text or len(new_icon):          
#           # 時間を取得　align_right
#           parent_usr_info = interacting_users[interacting_user_cnt].find_element(By.XPATH, "./..")
#           parent_usr_info = parent_usr_info.find_element(By.XPATH, "./..")
#           next_element = parent_usr_info.find_element(By.XPATH, value="following-sibling::*[1]")
#           current_year = datetime.now().year
#           date_string = f"{current_year} {next_element.text}"
#           date_format = "%Y %m/%d %H:%M" 
#           date_object = datetime.strptime(date_string, date_format)
#           now = datetime.today()   
#           elapsed_time = now - date_object
#           print(interacting_users[interacting_user_cnt].text)
#           print(f"メール到着からの経過時間{elapsed_time}")
#           if elapsed_time >= timedelta(minutes=4):
#             print("4分以上経過しています。")
#             # ユーザー名を保存
#             if interacting_user_name not in interacting_user_list:
#               interacting_user_name = " " + interacting_user_name
#               interacting_user_list.append(interacting_user_name)
#             send_message = ""
#             # リンクを取得
#             link_element = interacting_users[interacting_user_cnt].find_element(By.XPATH, "./..")
#             driver.get(link_element.get_attribute("href"))
#             wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#             time.sleep(2)
#             send_by_user = driver.find_elements(By.CLASS_NAME, value="balloon_left")
#             send_by_user_message = send_by_user[0].find_elements(By.CLASS_NAME, value="balloon")[0].text
#             # 相手からのメッセージが何通目か確認する
#             if not sended_mail:
#               send_by_me = driver.find_elements(By.CLASS_NAME, value="balloon_right")
#               if len(send_by_me) == 0:
#                 send_message = fst_message
#                 interacting_user_list.append(user_name)
#               elif len(send_by_me) == 1:
#                 send_message = second_message
#               elif second_message in send_by_me[0].text:
#                 print("捨てメアドに通知")
#                 print(f"{name}   {login_id}  {password} : {interacting_user_name}  ;;;;{send_by_user_message}")
#                 return_message = f"{name}jmail,{login_id}:{password}\n{interacting_user_name}「{send_by_user_message}」"
#                 return_list.append(return_message)  
#                 print("捨てメアドに、送信しました")
#             if send_message:
#               # 返信するをクリック
#               res_do = driver.find_elements(By.CLASS_NAME, value="color_variations_05")
#               res_do[1].click()
#               wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#               time.sleep(2)
#               # メッセージを入力　name=comment
#               text_area = driver.find_elements(By.NAME, value="comment")
#               # text_area[0].send_keys(send_message)
#               script = "arguments[0].value = arguments[1];"
#               driver.execute_script(script, text_area[0], send_message)
#               time.sleep(4)
#               # 画像があれば送信
#               if send_message == fst_message and image_path:              
#                 img_input = driver.find_elements(By.NAME, value="image1")
#                 img_input[0].send_keys(image_path)
#                 wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#                 time.sleep(2)  
#             # メール一覧に戻る　message_back
#             back_parent = driver.find_elements(By.CLASS_NAME, value="message_back")
#             back = back_parent[0].find_elements(By.TAG_NAME, value="a")
#             back[0].click()
#             wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#             time.sleep(2)
#         pager = driver.find_elements(By.CLASS_NAME, value="pager")
#         if len(pager):
#           pager_link = pager[0].find_elements(By.TAG_NAME, value="a")
#   # ///////////////初めまして送信///////////////////////////////////////////////
#   fst_send_limit = 1
#   returnfoot_send_limit = 1
  
#   if try_cnt % 12 == 0:
#     #メニューをクリック
#     menu_icon = driver.find_elements(By.CLASS_NAME, value="menu-off")
#     menu_icon[0].click()
#     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#     time.sleep(2)
#     menu = driver.find_elements(By.CLASS_NAME, value="iconMenu")
#     #プロフ検索をクリック
#     foot_menus = menu[0].find_elements(By.TAG_NAME, value="p")
#     foot_menu = foot_menus[0].find_elements(By.XPATH, "//*[contains(text(), 'プロフ検索')]")
#     foot_menu_link = foot_menu[0].find_element(By.XPATH, "./..")
#     driver.get(foot_menu_link.get_attribute("href"))
#     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#     time.sleep(2)
#     users_elem = driver.find_elements(By.CLASS_NAME, value="search_list_col")
#     fst_mail_cnt = 0
#     for i in range(len(users_elem)):
#       user_name = users_elem[i].find_element(By.CLASS_NAME, value="prof_name").text
#       # 送信済かチェック
#       if user_name not in interacting_user_list:
#         interacting_user_list.append(user_name)
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", users_elem[i])
#         users_elem[i].click()
#         wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#         time.sleep(2)
#         # 自己紹介文チェック
#         profile = driver.find_elements(By.CLASS_NAME, value="prof_pr")
#         if len(profile):
#           profile = profile[0].text.replace(" ", "").replace("\n", "")
#           if '通報' in profile or '業者' in profile:
#             print('自己紹介文に危険なワードが含まれていました')
#             interacting_user_list.append(user_name)
#             driver.back()
#             wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#             time.sleep(2)
#             continue
#         text_area = driver.find_elements(By.ID, value="textarea")
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area[0])
#         time.sleep(1)
#         script = "arguments[0].value = arguments[1];"
#         driver.execute_script(script, text_area[0], fst_message)
#         time.sleep(4)
#         # 画像があれば送付
#         if image_path:
#           upload_file = driver.find_element(By.ID, "upload_file")
#           # upload_file.send_keys("/Users/yamamotokenta/Desktop/myprojects/mail_operator/widget/picture/chara_img01.jpg")
#           upload_file.send_keys(image_path)
#           # file_icon
#           file_label = driver.find_element(By.ID, "file_icon")
#           class_attribute = file_label.get_attribute("class")
#           while not "file_img" in class_attribute.split():
#             time.sleep(1)
#             class_attribute = file_label.get_attribute("class")
#         send_btn = driver.find_elements(By.ID, value="message_send")
#         driver.execute_script("arguments[0].click();", send_btn[0])
#         wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#         time.sleep(2)
#         send_complete_element = driver.find_elements(By.ID, value="modal_title")
#         send_complete = send_complete_element[0].text
#         wait_cnt = 0
#         send_status = True
#         while send_complete != "送信完了しました":
#           time.sleep(4)
#           print(send_complete)
#           wait_cnt += 1
#           if wait_cnt > 3:
#             print("ロード時間が15秒以上かかっています")
#             print("送信失敗しました")
#             send_status = False
#             break
#           send_complete = send_complete_element[0].text
#         if send_status:
#           fst_mail_cnt += 1
#           print(f"jmail 1st_mail {name} : {fst_mail_cnt}件送信")
#         if fst_mail_cnt == fst_send_limit:
#           print("送信上限に達しました")
#           break
#         driver.back()
#         wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#         time.sleep(2)
#         users_elem = driver.find_elements(By.CLASS_NAME, value="search_list_col")

#     # /////////////////////////あしあと返し
#     # #メニューをクリック
#     # menu_icon = driver.find_elements(By.CLASS_NAME, value="menu-off")
#     # driver.execute_script("arguments[0].click();", menu_icon[0])
#     # # menu_icon[0].click()
#     # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#     # time.sleep(2)
#     # menu = driver.find_elements(By.CLASS_NAME, value="iconMenu")
#     # #足跡をクリック
#     # foot_menus = menu[0].find_elements(By.TAG_NAME, value="p")
#     # foot_menu = foot_menus[0].find_elements(By.XPATH, "//*[contains(text(), 'あしあと')]")
#     # foot_menu_link = foot_menu[0].find_element(By.XPATH, "./..")
#     # driver.get(foot_menu_link.get_attribute("href"))
#     # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#     # time.sleep(2)
#     # name_element = driver.find_elements(By.CLASS_NAME, value="icon_sex_m")
#     # print(111111111)
#     # print(len(name_element))
#     # for foot_return_cnt in range(len(name_element)):
#     #   # 年齢を取得
#     #   next_to_element = name_element[foot_return_cnt].find_element(By.XPATH, "following-sibling::*[1]")
#     #   user_age = next_to_element.text
#     #   # print(next_to_element.text)
#     #   age_list = ["18~21", "22~25", "26~29", "30~34", ]
#     #   if any(age in user_age.replace("～", "~") for age in age_list):
#     #     # print("age_list の中の文字列が string に含まれています。")
#     #     # 地域を判定
#     #     next_to_next_element = name_element[foot_return_cnt].find_element(By.XPATH, "following-sibling::*[2]")
#     #     if "大阪" in next_to_next_element.text or "兵庫" in next_to_next_element.text or "石川" in next_to_next_element.text:
#     #       continue
#     #     foot_user_name = name_element[foot_return_cnt].text
#     #     if "未読" in foot_user_name:
#     #         foot_user_name = foot_user_name.replace("未読", "")
#     #     if "退会" in foot_user_name:
#     #       foot_user_name = foot_user_name.replace("退会", "")
#     #     if " " in foot_user_name:
#     #       foot_user_name = foot_user_name.replace(" ", "")
#     #     if "　" in foot_user_name:
#     #       foot_user_name = foot_user_name.replace("　", "")
#     #     # 送信済かチェック
#     #     # if foot_user_name not in interacting_user_list:
#     #     if True:#DEBUG 
#     #       send_status = True
#     #       # print(f"{foot_user_name}はメールリストになかった")
#     #       foot_user_link = name_element[foot_return_cnt].find_element(By.XPATH, "./..")
#     #       driver.get(foot_user_link.get_attribute("href"))
#     #       wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#     #       time.sleep(2)
#     #       # 自己紹介文チェック
#     #       profile = driver.find_elements(By.CLASS_NAME, value="prof_pr")
#     #       if len(profile):
#     #         profile = profile[0].text.replace(" ", "").replace("\n", "")
#     #         if '通報' in profile or '業者' in profile:
#     #           print('自己紹介文に危険なワードが含まれていました')
#     #           interacting_user_list.append(foot_user_name)
#     #           send_status = False
#     #       if send_status:
#     #         text_area = driver.find_elements(By.ID, value="textarea")
#     #         driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area[0])
#     #         time.sleep(1)
#     #         # text_area[0].send_keys(return_foot_message)
#     #         script = "arguments[0].value = arguments[1];"
#     #         driver.execute_script(script, text_area[0], return_foot_message)
#     #         time.sleep(4)
#     #         # 画像があれば送付
#     #         if image_path:
#     #           img_input = driver.find_elements(By.ID, value="upload_file")
#     #           img_input[0].send_keys(image_path)
#     #           wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#     #           time.sleep(2)
#     #         send_btn = driver.find_elements(By.ID, value="message_send")
#     #         driver.execute_script("arguments[0].click();", send_btn[0])
#     #         wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#     #         time.sleep(2)
#     #         send_complete_element = driver.find_elements(By.ID, value="modal_title")
#     #         send_complete = send_complete_element[0].text
#     #         # print(888)
#     #         # print(send_complete)
#     #         wait_cnt = 0
#     #         while send_complete != "送信完了しました":
#     #           time.sleep(4)
#     #           # print(send_complete)
#     #           wait_cnt += 1
#     #           if wait_cnt > 4:
#     #             print("ロード時間が15秒以上かかっています")
#     #             print("送信失敗しました")
#     #             send_status = False
#     #             break
#     #           send_complete = send_complete_element[0].text
#     #         if send_status:
#     #           # ユーザー名を保存
#     #           interacting_user_list.append(foot_user_name)
#     #           returnfoot_send_limit += 1
#     #           print(f"jmail足跡返し {name} {user_age}: {returnfoot_send_limit}件送信")
#     #           if fst_mail_cnt == returnfoot_send_limit:
#     #             print(f"足跡返し送信上限に達しました")
#     #             break
#     #         # あしあとリストに戻る
#     #         driver.back()
#     #         wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#     #         time.sleep(2)
#     #         name_element = driver.find_elements(By.CLASS_NAME, value="icon_sex_m")
  
#   # interacting_user_listを保存
#   print(f"送信済ユーザーリスト {len(interacting_user_list)}人")
#   print(interacting_user_list)
#   send_list_string = " ".join(interacting_user_list)
#   conn = sqlite3.connect('user_data.db')
#   c = conn.cursor()
#   c.execute("UPDATE jmail SET send_list = ? WHERE name = ?", (send_list_string, name))
#   conn.commit()
#   conn.close()
  
#   if len(return_list):
#     return return_list
#   else:
#     return ""

def make_footprints(driver, wait):
  #メニューをクリック
  menu_icon = driver.find_elements(By.CLASS_NAME, value="menu-off")
  menu_icon[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  menu = driver.find_elements(By.CLASS_NAME, value="iconMenu")
  #プロフ検索をクリック
  foot_menus = menu[0].find_elements(By.TAG_NAME, value="p")
  for i in foot_menus:
    if i.text == "プロフ検索":
      prof_menu_link = i.find_element(By.XPATH, "./..")
      prof_link = prof_menu_link.get_attribute("href")
  driver.get(prof_link)
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  # 詳しく検索
  detail_query = driver.find_elements(By.ID, value="ac2h2")
  detail_query[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  # 年齢を選択

  age18_21 = driver.find_elements(By.XPATH, '//label[@for="CheckAge1"]')
  if "rgba(0, 0, 0, 0)" in age18_21[0].value_of_css_property("background-color"):
    age18_21[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  age22_25 = driver.find_elements(By.XPATH, '//label[@for="CheckAge2"]')
  if "rgba(0, 0, 0, 0)" in age22_25[0].value_of_css_property("background-color"):
    age22_25[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  age26_29 = driver.find_elements(By.XPATH, '//label[@for="CheckAge3"]')
  if "rgba(0, 0, 0, 0)" in age26_29[0].value_of_css_property("background-color"):
    age26_29[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  age30_34 = driver.find_elements(By.XPATH, '//label[@for="CheckAge4"]')
  if "rgba(0, 0, 0, 0)" in age30_34[0].value_of_css_property("background-color"):
    age30_34[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # 身長を選択
  height150 = driver.find_elements(By.XPATH, '//label[@for="CheckHeight1"]')
  if "rgba(0, 0, 0, 0)" in height150[0].value_of_css_property("background-color"):
    height150[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  height154 = driver.find_elements(By.XPATH, '//label[@for="CheckHeight2"]')
  if "rgba(0, 0, 0, 0)" in height154[0].value_of_css_property("background-color"):
    height154[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  height159 = driver.find_elements(By.XPATH, '//label[@for="CheckHeight3"]')
  if "rgba(0, 0, 0, 0)" in height154[0].value_of_css_property("background-color"):
    height159[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  height164 = driver.find_elements(By.XPATH, '//label[@for="CheckHeight4"]')
  if "rgba(0, 0, 0, 0)" in height164[0].value_of_css_property("background-color"):
    height164[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  height169 = driver.find_elements(By.XPATH, '//label[@for="CheckHeight5"]')
  if "rgba(0, 0, 0, 0)" in height169[0].value_of_css_property("background-color"):
    height169[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  height174 = driver.find_elements(By.XPATH, '//label[@for="CheckHeight6"]')
  if "rgba(0, 0, 0, 0)" in height174[0].value_of_css_property("background-color"):
    height174[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  height179 = driver.find_elements(By.XPATH, '//label[@for="CheckHeight7"]')
  if "rgba(0, 0, 0, 0)" in height179[0].value_of_css_property("background-color"):
    height179[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # 地域を選択
  tokyo_state = selected_state = driver.find_elements(By.XPATH, '//label[@for="CheckState-9"]')
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", tokyo_state[0])
  time.sleep(1)
  if "rgba(0, 0, 0, 0)" in tokyo_state[0].value_of_css_property("background-color"):
    tokyo_state[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
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
  # 検索するボタンをクリック可能にするため少しスクロール
  driver.execute_script("window.scrollBy(0, 300);")
  time.sleep(1)
  driver.execute_script("window.scrollBy(0, -300);")
  time.sleep(1)
  query_submit = driver.find_elements(By.ID, value="button")
  query_submit[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  users = driver.find_elements(By.CLASS_NAME, value="search_list_col")
  makefoot_cnt = random.randint(10, 15)
  for i in range(makefoot_cnt):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", users[i])
    time.sleep(1)
    users[i].find_element(By.TAG_NAME, value="a").click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    name = driver.find_element(By.CLASS_NAME, value="prof_name").text
    print(f"足跡{i+1} 件 : {name}")
    time.sleep(2)
    driver.back()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    users = driver.find_elements(By.CLASS_NAME, value="search_list_col")


def return_footprint(data, driver,wait,submitted_users):
  return_foot_message_cnt = 0
  return_foot_message = data["return_foot_message"]
  mail_img = data["chara_image"]
  name = data["name"]
  if mail_img:
    image_filename, image_path = encode_img(name, mail_img)
  else:
    image_filename, image_path = "", ""
  
  menu_icon = driver.find_elements(By.CLASS_NAME, value="menu-off")
  menu_icon[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  menu = driver.find_elements(By.CLASS_NAME, value="iconMenu")
  #あしあとをクリック
  foot_menus = menu[0].find_elements(By.TAG_NAME, value="p")
  foot_menu = foot_menus[0].find_elements(By.XPATH, "//*[contains(text(), 'あしあと')]")
  foot_menu_link = foot_menu[0].find_element(By.XPATH, "./..")
  driver.get(foot_menu_link.get_attribute("href"))
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  catch_warning(driver, wait)
  foot_users = driver.find_element(By.ID, value="ulList").find_elements(By.TAG_NAME, value="li")
  for i in range(len(foot_users)):
    # NEW があるかチェック 
    # if not "New" in foot_users[i].text:
    #   continue
    # 送信済ユーザーかチェック
    foot_user_name = foot_users[i].find_element(By.CLASS_NAME, value="icon_sex_m").text
    if foot_user_name in submitted_users:
      # print(f"{foot_user_name}は送信済ユーザーです")
      continue
    submitted_users.append(foot_user_name)
    foot_users[i].find_element(By.TAG_NAME, value="a").click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(0.5)
    # 自己紹介文チェック
    profile = driver.find_elements(By.CLASS_NAME, value="prof_pr")
    if len(profile):
      profile = profile[0].text.replace(" ", "").replace("\n", "")
      if '通報' in profile or '業者' in profile:
        print(f'{foot_user_name} 自己紹介文に危険なワードが含まれていました')
        driver.back()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
        continue
    text_area = driver.find_elements(By.ID, value="textarea")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area[0])
    time.sleep(1)
    script = "arguments[0].value = arguments[1];"
    driver.execute_script(script, text_area[0], return_foot_message)
    time.sleep(4)
    # 画像があれば送信 
    if image_path:
      img_input = driver.find_elements(By.NAME, value="image1")
      img_input[0].send_keys(image_path)
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(2)
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
      if len(driver.find_elements(By.ID, value="errormsg1")):
        if "連続送信はできません"in driver.find_element(By.ID, value="errormsg1").text:
          print("連続送信はできません")
        send_status = False
        break
    if send_status:
      return_foot_message_cnt += 1
      print(f"jmail 足跡返し　{foot_user_name} : {return_foot_message_cnt}件送信")
    if return_foot_message_cnt == 2:
      print("送信上限2件に達しました")
      driver.refresh()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      break
    driver.back()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    foot_users = driver.find_element(By.ID, value="ulList").find_elements(By.TAG_NAME, value="li")
  if image_filename:
    if os.path.exists(image_filename):
        os.remove(image_filename)

def post_set(post_title, post_contents, driver, wait):
  if "https://mintj.com/msm/mainmenu/?sid=" not in driver.current_url:
    driver.get("https://mintj.com/msm/mainmenu/?sid=")
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
  menu_icon = driver.find_elements(By.CLASS_NAME, value="menu-off")
  menu_icon[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  menu = driver.find_elements(By.CLASS_NAME, value="iconMenu")
  #その他募集をクリック
  foot_menus = menu[0].find_elements(By.TAG_NAME, value="p")
  foot_menu = foot_menus[0].find_elements(By.XPATH, "//*[contains(text(), 'その他募集')]") 
  if foot_menu[0].get_attribute("href"):
    post_link = foot_menu[0].get_attribute("href")
  else:
    post_link = foot_menu[0].find_element(By.XPATH, "./..").get_attribute("href")
  
  driver.get(post_link)
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  driver.find_element(By.CLASS_NAME, value="icon_pen").click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  # コーナー選択
  select = Select(driver.find_element(By.NAME, value="CornerId"))
  select.select_by_visible_text("今すぐ会いたい")
  time.sleep(1)
  # 掲示板タイトル入力
  script = "arguments[0].value = arguments[1];"
  driver.execute_script(script, driver.find_element(By.NAME, value="Subj"), post_title)
  time.sleep(0.5)
  # 掲示板投稿文入力
  driver.execute_script(script, driver.find_element(By.NAME, value="Comment"), post_contents)
  time.sleep(0.5)
  # 受信メール数選択
  select = Select(driver.find_element(By.NAME, value="ResMaxCount"))
  select.select_by_visible_text("5件")
  time.sleep(1.5)
  # 書き込むをクリック
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", driver.find_element(By.ID, value="Bw"))
  time.sleep(1.5)
  driver.find_element(By.ID, value="Bw").click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)

def change_areas(area, driver, wait):
  setting_icon = driver.find_elements(By.CLASS_NAME, value="setting-off")
  setting_icon[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  #プロフィール変更をクリック
  driver.find_element(By.ID, value="settingmenu-list").find_element(By.XPATH, "//*[contains(text(), 'マイプロフ')]").click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", driver.find_element(By.ID, value="state_id"))
  time.sleep(1.5)
  select = Select(driver.find_element(By.ID, value="state_id"))
  select.select_by_visible_text(area)
  time.sleep(1.5)
  driver.find_element(By.NAME, value="PfUpdate").click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1)

def re_post(data, post_areas, driver,wait):
  
  post_title = data["post_title"]
  post_contents = data["post_contents"]
  if not post_title:
    print(f"掲示板タイトルが設定されていません {post_title}")
    return
  # ~~~~~~~~~掲示板投稿〜〜〜〜〜〜〜〜〜〜〜〜〜
  print("エリア：　現在の地域")
  post_set(post_title, post_contents, driver, wait)
  print("投稿完了")
  time.sleep(15)
  # ~~~~~~~~~地域変更〜〜〜〜〜〜〜〜〜〜〜〜〜
  for area in random.sample(post_areas, 3):
    print(f"エリア変更：　{area}")
    change_areas(area, driver, wait)
    post_set(post_title, post_contents, driver, wait)
    print("投稿完了")
    # 間隔規制
    time.sleep(15)
  print("エリア変更：　東京")
  change_areas("東京", driver, wait)



   
   

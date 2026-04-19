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


def _encode_for_sjis_form(text):
  """Shift_JIS(CP932)で表現できない文字（絵文字など）をHTML数値参照に変換。
  Jmailの送信フォームはSJIS encoding のため、絵文字はそのままでは'?'に化ける。
  &#N; で送ればサーバ側で保持され、表示時に絵文字として描画される。"""
  if not text:
    return text
  out = []
  for ch in text:
    try:
      ch.encode('cp932')
      out.append(ch)
    except UnicodeEncodeError:
      out.append(f'&#{ord(ch)};')
  return ''.join(out)


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
      # if name != "えりか":
      #   continue
      profile_path = os.path.join(base_path, f"{i['name']}_{uuid.uuid4().hex}")

      # profile_path = os.path.join(base_path, i["name"])
      if os.path.exists(profile_path):
        shutil.rmtree(profile_path)  # フォルダごと削除
        os.makedirs(profile_path, exist_ok=True)  
      # iPhone14
      user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/537.36"
      driver,wait = func.get_multi_driver(profile_path, headless, user_agent)
      
      login_flug = login_jmail(driver, wait, i["login_id"], i["password"])
      drivers[i["name"]] = {"name":i["name"], "login_id":i["login_id"], "password":i["password"], "post_title":i["post_title"], "post_contents":i["post_contents"],"driver": driver, "wait": wait, "fst_message": i["fst_message"], "return_foot_message":i["return_foot_message"], "second_message":i["second_message"],"conditions_message":i["conditions_message"], "mail_img":i["chara_image"], "submitted_users":i["submitted_users"], "chara_image":i["chara_image"], "mail_address_image":i["mail_address_image"], "submitted_users":i["submitted_users"], "young_submitted_users":i["young_submitted_users"], "mail_address":i["mail_address"], "gmail_password":i["gmail_password"]}
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
  condition_message = jmail_info['conditions_message']
  submitted_users = jmail_info['submitted_users']
  mail_img = jmail_info['chara_image']
  mail_address_image = jmail_info['mail_address_image']
  submitted_users = jmail_info['submitted_users']
  young_submitted_users = jmail_info['young_submitted_users']
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
  check_mail_start = time.time()
  processed_users = set()
  while len(interacting_users):
    if time.time() - check_mail_start > 180:
      print(f"  [{name}] check_mail whileループ タイムアウト(180秒)")
      break
    # 未処理のユーザーを探す
    target_user = None
    for u in interacting_users:
      u_text = u.text.strip()
      if u_text not in processed_users:
        target_user = u
        break
    if target_user is None:
      print(f"  [{name}] 未処理の未読ユーザーなし")
      break
    interacting_user_name = target_user.text
    if "未読" in interacting_user_name:
      interacting_user_name = interacting_user_name.replace("未読", "")
    if "退会" in interacting_user_name:
      interacting_user_name = interacting_user_name.replace("退会", "")
    if " " in interacting_user_name:
      interacting_user_name = interacting_user_name.replace(" ", "")
    if "　" in interacting_user_name:
      interacting_user_name = interacting_user_name.replace("　", "")
    # 処理済みとしてマーク
    processed_users.add(target_user.text.strip())
    # 未読、退会以外でNEWのアイコンも存在してそう
    # NEWアイコンがあるかチェック
    new_icon = target_user.find_elements(By.TAG_NAME, value="img")
    if "テラ" in target_user.text or len(new_icon):
      submitted_users.append(interacting_user_name)
    if "未読" in target_user.text or len(new_icon):
    # deug
    # if True:
      # 時間を取得
      parent_usr_info = target_user.find_element(By.XPATH, "./..")
      parent_usr_info = parent_usr_info.find_element(By.XPATH, "./..")
      next_element = parent_usr_info.find_element(By.XPATH, value="following-sibling::*[1]")
      current_year = datetime.now().year
      date_string = f"{current_year} {next_element.text}"
      date_format = "%Y %m/%d %H:%M"
      date_object = datetime.strptime(date_string, date_format)
      now = datetime.today()
      elapsed_time = now - date_object

      if elapsed_time >= timedelta(minutes=4):
        print("4分以上経過しています。")
        # 年齢を取得
        age_element = driver.find_elements(By.CLASS_NAME, value="list_subtext")[0]
        match = re.search(r"\d+～\d+", age_element.text)
        if match:
          age_range = match.group()
          # 「～」で分割して数値に変換
          min_age, max_age = map(int, age_range.split("～"))
          if max_age <= 34:
            print("34歳以下です")
            young_flag = True
          else:
            print("35歳以上です")
            young_flag = False
        if young_flag:
          if interacting_user_name not in young_submitted_users:
            young_submitted_users.append(interacting_user_name)
        else:
          if interacting_user_name not in submitted_users:
            submitted_users.append(interacting_user_name)
        send_message = ""
        ojisan_flag = False
        # リンクを取得
        link_element = target_user.find_element(By.XPATH, "./..")
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
            print("icloud.comが含まれています")
            if gmail_address:
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
                driver.execute_script(script, text_area[0], icloud_text)
                time.sleep(4)
                
                send_button = driver.find_elements(By.NAME, value="sendbutton")
                send_button[0].click()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(2)
              except Exception:
                pass
          else:
            # アド内条件
            site = "Jメール"
            try:
              func.normalize_text(condition_message)
              # 2345
              func.send_conditional(interacting_user_name, email_list[0], gmail_address, gmail_password, condition_message, site)
              print("アドレス内1stメールを送信しました")
            except Exception:
              print(f"{name} アドレス内1stメールの送信に失敗しました")
              error = traceback.format_exc()
              traceback.print_exc()
              print(mail_info)
              print(condition_message)
              func.send_error(name, f"アドレス内1stメールの送信に失敗しました\n{mail_info}\n\n{error}",
                                    )
            send_message = ""
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
                return_message, 
                mail_info, 
                f"{name}jmail",
                )
              print("捨てメアドに、送信しました")
              image_path = ""
              image_filename = ""
          elif my_length >= 2:
            print("捨てメアドに通知")
            print(f"{name}   {login_id}  {password} : {interacting_user_name}  ;;;;{send_by_user_message}")
            return_message = f"{name}jmail,{login_id}:{password}\n{interacting_user_name}「{send_by_user_message}」"
            func.send_mail(
              return_message, 
              mail_info, 
              f"{name}jmail",
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
        # if ojisan_flag:
        #   user_links = driver.find_elements(By.CLASS_NAME, value="icon_sex_m")
        #   for user_link in user_links:
        #     if name != user_link.text:
        #       user_link.find_element(By.TAG_NAME, value="a").click()
        #       wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        #       time.sleep(2)
        #       catch_warning(driver, wait)
        #       driver.save_screenshot("screenshot.png")
        #       compressed_path = func.compress_image("screenshot.png")
        #       title = f"{name}jmail おじさんメッセージ"
        #       text = send_by_user_message
        #       if mail_info:
        #         func.send_mail(text, mail_info, title, compressed_path)
        #       for p in ["screenshot.png", compressed_path]:
        #         try:
        #           if os.path.exists(p):
        #             os.remove(p)
        #         except Exception as e:
        #           print(f"⚠️ 後処理で削除失敗: {p} -> {e}")
        #       break
        #   driver.back()
        #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        #   time.sleep(1)
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
                # アド内条件
                site = "Jメール"
                try:
                  func.normalize_text(condition_message)
                  func.send_conditional(interacting_user_name, email_list[0], gmail_address, gmail_password, condition_message, site)
                  print("アドレス内1stメールを送信しました")
                except Exception:
                  print(f"{name} アドレス内1stメールの送信に失敗しました")
                  error = traceback.format_exc()
                  traceback.print_exc()
                  print(mail_info)
                  print(condition_message)
                  func.send_error(name, f"アドレス内1stメールの送信に失敗しました\n{mail_info}\n\n{error}",
                                        )
                send_message = ""                        
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
                  return_message, 
                  mail_info, 
                  f"{name}jmail",
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
            # else:
            #   user_links = driver.find_elements(By.CLASS_NAME, value="icon_sex_m")
            #   for user_link in user_links:
            #     if name != user_link.text:
            #       user_link.find_element(By.TAG_NAME, value="a").click()
            #       wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            #       time.sleep(2)
            #       catch_warning(driver, wait)
            #       compressed_path = None
            #       title = f"{name}jmail おじさんAIチャットメッセージ"
            #       text = send_by_user_message
            #       if mail_info:
            #         func.send_mail(text, mail_info, title, compressed_path)
            #       for p in ["screenshot.png", compressed_path]:
            #         try:
            #           if os.path.exists(p):
            #             os.remove(p)
            #         except Exception as e:
            #           print(f"⚠️ 後処理で削除失敗: {p} -> {e}")
            #       break
            # メール一覧に戻る　message_back
            back_parent = driver.find_elements(By.CLASS_NAME, value="message_back")
            back = back_parent[0].find_elements(By.TAG_NAME, value="a")
            back[0].click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
        pager = driver.find_elements(By.CLASS_NAME, value="pager")
        if len(pager):
          pager_link = pager[0].find_elements(By.TAG_NAME, value="a")
  return young_submitted_users, submitted_users      
  

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
  # プロフ検索ページへ遷移
  driver.get('https://mintj.com/msm/PfSearch/Search/?sid=')
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
  # age30_34 = driver.find_elements(By.XPATH, '//label[@for="CheckAge4"]')
  # if "rgba(0, 0, 0, 0)" in age30_34[0].value_of_css_property("background-color"):
  #   age30_34[0].click()
  #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
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
  # height174 = driver.find_elements(By.XPATH, '//label[@for="CheckHeight6"]')
  # if "rgba(0, 0, 0, 0)" in height174[0].value_of_css_property("background-color"):
  #   height174[0].click()
  #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # height179 = driver.find_elements(By.XPATH, '//label[@for="CheckHeight7"]')
  # if "rgba(0, 0, 0, 0)" in height179[0].value_of_css_property("background-color"):
  #   height179[0].click()
  #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # 地域を選択
  accordion03 = driver.find_elements(By.ID, value="accordion03")
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", accordion03[0])
  time.sleep(0.5)
  accordion03[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(0.5)
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
  makefoot_cnt = random.randint(3, 7)
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
    # 年齢チェック
    age_elem = foot_users[i].find_elements(By.CLASS_NAME, 'list_subtext')[0]
    if not "2" in age_elem.text:
      # print(f"年齢が条件外です: {age_elem.text}")
      continue
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
    if return_foot_message_cnt == 1:
      print("送信上限1件に達しました")
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

def post_set(post_area, post_title, post_contents, driver, wait):
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

  print(f"エリア変更：　{post_area}")
  # ~~~~~~~~~地域変更〜〜〜〜〜〜〜〜〜〜〜〜〜
  area_select = driver.find_element(By.ID, value="writeState")
  select = Select(area_select)
  select.select_by_visible_text(post_area)
  time.sleep(0.5)

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

# def change_areas(area, driver, wait):
#   catch_warning(driver, wait)
#   setting_icon = driver.find_elements(By.CLASS_NAME, value="setting-off")
#   setting_icon[0].click()
#   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#   time.sleep(1)
#   #プロフィール変更をクリック
#   driver.find_element(By.ID, value="settingmenu-list").find_element(By.XPATH, "//*[contains(text(), 'マイプロフ')]").click()
#   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#   time.sleep(1)
#   catch_warning(driver, wait)
#   driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", driver.find_element(By.ID, value="state_id"))
#   time.sleep(1.5)
#   select = Select(driver.find_element(By.ID, value="state_id"))
#   select.select_by_visible_text(area)
#   time.sleep(1.5)
#   driver.find_element(By.NAME, value="PfUpdate").click()
#   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
#   time.sleep(1)

def re_post(data, post_areas, driver,wait):
  post_title = data["post_title"]
  post_contents = data["post_contents"]
  select_areas = random.sample(post_areas, 2)
  select_areas.append("東京")
  
  for post_area in post_areas: 
    post_set(post_area, post_title, post_contents, driver, wait)
    print("投稿完了")
    time.sleep(12)
    
    
  
  
  # for area in random.sample(post_areas, 3):
  #   print(f"エリア変更：　{area}")
  #   change_areas(area, driver, wait)
  #   post_set(post_title, post_contents, driver, wait)
  #   print("投稿完了")
  #   # 間隔規制
  #   time.sleep(15)
  # print("エリア変更：　東京")
  # change_areas("東京", driver, wait)


# ---- プロフィール編集 ----

# モデルの選択肢テキスト → フォームvalue のマッピング
JMAIL_AGE_MAP = {
  "18~21": "1", "22~25": "2", "26~29": "3", "30~34": "4",
  "35~39": "5", "40~44": "6", "45~49": "7", "50~54": "8",
  "55~59": "9", "60歳以上": "10",
}
JMAIL_HEIGHT_MAP = {
  "150cm未満": "1", "150～154cm": "2", "155～159cm": "3",
  "160～164cm": "4", "165～169cm": "5", "170～174cm": "6",
  "175～179cm": "7", "180cm以上": "8",
}
JMAIL_STYLE_MAP = {
  "細身": "1", "キモチ細身": "2", "標準": "3",
  "ナイスバディー": "4", "グラマー": "5",
}
JMAIL_CHARACTER_MAP = {
  "やさしい": "1", "明るい": "2", "面白い": "3", "冷静": "4",
  "積極的": "5", "甘えん坊": "6", "穏やか": "7", "寂しがり": "8",
  "社交的": "9",
}
JMAIL_SEXINESS_MAP = {
  "★": "1", "★★": "2", "★★★": "3", "★★★★": "4", "★★★★★": "5",
}
JMAIL_BLOOD_MAP = {
  "A型": "1", "O型": "2", "B型": "3", "AB型": "4",
}
JMAIL_STATE_MAP = {
  "東京都": "8",
}


def profile_edit(chara_data, driver, wait):
  """
  Jmailのプロフィールを3ページで更新する。
  1. MyProf/      : 興味・エリア・年齢等
  2. EditNickName/: ニックネーム
  3. EditPr/      : 自己PR
  """
  name = chara_data['name']
  print(f"[{name}] マイプロフ編集開始")

  # ===== 1. MyProf ページ =====
  driver.get('https://mintj.com/msm/MyProf/')
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(1)

  # --- 都道府県（先に設定してcityのAjax更新を済ませる）---
  activity_area = chara_data.get('activity_area')
  if activity_area and activity_area in JMAIL_STATE_MAP:
    Select(driver.find_element(By.NAME, 'state_id')).select_by_value(JMAIL_STATE_MAP[activity_area])
    time.sleep(1.2)  # cityのAjax更新を待つ
    print(f"  都道府県: {activity_area}")

  # --- 市区町村 ---
  detail_area = chara_data.get('detail_activity_area')
  if detail_area:
    try:
      Select(driver.find_element(By.NAME, 'city')).select_by_visible_text(detail_area)
      print(f"  市区町村: {detail_area}")
    except Exception:
      print(f"  市区町村「{detail_area}」が見つかりません（スキップ）")

  # --- 年齢 ---
  age = chara_data.get('age')
  if age and age in JMAIL_AGE_MAP:
    Select(driver.find_element(By.NAME, 'ProfAge')).select_by_value(JMAIL_AGE_MAP[age])
    print(f"  年齢: {age}")

  # --- 職業 ---
  job = chara_data.get('job')
  if job:
    try:
      Select(driver.find_element(By.NAME, 'ProfOccupation')).select_by_visible_text(job)
      print(f"  職業: {job}")
    except Exception:
      print(f"  職業「{job}」が見つかりません（スキップ）")

  # --- ルックス ---
  looks = chara_data.get('looks')
  if looks:
    try:
      Select(driver.find_element(By.NAME, 'ProfLooks')).select_by_visible_text(looks)
      print(f"  ルックス: {looks}")
    except Exception:
      print(f"  ルックス「{looks}」が見つかりません（スキップ）")

  # --- 身長 ---
  height = chara_data.get('height')
  if height and height in JMAIL_HEIGHT_MAP:
    Select(driver.find_element(By.NAME, 'ProfHeight')).select_by_value(JMAIL_HEIGHT_MAP[height])
    print(f"  身長: {height}")

  # --- スタイル ---
  body_shape = chara_data.get('body_shape')
  if body_shape and body_shape in JMAIL_STYLE_MAP:
    Select(driver.find_element(By.NAME, 'ProfStyle')).select_by_value(JMAIL_STYLE_MAP[body_shape])
    print(f"  スタイル: {body_shape}")

  # --- 性格 ---
  personality = chara_data.get('personality')
  if personality and personality in JMAIL_CHARACTER_MAP:
    Select(driver.find_element(By.NAME, 'ProfCharacter')).select_by_value(JMAIL_CHARACTER_MAP[personality])
    print(f"  性格: {personality}")

  # --- エッチ度 ---
  sexiness = chara_data.get('sexiness')
  if sexiness and sexiness in JMAIL_SEXINESS_MAP:
    Select(driver.find_element(By.NAME, 'ProfFiveRanks')).select_by_value(JMAIL_SEXINESS_MAP[sexiness])
    print(f"  エッチ度: {sexiness}")

  # --- 血液型 ---
  blood_type = chara_data.get('blood_type')
  if blood_type and blood_type in JMAIL_BLOOD_MAP:
    Select(driver.find_element(By.NAME, 'ProfBlood')).select_by_value(JMAIL_BLOOD_MAP[blood_type])
    print(f"  血液型: {blood_type}")

  # --- PurposeList チェックボックス（selectのAjax後に設定）---
  things = chara_data.get('things_interesting') or []
  if things:
    all_checks = driver.find_elements(By.NAME, 'PurposeList')
    for cb in all_checks:
      if cb.is_selected():
        driver.execute_script('arguments[0].click();', cb)
    for cb in all_checks:
      if cb.get_attribute('value') in things:
        driver.execute_script('arguments[0].click();', cb)
        print(f"  チェック: {cb.get_attribute('value')}")

  # --- 更新ボタン ---
  submit = driver.find_element(By.CSS_SELECTOR, 'input[name="PfUpdate"]')
  driver.execute_script('arguments[0].scrollIntoView({block:"center"});', submit)
  driver.execute_script('arguments[0].click();', submit)
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  print(f"  マイプロフ更新完了")

  # ===== 2. ニックネーム =====
  nick = chara_data.get('name')
  if nick:
    driver.get('https://mintj.com/msm/MyProf/EditNickName/')
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    nick_input = driver.find_element(By.NAME, 'EditedNickNameText')
    # JSで直接value設定 + input/changeイベント発火
    driver.execute_script("""
      var el = arguments[0]; el.value = arguments[1];
      el.dispatchEvent(new Event('input', {bubbles: true}));
      el.dispatchEvent(new Event('change', {bubbles: true}));
    """, nick_input, nick)
    # submitボタンまでスクロール + native click
    submit_btn = driver.find_element(By.CSS_SELECTOR, 'input[value="決定する"]')
    driver.execute_script('arguments[0].scrollIntoView({block:"center"});', submit_btn)
    time.sleep(0.5)
    # form submit を直接呼ぶ（action="#"でもmethod=postならサーバに送信される）
    driver.execute_script('arguments[0].closest("form").submit();', submit_btn)
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    # リダイレクト先URLで成否判定
    if 'EditNickName' not in driver.current_url:
      print(f"  ニックネーム設定完了: {nick}")
    else:
      print(f"  ⚠️ ニックネーム送信後にEditNickNameに残留: {driver.current_url}")

  # ===== 3. 自己PR =====
  self_pr = chara_data.get('self_promotion')
  if self_pr:
    driver.get('https://mintj.com/msm/MyProf/EditPr/')
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(0.8)
    pr_textarea = driver.find_element(By.NAME, 'EditedSelfPrText')
    driver.execute_script('arguments[0].value = arguments[1];', pr_textarea, self_pr)
    submit_btn = driver.find_element(By.CSS_SELECTOR, 'input[name="PrEdit"]')
    driver.execute_script('arguments[0].click();', submit_btn)
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(0.8)
    print(f"  自己PR設定完了")

  print(f"[{name}] プロフィール編集完了")


def _analyze_jmail_image(image_url, cookies_dict=None):
  """
  Claude APIでJmailユーザーの画像を解析して「女性慣れしていない・真面目そう、優しそう、気が弱そう」スコアを返す。
  戻り値: (score: int, reason: str)
  """
  import anthropic
  import httpx
  import base64
  import os
  import re

  api_key = os.environ.get('ANTHROPIC_API_KEY', '')
  if not api_key:
    try:
      import settings
      api_key = getattr(settings, 'anthropic_api_key', '')
    except Exception:
      pass
  if not api_key:
    return 0, '(APIキー未設定のためスキップ)'

  try:
    headers = {'Referer': 'https://mintj.com/'}
    if cookies_dict:
      headers['Cookie'] = '; '.join([f'{k}={v}' for k, v in cookies_dict.items()])

    resp = httpx.get(image_url, headers=headers, timeout=10, follow_redirects=True)
    if resp.status_code != 200:
      return 0, f'(画像取得失敗: {resp.status_code})'

    image_data = base64.standard_b64encode(resp.content).decode('utf-8')
    media_type = resp.headers.get('content-type', 'image/jpeg').split(';')[0]

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
      model='claude-haiku-4-5-20251001',
      max_tokens=256,
      messages=[{
        'role': 'user',
        'content': [
          {
            'type': 'image',
            'source': {'type': 'base64', 'media_type': media_type, 'data': image_data},
          },
          {
            'type': 'text',
            'text': (
              'この写真の雰囲気・印象を分析し、-10〜10点のスコアをつけてください。\n'
              '写真全体から受ける印象を以下の基準で評価します:\n'
              '・落ち着いた雰囲気・誠実な印象・穏やかな空気感: 高スコア\n'
              '・趣味に没頭していそうな雰囲気・インドア派な印象: 高スコア\n'
              '・派手・社交的・アクティブな雰囲気: 低スコア（マイナスも可）\n'
              '・加工が強い・SNS慣れしている印象: 低スコア\n\n'
              '必ず以下の形式のみで答えてください（説明不要）:\n'
              'SCORE:数字 REASON:一言理由'
            ),
          },
        ],
      }],
    )
    text = message.content[0].text.strip()
    m = re.search(r'SCORE:(-?\d+)\s+REASON:(.+)', text)
    if m:
      return int(m.group(1)), m.group(2).strip()
    return 0, f'(解析結果: {text[:50]})'

  except Exception as e:
    return 0, f'(画像解析エラー: {e})'


def _analyze_jmail_profile_text(profile_text):
  """
  Claude APIで自己PRテキストを解析し、-10〜10点のスコアを返す。
  評価基準は画像解析と同じ（落ち着き・真面目・インドア派=高、派手・SNS慣れ=低）。
  戻り値: (score: int, reason: str)
  """
  import anthropic
  import os
  import re

  if not profile_text or len(profile_text.strip()) < 10:
    return 0, '(自己PR短すぎスキップ)'

  api_key = os.environ.get('ANTHROPIC_API_KEY', '')
  if not api_key:
    try:
      import settings
      api_key = getattr(settings, 'anthropic_api_key', '')
    except Exception:
      pass
  if not api_key:
    return 0, '(APIキー未設定のためスキップ)'

  try:
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
      model='claude-haiku-4-5-20251001',
      max_tokens=256,
      messages=[{
        'role': 'user',
        'content': [{
          'type': 'text',
          'text': (
            '以下は出会い系サイトの男性プロフィール自己PRです。'
            '文面から受ける印象を -10〜10点で評価してください。\n'
            '評価基準:\n'
            '・落ち着いた雰囲気・誠実で真面目な印象・穏やかな文体: 高スコア\n'
            '・趣味に没頭している・インドア派な印象: 高スコア\n'
            '・派手・社交的・アクティブでチャラい印象: 低スコア（マイナスも可）\n'
            '・遊び目的・SNS慣れしている印象・露骨な性目的: 低スコア\n\n'
            f'自己PR:\n{profile_text[:1500]}\n\n'
            '必ず以下の形式のみで答えてください（説明不要）:\n'
            'SCORE:数字 REASON:一言理由'
          ),
        }],
      }],
    )
    text = message.content[0].text.strip()
    m = re.search(r'SCORE:(-?\d+)\s+REASON:(.+)', text)
    if m:
      return int(m.group(1)), m.group(2).strip()
    return 0, f'(解析結果: {text[:50]})'

  except Exception as e:
    return 0, f'(テキスト解析エラー: {e})'


def _score_jmail_user(profile_text, age_text):
  """
  プロフィールテキストと年齢からスコアを計算する。
  Returns: (score, reasons)
  """
  score = 0
  reasons = []

  # 年齢スコア
  age_score_map = {
    "18～21": 30, "22～25": 25, "26～29": 20,
    "30～34": 10, "35～39": 5,
  }
  for age_key, age_val in age_score_map.items():
    if age_key in age_text:
      score += age_val
      reasons.append(f"年齢{age_text}+{age_val}")
      break

  # 職業スコア（プロフテキストから）
  job_scores = {
    "大学生": 0, "院生": 0,
    "会社員": 2, "フリーランス": 1, "公務員": 2,
    "看護師": 3, "医療": 3,
    "アパレル": 0, "飲食": 2,
    "夜職": -5, "風俗": -5,
  }
  for job, jscore in job_scores.items():
    if job in profile_text:
      score += jscore
      reasons.append(f"{job}{'+' if jscore > 0 else ''}{jscore}")
      break

  # 自己PRに金銭系NGワードがあれば減点
  ng_words = ["金銭", "条件", "サポ", "パパ", "業者", "サクラ", "LINE交換", "インスタ"]
  for ng in ng_words:
    if ng in profile_text:
      score -= 50
      reasons.append(f"NG:{ng}")

  # 自己PR内容をClaudeで雰囲気評価（画像と同じ基準）
  pr_score, pr_reason = _analyze_jmail_profile_text(profile_text)
  if pr_score != 0:
    score += pr_score
    reasons.append(f"自己PR{pr_score:+d}({pr_reason})")

  return score, reasons


def score_and_send_fst_message(name, driver, wait, fst_message, image_path, submitted_users=None, user_check_cnt=None):
  """
  プロフ検索からuser_check_cnt人のユーザーをスコアリングして、
  最高スコアのユーザーにfst_messageを送信する。

  Args:
    name: 自キャラ名（ログ用）
    driver: WebDriver
    wait: WebDriverWait
    fst_message: 送信する初回メッセージ（{name}で相手名を埋め込み可）
    image_path: 送付画像URL（Noneの場合は画像なし）
    submitted_users: 送信済みユーザーリスト（スキップ対象）
    user_check_cnt: 確認するユーザー数（Noneの場合は8〜14のランダム）
  Returns:
    送信先ユーザー名（送信できなかった場合はNone）
  """
  if user_check_cnt is None:
    user_check_cnt = random.randint(8, 14)
  if submitted_users is None:
    submitted_users = []

  print(f"  [{name}] プロフ検索から{user_check_cnt}人をスコアリング中...")

  cookies_dict = {c['name']: c['value'] for c in driver.get_cookies()}

  # ===== プロフ検索ページへ遷移 =====
  driver.get('https://mintj.com/msm/PfSearch/Search/?sid=')
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(1.5)

  # 詳しく検索をクリック
  detail_query = driver.find_elements(By.ID, 'ac2h2')
  if detail_query:
    driver.execute_script('arguments[0].click();', detail_query[0])
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1.5)

  def _check_ids(ids, label_for_log=None):
    """checkbox idリストをすべて選択。すでに選択済みならスキップ。"""
    selected_values = []
    for cid in ids:
      cbs = driver.find_elements(By.ID, cid)
      if not cbs:
        continue
      cb = cbs[0]
      if not cb.is_selected():
        driver.execute_script('arguments[0].click();', cb)
        time.sleep(0.2)
      if cb.is_selected():
        selected_values.append(cb.get_attribute('value'))
    if label_for_log and selected_values:
      print(f"  [{name}] {label_for_log}: {selected_values}")

  def _open_accordion(acc_id):
    els = driver.find_elements(By.ID, acc_id)
    if els:
      driver.execute_script('arguments[0].click();', els[0])
      time.sleep(0.6)

  # 年齢: 18-34
  _check_ids(['CheckAge1', 'CheckAge2', 'CheckAge3', 'CheckAge4'], '年齢')

  # 身長: 169cm以下すべて
  _check_ids(
    ['CheckHeight1', 'CheckHeight2', 'CheckHeight3', 'CheckHeight4', 'CheckHeight5'],
    '身長'
  )

  # 写真あり
  _check_ids(['f01'], '写真あり')

  # 地域: 東京固定 + もう1つを 神奈川/千葉/埼玉/静岡/栃木/群馬 からランダム
  _open_accordion('accordion03')
  # サーバーが前回検索条件を保持してるので、まず全stateチェックを外す
  state_cbs = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][name='state']")
  for scb in state_cbs:
    if scb.is_selected():
      driver.execute_script('arguments[0].click();', scb)
      time.sleep(0.1)
  extra_area_id = random.choice([
    'CheckState-9',   # 神奈川
    'CheckState-10',  # 千葉
    'CheckState-11',  # 埼玉
    'CheckState-24',  # 静岡
    'CheckState-14',  # 栃木
    'CheckState-13',  # 群馬
  ])
  _check_ids(['CheckState-8', extra_area_id], '地域')

  # ルックス: かわいい系/癒し系/カジュアル系/スーツ系/オタ系/お笑い系
  _open_accordion('accordion04')
  _check_ids(
    ['CheckLooksType1', 'CheckLooksType4', 'CheckLooksType6',
     'CheckLooksType16', 'CheckLooksType17', 'CheckLooksType18'],
    'ルックス'
  )

  # 性格: やさしい/明るい/甘えん坊/穏やか/さびしがり/奥手/真面目
  _open_accordion('accordion05')
  _check_ids(
    ['CheckCharacter1', 'CheckCharacter2', 'CheckCharacter5', 'CheckCharacter6',
     'CheckCharacter7', 'CheckCharacter10', 'CheckCharacter11'],
    '性格'
  )

  # 職業: 役員・事業経営(2)/夜職(14)/美容関連(19)/法律関係(31)/モデル(33) 以外
  _open_accordion('accordion06')
  _occupation_exclude = {2, 14, 19, 31, 33}
  _check_ids(
    [f'CheckOccupation{n}' for n in range(1, 38) if n not in _occupation_exclude],
    '職業'
  )

  # 興味あること: 合コン(10)/カラオケ(14)/ギャンブル(15)/テレH・メールH(19)/
  # 不倫・浮気(22)/SM(24)/特殊プレイ(25)/写真・動画(27) 以外
  _open_accordion('accordion07')
  _purpose_exclude = {10, 14, 15, 19, 22, 24, 25, 27}
  _check_ids(
    [f'CheckPurpose{n}' for n in range(0, 28) if n not in _purpose_exclude],
    '目的'
  )

  # 検索実行
  driver.execute_script('window.scrollBy(0, 300);')
  time.sleep(0.5)
  driver.execute_script('window.scrollBy(0, -300);')
  time.sleep(0.5)
  query_submit = driver.find_elements(By.ID, 'button')
  if not query_submit:
    print(f"  [{name}] 検索ボタンが見つかりません")
    return None, submitted_users
  driver.execute_script('arguments[0].click();', query_submit[0])
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(1.5)

  # ===== 検索結果からスコアリング =====
  users = driver.find_elements(By.CLASS_NAME, 'search_list_col')
  if not users:
    print(f"  [{name}] 検索結果が0件です")
    return None, submitted_users

  results = []
  checked = 0
  for i in range(min(len(users), user_check_cnt * 2)):
    if checked >= user_check_cnt:
      break
    try:
      users = driver.find_elements(By.CLASS_NAME, 'search_list_col')
      if i >= len(users):
        break
      driver.execute_script('arguments[0].scrollIntoView({block:"center"});', users[i])
      time.sleep(0.5)
      users[i].find_element(By.TAG_NAME, 'a').click()
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(1)

      if 'err' in driver.current_url:
        driver.back()
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        continue

      # 名前取得
      name_els = driver.find_elements(By.CLASS_NAME, 'userPhotoCard_name')
      if not name_els:
        name_els = driver.find_elements(By.CLASS_NAME, 'prof_name')
      user_name = name_els[0].text.strip() if name_els else ''
      if not user_name:
        driver.back()
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        continue

      # 送信済みスキップ
      if user_name in submitted_users:
        print(f"    [{i+1}] {user_name}: 送信済みスキップ")
        checked += 1
        driver.back()
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        continue

      # mail-off = 未送信 / なければ送信済み
      if not driver.find_elements(By.CLASS_NAME, 'mail-off'):
        print(f"    [{i+1}] {user_name}: メール送信済みスキップ")
        checked += 1
        driver.back()
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        continue

      # 年齢・プロフ取得
      age_els = driver.find_elements(By.CLASS_NAME, 'prof_age')
      age_text = age_els[0].text.strip() if age_els else ''
      pw_els = driver.find_elements(By.CLASS_NAME, 'profile_wrap')
      profile_text = pw_els[0].text if pw_els else ''

      score, reasons = _score_jmail_user(profile_text, age_text)

      # 画像解析
      img_els = driver.find_elements(By.XPATH, '//img[contains(@src,"img2.mintj.com")]')
      if img_els:
        img_url = img_els[0].get_attribute('src')
        img_score, img_reason = _analyze_jmail_image(img_url, cookies_dict)
        print(f"    画像解析: {img_score}点 ({img_reason})")
        if img_score != 0:
          score += img_score
          reasons.append(f'画像{img_score:+d}({img_reason})')

      results.append({
        'name': user_name,
        'score': score,
        'reasons': reasons,
        'url': driver.current_url,
        'index': i,
      })
      print(f"    [{i+1}] {user_name}({age_text}) スコア:{score} ({', '.join(reasons[:3])})")
      checked += 1

      driver.back()
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(1)

    except Exception as e:
      print(f"    [{i+1}] スコアリングエラー: {e}")
      try:
        driver.back()
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
      except Exception:
        pass
      continue

  if not results:
    print(f"  [{name}] 送信対象が見つかりませんでした")
    return None, submitted_users

  # 最高スコアのユーザーへ遷移
  results.sort(key=lambda x: x['score'], reverse=True)
  best = results[0]
  print(f"  [{name}] 最高スコア: {best['name']} ({best['score']}点) → メッセージ送信")

  # 検索結果ページから対象ユーザーを再クリック（URLのsidが空で遷移できないため）
  users = driver.find_elements(By.CLASS_NAME, 'search_list_col')
  if best['index'] < len(users):
    driver.execute_script('arguments[0].scrollIntoView({block:"center"});', users[best['index']])
    time.sleep(0.5)
    users[best['index']].find_element(By.TAG_NAME, 'a').click()
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1.5)
  else:
    # フォールバック: URL直接遷移
    driver.get(best['url'])
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1.5)

  local_img_path = None
  try:
    # メッセージ入力
    textarea = driver.find_elements(By.ID, 'textarea')
    if not textarea:
      print(f"  [{name}] テキストエリアが見つかりません")
      return None, submitted_users
    message = fst_message.format(name=best['name']) if '{name}' in fst_message else fst_message
    message = _encode_for_sjis_form(message)
    driver.execute_script('arguments[0].scrollIntoView({block:"center"});', textarea[0])
    driver.execute_script(
      'arguments[0].value = arguments[1];'
      'arguments[0].dispatchEvent(new Event("input", {bubbles: true}));'
      'arguments[0].dispatchEvent(new Event("change", {bubbles: true}));',
      textarea[0], message
    )
    time.sleep(1)

    # 画像があればダウンロードしてセット
    if image_path:
      try:
        if image_path.startswith('http'):
          img_url = image_path
        else:
          img_url = f'https://meruopetyan.com{image_path}'
        img_response = requests.get(img_url, timeout=10)
        ext = os.path.splitext(image_path)[1] or '.jpg'
        local_img_path = os.path.abspath(f"{name}_jmail_fst{ext}")
        with open(local_img_path, 'wb') as f:
          f.write(img_response.content)
        img_input = driver.find_elements(By.NAME, 'image1')
        if img_input:
          img_input[0].send_keys(local_img_path)
          time.sleep(2)
      except Exception as e:
        print(f"  [{name}] 画像セットエラー: {e}")

    # 送信（labelをクリック）
    send_label = driver.find_elements(By.CSS_SELECTOR, 'label[for="message_send"]')
    if not send_label:
      send_label = driver.find_elements(By.ID, 'message_send')
    if not send_label:
      print(f"  [{name}] 送信ボタンが見つかりません")
      return None, submitted_users
    driver.execute_script('arguments[0].click();', send_label[0])
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    print(f"  [{name}] → {best['name']} に送信完了")
    submitted_users.append(best['name'])

    if local_img_path and os.path.exists(local_img_path):
      os.remove(local_img_path)

    return best['name'], submitted_users

  except Exception as e:
    print(f"  [{name}] メッセージ送信エラー: {e}")
    traceback.print_exc()
    if local_img_path and os.path.exists(local_img_path):
      os.remove(local_img_path)
    return None, submitted_users

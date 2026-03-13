from selenium import webdriver
from selenium.webdriver.common.keys import Keys
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
import base64
import json
from selenium.webdriver.support import expected_conditions as EC
import base64
import requests
from selenium.common.exceptions import WebDriverException
import gc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from twocaptcha import TwoCaptcha
import shutil
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
  StaleElementReferenceException,
  ElementClickInterceptedException,
  InvalidArgumentException,
  NoSuchElementException,
  TimeoutException,
)

# 元のメソッドを退避
_original_find_element = WebDriver.find_element
_original_find_elements = WebDriver.find_elements
_original_we_find_element = WebElement.find_element
_original_we_find_elements = WebElement.find_elements

def _fix_locator(by, value):
    """
    Appium + Android Chrome で invalid locator になりがちなパターンを
    CSS セレクタなどに変換する
    """
    # CLASS_NAME → CSS
    if by == By.CLASS_NAME:
        # "warning screen" みたいにスペース区切りの場合、
        # class="warning screen" → .warning.screen に変換
        classes = value.split()
        css = "." + ".".join(classes)
        return By.CSS_SELECTOR, css

    # ID → CSS
    if by == By.ID:
        return By.CSS_SELECTOR, f"#{value}"

    # NAME → CSS
    if by == By.NAME:
        return By.CSS_SELECTOR, f'[name="{value}"]'

    # 他はそのまま
    return by, value


def _patched_find_element(self, by=By.ID, value=None):
    try:
        return _original_find_element(self, by, value)
    except InvalidArgumentException:
        new_by, new_value = _fix_locator(by, value)
        if (new_by, new_value) == (by, value):
            # 変換できないならそのまま投げ直す
            raise
        # 変換したロケータでもう一度トライ
        return _original_find_element(self, new_by, new_value)


def _patched_find_elements(self, by=By.ID, value=None):
    try:
        return _original_find_elements(self, by, value)
    except InvalidArgumentException:
        new_by, new_value = _fix_locator(by, value)
        if (new_by, new_value) == (by, value):
            raise
        return _original_find_elements(self, new_by, new_value)

def _patched_we_find_element(self, by=By.ID, value=None):
    try:
        return _original_we_find_element(self, by, value)
    except InvalidArgumentException:
        new_by, new_value = _fix_locator(by, value)
        if (new_by, new_value) == (by, value):
            raise
        return _original_we_find_element(self, new_by, new_value)


def _patched_we_find_elements(self, by=By.ID, value=None):
    try:
        return _original_we_find_elements(self, by, value)
    except InvalidArgumentException:
        new_by, new_value = _fix_locator(by, value)
        if (new_by, new_value) == (by, value):
            raise
        return _original_we_find_elements(self, new_by, new_value)

# WebDriver をモンキーパッチ
WebDriver.find_element = _patched_find_element
WebDriver.find_elements = _patched_find_elements
WebElement.find_element = _patched_we_find_element
WebElement.find_elements = _patched_we_find_elements


# 警告画面
def catch_warning_screen(driver):
  wait = WebDriverWait(driver, 15)
  anno = driver.find_elements(By.CLASS_NAME, value="anno")
  warning = driver.find_elements(By.CLASS_NAME, value="warning screen")
  dialog = driver.find_elements(By.ID, value="_information_dialog")
  dialog2 = driver.find_elements(By.ID, value="_information_dialog")
  dialog3 = driver.find_elements(By.ID, value="information__dialog")
  remodal_image = driver.find_elements(By.CLASS_NAME, value="remodal-image")
  remodal_wrapper = driver.find_elements(By.CLASS_NAME, value="remodal-wrapper")
  remodal = driver.find_elements(By.CLASS_NAME, value="remodal")
  loader = driver.find_elements(By.CLASS_NAME, "loader")
  # loaderが表示されている場合は待機
  loader_cnt = 0
  while loader and loader[0].is_displayed():
    print("loaderが表示されています")      
    time.sleep(2)
    loader = driver.find_elements(By.CLASS_NAME, "loader")
    loader_cnt += 1
    if loader_cnt > 5:
      break
  if len(remodal):
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="modal-cancel")
    print(len(modal_cancel))
    if len(modal_cancel):
      modal_cancel[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      # print("ボタンを押して10秒待機します")
      time.sleep(1)
      # print("待機しました")
      swiper_button = driver.find_elements(By.CLASS_NAME, value="swiper-button-next")
      if len(swiper_button):
        driver.execute_script("arguments[0].click();", swiper_button[0])
        time.sleep(1)
  ds_t_center = driver.find_elements(By.CLASS_NAME, value="ds_t_center")
  if len(ds_t_center):
    if "警告" in ds_t_center[0].text:
      ds_round_btn = driver.find_elements(By.CLASS_NAME, value="ds_round_btn")
      ds_round_btn[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1.5)
  re_login_button_elem = driver.find_elements(By.CLASS_NAME, value="ds_pt5p")
  if len(re_login_button_elem):
    if "ログインへ" in re_login_button_elem[0].text:
      re_login_button = re_login_button_elem[0].find_elements(By.TAG_NAME, value="a")
      re_login_button[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1.5)
  if len(dialog):
    if "この登録は利用できません" in dialog[0].text:
      return "この登録は利用できません"
  if len(dialog3):
    if "この登録は利用できません" in dialog3[0].text:
      return "この登録は利用できません"
  warinig_cnt =0
  while len(warning) or len(anno) or len(dialog) or len(dialog2) or len(dialog3) or len(remodal_image) or len(remodal_wrapper):
    driver.refresh()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    warning = driver.find_elements(By.CLASS_NAME, value="warning screen")
    anno = driver.find_elements(By.CLASS_NAME, value="anno")
    dialog = driver.find_elements(By.ID, value="_information_dialog")
    dialog2 = driver.find_elements(By.ID, value="information__dialog")
    remodal = driver.find_elements(By.CLASS_NAME, value="remodal-image")
    remodal_wrapper = driver.find_elements(By.CLASS_NAME, value="remodal-wrapper")
    warinig_cnt += 1
    if warinig_cnt > 2:
       return "警告画面が出ている可能性があります"
  acceptance = driver.find_elements(By.CLASS_NAME, value="ds_round_btn")
  if len(acceptance):
    # print(acceptance[0].text)
    if acceptance[0].text == "承諾":
      acceptance[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(2)
      print("警告画面に承諾しました。一度ログアウトします")
  # ds_main_header_text
  some_erorr = driver.find_elements(By.CLASS_NAME, value="ds_main_header_text")
  if len(some_erorr):
    if 'ログインできません' in some_erorr[0].text:
      return "ログインできませんでした"
  return False

def nav_item_click(nav_name, driver, wait):
  catch_warning_screen(driver)
  nav_list = driver.find_elements(By.ID, value='ds_nav')
  if not len(nav_list):
    driver.get("https://happymail.co.jp/sp/app/html/mbmenu.php")
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    nav_list = driver.find_elements(By.ID, value='ds_nav')
    if not len(nav_list):
      print(f"ナビゲーターリストの取得に失敗しました")
      return False
  navs = nav_list[0].find_elements(By.CLASS_NAME, value="ds_nav_item")
  for nav in navs:
    if nav_name in nav.text:
      if nav_name == "メッセージ":
        # nav_link = nav.find_elements(By.TAG_NAME, value="a")
        # driver.execute_script("arguments[0].click();", nav_link[0])
        # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        # time.sleep(2) 
        # break
        new_message = nav.find_elements(By.CLASS_NAME, value="ds_red_circle")
        if not len(new_message):
          return "新着メールなし"   
      nav_link = nav.find_elements(By.TAG_NAME, value="a")
      driver.execute_script("arguments[0].click();", nav_link[0])
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(2) 
      if nav_name == "メッセージ":   
        if driver.current_url not in (
            "https://happymail.co.jp/app/html/message_list.php",
            "https://happymail.co.jp/sp/app/html/message_list.php",
        ):    
          catch_warning_screen(driver)
          driver.execute_script("arguments[0].click();", nav_link[0])
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)    
        return True
      break
  return False

def login(name, happymail_id, happymail_pass, driver, wait,):
  try:
    driver.delete_all_cookies()
    driver.get("https://happymail.jp/login/")
    # loaderが消えるのを待つ
    WebDriverWait(driver, 10).until(
      EC.invisibility_of_element_located((By.CLASS_NAME, "loader"))
    )
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    wait_time = random.uniform(1.5, 4)
    time.sleep(1.5)
    if "https://happymail.jp/" == driver.current_url:
      # ds_gree_botton
      ds_gree_botton = driver.find_elements(By.CLASS_NAME, value="ds_gree_botton")
      ds_gree_botton[0].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1.5)
    re_login_button_elem = driver.find_elements(By.CLASS_NAME, value="ds_pt5p")
    if len(re_login_button_elem):
      if "ログインへ" in re_login_button_elem[0].text:
        re_login_button = re_login_button_elem.find_elements(By.TAG_NAME, value="a")
        re_login_button[0].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1.5)
    id_form = driver.find_element(By.ID, value="TelNo") 
    id_form.send_keys(happymail_id)
    pass_form = driver.find_element(By.ID, value="TelPass")
    pass_form.send_keys(happymail_pass)
    time.sleep(wait_time)
    send_form = driver.find_element(By.ID, value="login_btn")
    send_form.click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    login_judge_flug = driver.find_elements(By.ID, value="ds_header")
    if not len(login_judge_flug):
      print("reCAPTCHA認証中。。。")
      login_url = "https://happymail.jp/login/"
      site_key = "6Lctr88qAAAAAJtvi_1IhWBSdmMcV8k23_lb63xf"
      API_KEY = "1bc4af1c018d3882d89bae813594befb"  
      solver = TwoCaptcha(API_KEY)
      try:
        result = solver.recaptcha(
          sitekey=site_key,
          url=login_url,
          invisible=1)
      except Exception as e:
        sys.exit(e)
      else:
        # print('solved: ' + str(result))
        print("reCAPTCHA認証に成功しました")
        g_recaptcha_response = driver.find_elements(By.ID, value="g-recaptcha-response")    
        # print(len(g_recaptcha_response))
        # print('===========')
        if len(g_recaptcha_response):
          try:
            driver.execute_script("""
                let recaptchaInput = document.getElementById("g-recaptcha-response");
                recaptchaInput.style.display = "block"; // 一時的に表示
                recaptchaInput.value = arguments[0]; // 値をセット
                recaptchaInput.style.display = "none"; // 再度非表示

                // grecaptcha を強制実行
                if (typeof(grecaptcha) !== 'undefined') {
                    let recaptchaResponse = recaptchaInput.value;
                    grecaptcha.getResponse = function() { return recaptchaResponse; };
                    document.querySelector('form').submit();
                }
            """, result["code"])
          except Exception as e:
              print(f"❌ reCAPTCHA の解決に失敗: {e}")
    return False
  except Exception as e:  
    print(f"ログインに失敗しました")
    print(traceback.format_exc())
    return f"ログインに失敗しました"

def check_top_image(name, driver, wait):
  nav_item_click("マイページ", driver, wait)
  # 名前チェック
  name_ele = driver.find_elements(By.CLASS_NAME, value="ds_mypage_name")
  if len(name_ele):
    if name != name_ele[0].text:
      print(f"{name}のブラウザが{name_ele[0].text}になっています")
      return f"{name}のブラウザが{name_ele[0].text}になっています"
  else:
    print(f"{name}の名前チェックでds_mypage_name要素が見つかりません")
    print(driver.current_url)
  # 画像チェック　
  top_img_element = driver.find_elements(By.CLASS_NAME, value="ds_mypage_user_image")
  if len(top_img_element):
    top_img = top_img_element[0].get_attribute("style")
    if "noimage" in top_img:
      print(f"{name}のトップ画の設定がNoImageです")
      return f"ハッピーメール{name}のトップ画の設定がNoImageです"
  return False
    

def start_the_drivers_login(mail_info, happymail_list, headless, base_path, tab):
  drivers = {}
  try:
    # driver起動,ログイン
    # mohu = 0
    for i in happymail_list:
      
      # mohu += 1
      # if mohu > 4:
      #   continue
      # if  i["name"] != "ゆっこ":
      #   continue
      
      print("変更前:", func.get_current_ip())
      func.change_tor_ip()
      print("変更後:", func.get_current_ip())
      profile_path = os.path.join(base_path, i["name"])
      if os.path.exists(profile_path):
        shutil.rmtree(profile_path)  # フォルダごと削除
        os.makedirs(profile_path, exist_ok=True)
      # iPhone14
      user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/537.36"
      driver,wait = func.get_multi_driver(profile_path, headless, user_agent)
      login_flug = login(i["name"], i["login_id"], i["password"], driver, wait)
      if login_flug:
        # print(f"{i['name']} {login_flug}")
        if mail_info:
          title = "メッセージ"
          text = f"ハッピーメール {i['name']}:{i['login_id']}:{i['password']}:  {login_flug}"
          # メール送信
          if mail_info:
            func.send_mail(text, mail_info, title)
          else:
            print("通知メールの送信に必要な情報が不足しています")
            print(f"{mail_info}")
        driver.quit()
        continue
      warning = catch_warning_screen(driver)
      if warning:
        # print(f"{i['name']} {warning}")
        if mail_info:
          img_path = f"{i['name']}_ban.png"
          driver.save_screenshot(img_path)
          title = "メッセージ"
          text = f"ハッピーメール {i['name']}:{i['login_id']}:{i['password']}:  {warning}"
          # メール送信
          if mail_info:
            func.send_mail(text, mail_info, title, img_path)
          else:
            print("通知メールの送信に必要な情報が不足しています")
            print(f"{mail_info}")
        
        driver.quit()
        continue
      else:
        print(f"{i['name']}のログインに成功しました")
      # タブを追加する
      # if tab:
      #   driver.execute_script("window.open('https://happymail.co.jp/sp/app/html/mbmenu.php', '_blank');")
      #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      #   time.sleep(1)
      drivers[i["name"]] = {"name":i["name"], "login_id":i["login_id"], "password":i["password"], "post_title":i["post_title"], "post_contents":i["post_contents"],"driver": driver, "wait": wait, "fst_message": i["fst_message"], "return_foot_message":i["return_foot_message"], "conditions_message":i["second_message"], "mail_img":i["chara_image"], "post_return_message":i["post_return_message"],}
    time.sleep(1)
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
  
def multidrivers_checkmail(name, driver, wait, login_id, password, return_foot_message, fst_message, post_return_message, second_message, conditions_message, confirmation_mail, mail_img, gmail_address, gmail_password, return_check_cnt, android,  chara_prompt,):
    return_list = []
    new_mail_cnt = 0
    loop_cnt = 0
    if driver.current_url != "https://happymail.co.jp/sp/app/html/mbmenu.php":
      driver.get("https://happymail.co.jp/sp/app/html/mbmenu.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(0.7)
    else:
      driver.refresh()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(0.7)

    ban_flug = catch_warning_screen(driver)
    if isinstance(ban_flug, str) and "利用できません" in ban_flug:
      return "この登録は利用できません"
    new_message_flug = nav_item_click("メッセージ", driver, wait)
    # print(f"新着メールフラグ: {new_message_flug}")
    if new_message_flug == "新着メールなし":
      return
    else:  
    # 新着があった
    # if True:
      #  未読のみ表示
      catch_warning_screen(driver)
      only_new_message = driver.find_elements(By.CLASS_NAME, value="ds_message_tab_item")[1]
      # only_new_message = driver.find_elements(By.CLASS_NAME, value="ds_message_tab_item")[2] #未返信
      only_new_message.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      new_mail = driver.find_elements(By.CLASS_NAME, value="ds_message_list_mini") 
      print(f"新着メール数:{len(new_mail)} ")
      if not len(new_mail):
        list_load = driver.find_elements(By.ID, value="load_bL")
        if len(list_load):
          list_load[0].click()
        time.sleep(2)
      #新着がある間はループ
      while len(new_mail):
      # while True:
        date_elems = new_mail[0].find_elements(By.CLASS_NAME, value="ds_message_date")
        text = date_elems[0].text if date_elems else ""
        now = datetime.now()
        # print(f"メッセージ日時テキスト: {text}")
        arrival_datetime = func.parse_arrival_datetime(text, now)
        if arrival_datetime is None:
            # 取れないときは安全側に倒す（4分経過扱い）
            for_minutes_passed = True
        else:
            elapsed_time = now - arrival_datetime
            # print(f"メール到着からの経過時間{elapsed_time}")
            for_minutes_passed = elapsed_time >= timedelta(minutes=4)
        # if True:
        if for_minutes_passed:
          print("4分以上経過しているメッセージあり")  
          user_name = new_mail[new_mail_cnt].find_element(By.CLASS_NAME, value="ds_message_name__item").text 
          # 年齢チェック
          user_age = new_mail[0].find_element(By.CLASS_NAME, value="ds_message_pref")
          # print(f"年齢チェック {user_age.text} {user_name}")
          if not re.search(r"20代|18.?19", user_age.text):
            print("年齢が１０〜２０代ではないユーザー　AIで返信します") 
            print(f"{user_name} {user_age.text}")
            chat_ai_flug = True
          else:
            print("年齢が10代〜20代のユーザー 定型分送信")
            chat_ai_flug = False
          new_mail[new_mail_cnt].click()
          # new_mail[1].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
          catch_warning_screen(driver)
          send_message = driver.find_elements(By.CLASS_NAME, value="message__block--send")      
          send_me_length = len(send_message)
          received_elem = driver.find_elements(By.CLASS_NAME, "message__block--receive")
          if len(received_elem):
            received_message = received_elem[-1].text
            print(f"受信メッセージ: {received_message}")
            email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
            email_list = re.findall(email_pattern, received_message)
            if email_list:
              if "icloud.com" in received_message:
                print("icloud.comが含まれています")
                icloud_text = "メール送ったんですけど、ブロックされちゃって届かないのでこちらのアドレスにお名前添えて送ってもらえますか？\n" + gmail_address
                try:
                  text_area = driver.find_element(By.ID, value="text-message")
                  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
                  script = "arguments[0].value = arguments[1];"  
                  driver.execute_script(script, text_area, icloud_text)
                  time.sleep(0.5)
                  driver.execute_script("arguments[0].click();", text_area)
                  # 送信
                  send_mail = driver.find_element(By.ID, value="submitButton")
                  send_mail.click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(1.5) 
                  send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
                  reload_cnt = 0
                  send_message_clean = func.normalize_text(icloud_text)
                  send_text_clean = func.normalize_text(send_msg_elem[-1].text)
                  while send_text_clean != send_message_clean:
                    # print(send_text_clean)
                    # print("~~~~~~~~~~~~~~~~~~~~~")
                    # print(send_message)
                    driver.refresh()
                    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                    time.sleep(5)
                    send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
                    reload_cnt += 1
                    if reload_cnt == 3:
                        driver.refresh()
                        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                        time.sleep(1.5)
                        break
                except Exception:
                  pass
              else:
                for user_address in email_list:
                  user_address = func.normalize_text(user_address)
                  site = "ハッピーメール"
                  try:
                    
                    func.send_conditional(user_name, user_address, gmail_address, gmail_password, conditions_message, site)
                    print(f"{user_name}にアドレス内1stメールを送信しました")
                  except Exception:
                    print(f"{name} アドレス内1stメールの送信に失敗しました")
                    error = traceback.format_exc()
                    traceback.print_exc()
                    print(f"user_address:{user_address}  gmail_address:{gmail_address} gmail_password:{gmail_password}")
                    print(conditions_message)
                    func.send_error(name, f"アドレス内1stメールの送信に失敗しました\n{user_address}\n {gmail_address}\n {gmail_password}\n\n{error}",
                                          )
                if confirmation_mail:
                  try:
                    text_area = driver.find_element(By.ID, value="text-message")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
                    script = "arguments[0].value = arguments[1];"  
                    driver.execute_script(script, text_area, confirmation_mail)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", text_area)
                    # 送信
                    send_mail = driver.find_element(By.ID, value="submitButton")
                    send_mail.click()
                    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                    time.sleep(1.5) 
                    send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
                    reload_cnt = 0
                    send_message_clean = func.normalize_text(confirmation_mail)
                    send_text_clean = func.normalize_text(send_msg_elem[-1].text)
                    while send_text_clean != send_message_clean:
                      # print(send_text_clean)
                      # print("~~~~~~~~~~~~~~~~~~~~~")
                      # print(send_message)
                      driver.refresh()
                      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                      time.sleep(5)
                      send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
                      reload_cnt += 1
                      if reload_cnt == 3:
                          driver.refresh()
                          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                          time.sleep(1.5)
                          break
                  except Exception:
                    pass
            
              # みちゃいや
              plus_icon_parent = driver.find_elements(By.CLASS_NAME, value="message__form__action")
              plus_icon = plus_icon_parent[0].find_elements(By.CLASS_NAME, value="icon-message_plus")
              driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", plus_icon[0])
              plus_icon[0].click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
              mityaiya = ""
              candidate_mityaiya = driver.find_elements(By.CLASS_NAME, value="ds_message_txt_media_text")
              for c_m in candidate_mityaiya:
                if c_m.text == "見ちゃいや":
                    mityaiya = c_m
              if mityaiya:
                # print('<<<<<<<<<<<<<<<<<みちゃいや登録>>>>>>>>>>>>>>>>>>>')
                mityaiya.click()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(2)
                mityaiya_send = driver.find_elements(By.CLASS_NAME, value="input__form__action__button__send")
                if len(mityaiya_send):
                  mityaiya_send[0].click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(1)   
              driver.get("https://happymail.co.jp/sp/app/html/message_list.php")
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
              new_mail = driver.find_elements(By.CLASS_NAME, value="happy_blue_10")  
              continue
          if len(send_message):
            # print(send_message[-1].get_attribute("outerHTML"))   
            img = send_message[-1].find_elements(By.CLASS_NAME, value="attached_media_link")
            if len(img):
              # print("画像あり")
              send_me_length -= 1
            
            # print(send_message[-2].text)
            # sent_text_element = send_message[-2]
          # script = """
          # var element = arguments[0];

          # // 除外するクラスを持つ子要素を取得
          # var elementsToRemove = element.querySelectorAll('.transit_info, .message__block__body__time');

          # // 一時的に削除
          # elementsToRemove.forEach(el => el.remove());

          # // 要素Aのテキストを取得
          # var textContent = element.textContent.trim();

          # // 削除した子要素を元に戻す
          # elementsToRemove.forEach(el => element.appendChild(el));

          # return textContent;
          # """
          # text_without_children = driver.execute_script(script, sent_text_element) 
          print(f"{send_message} len(send_message)")

          if not chat_ai_flug:    
            if send_me_length == 0:
              send_message = fst_message.format(name=user_name) 
              # print(user_name)
              # 掲示板からきたか確認
              text_from_users = driver.find_elements(By.CLASS_NAME, value="message__block--receive")
              for t_f_u in text_from_users:
                if "募集から送信" in t_f_u.text:
                  if post_return_message:
                    send_message = post_return_message.format(name=user_name)    
                    # print(user_name)
                    # print(send_message)     
              text_area = driver.find_element(By.ID, value="text-message")
              driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
              script = "arguments[0].value = arguments[1];"
              driver.execute_script(script, text_area, send_message)
              time.sleep(0.5)
              driver.execute_script("arguments[0].click();", text_area)
              time.sleep(0.5)
              # 送信
              send_mail = driver.find_element(By.ID, value="submitButton")
              send_mail.click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(1.5)
              send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
              reload_cnt = 0
              send_message_clean = func.normalize_text(send_message)
              while not len(send_msg_elem):
                if android:
                  send_mail.click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(7)
                else:
                  driver.refresh()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(3)
                  # message__block__body__text--female 
                send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
                reload_cnt += 1
                if reload_cnt == 3:
                  driver.refresh()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(3)
                  break
              # 画像があれば送信 
              try:
                if mail_img:  
                  # 画像データを取得してBase64にエンコード
                  image_response = requests.get(mail_img)
                  image_base64 = base64.b64encode(image_response.content).decode('utf-8')
                  # ローカルに一時的に画像ファイルとして保存
                  image_filename = f"{name}_image.png"
                  with open(image_filename, 'wb') as f:
                      f.write(base64.b64decode(image_base64))
                  # 画像の保存パスを取得
                  image_path = os.path.abspath(image_filename)
                  img_conform = driver.find_element(By.ID, value="media-confirm")
                  plus_icon = driver.find_elements(By.ID, value="ds_js_media_display_btn")
                  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", plus_icon[0])
                  time.sleep(1)
                  driver.execute_script("arguments[0].click();", plus_icon[0])
                  time.sleep(1)
                  upload_file = driver.find_element(By.ID, "upload_file")
                  upload_file.send_keys(image_path)
                  time.sleep(2)
                  submit = driver.find_element(By.ID, value="submit_button")
                  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", submit)
                  driver.execute_script("arguments[0].click();", submit)
                  while img_conform.is_displayed():
                    time.sleep(2)
                    modal_content = driver.find_elements(By.CLASS_NAME, value="modal-content")
                    if len(modal_content):
                      break # modal-content お相手が年齢確認されていない為
              except Exception as e:
                print("画像の送信に失敗しました", e)
                print(traceback.format_exc())
            elif send_me_length == 1:
              send_message = second_message.format(name=user_name) 
              # print(user_name)
              # print(send_message)
              # 掲示板からきたか確認
              text_from_users = driver.find_elements(By.CLASS_NAME, value="message__block--receive")
              for t_f_u in text_from_users:
                if "募集から送信" in t_f_u.text:
                  if post_return_message:
                    send_message = ""
                    print('やり取りしてます')
                    receive_contents = driver.find_elements(By.CLASS_NAME, value="message__block--receive")[-1]
                    return_message = f"{name}happymail,{login_id}:{password}\n{user_name}「{receive_contents.text}」"
                    return_list.append(return_message)      
              if send_message:
                text_area = driver.find_element(By.ID, value="text-message")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
                script = "arguments[0].value = arguments[1];"  
                driver.execute_script(script, text_area, send_message)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", text_area)
                # 送信
                send_mail = driver.find_element(By.ID, value="submitButton")
                send_mail.click()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(1.5) 
                send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
                reload_cnt = 0
                send_message_clean = func.normalize_text(send_message)
                send_text_clean = func.normalize_text(send_msg_elem[-1].text)
                while send_text_clean != send_message_clean:
                  # print(send_text_clean)
                  # print("~~~~~~~~~~~~~~~~~~~~~")
                  # print(send_message)
                  driver.refresh()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(5)
                  send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
                  reload_cnt += 1
                  if reload_cnt == 3:
                      driver.refresh()
                      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                      time.sleep(1.5)
                      break       
            else:
              print('やり取りしてます')
              receive_contents = driver.find_elements(By.CLASS_NAME, value="message__block--receive")[-1]
              return_message = f"{name}happymail,{login_id}:{password}\n{user_name}「{receive_contents.text}」"
              return_list.append(return_message) 
              # みちゃいや
              plus_icon_parent = driver.find_elements(By.CLASS_NAME, value="message__form__action")
              plus_icon = plus_icon_parent[0].find_elements(By.CLASS_NAME, value="icon-message_plus")
              driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", plus_icon[0])
              plus_icon[0].click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
              mityaiya = ""
              candidate_mityaiya = driver.find_elements(By.CLASS_NAME, value="ds_message_txt_media_text")
              for c_m in candidate_mityaiya:
                if c_m.text == "見ちゃいや":
                    mityaiya = c_m
              if mityaiya:
                # print('<<<<<<<<<<<<<<<<<みちゃいや登録>>>>>>>>>>>>>>>>>>>')
                mityaiya.click()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(2)
                mityaiya_send = driver.find_elements(By.CLASS_NAME, value="input__form__action__button__send")
                if len(mityaiya_send):
                  mityaiya_send[0].click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(1)   
          else: #AIチャット返信
            if chara_prompt:
              history = []
              male_history = []
              message__blocks = driver.find_elements(By.CLASS_NAME, value="message__block")
              for message__block in message__blocks:
                femail_flug = message__block.find_elements(By.CLASS_NAME, value="message__block__body__text--female") 
                if len(femail_flug):
                  history.append({"role": "model", "text": femail_flug[0].text})
                mail_flug = message__block.find_elements(By.CLASS_NAME, value="message__block__body__text--male") 
                if len(mail_flug):
                  history.append({"role": "user", "text": mail_flug[0].text})
                  male_history.append(mail_flug[0].text)
              if not male_history:
                user_input = None
              else:
                user_input = male_history[-1]
              print("AIチャット返信処理を開始します")
              print(history)
              print("-----------")
              ai_response, all_history = func.chat_ai(chara_prompt, history, fst_message, user_input) 
              if ai_response is None:
                print("Gemini制限中のため返信しません")
                return
              text_area = driver.find_element(By.ID, value="text-message")
              driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
              script = "arguments[0].value = arguments[1];"  
              driver.execute_script(script, text_area, ai_response)
              time.sleep(0.5)
              driver.execute_script("arguments[0].click();", text_area)
              # 送信
              send_mail = driver.find_element(By.ID, value="submitButton")
              send_mail.click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(1.5) 
              send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
              reload_cnt = 0
              send_message_clean = func.normalize_text(ai_response)
              send_text_clean = func.normalize_text(send_msg_elem[-1].text)
              while send_text_clean != send_message_clean:
                # print(send_text_clean)
                # print("~~~~~~~~~~~~~~~~~~~~~")
                # print(send_message)
                driver.refresh()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(5)
                send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
                reload_cnt += 1
                if reload_cnt == 3:
                    driver.refresh()
                    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                    time.sleep(1.5)
                    break  
              #やり取りを通知  
              # Improve formatting
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
              return_message = f"{name}happymail,{login_id}:{password}\n{user_name}\n{mail_text}"
              return_list.append(return_message) 
          driver.get("https://happymail.co.jp/sp/app/html/message_list.php")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
          new_mail = driver.find_elements(By.CLASS_NAME, value="happy_blue_10")
        else:
          if len(new_mail):
            new_mail_cnt += 1
            if len(new_mail) <= new_mail_cnt:
              break
        loop_cnt += 1
        if loop_cnt >= return_check_cnt:
          print("新着メール確認ループ回数上限に達しました")
          break
    if len(return_list):
      return return_list
    else:
      return None

def re_post(name,  driver, wait, title, post_text):
  try:
    area_list = ["東京都", "千葉県", "埼玉県", "神奈川県", "栃木県", "静岡県"]
    repost_flug_list = []  
    wait_time = random.uniform(2, 3)
    # TOPに戻る
    driver.get("https://happymail.co.jp/sp/app/html/mbmenu.php")
    driver.delete_cookie("outbrain_cid_fetch")
    # 警告画面が出たらスキップ
    warning_flug = catch_warning_screen(driver)
    if warning_flug:
      print(f"{name}：警告画面が出ている可能性があります")
      return False
    # マイページをクリック
    nav_item_click("マイページ", driver, wait)
    # マイリストをクリック
    common_list = driver.find_element(By.CLASS_NAME, "ds_common_table")
    common_table = common_list.find_elements(By.CLASS_NAME, "ds_mypage_text")
    for common_table_elem in common_table:
      if "マイリスト" in common_table_elem.text:
          mylist = common_table_elem
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", mylist)
    time.sleep(wait_time)
    mylist.click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    # 掲示板履歴をクリック
    menu_list = driver.find_element(By.CLASS_NAME, "ds_menu_link_list")
    menu_link = menu_list.find_elements(By.CLASS_NAME, "ds_next_arrow")
    bulletin_board_history = menu_link[4]
    bulletin_board_history.click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    warning_flug = catch_warning_screen(driver)
    #その他掲示板をクリック
    link_tab = driver.find_elements(By.CLASS_NAME, "ds_link_tab_text")
    others_bulletin_board = link_tab[1]
    others_bulletin_board.click()
    time.sleep(1)
  
    # ジャンル選択
    # genre_dict = {0:"今すぐ会いたい", 1:"大人の出会い"}  
    genre = driver.find_elements(By.CLASS_NAME, value="ds_bd_none")
    road_cnt = 1
    while len(genre) <= 2:
      time.sleep(2)
      genre = driver.find_elements(By.CLASS_NAME, value="ds_bd_none")
      road_cnt += 1
      if road_cnt == 7:
          break
    
    if len(genre) == 1:
      print(f"{name} 掲示板投稿がありません")
      repost_flug_list.append(f"{name} 掲示板投稿がありません")
      return repost_flug_list
    genre = genre[1].text
    print("<<<再投稿する掲示板のジャンル取得>>>")
    print(genre)
    # 1日に書き込めるのは五回まで
      # for i, kanto in enumerate(area_list):
      #   # 掲示板重複を削除する
      #   driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      #   time.sleep(2)
      #   area_texts = driver.find_elements(By.CLASS_NAME, value="ds_write_bbs_status")
      #   area_texts_list = []
      #   for area in area_texts:
      #     shaping_area = area.text.replace(" ", "").replace("\n", "")
      #     area_texts_list.append(shaping_area)
      #   area_cnt = 0
      #   list = []
      #   for area_text in area_texts_list:
      #     if area_text not in list:
      #         list.append(area_text)
      #         area_cnt += 1
      #     else:
      #         print("重複があった")
      #         duplication_area = driver.find_elements(By.CLASS_NAME, value="ds_round_btn_red")[area_cnt]
      #         driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", duplication_area)
      #         time.sleep(2)
      #         duplication_area.click()
      #         wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      #         time.sleep(wait_time)
      #         delete = driver.find_element(By.CLASS_NAME, "modal-confirm")
      #         delete.click()
      #         time.sleep(2)

      #   #  掲示板をクリック
      #   nav_list = driver.find_element(By.ID, value='ds_nav')
      #   bulletin_board = nav_list.find_element(By.LINK_TEXT, "募集")
      #   bulletin_board.click()
      #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      #   time.sleep(wait_time)
      #   # 書き込みをクリック
      #   write = driver.find_element(By.CLASS_NAME, value="icon-header_kakikomi")
      #   write.click()
      #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      #   time.sleep(wait_time)
      #   # 書き込み上限に達したらスキップ
      #   adult = driver.find_elements(By.CLASS_NAME, value="remodal-wrapper")
      #   print(len(adult))
      #   if len(adult):
      #       print("24時間以内の掲示板書き込み回数の上限に達しています(1日5件まで)")
      #       cancel = driver.find_element(By.CLASS_NAME, value="modal-cancel")
      #       cancel.click()
      #       driver.get("https://happymail.co.jp/sp/app/html/mbmenu.php")
      #       continue
      #   # その他掲示板をクリック
      #   link_tab = driver.find_elements(By.CLASS_NAME, "ds_link_tab_text")
      #   others_bulletin_board = link_tab[1]
      #   others_bulletin_board.click()
      #   time.sleep(2)
      #   # ジャンルを選択
      #   select_genre = driver.find_element(By.ID, value="keijiban_adult_janl")
      #   select = Select(select_genre)
      #   select.select_by_visible_text(genre_dict[genre_flag])
      #   time.sleep(1)
      #   # タイトルを書き込む
      #   input_title = driver.find_element(By.NAME, value="Subj")
      #   driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", input_title)
      #   input_title.send_keys(title)
      #   time.sleep(1)
      #   # 本文を書き込む
      #   text_field = driver.find_element(By.ID, value="text-message")
      #   driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_field)
      #   text_field.send_keys(post_text)
      #   time.sleep(1)
      #   # 書き込みエリアを選択
      #   select_area = driver.find_element(By.NAME, value="wrtarea")
      #   select = Select(select_area)
      #   select.select_by_visible_text(kanto)
      #   time.sleep(1)
      #   mail_rep =driver.find_element(By.NAME, value="Rep")
      #   select = Select(mail_rep)
      #   select.select_by_visible_text("10件")
      #   time.sleep(1)
      #   # 書き込む
      #   writing = driver.find_element(By.ID, value="billboard_submit")
      #   writing.click()
      #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      #   time.sleep(wait_time)
      #   # 書き込み成功画面の判定
      #   success = driver.find_elements(By.CLASS_NAME, value="ds_keijiban_finish")
      #   if len(success):
      #     print(f"{name}: {i + 1} の書き込みに成功しました")
      #     # マイページをクリック
      #     nav_list = driver.find_element(By.ID, value='ds_nav')
      #     mypage = nav_list.find_element(By.LINK_TEXT, "マイページ")
      #     mypage.click()
      #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      #     time.sleep(wait_time)
      #     # マイリストをクリック
      #     common_list = driver.find_element(By.CLASS_NAME, "ds_common_table")
      #     common_table = common_list.find_elements(By.CLASS_NAME, "ds_mypage_text")
      #     mylist = common_table[4]
      #     driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", mylist)
      #     time.sleep(wait_time)
      #     mylist.click()
      #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      #     time.sleep(wait_time)
      #     # 掲示板履歴をクリック
      #     menu_list = driver.find_element(By.CLASS_NAME, "ds_menu_link_list")
      #     menu_link = menu_list.find_elements(By.CLASS_NAME, "ds_next_arrow")
      #     bulletin_board_history = menu_link[5]
      #     bulletin_board_history.click()
      #   else:
      #     print(str(i +1) + "の書き込みに失敗しました")
      #     driver.get("https://happymail.co.jp/sp/app/html/mbmenu.php")
          
    
      
    # 掲示板重複を削除する
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    area_texts = driver.find_elements(By.CLASS_NAME, value="ds_write_bbs_status")
    area_texts_list = []
    for area in area_texts:
      area = area.text.replace(" ", "").replace("\n", "")
      area_texts_list.append(area)
    area_cnt = 0
    list = []
    for area_text in area_texts_list:
      for area in area_list:
        if area in area_text:
          # print(area)
          if area not in list:
              list.append(area)
              area_cnt += 1
          else:
              # print("重複があった")
              # print(area_cnt)
              if area_cnt >= 4:
                  continue
              duplication_area = driver.find_elements(By.CLASS_NAME, value="ds_round_btn_red")[area_cnt]
              driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", duplication_area)
              time.sleep(2)
              duplication_area.click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(wait_time)
              delete = driver.find_element(By.CLASS_NAME, "modal-confirm")
              delete.click()
              time.sleep(2)
    # 再掲載をクリック
    # for repost_cnt in range(4):
    repost_cnt = 0
    not_be_repost_areas = []
    blue_round_buttons = driver.find_elements(By.CLASS_NAME, "ds_round_btn_blue2")
    if not len(blue_round_buttons):
      print(f"{name}掲示板投稿から２時間経過していない可能性があります")
    while len(blue_round_buttons):
      blue_round_button = blue_round_buttons[0]
      # 再掲載できなかった場合はスキップ
      js_parent_script = "return arguments[0].parentNode;"
      parent_blue_round_button = driver.execute_script(js_parent_script, blue_round_button)
      # area_text = driver.find_elements(By.CLASS_NAME, value="ds_write_bbs_status")
      area_text = parent_blue_round_button.text.replace(" ", "").replace("\n", "")
      skip_flug = False
      this_area = ""
      for area in area_list:
        if area in area_text:
          # print("今回のエリア")
          this_area = area
          # print(area)
          if area in not_be_repost_areas:
            # print("リポストできなかったのでスキップ")
            # print(area)
            skip_flug = True
      if skip_flug:
          break   
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", blue_round_button)
      time.sleep(wait_time)
      driver.execute_script('arguments[0].click();', blue_round_button)
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
      # 再掲載する
      re_posting = driver.find_element(By.CLASS_NAME, "modal-confirm")
      re_posting.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
      if this_area:
        print(str(this_area) + "の再投稿に成功しました")
        repost_flug_list.append(str(this_area) + "◯")
      # id=modalの要素が出たら失敗 class=remodal-wrapperが4つともdiplay:noneなら成功
      warning = driver.find_elements(By.CLASS_NAME, value="remodal-wrapper ")
      if len(warning):
          display_property = driver.execute_script("return window.getComputedStyle(arguments[0]).getPropertyValue('display');", warning[0])
          if display_property == 'block':
            # ２時間経ってない場合は終了
            modal_text = warning[0].find_element(By.CLASS_NAME, value="modal-content")
            if modal_text.text == "掲載から2時間以上経過していない為、再掲載できません":
                print("掲載から2時間以上経過していない為、再掲載できません")
                cancel = driver.find_element(By.CLASS_NAME, value="modal-cancel")
                cancel.click()
                driver.get("https://happymail.co.jp/sp/app/html/mbmenu.php")
                break
            # リモーダルウィンドウを閉じる
            print("再投稿に失敗したので新規書き込みします")
            cancel = driver.find_element(By.CLASS_NAME, value="modal-cancel")
            cancel.click()
            time.sleep(wait_time)
            # 都道府県を取得
            js_parent_script = "return arguments[0].parentNode;"
            parent_blue_round_button = driver.execute_script(js_parent_script, blue_round_button)
            # area_text = driver.find_elements(By.CLASS_NAME, value="ds_write_bbs_status")
            area_text = parent_blue_round_button.text.replace(" ", "").replace("\n", "")
            for area in area_list:
              if area in area_text:
                #  掲示板をクリック
                nav_list = driver.find_element(By.ID, value='ds_nav')
                bulletin_board = nav_list.find_element(By.LINK_TEXT, "募集")
                bulletin_board.click()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(wait_time)
                catch_warning_screen(driver)
                # 書き込みをクリック
                write = driver.find_element(By.CLASS_NAME, value="icon-kakikomi_float")
                # write = driver.find_element(By.CLASS_NAME, value="icon-header_kakikomi")
                write.click()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(wait_time)
                # 書き込み上限に達したらスキップ
                adult = driver.find_elements(By.CLASS_NAME, value="remodal-wrapper")
                print(len(adult))
                if len(adult):
                    print("24時間以内の掲示板書き込み回数の上限に達しています(1日5件まで)")
                    cancel = driver.find_element(By.CLASS_NAME, value="modal-cancel")
                    cancel.click()
                    driver.get("https://happymail.co.jp/sp/app/html/mbmenu.php")
                    continue
                # その他掲示板をクリック
                link_tab = driver.find_elements(By.CLASS_NAME, "ds_link_tab_text")
                others_bulletin_board = link_tab[1]
                others_bulletin_board.click()
                time.sleep(2)
                # タイトルを書き込む
                input_title = driver.find_element(By.NAME, value="Subj")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", input_title)
                script = "arguments[0].value = arguments[1];"
                driver.execute_script(script, input_title, title)
                # input_title.send_keys(title)
                time.sleep(1)
                # 本文を書き込む
                text_field = driver.find_element(By.ID, value="text-message")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_field)
                script = "arguments[0].value = arguments[1];"
                driver.execute_script(script, text_field, post_text)
                # text_field.send_keys(post_text)
                time.sleep(1)
                # 書き込みエリアを選択
                select_area = driver.find_element(By.NAME, value="wrtarea")
                select = Select(select_area)
                select.select_by_visible_text(area)
                time.sleep(1)
                mail_rep =driver.find_element(By.NAME, value="Rep")
                select = Select(mail_rep)
                select.select_by_visible_text("10件")
                time.sleep(1)
                # 書き込む
                writing = driver.find_element(By.ID, value="billboard_submit")
                writing.click()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(wait_time)
                # 書き込み成功画面の判定
                success = driver.find_elements(By.CLASS_NAME, value="ds_keijiban_finish")
                if len(success):
                  # print(str(area) + "の再投稿に成功しました")
                  repost_flug_list.append(str(area) + ":◯")
                  # マイページをクリック
                  nav_list = driver.find_element(By.ID, value='ds_nav')
                  mypage = nav_list.find_element(By.LINK_TEXT, "マイページ")
                  mypage.click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(wait_time)
                  # マイリストをクリック
                  common_list = driver.find_element(By.CLASS_NAME, "ds_common_table")
                  common_table = common_list.find_elements(By.CLASS_NAME, "ds_mypage_text")
                  for common_table_elem in common_table:
                    if common_table_elem.text == "マイリスト":  
                      mylist = common_table_elem
                  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", mylist)
                  time.sleep(wait_time)
                  mylist.click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(wait_time)
                  # 掲示板履歴をクリック
                  menu_list = driver.find_element(By.CLASS_NAME, "ds_menu_link_list")
                  menu_link = menu_list.find_elements(By.CLASS_NAME, "ds_next_arrow")
                  bulletin_board_history = menu_link[5]
                  bulletin_board_history.click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(wait_time)
                else:
                  print(str(area) + "の再投稿に失敗しました")
                  repost_flug_list.append(str(area) + "：×")
                  not_be_repost_areas.append(str(area))
                  driver.get("https://happymail.co.jp/sp/app/html/mbmenu.php")
                  # マイページをクリック
                  nav_list = driver.find_element(By.ID, value='ds_nav')
                  mypage = nav_list.find_element(By.LINK_TEXT, "マイページ")
                  mypage.click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(wait_time)
                  # マイリストをクリック
                  common_list = driver.find_element(By.CLASS_NAME, "ds_common_table")
                  common_table = common_list.find_elements(By.CLASS_NAME, "ds_mypage_text")
                  mylist = common_table[4]
                  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", mylist)
                  time.sleep(wait_time)
                  mylist.click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(wait_time)
                  # 掲示板履歴をクリック
                  menu_list = driver.find_element(By.CLASS_NAME, "ds_menu_link_list")
                  menu_link = menu_list.find_elements(By.CLASS_NAME, "ds_next_arrow")
                  bulletin_board_history = menu_link[4]
                  bulletin_board_history.click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(wait_time)
                  
                  
      blue_round_buttons = driver.find_elements(By.CLASS_NAME, "ds_round_btn_blue2")
      # print(f"「{name}」ハッピーメールの掲示板書き込みに成功しました")
      repost_cnt += 1
      if repost_cnt == 4:
          break
    if repost_flug_list == False:
      repost_flug_list = "0件"
    return repost_flug_list
  except WebDriverException as e:
    error_message = str(e)
    if "unexpectedly exited. Status code was: -9" in error_message:
        print("in repost")
        print("Chromedriverが予期せず終了しました。再起動して起動してください。")
        driver.quit()

def return_matching(name, wait, wait_time, driver, user_name_list, duplication_user, fst_message, return_foot_img, matching_cnt,  matching_daily_limit, oneday_total_match, send_cnt):
  return_matching_counted = 0
  mail_icon_cnt = 0
  user_icon = 0
  limit_flug = False
  send_user_list = []
  # #  タイプをクリック
  # nav_flug = nav_item_click("タイプ", driver, wait)
  # if not nav_flug:
  #   return
  # 「マッチング」をクリック
  catch_warning_screen(driver)
  from_myself = driver.find_elements(By.CLASS_NAME, value="ds_common_tab_item")[2]
  from_myself.click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(0.4)
  while return_matching_counted < matching_cnt:
    active = driver.find_element(By.CLASS_NAME, value="active")
    send_status = True
    matching_users = active.find_elements(By.CLASS_NAME, value="type_list_outer")
    matching_users_wait_cnt = 0
    while len(matching_users) == 0:
      time.sleep(0.5)
      matching_users = active.find_elements(By.CLASS_NAME, value="type_list_outer")
      matching_users_wait_cnt += 1
      if matching_users_wait_cnt == 3:
        return return_matching_counted, limit_flug, send_user_list
    name_field = matching_users[user_icon].find_element(By.CLASS_NAME, value="ds_like_list_name")
    user_name = name_field.text
    mail_icon = name_field.find_elements(By.TAG_NAME, value="img")   
    
    while len(mail_icon):
      # print(f'送信履歴あり {user_name}　~ skip ~')
      mail_icon_cnt += 1
      user_icon += 1
      # # メールアイコンが20つ続いたら終了
      if mail_icon_cnt == 18:
        ds_logo = driver.find_element(By.CLASS_NAME, value="ds_logo")
        top_link = ds_logo.find_element(By.TAG_NAME, value="a")
        top_link.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(0.5)
        # print("マッチングリストで送信履歴のあるユーザーが20回続きました")
        # print(len(matching_users))
        return return_matching_counted, limit_flug
      if 0 <= user_icon < len(matching_users):
        name_field = matching_users[user_icon].find_element(By.CLASS_NAME, value="ds_like_list_name")
      else:
        # print(len(matching_users))
        # print(user_icon)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        matching_users = active.find_elements(By.CLASS_NAME, value="type_list_outer")
        if user_icon <= len(matching_users):
          driver.get("https://happymail.co.jp/sp/app/html/type_list.php")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(wait_time)
          catch_warning_screen(driver)
          return return_matching_counted, limit_flug, send_user_list
        name_field = matching_users[user_icon].find_element(By.CLASS_NAME, value="ds_like_list_name")
      user_name = name_field.text
      mail_icon = name_field.find_elements(By.TAG_NAME, value="img")
    # ユーザー重複チェック
    if len(user_name_list):
      while user_name in user_name_list:
        # print(f'重複ユーザー {user_name}　~ skip ~')
        user_icon = user_icon + 1
        if len(matching_users) <= user_icon:
            duplication_user = True
            return return_matching_counted, limit_flug, send_user_list
        name_field = matching_users[user_icon].find_element(By.CLASS_NAME, value="ds_like_list_name")
        user_name = name_field.text
    # マッチングユーザーをクリック
    message_button = matching_users[user_icon].find_element(By.CLASS_NAME, value="message_button")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", message_button)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(0.5)
    driver.execute_script('arguments[0].click();', message_button)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(0.5)
    catch_warning_screen(driver)
    prof_text = driver.find_elements(By.CLASS_NAME, value="ds_common_text")
    # prof_text = driver.find_elements(By.ID, value="first_m_profile_introduce")
    if len(prof_text):
      if prof_text[0].text == "プロフィール情報の取得に失敗しました":
          user_icon += 1
      # 自己紹介文に業者、通報が含まれているかチェック
      else:
        contains_violations = prof_text[0]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", contains_violations)
        self_introduction_text = contains_violations.text.replace(" ", "").replace("\n", "")
        ngword_list = ["通報", "業者", "金銭", "条件"]
        if any(ngword in self_introduction_text for ngword in ngword_list):
          # print(f'自己紹介文に危険なワードが含まれていました {user_name}')
          # icon_other_div = driver.find_element(By.ID, value="btn-other")
          # other_icon = icon_other_div.find_element(By.TAG_NAME, value="img")
          # driver.execute_script("arguments[0].click();", other_icon)
          # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          # time.sleep(1)
          # driver.find_elements(By.CLASS_NAME, value="footer_menu-list-item")[3].click()
          # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          # time.sleep(1)
          # regist_mushi = driver.find_element(By.CLASS_NAME, value="input__form__action__button__pink")
          # driver.execute_script("arguments[0].click();", regist_mushi)
          # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          # time.sleep(1)
          # user_name_list.append(user_name)
          # send_status = False

          print(f'自己紹介文に危険なワードが含まれていました {user_name}')
          send_status = False
          user_icon += 1
          plus_icon = driver.find_element(By.CLASS_NAME, value="icon-message_plus")
          plus_icon.click()
          time.sleep(0.6)
          # 無視登録
          other_icon = driver.find_elements(By.CLASS_NAME, value="ds_message_txt_media_item")[4].find_element(By.TAG_NAME, value="a")
          other_icon.click()
          time.sleep(0.5)
          submit = driver.find_element(By.CLASS_NAME, value="input__form__action__button__pink")
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", submit)
          driver.execute_script("arguments[0].click();", submit)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(0.5)
        
    # メールするをクリック
    if send_status and fst_message:
      fst_message = fst_message.format(name=user_name)
      catch_warning_screen(driver)
      text_area = driver.find_element(By.ID, value="text-message")
      script = "arguments[0].value = arguments[1];"
      driver.execute_script(script, text_area, fst_message)
      time.sleep(0.5)
      driver.execute_script("arguments[0].click();", text_area)
      time.sleep(0.5)
      text_area.send_keys("\n")
      time.sleep(0.5)
      # 送信
      send_mail = driver.find_element(By.ID, value="submitButton")
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", send_mail)
      send_mail.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
      # 画像があれば送信 
      try:
        if return_foot_img:
          img_conform = driver.find_element(By.ID, value="media-confirm")
          plus_icon = driver.find_elements(By.ID, value="ds_js_media_display_btn")
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", plus_icon[0])
          time.sleep(1)
          driver.execute_script("arguments[0].click();", plus_icon[0])
          time.sleep(1)
          upload_file = driver.find_element(By.ID, "upload_file")
          upload_file.send_keys(return_foot_img)
          time.sleep(2)
          submit = driver.find_element(By.ID, value="submit_button")
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", submit)
          driver.execute_script("arguments[0].click();", submit)
          while img_conform.is_displayed():
            time.sleep(2)
            modal_content = driver.find_elements(By.CLASS_NAME, value="modal-content")
            if len(modal_content):
              break # modal-content お相手が年齢確認されていない為
      except Exception as e:
            print("画像の送信に失敗しました", e)
            print(traceback.format_exc())
      mail_icon_cnt = 0
      user_icon = 0
      return_matching_counted += 1
      now = datetime.now().strftime('%m-%d %H:%M:%S')
      send_user_list.append(f"{user_name} :{now}")
      print(f'{name}:マッチング返し {user_name} ~ {str(return_matching_counted)} ~ {now}')
      if send_cnt == return_matching_counted:
        return return_matching_counted, limit_flug, send_user_list
      if matching_daily_limit == return_matching_counted + oneday_total_match:
        print("マッチング上限に達しました")
        limit_flug = True
        return return_matching_counted, limit_flug, send_user_list
      driver.get("https://happymail.co.jp/sp/app/html/type_list.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
    else:
      user_name_list.append(user_name) 
      driver.get("https://happymail.co.jp/sp/app/html/type_list.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
    catch_warning_screen(driver)
  user_icon = 0
  return return_matching_counted, limit_flug, send_user_list

def return_type(name, wait, wait_time, driver, user_name_list, duplication_user, fst_message, return_foot_img, type_cnt):
  return_type_counted = 0
  mail_icon_cnt = 0
  user_icon_type = 0
  #  タイプをクリック
  nav_flug = nav_item_click("タイプ", driver, wait)
  # if not nav_flug:
  #   return
  # 「相手から」をクリック
  from_other = driver.find_elements(By.CLASS_NAME, value="ds_common_tab_item")[0]
  from_other.click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(0.5)
  under_scroll_count = 0
  while return_type_counted < type_cnt:
    type_list = driver.find_element(By.ID , value="list_myself")
    type_users = type_list.find_elements(By.CLASS_NAME, value="ds_user_post_link_item_r")
    type_users_wait_cnt = 0
    
    if len(type_users) <= user_icon_type: 
      # print("ページの最後までスクロール")
      driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      under_scroll_count += 1
      type_list = driver.find_element(By.ID , value="list_myself")
      type_users = type_list.find_elements(By.CLASS_NAME, value="type_list_outer")
      # print('---------')
      # print(len(type_users))
      # print(user_icon_type)
      # print('---------')
      if under_scroll_count > 7:
        print(999)
        break
    while len(type_users) == 0:
      time.sleep(2)
      type_users = driver.find_elements(By.CLASS_NAME, value="ds_user_post_link_item_r")
      type_users_wait_cnt += 1
      if type_users_wait_cnt == 3:
          return return_type_counted
    if len(type_users) <= user_icon_type:
      print("ユーザーアイコンの範囲を超えました1111")
      print(f"{len(type_users)}  {user_icon_type} ")
      duplication_user = True
      break
    name_field = type_users[user_icon_type].find_element(By.CLASS_NAME, value="ds_like_list_name")
    user_name = name_field.text
    mail_icon = name_field.find_elements(By.TAG_NAME, value="img")
    while len(mail_icon):
      # print(f'送信履歴あり {user_name} ~ skip ~ {mail_icon_cnt} {len(type_users)} ::{user_icon_type}')
      mail_icon_cnt += 1
      user_icon_type += 1
      # # メールアイコンが5つ続いたら終了
      if mail_icon_cnt == 20: 
        print("タイプリストで送信履歴のあるユーザーが20回続きました")
        return return_type_counted
      
      name_field = type_users[user_icon_type].find_element(By.CLASS_NAME, value="ds_like_list_name")
      user_name = name_field.text
      mail_icon = name_field.find_elements(By.TAG_NAME, value="img")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(0.2)
      name_field = type_users[user_icon_type].find_element(By.CLASS_NAME, value="ds_like_list_name")
      user_name = name_field.text
      mail_icon = name_field.find_elements(By.TAG_NAME, value="img")
      if user_icon_type % 8 == 0:
        # ページの最後までスクロール
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(0.5)
        type_users = type_list.find_elements(By.CLASS_NAME, value="ds_user_post_link_item_r")
        # print(len(type_users))
      if user_name == "ユーザーネーム取得に失敗しました":
        print("ユーザーネーム取得に失敗しました")
        break  
    # ユーザー重複チェック
    if len(user_name_list):
      while user_name in user_name_list:
        # print('重複ユーザー')
        user_icon_type = user_icon_type + 1
        if len(type_users) <= user_icon_type:
            duplication_user = True
            break
        name_field = type_users[user_icon_type].find_element(By.CLASS_NAME, value="ds_like_list_name")
        user_name = name_field.text
    # 年齢チェック
    user_age = type_users[user_icon_type].find_element(By.CLASS_NAME, value="ds_like_list_age")
    # print(f"年齢チェック {user_age.text} {user_name}")
    if not re.search(r"20代|18.?19", user_age.text):
      # print("年齢が１０〜２０代ではないユーザー　スキップします") 
      # print(len(type_users), user_icon_type)
      user_icon_type += 1
      continue
    # タイプユーザーをクリック
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", type_users[user_icon_type])
    if duplication_user:
      print(1234)
      name_field = type_users[user_icon_type+1].find_element(By.CLASS_NAME, value="ds_like_list_name")
      user_name = name_field.text
      user_name_list.append(user_name) 
      type_button = type_users[user_icon_type+1].find_elements(By.CLASS_NAME, value="type_button")
      type_button[0].click()
    else:
      print(f"タイプ返しユーザー: {user_name}")
      type_button = type_users[user_icon_type].find_elements(By.CLASS_NAME, value="type_button")
      type_button[0].click()
    return_type_counted += 1
    print(f"タイプ返し　~{user_name}~ {return_type_counted}件")
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(0.6)
    type_confirm = driver.find_elements(By.CLASS_NAME, value="modal-confirm")
    type_confirm_wait_cnt = 0
    while len(type_confirm) == 0:
      type_confirm_wait_cnt += 1
      time.sleep(1)
      type_confirm = driver.find_elements(By.CLASS_NAME, value="modal-confirm")
      if type_confirm_wait_cnt == 2:
        break
    if not len(type_confirm):   
      return 
    type_confirm[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(0.5)
    driver.get("https://happymail.co.jp/sp/app/html/type_list.php")
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(0.6)
    
  return return_type_counted
      
def return_footpoint(name, driver, wait, return_foot_message, matching_cnt, type_cnt, return_foot_cnt, return_foot_img, fst_message, matching_daily_limit, daily_limit, oneday_total_match, oneday_total_returnfoot, send_cnt):
  wait_time = random.uniform(1.5, 3.5)
  warning_pop = catch_warning_screen(driver)
  return_cnt = 0
  mail_icon_cnt = 0
  duplication_user = False
  user_name_list = []
  user_icon = 0
  send_users = []
  catch_warning_screen(driver)
  if return_foot_img:
    # 画像データを取得してBase64にエンコード
    image_response = requests.get(return_foot_img)
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
  # タイプ返し
  type_counted = 0
  try:
    type_counted = return_type(name, wait, wait_time, driver, user_name_list, duplication_user, fst_message, image_path, type_cnt)
    print(f"タイプ返し総数 {type_counted}")
  except Exception as e:  
    print("タイプ返しエラー")
    print(traceback.format_exc())
  # マッチング返し
  if matching_daily_limit >= oneday_total_match:
    matching_counted = 0
    matching_limit_flug = True
    try:
      print(f"マッチングリストチェック...")
      matching_counted, matching_limit_flug, send_users= return_matching(name, wait, wait_time, driver, user_name_list, duplication_user, fst_message, image_path, matching_cnt, matching_daily_limit, oneday_total_match, send_cnt)     
    except Exception as e:   
      print("マッチング返しエラー")
      print(traceback.format_exc())
      driver.get("https://happymail.co.jp/sp/app/html/mbmenu.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
    finally:
      driver.get("https://happymail.co.jp/sp/app/html/mbmenu.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
  if send_cnt == matching_counted:
    return matching_counted
  returnfoot_limit_flug = True
  if daily_limit  >= oneday_total_returnfoot:
    returnfoot_limit_flug = False
    # 足跡返し
    print(f"足跡返し開始...")
    try:
      warning_pop = catch_warning_screen(driver)
      if warning_pop:
        print(f"{name}：警告画面が出ている可能性があります")
        print(warning_pop)
        return
      # マイページをクリック
      nav_list = driver.find_elements(By.ID, value='ds_nav')
      if not len(nav_list):
        print(f"{name}: 警告画面が出ている可能性があります。")
        return
      mypage = nav_list[0].find_element(By.LINK_TEXT, "マイページ")
      mypage.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
      # 足あとをクリック
      return_footpoint = driver.find_element(By.CLASS_NAME, value="icon-ico_footprint")
      driver.execute_script("arguments[0].click();", return_footpoint)
      # return_footpoint.click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(3)
      catch_warning_screen(driver)
      while return_foot_cnt >= return_cnt + 1:
        # print("足跡返しループ")
        send_status = True
        f_user = driver.find_elements(By.CLASS_NAME, value="ds_post_head_main_info")          
        # ページが完全に読み込まれるまで待機
        while len(f_user) < 1:
          print("足跡ユーザーが見つかりませんでした,# ページをリフレッシュして再度取得")
          driver.refresh()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)        
        name_field = f_user[user_icon].find_element(By.CLASS_NAME, value="ds_like_list_name")
        user_name = name_field.text
        mail_icon = name_field.find_elements(By.TAG_NAME, value="img")
        send_skip_cnt = 0
        while len(mail_icon) or user_name in user_name_list:
          if len(mail_icon):
            # print("***")
            # print(send_skip_cnt)
            user_icon += 1
            # print(f'送信履歴あり {user_name} ~ skip ~')
            send_skip_cnt += 1
            if len(f_user) <= user_icon:
              # ページの最後までスクロール
              driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(0.7)
              f_user = driver.find_elements(By.CLASS_NAME, value="ds_post_head_main_info")
              # print(len(f_user))
            name_field = f_user[user_icon].find_element(By.CLASS_NAME, value="ds_like_list_name")
            user_name = name_field.text
            mail_icon = name_field.find_elements(By.TAG_NAME, value="img")
            
            if send_skip_cnt > 50:
              # print("送れないユーザーが50回続きました")
              return return_cnt
          elif len(user_name_list):
            while user_name in user_name_list:
                # print('重複ユーザー')
                # print("~~~")
                # print(send_skip_cnt)
                send_skip_cnt += 1
                user_icon = user_icon + 1
                if len(f_user) <= user_icon:
                  duplication_user = True
                  break
                name_field = f_user[user_icon].find_element(By.CLASS_NAME, value="ds_like_list_name")
                user_name = name_field.text
                if send_skip_cnt > 19:
                  print("送れないユーザーが20回続きました")
                  return return_cnt
        # 足跡ユーザーをクリック
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", f_user[user_icon])
        time.sleep(0.1)
        # 年齢チェック

        age_elm = f_user[user_icon].find_elements(By.CLASS_NAME, value="ds_like_list_age")
        if "20代" not in age_elm[0].text and "18~19" not in age_elm[0].text:
          # print("年齢が１０〜２０代ではないユーザーです")
          # print(len(f_user))
          user_icon += 1
          if len(f_user) <= user_icon:
            # ページの最後までスクロール
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(0.7)
            f_user = driver.find_elements(By.CLASS_NAME, value="ds_post_head_main_info")
            print(888)
            break
          elif user_icon > 50:
            print("送信条件に当てはまらない足跡リストユーザーが50人を超えました")
            break
          else:
            continue
        if duplication_user:
          name_field = f_user[user_icon+1].find_element(By.CLASS_NAME, value="ds_like_list_name")
          user_name = name_field.text
          user_name_list.append(user_name) 
          f_user[user_icon+1].click()
        else:
          f_user[user_icon].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(wait_time)
        catch_warning_screen(driver)
        m = driver.find_elements(By.XPATH, value="//*[@id='ds_main']/div/p")
        if len(m):
          print(m[0].text)
          if m[0].text == "プロフィール情報の取得に失敗しました":
              user_icon += 1
              continue
        # 自己紹介文に業者、通報が含まれているかチェック
        if len(driver.find_elements(By.CLASS_NAME, value="translate_body")):
          contains_violations = driver.find_element(By.CLASS_NAME, value="translate_body")
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", contains_violations)
          self_introduction_text = contains_violations.text.replace(" ", "").replace("\n", "")
          ngword_list = ["通報", "業者", "金銭", "条件"]
          if any(ngword in self_introduction_text for ngword in ngword_list):
            print(f'自己紹介文に危険なワードが含まれていました {user_name}')
            icon_other_div = driver.find_element(By.ID, value="btn-other")
            other_icon = icon_other_div.find_element(By.TAG_NAME, value="img")
            driver.execute_script("arguments[0].click();", other_icon)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(1)
            driver.find_elements(By.CLASS_NAME, value="footer_menu-list-item")[3].click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(1)
            regist_mushi = driver.find_element(By.CLASS_NAME, value="input__form__action__button__pink")
            driver.execute_script("arguments[0].click();", regist_mushi)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(1)
            user_name_list.append(user_name)
            send_status = False
        # メッセージ履歴があるかチェック
        if send_status:
          mail_field = driver.find_element(By.ID, value="ds_nav")
          mail_history = mail_field.find_elements(By.ID, value="mail-history")
          if len(mail_history):
            display_value = mail_history[0].value_of_css_property("display")
            if display_value != "none":
              # print('メール履歴があります')
              # print(user_name)
              user_name_list.append(user_name) 
              send_status = False
              mail_icon_cnt += 1
        # メールするをクリック
        if send_status:
          send_mail = driver.find_element(By.ID, value="btn-mail")
          send_mail = send_mail.find_element(By.CLASS_NAME, value="icon-float_message")
          send_mail.click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(wait_time)
          # 足跡返しを入力
          
          catch_warning_screen(driver)
          text_area = driver.find_element(By.ID, value="text-message")
          script = "arguments[0].value = arguments[1];"
          return_foot_message = return_foot_message.format(name=user_name)
          driver.execute_script(script, text_area, return_foot_message)
          time.sleep(0.5)
          driver.execute_script("arguments[0].click();", text_area)
          time.sleep(0.5)
          text_area.send_keys("\n")
          time.sleep(0.5)
          
          # 送信
          send_mail = driver.find_element(By.ID, value="submitButton")
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", send_mail)
          send_mail.click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(wait_time)
          send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
          reload_cnt = 0
          most_recent_msg = send_msg_elem[-1]  
          script = """
            var element = arguments[0];

            // 除外するクラスを持つ子要素を取得
            var elementsToRemove = element.querySelectorAll('.transit_info, .message__block__body__time');

            // 一時的に削除
            elementsToRemove.forEach(el => el.remove());

            // 要素Aのテキストを取得
            var textContent = element.textContent.trim();

            // 削除した子要素を元に戻す
            elementsToRemove.forEach(el => element.appendChild(el));

            return textContent;
            """
          most_recent_msg = driver.execute_script(script, most_recent_msg) 
          most_recent_msg_clean = func.normalize_text(most_recent_msg)
          return_foot_message_clean = func.normalize_text(return_foot_message)
          while most_recent_msg_clean != return_foot_message_clean:
            # print(most_recent_msg)
            # print("~~~~~~~~~~~~~~~~~~~~")
            # print(return_foot_message)
            driver.refresh()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(wait_time)
            send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
            reload_cnt += 1
            if reload_cnt == 1:
              driver.refresh()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(wait_time)
              break
          # 画像があれば送信
          try:
            if image_path:
              img_conform = driver.find_element(By.ID, value="media-confirm")
              plus_icon = driver.find_elements(By.ID, value="ds_js_media_display_btn")
              driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", plus_icon[0])
              time.sleep(1)
              driver.execute_script("arguments[0].click();", plus_icon[0])         
              time.sleep(1)
              upload_file = driver.find_element(By.ID, "upload_file")
              # DEBUG
              # upload_file.send_keys("/Users/yamamotokenta/Desktop/myprojects/mail_operator/widget/picture/kumi_mizugi.jpeg")
              upload_file.send_keys(image_path)
              time.sleep(1.5)
              submit = driver.find_element(By.ID, value="submit_button")
              driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", submit)
              driver.execute_script("arguments[0].click();", submit)
              img_wait_cnt = 0
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(1.5)
              while img_conform.is_displayed():
                time.sleep(2)
                modal_content = driver.find_elements(By.CLASS_NAME, value="modal-content")
                if len(modal_content) and img_wait_cnt > 1:
                  break # modal-content お相手が年齢確認されていない為
                img_wait_cnt += 1
          except Exception as e:
            print("画像の送信に失敗しました", e)
            print(traceback.format_exc())
          return_cnt += 1
          mail_icon_cnt = 0
          user_icon = 0
          now = datetime.now().strftime('%m-%d %H:%M:%S')
          print(f'{name}:足跡返し  ~ {str(return_cnt)} ~ {user_name} {now}')  
          if send_cnt == return_cnt + matching_counted:
            return [matching_counted, type_counted, return_cnt, matching_limit_flug, returnfoot_limit_flug]
          if daily_limit  <= oneday_total_returnfoot + return_cnt:
            print("足跡返し　送信上限に達しました")
            returnfoot_limit_flug = True
            return [matching_counted, type_counted, return_cnt, matching_limit_flug, returnfoot_limit_flug]
          driver.get("https://happymail.co.jp/sp/app/html/ashiato.php")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1.5)
        else:
          user_name_list.append(user_name)       
          driver.get("https://happymail.co.jp/sp/app/html/ashiato.php")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1.5)
          # TOPに戻る
          ds_logo = driver.find_element(By.CLASS_NAME, value="ds_logo")
          top_link = ds_logo.find_element(By.TAG_NAME, value="a")
          driver.execute_script("arguments[0].click();", top_link)
          # top_link.click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(wait_time)

      # ファイルが存在しているか確認し、削除
      if image_filename:
        if os.path.exists(image_filename):
            os.remove(image_filename)
      if return_cnt == None:
        return_cnt = 0
    except WebDriverException as e:
      print("in return_footpoint")
      error_message = str(e)
      print(error_message)
      if "unexpectedly exited. Status code was: -9" in error_message:
          print("Chromedriverが予期せず終了しました。再起動して起動してください。")
          driver.quit()

    finally: 
      
      # ファイルが存在しているか確認し、削除
      if image_filename:
        if os.path.exists(image_filename):
            os.remove(image_filename)
      if return_cnt == None:
        return_cnt = 0
      
      return [matching_counted, type_counted, return_cnt, matching_limit_flug, returnfoot_limit_flug]
  

  return [matching_counted, type_counted, return_cnt, matching_limit_flug, returnfoot_limit_flug, send_users]
def set_mutidriver_make_footprints(driver,wait):
  # 並びの表示を設定
  # sort_order = driver.find_elements(By.ID, value="kind_select")
  # select = Select(sort_order[0])
  # select.select_by_visible_text("プロフ一覧")
  # wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # time.sleep(1)
  # user_list = driver.find_elements(By.CLASS_NAME, value="ds_user_post_link_item_r")

  user_list = driver.find_elements(By.CLASS_NAME, value="profile_list_big_item")
  reload_cnt = 0
  while not len(user_list):
    time.sleep(4)
    reload_cnt += 1
    driver.refresh()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    if reload_cnt == 2:
      break
    user_list = driver.find_elements(By.CLASS_NAME, value="ds_user_post_link_item_r")
  if not len(user_list):
    print(f"足跡リストにユーザーがいません")
    return
  user_link = user_list[0].find_elements(By.TAG_NAME, value="a")
  driver.execute_script("arguments[0].click();", user_link[0])
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1.5)
  
def mutidriver_make_footprints(name,login_id, password, driver,wait, mf_cnt, type_cnt):
  if driver.current_url != "https://happymail.co.jp/sp/app/html/mbmenu.php":
    driver.get("https://happymail.co.jp/sp/app/html/mbmenu.php")
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(0.5)
  wait_time = random.uniform(0.25, 0.75)
  warning = catch_warning_screen(driver)
  bottom_scroll_cnt = 0
  if warning:
    print(f"{name} :{warning}")
  # print("足跡付け前のurl確認")
  # print(driver.current_url)
  mail_icon_cnt = 0
  user_icon = 0
  # num = random.randint(8)
  nav_flug = nav_item_click("プロフ検索", driver, wait)
  # if not nav_flug:
  #   print(f"{name} :プロフ検索に移動できません")
    # print(driver.current_url)
    # print(f"{name} {login_id} {password}  でログインします")
    # login_flug = login(name, login_id, password, driver, wait,)
    # if login_flug:
    #   print(f"{name} ::{login_flug}") 
    # warning = catch_warning_screen(driver)
    # if warning:
    #   print(f"{name} :::{warning}")
    #   return
    # print(f"{name}のログインに成功しました")
    # print(driver.current_url)
    # nav_flug = nav_item_click("プロフ検索", driver, wait)
    # return
  print(f"{mf_cnt}件足あと {type_cnt}件タイプ付けします")
  for i in range(mf_cnt):
    catch_warning_screen(driver)
    # 並びの表示を設定
    active_tab = driver.find_elements(By.CLASS_NAME, value="active")
    if not len(active_tab):
      print("アクティブなタブが見つかりません")
      print(driver.current_url)
      time.sleep(2)
      driver.refresh()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
      active_tab = driver.find_elements(By.CLASS_NAME, value="active")
      
    children = active_tab[0].find_elements(By.XPATH, "./*")
    all_have_class = all("ds_user_post_link_item_r" in child.get_attribute("class") for child in children)
    if not all_have_class:
      sort_order = driver.find_elements(By.ID, value="kind_select")
      if len(sort_order):
        select = Select(sort_order[0])
        select.select_by_visible_text("プロフ一覧")
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    login_users_wait_cnt = 0
    login_users = driver.find_elements(By.CLASS_NAME, value="ds_user_post_link_item_r")
    while len(login_users) == 0:
      time.sleep(1)
      login_users = driver.find_elements(By.CLASS_NAME, value="ds_user_post_link_item_r")
      login_users_wait_cnt += 1
      if login_users_wait_cnt == 3:
        return
    name_field = login_users[user_icon].find_element(By.CLASS_NAME, value="ds_post_body_name_small")
    user_name = name_field.text
    mail_icon = name_field.find_elements(By.TAG_NAME, value="img")
    while len(mail_icon):
      # print(f'送信履歴あり {user_name}　~ skip ~')
      mail_icon_cnt += 1
      user_icon += 1
      # # メールアイコンが5つ続いたら終了
      if mail_icon_cnt == 5:
        ds_logo = driver.find_element(By.CLASS_NAME, value="ds_logo")
        top_link = ds_logo.find_element(By.TAG_NAME, value="a")
        top_link.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(wait_time)
        print("送信履歴のあるユーザーが5回続きました")
        return 
      name_field = login_users[user_icon].find_element(By.CLASS_NAME, value="ds_post_body_name_small")
      user_name = name_field.text
      mail_icon = name_field.find_elements(By.TAG_NAME, value="img")
    candidate_footprint = login_users[user_icon]
    while "ds_ribbon" in candidate_footprint.get_attribute("class"):
      # print(f"✅ {user_name} 確認済み")
      user_icon += 1
      while len(login_users) <= user_icon:
        # print("************************")
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(3)
        login_users = driver.find_elements(By.CLASS_NAME, value="ds_user_post_link_item_r")
        bottom_scroll_cnt += 1
        
      if bottom_scroll_cnt == 5:
        print("ユーザーが見つかりません")
        return
      
      candidate_footprint = login_users[user_icon]
      name_field = login_users[user_icon].find_element(By.CLASS_NAME, value="ds_post_body_name_small")
      user_name = name_field.text
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", candidate_footprint)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    catch_warning_screen(driver)
    candidate_footprint.find_element(By.TAG_NAME, "a").click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    catch_warning_screen(driver)
    type_flug = False
    if type_cnt > 0:
      type_button = driver.find_elements(By.ID, value="btn-type")
      type_loop_cnt = 0
      while not len(type_button):
        time.sleep(4)
        type_button = driver.find_elements(By.CLASS_NAME, value="btn-type")
        type_loop_cnt += 1
        if type_loop_cnt == 4:
          break
      if len(type_button):
        driver.execute_script("arguments[0].click();", type_button[0])
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(4)
        type_cnt -= 1
        type_flug = True
    now = datetime.now().strftime('%m-%d %H:%M:%S')
    if type_flug:
      print(f'{name}:足跡付け＋タイプ付け  {user_name}  {now}')
    else:
      print(f'{name}:足跡付け,  {user_name}  {now}')
    driver.find_element(By.CLASS_NAME, value="ds_link_back").click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)

    # if not "https://happymail.co.jp/sp/app/html/profile_detail_list.php?a=a&from=prof&idx=" in driver.current_url:
    #   driver.get("https://happymail.co.jp/sp/app/html/profile_detail_list.php?a=a&from=prof&idx=1")
    #   if "https://happymail.co.jp/sp/app/html/profile_list.php" in driver.current_url:
    #     set_mutidriver_make_footprints(driver,wait)    
    # # ユーザ名を取得
    # user_name = driver.find_elements(By.CLASS_NAME, value="ds_user_display_name")
    # if user_name:
    #   user_name = user_name[0].text
    # else:
    #   print(f"{name} {login_id} {password}  でログインします")
    #   login_flug = login(name, login_id, password, driver, wait,)
    #   if login_flug:
    #     print(f"{name} ::{login_flug}")
    #     break
    #   warning = catch_warning_screen(driver)
    #   if warning:
    #     print(f"{name} :::{warning}")
    #     break
    #   print(f"{name}のログインに成功しました")
    #   print(driver.current_url)
    #   nav_flug = nav_item_click("プロフ検索", driver, wait)
    #   if not nav_flug:
    #     break
    #   set_mutidriver_make_footprints(driver,wait)
    #   print("スクショします")
    #   filename = f'screenshot_{time.strftime("%Y%m%d_%H%M%S")}.png'
    #   driver.save_screenshot(filename)
    #   user_name = "取得に失敗しました"
    # # タイプ実装
    # like_age_list = [
    #   "18~19歳", "20代前半", "20代半ば", "20代後半",
    # ]
    # like_height_list = [
    #   "〜149", "150〜154", "155〜159", "160〜164","165〜169"
    #   "170～174", "160～164", "165~169",
    # ]
    # like_etc_list = [
    #   "実家暮らし", "100〜300万円", "かわいい系", 
    # ]
    # active_profiles = driver.find_elements(By.CLASS_NAME, value="swiper-slide-active")
    # if len(active_profiles):
    #   user_profiles = active_profiles[0].find_elements(By.CLASS_NAME, value="ds_profile_select_choice")
    #   age_like = False
    #   height_like = False
    #   etc_like = False
    #   type_flug = False
    #   type_age, type_height, etc_type = "", "", ""
    #   for i in user_profiles:
    #     text = i.text.strip()
    #     if text in like_age_list:
    #       # print("✅ 年齢一致しました！ →", text)
    #       type_age = text
    #       age_like = True
    #     if text in like_height_list:
    #       # print("✅ 身長一致しました！ →", text)
    #       type_height = text
    #       height_like = True
    #     if text in like_etc_list:
    #       # print("✅ その他一致しました！ →", text)
    #       etc_type = text
    #       etc_like = True
    #   if age_like:
    #     if height_like:
    #       if etc_like:
    #       # age_like,type_height,etc_typeがそれぞれFalseじゃなければprintで表示する
    #         print(f"✅ タイプ一致しました！{user_name} {type_age} {type_height} {etc_type}")
    #         type_flug = True
    #   if type_flug:
    #     type_button = driver.find_elements(By.ID, value="btn-type")
    #     type_loop_cnt = 0
    #     while not len(type_button):
    #       time.sleep(4)
    #       type_button = driver.find_elements(By.CLASS_NAME, value="btn-type")
    #       type_loop_cnt += 1
    #       if type_loop_cnt == 4:
    #         break
    #     if len(type_button):
    #       driver.execute_script("arguments[0].click();", type_button[0])
    #       wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    #       time.sleep(4)
    # mail_button = driver.find_elements(By.ID, value="btn-mail")
    # if not len(mail_button):
    #   print(f"{name}")
    #   print("メールをするボタンが見つかりません")
    #   current_url = driver.current_url
    #   # print(f"現在のURL: {current_url}")
    #   # print(driver.current_url)
    #   time.sleep(7)
    #   # ユーザ名を取得
    #   user_name = driver.find_elements(By.CLASS_NAME, value="ds_user_display_name")
    #   if user_name:
    #     user_name = user_name[0].text
    #   else:
    #     user_name = "取得に失敗しました"
    #   mail_button = driver.find_elements(By.CLASS_NAME, value="btn-mail")
    #   print(user_name)
    #   print(len(mail_button))
    #   time.sleep(1.5)
    # mail_button = mail_button[0].find_elements(By.TAG_NAME, value="a")
    # if len(mail_button):
    #   driver.execute_script("arguments[0].click();", mail_button[0])
    #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    #   time.sleep(1.5)
    #   driver.back()
    #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    #   time.sleep(1)
    #   now = datetime.now().strftime('%m-%d %H:%M:%S')
    #   print(f'{name}:足跡付け,  {user_name}  {now}')
    #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    #   time.sleep(wait_time)
    #   warning_pop = catch_warning_screen(driver)
    #   if warning_pop:
    #     print(f"{name}：警告画面が出ている可能性があります")
    #     print(warning_pop)
    #     break
    #   swiper_button = driver.find_elements(By.CLASS_NAME, value="swiper-button-next")
    #   if not len(swiper_button):
    #     break
    #   driver.execute_script("arguments[0].click();", swiper_button[0])
    #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    #   time.sleep(1)
    #   catch_warning_screen(driver)
  

def make_footprints(name, happymail_id, happymail_pass, driver, wait, foot_count):
  wait_time = random.uniform(2, 5)
  login(name, happymail_id, happymail_pass, driver, wait)
  warinig_flug = catch_warning_screen(driver)
  if warinig_flug:
    print(f"{name}:警告画面が出ている可能性があります")
    return
  # プロフ検索をクリック
  nav_flug = nav_item_click("プロフ検索", driver, wait)
  if not nav_flug:
    return
  # 並びの表示を設定
  sort_order = driver.find_elements(By.ID, value="kind_select")
  select = Select(sort_order[0])
  select.select_by_visible_text("プロフ一覧")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  foot_counted = 0
  for i in range(50):
    warinig_flug = catch_warning_screen(driver)
    if warinig_flug:
      print(f"{name}:警告画面が出ている可能性があります")
      return
    user_list = driver.find_elements(By.CLASS_NAME, value="ds_user_post_link_item_r")
    # print(f"ユーザーリストの数{len(user_list)}")
    if not len(user_list):
        print("ユーザーリストの取得に失敗しました")
        break
    mail_icon_flag = True
    mail_icon_try_cnt = 0
    while mail_icon_flag:
      # インデックスがリストの範囲外でないか確認
      if i >= len(user_list):
        break        
      user = user_list[i]
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", user)
      mail_icon_parent = user.find_elements(By.CLASS_NAME, value="text-male")
      mail_icon = mail_icon_parent[0].find_elements(By.TAG_NAME, value="img")
      print(f"メールアイコンの数{len(mail_icon)}")
      if  not len(mail_icon):
        mail_icon_flag = False
        break
      mail_icon_try_cnt += 1
      if mail_icon_try_cnt == 10:
          print("送信済ユーザーが10件続きました")
          break
    if i >= len(user_list):
      return
    user = user_list[i]
    # 閲覧済みユーザーをスキップ
    before_content = driver.execute_script(
    'return window.getComputedStyle(arguments[0], "::before").getPropertyValue("content");',
    user
    )
    if before_content != "none":
      continue

    user_link = user.find_elements(By.TAG_NAME, value="a")
    loader = driver.find_elements(By.CLASS_NAME, "loader")
    # loaderが表示されている場合は待機
    if len(loader):
      print("loaderが表示されています")      
      WebDriverWait(driver, 10).until_not(
        EC.presence_of_element_located((By.CLASS_NAME, "loader"))
      )
    user_link[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    catch_warning_screen(driver)
    # ユーザ名を取得
    user_name = driver.find_elements(By.CLASS_NAME, value="ds_user_display_name")
    if user_name:
      user_name = user_name[0].text
    else:
      user_name = "取得に失敗しました"
    # タイプ
    # ランダムな数値を生成し、実行確率と比較
    type_flag = False
    # 実行確率
    probability = 0.01
    execution_probability = probability
    if random.random() < execution_probability:
      type_button = driver.find_element(By.ID, value="btn-type")
      type_button.click()
      type_flag = True
      time.sleep(2)
    # いいね
    # # ランダムな数値を生成し、実行確率と比較
    # like_flag = False
    # # 実行確率
    # execution_probability = probability
    # if random.random() < execution_probability:
    #   others_icon = driver.find_elements(By.CLASS_NAME, value="icon-profile_other_on")
    #   others_icon[0].click()
    #   wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    #   time.sleep(1)
    #   like_icon = driver.find_elements(By.ID, value="btn-like")
    #   like_icon_classes = like_icon[0].get_attribute("class")
    #   if not "disabled" in like_icon_classes:
    #     like_flag = True
    #     # footer_menu-list-item-link
    #     like = like_icon[0].find_elements(By.CLASS_NAME, value="footer_menu-list-item-link")
    #     like[0].click()
    #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    #     time.sleep(2)
    #     like_cancel = driver.find_elements(By.CLASS_NAME, value="modal-cancel")
    #     while not len(like_cancel):
    #        time.sleep(1)
    #        like_cancel = driver.find_elements(By.CLASS_NAME, value="modal-cancel")
    #     like_cancel[0].click()
    #     wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    #     time.sleep(2)
    # print(f'{name}:足跡付け{i+1}件, いいね:{like_flag}、タイプ{type_flag}  {user_name}')
    # print(f'{name}:足跡付け{i+1}件, タイプ{type_flag}  {user_name}')
    now = datetime.now().strftime('%m-%d %H:%M:%S')
    foot_counted += 1
    print(f'{name}:足跡付け{foot_counted}件,  {user_name}  {now}')
    if foot_counted >= foot_count:
        return
    # 戻る
    catch_warning_screen(driver)
    back = driver.find_elements(By.CLASS_NAME, value="ds_prev_arrow")
    driver.execute_script("arguments[0].click();", back[0])
    # back[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1.5)
    # たまに変なページに遷移するのでurl確認
    current_url = driver.current_url
    # 特定の文字列で始まっているか確認
    if not current_url.startswith("https://happymail.co.jp/sp/app/html/profile_list.php"):
        # print("URLは指定した文字列で始まっていません。")
        driver.get("https://happymail.co.jp/sp/app/html/profile_list.php")
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(wait_time)


def send_fst_message(happy_user_list, driver, wait):
  for user_info in happy_user_list:
    name,login_id, passward, fst_message, mail_img = user_info
    limit_cnt = 1
    driver.delete_all_cookies()
    driver.get("https://happymail.jp/login/")
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    wait_time = random.uniform(3, 6)
    time.sleep(wait_time)
    id_form = driver.find_element(By.ID, value="TelNo")
    id_form.send_keys(login_id)
    pass_form = driver.find_element(By.ID, value="TelPass")
    pass_form.send_keys(passward)
    time.sleep(wait_time)
    send_form = driver.find_element(By.ID, value="login_btn")
    send_form.click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    #リモーダル画面が開いていれば閉じる
    catch_warning_screen(driver)
    # # プロフ検索をクリック
    nav_list = driver.find_element(By.ID, value='ds_nav')
    seach_profile = nav_list.find_element(By.LINK_TEXT, "プロフ検索")
    seach_profile.click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    send_cnt = 0
    user_colum = 0
    # 並びの表示を設定
    sort_order = driver.find_elements(By.ID, value="kind_select")
    select = Select(sort_order[0])
    select.select_by_visible_text("プロフ一覧")
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    
    while send_cnt < limit_cnt:
      # ユーザーをクリック
      users = driver.find_elements(By.CLASS_NAME, value="ds_thum_contain")
      # print('取得したユーザー数')
      # print(len(users))
      styles = users[user_colum].get_attribute('style')
      e = driver.find_elements(By.CLASS_NAME, value="ds_mb2p")
      age_text = e[user_colum].find_elements(By.CLASS_NAME, value="ds_post_body_age_small")
      while not "20" in age_text[0].text:
        user_colum += 1
        e = driver.find_elements(By.CLASS_NAME, value="ds_mb2p")
        age_text = e[user_colum].find_elements(By.CLASS_NAME, value="ds_post_body_age_small")
        if user_colum == len(users):
          break
          
      # 画像なしのユーザーを探す
      # while "noimage" not in styles:
      #   user_colum += 1
      #   print(user_colum)
      #   styles = users[user_colum].get_attribute('style')
      
      driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", users[user_colum])
      users[user_colum].click()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
      send_status = True
      m = driver.find_elements(By.XPATH, value="//*[@id='ds_main']/div/p")
      if len(m):
        print(m[0].text)
        if m[0].text == "プロフィール情報の取得に失敗しました":
            send_status = False
            user_colum += 1
      # 自己紹介文に業者、通報が含まれているかチェック
      if len(driver.find_elements(By.CLASS_NAME, value="translate_body")):
        contains_violations = driver.find_element(By.CLASS_NAME, value="translate_body")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", contains_violations)
        self_introduction_text = contains_violations.text.replace(" ", "").replace("\n", "")
        ngword_list = ["通報", "業者", "金銭", "条件"]
        if any(ngword in self_introduction_text for ngword in ngword_list):
          print('自己紹介文に危険なワードが含まれていました')
          send_status = False
          user_colum += 1
      # メール送信
      if send_status:
        do_mail_icon = driver.find_elements(By.CLASS_NAME, value="ds_profile_target_btn")
        do_mail_icon[0].click()
        # 初めましてメッセージを入力
        text_area = driver.find_element(By.ID, value="text-message")
        text_area.send_keys(fst_message)
        # 送信
        send_mail = driver.find_element(By.ID, value="submitButton")
        send_mail.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(wait_time)
        # 画像があれば送信
        # mail_img = setting.debug_img
        if mail_img:
          img_conform = driver.find_element(By.ID, value="media-confirm")
          plus_icon = driver.find_element(By.CLASS_NAME, value="icon-message_plus")
          plus_icon.click()
          time.sleep(1)
          upload_file = driver.find_element(By.ID, "upload_file")
          upload_file.send_keys(mail_img)
          time.sleep(2)
          submit = driver.find_element(By.ID, value="submit_button")
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", submit)
          driver.execute_script("arguments[0].click();", submit)
          while img_conform.is_displayed():
            time.sleep(2)
        send_cnt += 1
        user_colum += 1
        print(f"fst_message {name}~{send_cnt}~")
      driver.get("https://happymail.co.jp/sp/app/html/profile_list.php")
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
      # リモーダル画面が出たら閉じる
      remodal = driver.find_elements(By.CLASS_NAME, value="remodal-close")
      if len(remodal):
        print('リモーダル画面')
        remodal[0].click()
        time.sleep(wait_time)
    
  print("fstmail end")
  

def check_new_mail(happy_info, driver, wait, android=False):
  return_list = []
  name = happy_info["name"]
  login_id = happy_info["login_id"]
  login_pass = happy_info["password"]
  fst_message = happy_info["fst_message"]
  conditions_message = happy_info["second_message"]   
  return_foot_message = happy_info["return_foot_message"]   
  # if name != 'ゆっこ':
  #    return
  print(f"{name} チェック開始")
  if not login_id:
    print(f"{name}のログインIDを取得できませんでした")
    return
  wait_time = random.uniform(2, 5)
  # login(name, login_id, login_pass, driver, wait)
  warinig_flug = catch_warning_screen(driver)
  if warinig_flug:
    print(f"{name}:警告画面が出ている可能性があります")
    return_list.append(f"ハッピーメール　{name}:警告画面が出ている可能性があります")
    return return_list
  # 画像チェック
  top_img_element = driver.find_elements(By.CLASS_NAME, value="ds_mypage_user_image")
  if len(top_img_element):
     top_img = top_img_element[0].get_attribute("style")
     if "noimage" in top_img:
        print(f"ハッピーメール、{name}のトップ画の設定がNoImageです")
        return_list.append(f"ハッピーメール、{name}のトップ画の設定がNoImageです")
  new_message_flug = nav_item_click("メッセージ", driver, wait)
  if "新着メールなし" == new_message_flug:
    return None
  elif not new_message_flug:
    print(driver.current_url)
    print(f"{name} {login_id} {login_pass}  でログインします")
    login_flug = login(name, login_id, login_pass, driver, wait,)
    if login_flug:
      print(f"{name} ::{login_flug}") 
    warning = catch_warning_screen(driver)
    if warning:
      print(f"{name} :::{warning}")
      return
    print(f"{name}のログインに成功しました")
    print(driver.current_url)
    nav_flug = nav_item_click("プロフ検索", driver, wait)
    if not nav_flug:
      print(12345689)
      return
  else:  
  # 新着があった
  # if True:
    #  未読のみ表示
     only_new_message = driver.find_elements(By.CLASS_NAME, value="ds_message_tab_item")[1]
     only_new_message.click()
     time.sleep(1)
     new_mail = driver.find_elements(By.CLASS_NAME, value="ds_message_list_mini")  
     if not len(new_mail):
         list_load = driver.find_elements(By.ID, value="load_bL")
         if len(list_load):
          list_load[0].click()
         time.sleep(2)
    #  新着がある間はループ
     
     while len(new_mail):
    #  while True:
        date = new_mail[0].find_elements(By.CLASS_NAME, value="ds_message_date") 
        date_numbers = re.findall(r'\d+', date[0].text)
        if not len(date_numbers):
           for_minutes_passed = True
        else:
          now = datetime.today()
          arrival_datetime = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=int(date_numbers[0]),
            minute=int(date_numbers[1])
          )
          elapsed_time = now - arrival_datetime
          # print(f"メール到着からの経過時間{elapsed_time}")
          # 4分経過しているか
          # if True:
          if elapsed_time >= timedelta(minutes=4):
             for_minutes_passed = True
          else:
             for_minutes_passed = False
        if for_minutes_passed:
        # if True:
          # print("4分以上経過しているメッセージあり")          
          new_mail[0].click()
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
          catch_warning_screen(driver)
          user_name = driver.find_elements(By.CLASS_NAME, value="app__navbar__item--title")[1]
          user_name = user_name.text
          send_message = driver.find_elements(By.CLASS_NAME, value="message__block--send")    
         
          if len(send_message):
            chara_img_senf_flug = send_message[-1].find_elements(By.CLASS_NAME, value="attached_photo_link")
            if len(chara_img_senf_flug):
              # print("画像あり")
              sent_text_element = send_message[-2]
            else:
              sent_text_element = send_message[-1]            
            script = """
            var element = arguments[0];

            // 除外するクラスを持つ子要素を取得
            var elementsToRemove = element.querySelectorAll('.transit_info, .message__block__body__time');

            // 一時的に削除
            elementsToRemove.forEach(el => el.remove());

            // 要素Aのテキストを取得
            var textContent = element.textContent.trim();

            // 削除した子要素を元に戻す
            elementsToRemove.forEach(el => element.appendChild(el));

            return textContent;
            """
            text_without_children = driver.execute_script(script, sent_text_element) 
            send_text = text_without_children
            # print("<<<<<<<<<<<send_text>>>>>>>>>>>>>")
            # print("<<<<<<<<<<<fst_message>>>>>>>>>>>>>")
            # print(fst_message)
            # print("<<<<<<<<<<<return_foot_message>>>>>>>>>>>>>")
            # print(return_foot_message)
            # 改行と空白を削除
            send_text_clean = func.normalize_text(send_text)
            fst_message_clean = func.normalize_text(fst_message)
            return_foot_message_clean = func.normalize_text(return_foot_message)
            conditions_message_clean = func.normalize_text(conditions_message)
            
            # 変換後のデバッグ表示
            # print("---------------------------------------")
            # print(f"変換後のsend_text: {repr(send_text_clean)}")
            # print("---------------------------------------")
            # print(f"変換後のfst_message: {repr(fst_message_clean)}")
            # print("---------------------------------------")
            # print(f"変換後のreturn_foot_message: {repr(return_foot_message_clean)}")
            
            # print("---------------------------------------")
            # print(fst_message_clean == send_text_clean)
            # print("---------------------------------------")
            # print(return_foot_message_clean == send_text_clean)
            # print("---------------------------------------")
            # print("募集メッセージ" in send_text)
            if fst_message_clean == send_text_clean or return_foot_message_clean == send_text_clean or "募集メッセージ" in send_text_clean:
              if conditions_message:
                text_area = driver.find_element(By.ID, value="text-message")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
                # text_area.send_keys(return_foot_message)
                driver.execute_script("document.body.click();")
                time.sleep(0.5)
                script = "arguments[0].value = arguments[1];"
                driver.execute_script(script, text_area, conditions_message)
                time.sleep(0.5)
                text_area.send_keys("\n")
                time.sleep(0.5)
                # 送信
                send_mail = driver.find_element(By.ID, value="submitButton")
                send_mail.click()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(wait_time)
                send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
                reload_cnt = 0
                send_text_clean = func.normalize_text(send_msg_elem[-1].text)
                while send_text_clean != conditions_message_clean:
                  # print(send_text_clean)
                  # print("~~~~~~~~~~~~~~~~~~~~~")
                  # print(conditions_message_clean)
                  driver.refresh()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(5)
                  send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
                  reload_cnt += 1
                  if reload_cnt == 3:
                      driver.refresh()
                      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                      time.sleep(wait_time)
                      break
              else:
                # print('やり取りしてます')
                
                receive_contents = driver.find_elements(By.CLASS_NAME, value="message__block--receive")[-1]
                return_message = f"{name}happymail,{login_id}:{login_pass}\n{user_name}「{receive_contents.text}」"
                return_list.append(return_message)
                # みちゃいや
                plus_icon_parent = driver.find_elements(By.CLASS_NAME, value="message__form__action")
                plus_icon = plus_icon_parent[0].find_elements(By.CLASS_NAME, value="icon-message_plus")
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", plus_icon[0])
                plus_icon[0].click()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(2)
                # ds_message_txt_media_text
                mityaiya = ""
                candidate_mityaiya = driver.find_elements(By.CLASS_NAME, value="ds_message_txt_media_text")
                for c_m in candidate_mityaiya:
                  if c_m.text == "見ちゃいや":
                      mityaiya = c_m
                if mityaiya:
                  # print('<<<<<<<<<<<<<<<<<みちゃいや登録>>>>>>>>>>>>>>>>>>>')
                  mityaiya.click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(2)
                  mityaiya_send = driver.find_elements(By.CLASS_NAME, value="input__form__action__button__send")
                  if len(mityaiya_send):
                    mityaiya_send[0].click()
                    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                    time.sleep(1)
                  
            else:
              # print('やり取りしてます')
              user_name = driver.find_elements(By.CLASS_NAME, value="app__navbar__item--title")[1]
              user_name = user_name.text
              receive_contents = driver.find_elements(By.CLASS_NAME, value="message__block--receive")[-1]
              return_message = f"{name}happymail,{login_id}:{login_pass}\n{user_name}「{receive_contents.text}」"
              return_list.append(return_message)

              # みちゃいや
              plus_icon_parent = driver.find_elements(By.CLASS_NAME, value="message__form__action")
              plus_icon = plus_icon_parent[0].find_elements(By.CLASS_NAME, value="icon-message_plus")
              
              driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", plus_icon[0])
              plus_icon[0].click()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(2)
              # ds_message_txt_media_text
              mityaiya = ""
              candidate_mityaiya = driver.find_elements(By.CLASS_NAME, value="ds_message_txt_media_text")
              for c_m in candidate_mityaiya:
                if c_m.text == "見ちゃいや":
                  mityaiya = c_m
              if mityaiya:
                # print('<<<<<<<<<<<<<<<<<みちゃいや登録>>>>>>>>>>>>>>>>>>>')
                mityaiya.click()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(2)
                mityaiya_send = driver.find_elements(By.CLASS_NAME, value="input__form__action__button__send")
                if len(mityaiya_send):
                  mityaiya_send[0].click()
                  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                  time.sleep(1)
          else:
            text_area = driver.find_element(By.ID, value="text-message")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area)
            driver.execute_script("document.body.click();")
            time.sleep(0.5)
            script = "arguments[0].value = arguments[1];"
            driver.execute_script("arguments[0].click();", text_area)
            driver.execute_script(script, text_area, fst_message.format(name=user_name))
            time.sleep(0.5)
            text_area.send_keys("\n")
            time.sleep(0.5)
            # 送信
            send_mail = driver.find_element(By.CLASS_NAME, "icon-message_send")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", send_mail)
            send_mail.click()
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(wait_time)
            send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
            reload_cnt = 0
            while not len(send_msg_elem):
              driver.refresh()
              wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
              time.sleep(wait_time)
              send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
              reload_cnt += 1
              if reload_cnt == 3:
                driver.refresh()
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(wait_time)
                break
            
        else:
          if len(return_list):
              return return_list
          else:
              return None
        driver.get("https://happymail.co.jp/sp/app/html/message_list.php")
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
        new_mail = driver.find_elements(By.CLASS_NAME, value="happy_blue_10")
  if len(return_list):
    
    return return_list
  else:
    return None
  
def re_registration(chara_data, driver, wait):
  login_flug = login(chara_data['name'], chara_data['login_id'], chara_data['password'], driver, wait)
  if login_flug:
    print(f"{i['name']} {login}")
    return 
  warning = catch_warning_screen(driver)
  if warning:
    print(f"{chara_data['name']} {warning}")
    return
  print(f"{chara_data['name']}のログインに成功しました")
  nav_flug = nav_item_click("マイページ", driver, wait)
  if not nav_flug:
    print("nav_listが見つかりません")
    return
  # プロフィールをクリック 
  profile = driver.find_element(By.CLASS_NAME, value="icon-ico_profile ")
  driver.execute_script("arguments[0].click();", profile)
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(6)
  # name 
  name_form = driver.find_elements(By.ID, value="nickname_frame")
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", name_form[0])
  name_form[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1.5)
  # text_content
  name_text_area = driver.find_elements(By.CLASS_NAME, value="text_content")
  if name_text_area[0].get_attribute("value") != chara_data["name"]:
    name_text_area[0].clear()
    name_text_area[0].send_keys(chara_data["name"])
    time.sleep(1)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    # save
    save_button = driver.find_elements(By.ID, value="save")
    save_button[0].click()
    time.sleep(2)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    # modal-button-blue
    modal_save_button = driver.find_elements(By.CLASS_NAME, value="modal-button-blue")
    modal_save_button[0].click()
    time.sleep(2)
    print(f"名前{chara_data['name']}")
  else:
    driver.back()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1.5)
  # 年齢
  if chara_data["age"]:
    age_text_area = driver.find_elements(By.ID, value="age")    
    select = Select(age_text_area[0])
    select.select_by_visible_text(chara_data["age"])
    time.sleep(1)
    if age_text_area[0].get_attribute("value") != chara_data["age"]:
      select.select_by_visible_text(chara_data["age"])
      time.sleep(2)
    print(f"年齢：{chara_data['age']}")

  # 居住地
  if chara_data["activity_area"]:
    activity_area_text_area = driver.find_elements(By.ID, value="area")
    select = Select(activity_area_text_area[0])
    select.select_by_visible_text(chara_data["activity_area"])
    time.sleep(2)
    if activity_area_text_area[0].get_attribute("value") != chara_data["activity_area"]:
      select.select_by_visible_text(chara_data["activity_area"])
      time.sleep(2)
    print(f"居住地:{chara_data['activity_area']}")
  # 詳細エリア
  if chara_data["detail_activity_area"]:
    detail_activity_area_text_area = driver.find_elements(By.ID, value="city")
    select = Select(detail_activity_area_text_area[0])
    select.select_by_visible_text(chara_data["detail_activity_area"])
    time.sleep(2)
    if detail_activity_area_text_area[0].get_attribute("value") != chara_data["detail_activity_area"]:
      select.select_by_visible_text(chara_data["detail_activity_area"])
      time.sleep(2)
    print(f"詳細エリア:{chara_data['detail_activity_area']}")
  # member_birth_area 
  if chara_data["birth_place"]:
    member_birth_area_text_area = driver.find_elements(By.NAME, value="member_birth_area")
    select = Select(member_birth_area_text_area[0])
    select.select_by_visible_text(chara_data["birth_place"])
    time.sleep(2)
    if member_birth_area_text_area[0].get_attribute("value") != chara_data["birth_place"]:
      select.select_by_visible_text(chara_data["birth_place"])
      time.sleep(2)
    print(f"出身地:{chara_data['birth_place']}")
  # blood_type
  if chara_data["blood_type"]:
    blood_type_text_area = driver.find_elements(By.NAME, value="blood_type")
    select = Select(blood_type_text_area[0])
    select.select_by_visible_text(chara_data["blood_type"])
    time.sleep(2)
    if blood_type_text_area[0].get_attribute("value") != chara_data["blood_type"]:
      select.select_by_visible_text(chara_data["blood_type"])
      time.sleep(2)
    print(f"血液型:{chara_data['blood_type']}")
  # constellation
  if chara_data["constellation"]:
    constellation_text_area = driver.find_elements(By.NAME, value="constellation")
    select = Select(constellation_text_area[0])
    select.select_by_visible_text(chara_data["constellation"])
    time.sleep(2)
    if constellation_text_area[0].get_attribute("value") != chara_data["constellation"]:
      select.select_by_visible_text(chara_data["constellation"])
      time.sleep(2)
    print(f"星座:{chara_data['constellation']}")
  # height
  if chara_data["height"]:
    height_text_area = driver.find_elements(By.NAME, value="height")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", height_text_area[0])
    driver.execute_script("arguments[0].click();", height_text_area[0])
    time.sleep(2)
    height_choicises_elem = driver.find_elements(By.ID, value="height_choice")
    height_choices = height_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in height_choices:
      if i.text == chara_data["height"]:
        classes = i.get_attribute("class")
        if not "chose" in classes.split():
          i.click()
          time.sleep(2)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  # menu_modal_cancel
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"身長:{chara_data['height']}")
  # スタイル
  if chara_data["style"]:
    style_text_area = driver.find_elements(By.NAME, value="style")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", style_text_area[0])
    driver.execute_script("arguments[0].click();", style_text_area[0])
    time.sleep(1)
    style_choicises_elem = driver.find_elements(By.ID, value="style_choice")
    style_choices = style_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in style_choices:
      if i.text == chara_data["style"]:
        classes = i.get_attribute("class")
        if not "chose" in classes.split():
          i.click()
          time.sleep(2)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    # menu_modal_cancel
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"スタイル:{chara_data['style']}")
  # ルックス
  if chara_data["looks"]:
    looks_text_area = driver.find_elements(By.NAME, value="type")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", looks_text_area[0])
    driver.execute_script("arguments[0].click();", looks_text_area[0])
    time.sleep(1)
    looks_choicises_elem = driver.find_elements(By.ID, value="type_choice")
    looks_choices = looks_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in looks_choices:
      if i.text == chara_data["looks"]:
        classes = i.get_attribute("class")
        if not "chose" in classes.split():
          i.click()
          time.sleep(2)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    # menu_modal_cancel
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"ルックス:{chara_data['looks']}")
  # カップ
  if chara_data["cup"]:
    cup_text_area = driver.find_elements(By.NAME, value="bust_size")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", cup_text_area[0])
    driver.execute_script("arguments[0].click();", cup_text_area[0])
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    cup_choicises_elem = driver.find_elements(By.ID, value="bust_size_choice")
    cup_choices = cup_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in cup_choices:
      if i.text == chara_data["cup"]:
        classes = i.get_attribute("class")
        if not "chose" in classes.split():
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", i)
          driver.execute_script("arguments[0].click();", i)
          time.sleep(2)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    # menu_modal_cancel
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"カップ:{chara_data['cup']}")
  # 職業
  if chara_data["job"]:
    job_text_area = driver.find_elements(By.NAME, value="job")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", job_text_area[0])
    driver.execute_script("arguments[0].click();", job_text_area[0])
    time.sleep(1)
    job_choicises_elem = driver.find_elements(By.ID, value="job_choice")
    job_choices = job_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in job_choices:
      if i.text == chara_data["job"]:
        classes = i.get_attribute("class")
        if not "chose" in classes.split():
          i.click()
          time.sleep(2)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    # menu_modal_cancel
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"職業:{chara_data['job']}")
  # educational_background
  if chara_data["education"]:
    education_text_area = driver.find_elements(By.NAME, value="educational_background")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", education_text_area[0])
    driver.execute_script("arguments[0].click();", education_text_area[0])
    time.sleep(1)
    education_choicises_elem = driver.find_elements(By.ID, value="educational_background_choice")
    education_choices = education_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in education_choices:
      if i.text == chara_data["education"]:
        classes = i.get_attribute("class")
        if not "chose" in classes.split():
          i.click()
          time.sleep(2)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"学歴:{chara_data['education']}")
  # holiday
  if chara_data["holiday"]:
    holiday_text_area = driver.find_elements(By.NAME, value="holiday")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", holiday_text_area[0])
    driver.execute_script("arguments[0].click();", holiday_text_area[0])
    time.sleep(1)
    holiday_choicises_elem = driver.find_elements(By.ID, value="holiday_choice")
    holiday_choices = holiday_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in holiday_choices:
      if i.text == chara_data["holiday"]:
        classes = i.get_attribute("class")
        if not "chose" in classes.split():
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", i)
          driver.execute_script("arguments[0].click();", i)
          time.sleep(2)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"休日:{chara_data['holiday']}")
  # 交際ステータス
  if chara_data["relationship_status"]:
    relationship_status_text_area = driver.find_elements(By.NAME, value="marriage")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", relationship_status_text_area[0])
    driver.execute_script("arguments[0].click();", relationship_status_text_area[0])
    time.sleep(1)
    relationship_status_elem = driver.find_elements(By.ID, value="marriage_choice")
    relationship_status_choices = relationship_status_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in relationship_status_choices:
      if i.text == chara_data["relationship_status"]:
          classes = i.get_attribute("class")
          if not "chose" in classes.split():
            i.click()
            time.sleep(2)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"交際ステータス:{chara_data['relationship_status']}")
  # child
  if chara_data["having_children"]:
    child_text_area = driver.find_elements(By.NAME, value="child")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", child_text_area[0])
    driver.execute_script("arguments[0].click();", child_text_area[0])
    time.sleep(1)
    child_choicises_elem = driver.find_elements(By.ID, value="child_choice")
    child_choices = child_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in child_choices:
      if i.text == chara_data["having_children"]:
          classes = i.get_attribute("class")
          if not "chose" in classes.split():
            i.click()
            time.sleep(2)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"子供:{chara_data['having_children']}")
  # 結婚に対する意思
  if chara_data["intention_to_marry"]:
    intention_to_marry_text_area = driver.find_elements(By.NAME, value="intention_to_marry")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", intention_to_marry_text_area[0])
    driver.execute_script("arguments[0].click();", intention_to_marry_text_area[0])
    time.sleep(1)
    intention_to_marry_choicises_elem = driver.find_elements(By.ID, value="intention_to_marry_choice")
    intention_to_marry_choices = intention_to_marry_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in intention_to_marry_choices:
      if i.text == chara_data["intention_to_marry"]:
          classes = i.get_attribute("class")
          if not "chose" in classes.split():
            i.click()
            time.sleep(2)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"結婚に対する意思:{chara_data['intention_to_marry']}")
  # tobacco
  if chara_data["smoking"]:
    tobacco_text_area = driver.find_elements(By.NAME, value="tobacco")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", tobacco_text_area[0])
    driver.execute_script("arguments[0].click();", tobacco_text_area[0])
    time.sleep(1)
    tobacco_choicises_elem = driver.find_elements(By.ID, value="tobacco_choice")
    tobacco_choices = tobacco_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in tobacco_choices:
      if i.text == chara_data["smoking"]:
          classes = i.get_attribute("class")
          if not "chose" in classes.split():
            i.click()
            time.sleep(2)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"タバコ:{chara_data['smoking']}")
  # liquor
  if chara_data["sake"]:
    liquor_text_area = driver.find_elements(By.NAME, value="liquor")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", liquor_text_area[0])
    driver.execute_script("arguments[0].click();", liquor_text_area[0])
    time.sleep(1)
    liquor_choicises_elem = driver.find_elements(By.ID, value="liquor_choice")
    liquor_choices = liquor_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in liquor_choices:
      if i.text == chara_data["sake"]:
          classes = i.get_attribute("class")
          if not "chose" in classes.split():
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", i)
            driver.execute_script("arguments[0].click();", i)
            time.sleep(2)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"酒:{chara_data['sake']}")
  # car
  if chara_data["car_ownership"]:
    car_text_area = driver.find_elements(By.NAME, value="car")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", car_text_area[0])
    driver.execute_script("arguments[0].click();", car_text_area[0])
    time.sleep(1)
    car_choicises_elem = driver.find_elements(By.ID, value="car_choice")
    car_choices = car_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in car_choices:
      if i.text == chara_data["car_ownership"]:
        classes = i.get_attribute("class")
        if not "chose" in classes.split():
          driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", i)
          driver.execute_script("arguments[0].click();", i)
          time.sleep(2)
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"クルマ:{chara_data['car_ownership']}")
  # housemate
  if chara_data["roommate"]:
    housemate_text_area = driver.find_elements(By.NAME, value="housemate")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", housemate_text_area[0])
    driver.execute_script("arguments[0].click();", housemate_text_area[0])
    time.sleep(1)
    housemate_choicises_elem = driver.find_elements(By.ID, value="housemate_choice")
    housemate_choices = housemate_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in housemate_choices:
      if i.text == chara_data["roommate"]:
          classes = i.get_attribute("class")
          if not "chose" in classes.split():
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", i)
            driver.execute_script("arguments[0].click();", i)
            time.sleep(2)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"同居人:{chara_data['roommate']}")
  # brother
  if chara_data["brothers_and_sisters"]:
    brother_text_area = driver.find_elements(By.NAME, value="brother")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", brother_text_area[0])
    driver.execute_script("arguments[0].click();", brother_text_area[0])
    time.sleep(1)
    brother_choicises_elem = driver.find_elements(By.ID, value="brother_choice")
    brother_choices = brother_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in brother_choices:
      if i.text == chara_data["brothers_and_sisters"]:
          classes = i.get_attribute("class")
          if not "chose" in classes.split():
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", i)
            driver.execute_script("arguments[0].click();", i)
            time.sleep(2)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"兄弟姉妹:{chara_data['brothers_and_sisters']}")
  # hope_before_meet
  if chara_data["until_we_met"]:
    hope_before_meet_text_area = driver.find_elements(By.NAME, value="hope_before_meet")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", hope_before_meet_text_area[0])
    driver.execute_script("arguments[0].click();", hope_before_meet_text_area[0])
    time.sleep(1)
    hope_before_meet_choicises_elem = driver.find_elements(By.ID, value="hope_before_meet_choice")
    hope_before_meet_choices = hope_before_meet_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in hope_before_meet_choices:
      if i.text == chara_data["until_we_met"]:
          classes = i.get_attribute("class")
          if not "chose" in classes.split():
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", i)
            driver.execute_script("arguments[0].click();", i)
            time.sleep(2)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    print(f"会うまでのプロセス:{chara_data['until_we_met']}")
  # first_date_cost
  if chara_data["date_expenses"]:
    first_date_cost_text_area = driver.find_elements(By.NAME, value="first_date_cost")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", first_date_cost_text_area[0])
    driver.execute_script("arguments[0].click();", first_date_cost_text_area[0])
    time.sleep(1)
    first_date_cost_choicises_elem = driver.find_elements(By.ID, value="first_date_cost_choice")
    first_date_cost_choices = first_date_cost_choicises_elem[0].find_elements(By.TAG_NAME, value="span")
    for i in first_date_cost_choices:
      if i.text == chara_data["date_expenses"]:
          classes = i.get_attribute("class")
          if not "chose" in classes.split():
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", i)
            driver.execute_script("arguments[0].click();", i)
            time.sleep(2)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    modal_cancel = driver.find_elements(By.CLASS_NAME, value="menu_modal_cancel")
    modal_cancel[0].click()
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 0);")
    print(f"デート費用:{chara_data['date_expenses']}")
  # profile_confirmation
  profile_save = driver.find_elements(By.ID, value="profile_confirmation")
  profile_save[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(2)


def profile_edit_without_login(chara_data, driver, wait):
  """既にログイン済みの状態からプロフィール編集を行う（ログイン処理をスキップ）"""
  warning = catch_warning_screen(driver)
  if warning:
    print(f"{chara_data['name']} {warning}")
    return
  # マイページへ直接移動
  driver.get("https://happymail.co.jp/app/html/mypage.php")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(2)
  # プロフィールをクリック
  profile = driver.find_element(By.CLASS_NAME, value="icon-ico_profile ")
  driver.execute_script("arguments[0].click();", profile)
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(6)
  # name
  name_form = driver.find_elements(By.ID, value="nickname_frame")
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", name_form[0])
  driver.execute_script("arguments[0].click();", name_form[0])
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1.5)
  # text_content
  name_text_area = driver.find_elements(By.CLASS_NAME, value="text_content")
  if name_text_area[0].get_attribute("value") != chara_data["name"]:
    name_text_area[0].clear()
    name_text_area[0].send_keys(chara_data["name"])
    time.sleep(1)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    save_button = driver.find_elements(By.ID, value="save")
    save_button[0].click()
    time.sleep(2)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    modal_save_button = driver.find_elements(By.CLASS_NAME, value="modal-button-blue")
    modal_save_button[0].click()
    time.sleep(2)
    print(f"名前:{chara_data['name']}")
  else:
    driver.back()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1.5)
  def _save_field(field_name, elem):
    """happyMailSP.api.update_profile_itemを直接呼んで保存"""
    numeric_val = elem.get_attribute('value')
    driver.execute_script("""
      var token = jQuery('#uid').val();
      happyMailSP.api.update_profile_item({token: token, type: arguments[0], value: arguments[1]});
    """, field_name, numeric_val)
    time.sleep(2)

  def _set_and_save(by, locator, field_name, text_value, label):
    """selectの値を設定してAPIで保存"""
    if not text_value:
      return
    elems = driver.find_elements(by, locator)
    if not elems:
      print(f"  {label}: 要素が見つかりません")
      return
    try:
      Select(elems[0]).select_by_visible_text(str(text_value))
      _save_field(field_name, elems[0])
      print(f"  {label}: {text_value}")
    except Exception as e:
      print(f"  {label}: 設定失敗 ({e})")

  # 年齢
  _set_and_save(By.ID, "age", "age", chara_data.get("age"), "年齢")
  # 居住地
  _set_and_save(By.ID, "area", "area", chara_data.get("activity_area"), "居住地")
  # 詳細エリア
  _set_and_save(By.ID, "city", "city", chara_data.get("detail_activity_area"), "詳細エリア")
  # 出身地
  _set_and_save(By.NAME, "member_birth_area", "member_birth_area", chara_data.get("birth_place"), "出身地")
  # 血液型
  _set_and_save(By.NAME, "blood_type", "blood_type", chara_data.get("blood_type"), "血液型")
  # 星座
  _set_and_save(By.NAME, "constellation", "constellation", chara_data.get("constellation"), "星座")

  for field_name, value in [
    ("height", chara_data.get("height")),
    ("style", chara_data.get("style")),
    ("type", chara_data.get("looks")),
    ("bust_size", chara_data.get("cup")),
    ("job", chara_data.get("job")),
    ("educational_background", chara_data.get("education")),
    ("holiday", chara_data.get("holiday")),
    ("marriage", chara_data.get("relationship_status")),
    ("child", chara_data.get("having_children")),
    ("intention_to_marry", chara_data.get("intention_to_marry")),
    ("tobacco", chara_data.get("smoking")),
    ("liquor", chara_data.get("sake")),
    ("car", chara_data.get("car_ownership")),
    ("housemate", chara_data.get("roommate")),
    ("brother", chara_data.get("brothers_and_sisters")),
    ("hope_before_meet", chara_data.get("until_we_met")),
    ("first_date_cost", chara_data.get("date_expenses")),
  ]:
    _set_and_save(By.NAME, field_name, field_name, value, field_name)
  # 自己紹介
  self_promotion = chara_data.get("self_promotion")
  if self_promotion:
    driver.get("https://happymail.co.jp/app/html/profileComment.php")
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    textarea = driver.find_elements(By.ID, "self_introduction")
    if textarea:
      # textareaはモバイルビューではdisabledになっているためJSで解除
      driver.execute_script("arguments[0].removeAttribute('disabled'); arguments[0].removeAttribute('readonly');", textarea[0])
      # テキストを設定してinputイベントで保存ボタンを有効化
      driver.execute_script("arguments[0].value = '';", textarea[0])
      textarea[0].send_keys(self_promotion)
      time.sleep(0.5)
      driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles:true}));", textarea[0])
      time.sleep(0.5)
      # 審査ボタン（#save）をクリック
      save_btn = driver.find_elements(By.ID, "save")
      if save_btn:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn[0])
        driver.execute_script("arguments[0].click();", save_btn[0])
        time.sleep(2)
        # 確認モーダルの「提出する」ボタンをクリック
        submit_btn = driver.find_elements(By.XPATH, "//*[contains(text(),'提出する')]")
        if submit_btn:
          driver.execute_script("arguments[0].click();", submit_btn[0])
          time.sleep(3)
          print(f"  自己紹介: 審査に提出しました")
        else:
          print(f"  自己紹介: 提出するボタンが見つかりません")
      else:
        print(f"  自己紹介: 審査ボタン(#save)が見つかりません")
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
    else:
      print(f"  自己紹介: textarea が見つかりません")
  time.sleep(1)
  print(f"\n{chara_data['name']} のプロフィール編集が完了しました")


HAPPYMAIL_AREA_MAP = {
  '北海道(道央)': 51, '北海道(道東)': 52, '北海道(道南)': 54, '北海道(道北)': 55,
  '青森県': 2, '岩手県': 3, '宮城県': 4, '秋田県': 5, '山形県': 6, '福島県': 7,
  '茨城県': 8, '栃木県': 9, '群馬県': 10, '埼玉県': 11, '千葉県': 12,
  '神奈川県': 13, '東京都': 14, '新潟県': 15, '山梨県': 19, '長野県': 20,
  '富山県': 16, '石川県': 17, '福井県': 18,
  '岐阜県': 21, '静岡県': 22, '愛知県': 23, '三重県': 24,
  '滋賀県': 25, '京都府': 26, '大阪府': 27, '兵庫県': 28, '奈良県': 29, '和歌山県': 30,
  '鳥取県': 31, '島根県': 32, '岡山県': 33, '広島県': 34, '山口県': 35,
  '徳島県': 36, '香川県': 37, '愛媛県': 38, '高知県': 39,
  '福岡県': 40, '佐賀県': 41, '長崎県': 42, '熊本県': 43, '大分県': 44,
  '宮崎県': 45, '鹿児島県': 46, '沖縄県': 47,
  '福岡(北九州)': 48, '福岡(久留米・筑後)': 49, '長崎県(佐世保)': 50,
}


def set_search_conditions(chara_data, driver, wait):
  """プロフ一覧検索の検索条件を設定して保存する"""
  driver.get("https://happymail.co.jp/app/html/profile_list_search.php")
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(2)

  # 年齢(下)
  age_low = chara_data.get("prof_search_youngest_age")
  elems = driver.find_elements(By.NAME, "interest_age_low")
  if elems and age_low:
    try:
      Select(elems[0]).select_by_visible_text(str(age_low))
      print(f"  希望年齢(下): {age_low}")
    except Exception as e:
      print(f"  希望年齢(下): 設定失敗 ({e})")

  # 年齢(上)
  age_high = chara_data.get("prof_search_oldest_age")
  elems = driver.find_elements(By.NAME, "interest_age_high")
  if elems and age_high:
    try:
      Select(elems[0]).select_by_visible_text(str(age_high))
      print(f"  希望年齢(上): {age_high}")
    except Exception as e:
      print(f"  希望年齢(上): 設定失敗 ({e})")

  # 身長(下)
  height_low = chara_data.get("prof_search_height_min")
  elems = driver.find_elements(By.NAME, "interest_height_low")
  if elems and height_low:
    try:
      Select(elems[0]).select_by_visible_text(str(height_low))
      print(f"  希望身長(下): {height_low}")
    except Exception as e:
      print(f"  希望身長(下): 設定失敗 ({e})")

  # 身長(上)
  height_high = chara_data.get("prof_search_height_max")
  elems = driver.find_elements(By.NAME, "interest_height_high")
  if elems and height_high:
    try:
      Select(elems[0]).select_by_visible_text(str(height_high))
      print(f"  希望身長(上): {height_high}")
    except Exception as e:
      print(f"  希望身長(上): 設定失敗 ({e})")

  # エリア（チェックボックス）
  search_areas = chara_data.get("prof_search_area")
  if search_areas:
    area_names = [a.strip() for a in search_areas.split(",") if a.strip()]
    # 一旦全チェックを外す
    all_area_cbs = driver.find_elements(By.NAME, "area[]")
    for cb in all_area_cbs:
      if cb.is_selected():
        driver.execute_script("arguments[0].click();", cb)
    time.sleep(0.3)
    # 指定エリアをチェック
    for area_name in area_names:
      area_val = HAPPYMAIL_AREA_MAP.get(area_name)
      if area_val is None:
        print(f"  エリア '{area_name}': マッピングなし")
        continue
      cb = driver.find_elements(By.ID, f"area-{area_val}")
      if cb:
        if not cb[0].is_selected():
          driver.execute_script("arguments[0].click();", cb[0])
        print(f"  エリア: {area_name} (val={area_val})")
      else:
        print(f"  エリア '{area_name}': 要素が見つかりません")
    time.sleep(0.5)

  # 検索するボタンをクリック
  search_btn = driver.find_elements(By.ID, "btn-search-start")
  if not search_btn:
    search_btn = driver.find_elements(By.XPATH, "//*[contains(text(),'検索する')]")
  if search_btn:
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", search_btn[0])
    driver.execute_script("arguments[0].click();", search_btn[0])
    time.sleep(2)
    print(f"  検索しました")
  else:
    print(f"  検索ボタンが見つかりません")


def set_footprint_settings(driver, wait):
  """足あと設定: 足あとを残す=ON、女性を表示する=OFF(男性のみ表示)"""
  driver.get("https://happymail.co.jp/app/html/ashiato_setting.php")
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(1)

  from selenium.webdriver.support.ui import Select

  # 足あとを残す (enable: 0=残さない, 1=残す)
  enable_sel = driver.find_elements(By.CSS_SELECTOR, "select[name='enable']")
  if enable_sel:
    Select(enable_sel[0]).select_by_value("1")
    print("  足あとを残す: ON")

  # 女性を表示しない (view: 0=すべて, 1=男性のみ, 2=女性のみ)
  view_sel = driver.find_elements(By.CSS_SELECTOR, "select[name='view']")
  if view_sel:
    Select(view_sel[0]).select_by_value("1")
    print("  足あと表示: 男性のみ")

  # 変更ボタンをクリック
  submit_btn = driver.find_elements(By.ID, "submit")
  if submit_btn:
    driver.execute_script("arguments[0].click();", submit_btn[0])
    time.sleep(2)
    print("  足あと設定を保存しました")
  else:
    print("  変更ボタンが見つかりません")


# =====================================================================
# ユーザープロフィール解析・スコアリング
# =====================================================================

def get_profile_image_urls(driver):
  """プロフィール詳細ページからユーザー画像URLリストを取得（background-image形式）"""
  import re
  result = driver.execute_script('''
    var found = [];
    document.querySelectorAll("*").forEach(function(el){
      var bg = window.getComputedStyle(el).backgroundImage;
      if(bg && bg !== "none" && bg.includes("pict.happymail.co.jp")){
        var match = bg.match(/url\\(["']?([^"')]+)["']?\\)/);
        if(match) found.push(match[1]);
      }
    });
    // 重複除去・サムネ除外（800px幅を優先）
    return [...new Set(found)].filter(function(u){ return u.includes("/ph/800/") || u.includes("/ph/"); });
  ''')
  return result


def analyze_image_with_claude(image_url, cookies_dict=None):
  """
  Claude APIで画像を解析して「芋っぽい・真面目そう」スコアを返す。
  戻り値: (score: int, reason: str)
  """
  import anthropic
  import httpx
  import base64
  import os

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
    # ブラウザのCookieを使って画像をダウンロード
    headers = {'Referer': 'https://happymail.co.jp/'}
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
              'この男性の写真を見て、以下の観点で0〜30点のスコアをつけてください。\n'
              '・芋っぽい・地味・オタク系の見た目: 高スコア\n'
              '・真面目そう・おとなしそう: 高スコア\n'
              '・女性慣れしていなそう・モテなそう: 高スコア\n'
              '・イケメン・チャラい・自信ありそう: 低スコア\n\n'
              '必ず以下の形式のみで答えてください（説明不要）:\n'
              'SCORE:数字 REASON:一言理由'
            ),
          },
        ],
      }],
    )
    text = message.content[0].text.strip()
    import re
    m = re.search(r'SCORE:(\d+)\s+REASON:(.+)', text)
    if m:
      return int(m.group(1)), m.group(2).strip()
    return 0, f'(解析結果: {text[:50]})'

  except Exception as e:
    return 0, f'(画像解析エラー: {e})'


def get_profile_detail(driver, wait):
  """現在開いている詳細ページからプロフィール情報を全取得してdictで返す"""
  profile = {}

  # 基本項目（ds_profile_select_list_item: 「ラベル\n値」形式）
  items = driver.find_elements(By.CLASS_NAME, 'ds_profile_select_list_item')
  for item in items:
    text = item.text.strip()
    if '\n' in text:
      label, value = text.split('\n', 1)
      # 重複キーは最初の値（基本情報）を優先
      if label not in profile:
        profile[label] = value.strip()

  # 興味・関心
  interests = driver.find_elements(By.CLASS_NAME, 'ds_circle_text_list_item_pc')
  profile['興味'] = [el.text.strip() for el in interests if el.text.strip()]

  # 出会いの目的
  purposes = driver.find_elements(By.CSS_SELECTOR, '.ds_circle_text_list_item_pc')
  # 自己紹介文
  intro_els = driver.find_elements(By.CLASS_NAME, 'translate_body')
  profile['自己紹介'] = intro_els[0].text.strip() if intro_els else ''

  # ニックネーム：「XXXさんを通報する」要素から抽出（最も確実）
  tuhou_el = driver.find_elements(By.CSS_SELECTOR, '[class*=tuhou]')
  if tuhou_el:
    profile['名前'] = tuhou_el[0].text.strip().replace('さんを通報する', '')
  else:
    name_el = driver.find_elements(By.CSS_SELECTOR, '.profile_name_text, [class*=profile_name]')
    profile['名前'] = name_el[0].text.strip() if name_el else ''

  login_el = driver.find_elements(By.CSS_SELECTOR, '[class*=login_date], [class*=last_login]')
  profile['最終ログイン'] = login_el[0].text.strip() if login_el else ''

  # プロフ画像URL（background-imageから取得）
  image_urls = get_profile_image_urls(driver)
  profile['画像あり'] = len(image_urls) > 0
  profile['画像urls'] = image_urls

  # 現在のURL（user_id取得用）
  profile['url'] = driver.current_url

  return profile


def score_user(profile):
  """
  プロフィール情報から「好みタイプ」スコアを算出する。
  点数が高いほど好みに合致。

  判定基準:
    - 道程・女性慣れしていない (inexperienced)
    - 年収が低い
    - 真面目そう・芋っぽい
  """
  score = 0
  reasons = []
  intro = profile.get('自己紹介', '')
  interests = profile.get('興味', [])

  # ── 年収スコア ──────────────────────────────
  income = profile.get('年収', '')
  if not income:
    score += 15
    reasons.append('年収未記入(+15)')
  elif '～300' in income or '300万円未満' in income:
    score += 20
    reasons.append(f'年収低め {income}(+20)')
  elif '300～600' in income:
    score += 10
    reasons.append(f'年収やや低め {income}(+10)')
  elif '600～1000' in income:
    score += 0
  elif '1000万' in income or '5000万' in income:
    score -= 10
    reasons.append(f'高収入 {income}(-10)')

  # ── 職業スコア ──────────────────────────────
  job = profile.get('職業', '')
  if job in ['学生']:
    pass  # 学生はスコアなし
  elif job in ['フリーター・アルバイト', 'フリーランス・個人事業主']:
    score += 8
    reasons.append(f'職業:{job}(+8)')
  elif job in ['会社員・OL', '大手企業', 'IT・Web関連']:
    score += 0
  elif job in ['公務員', '医師・歯科医師', '弁護士・会計士']:
    score -= 5
    reasons.append(f'エリート職業:{job}(-5)')

  # ── 道程・女性慣れしていない ──────────────────────────
  inexperienced_words = [
    '奥手', '人見知り', '草食', 'コミュ障', '慣れていない', '初めて', '初心者',
    '緊張', 'モテない', '女性と話す', '苦手', '話しかけてください', 'リードして',
    'リードされたい', 'ぼっち', '友達いない', '孤独', '引きこもり', '内気',
  ]
  hit_words = [w for w in inexperienced_words if w in intro]
  if hit_words:
    add = min(len(hit_words) * 8, 30)
    score += add
    reasons.append(f'道程ワード{hit_words}(+{add})')

  # 自己紹介が短い・ぎこちない
  if len(intro) < 30 and intro:
    score += 8
    reasons.append(f'自己紹介が短い({len(intro)}文字)(+8)')
  elif len(intro) == 0:
    score += 12
    reasons.append('自己紹介なし(+12)')

  # ── 芋っぽい・真面目系 ──────────────────────────────
  nerdy_words = [
    'アニメ', 'ゲーム', '漫画', 'マンガ', 'フィギュア', '鉄道', '電車',
    'プログラム', 'コード', 'パソコン', 'PC', '読書', '映画鑑賞', '一人',
    '在宅', 'テレワーク', 'インドア', 'ニコニコ', 'YouTube', '料理',
  ]
  nerdy_interests = [w for w in nerdy_words if w in intro or w in ' '.join(interests)]
  if nerdy_interests:
    add = min(len(nerdy_interests) * 5, 25)
    score += add
    reasons.append(f'芋系ワード{nerdy_interests}(+{add})')

  # ── 画像なし ──────────────────────────────────
  if not profile.get('画像あり'):
    score += 15
    reasons.append('プロフ画像なし(+15)')

  # ── スタイル ──────────────────────────────────
  style = profile.get('スタイル', '')
  if style in ['やや細め', '細め']:
    score += 5
    reasons.append(f'スタイル:{style}(+5)')
  elif style == 'ぽっちゃり':
    score += 8
    reasons.append(f'スタイル:{style}(+8)')

  # ── タバコ ────────────────────────────────────
  tobacco = profile.get('タバコ', '')
  if '吸わない' in tobacco:
    score += 5
    reasons.append('非喫煙(+5)')

  # ── 出会いの目的（真面目系）──────────────────────
  purpose_text = ' '.join(profile.get('興味', []))
  if '友達' in purpose_text or '真剣' in purpose_text or '結婚' in purpose_text:
    score += 8
    reasons.append('真剣系目的(+8)')

  return score, reasons


def analyze_profile_list(driver, wait, top_n=10):
  """
  プロフ一覧の上位top_nユーザーを順に詳細ページで解析してスコア一覧を返す。
  戻り値: list of dict {name, score, reasons, profile, url}
  """
  driver.get('https://happymail.co.jp/app/html/profile_list.php?a=a')
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(2)

  results = []
  for idx in range(1, top_n + 1):
    try:
      url = f'https://happymail.co.jp/app/html/profile_detail_list.php?a=a&from=prof&idx={idx}'
      driver.get(url)
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(1)

      # 存在チェック（一覧の範囲外なら終了）
      if 'profile_list' in driver.current_url and 'detail' not in driver.current_url:
        break

      profile = get_profile_detail(driver, wait)
      score, reasons = score_user(profile)

      # 画像がある場合はClaude APIで画像解析してスコア加算
      image_urls = profile.get('画像urls', [])
      if image_urls:
        cookies_dict = {c['name']: c['value'] for c in driver.get_cookies()}
        img_score, img_reason = analyze_image_with_claude(image_urls[0], cookies_dict)
        if img_score > 0:
          score += img_score
          reasons.append(f'画像解析+{img_score}点({img_reason})')

      name = profile.get('名前') or profile.get('ニックネーム', f'user{idx}')
      results.append({
        'name': name,
        'score': score,
        'reasons': reasons,
        'profile': profile,
        'url': profile['url'],
      })
      print(f"  [{idx}] {name} | 年収:{profile.get('年収','-')} | 職業:{profile.get('職業','-')} | スコア:{score}")

    except Exception as e:
      print(f"  [{idx}] エラー: {e}")
      continue

  # スコア降順にソート
  results.sort(key=lambda x: x['score'], reverse=True)
  return results


def print_score_report(results):
  """スコアリング結果をわかりやすく表示"""
  print(f"\n{'='*55}")
  print(f"  スコアランキング (高スコア = 好みタイプ)")
  print(f"{'='*55}")
  for i, r in enumerate(results, 1):
    p = r['profile']
    print(f"\n{i}位 {r['name']}  スコア:{r['score']}点")
    print(f"  年齢:{p.get('年齢','-')} 居住地:{p.get('居住地','-')} 年収:{p.get('年収','-')}")
    print(f"  職業:{p.get('職業','-')} スタイル:{p.get('スタイル','-')}")
    print(f"  自己紹介: {p.get('自己紹介','')[:60]}")
    print(f"  理由: {', '.join(r['reasons'])}")
    print(f"  URL: {r['url']}")


def score_and_send_fst_message(name, driver, wait, fst_message, image_path, user_check_cnt=None):
  """
  プロフ一覧からuser_check_cnt人をスコアリングして、
  最高スコアのユーザーにfst_messageを送信する。

  Args:
    name: 自キャラ名（ログ用）
    driver: WebDriver
    wait: WebDriverWait
    fst_message: 送信する初回メッセージ（{name}で相手名を埋め込み可）
    user_check_cnt: 確認するユーザー数（Noneの場合は8〜14のランダム）
  Returns:
    送信先ユーザー名（送信できなかった場合はNone）
  """
  if user_check_cnt is None:
    user_check_cnt = random.randint(8, 14)

  print(f"  [{name}] プロフ一覧から{user_check_cnt}人をスコアリング中...")

  driver.get('https://happymail.co.jp/app/html/profile_list.php?a=a')
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(2)

  results = []
  cookies_dict = {c['name']: c['value'] for c in driver.get_cookies()}

  for idx in range(1, user_check_cnt + 1):
    try:
      url = f'https://happymail.co.jp/app/html/profile_detail_list.php?a=a&from=prof&idx={idx}'
      driver.get(url)
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(1)

      if 'detail' not in driver.current_url:
        break

      # メッセージ履歴チェック（mail_history_off = 未送信、それ以外はスキップ）
      mail_el = driver.find_elements(By.CLASS_NAME, 'ds_profile_detail_mail')
      if mail_el and 'mail_history_off' not in mail_el[0].get_attribute('class'):
        print(f"    [{idx}] 送信済みスキップ")
        continue

      profile = get_profile_detail(driver, wait)
      score, reasons = score_user(profile)

      # 画像解析
      image_urls = profile.get('画像urls', [])
      if image_urls:
        img_score, img_reason = analyze_image_with_claude(image_urls[0], cookies_dict)
        print(f"    [{idx}] 画像解析スコア: {img_score}点 ({img_reason})")
        if img_score > 0:
          score += img_score
          reasons.append(f'画像+{img_score}({img_reason})')

      # NGワードチェック
      intro = profile.get('自己紹介', '')
      ngword_list = ['通報', '業者', '金銭', '条件', 'サクラ']
      if any(ng in intro for ng in ngword_list):
        print(f"    [{idx}] NGワード検出スキップ")
        continue

      user_name = profile.get('名前') or f'user{idx}'

      results.append({
        'name': user_name,
        'score': score,
        'reasons': reasons,
        'profile': profile,
        'url': driver.current_url,
        'idx': idx,
      })
      print(f"    [{idx}] {user_name} スコア:{score} ({', '.join(reasons[:3])})")

    except Exception as e:
      print(f"    [{idx}] エラー: {e}")
      continue

  if not results:
    print(f"  [{name}] 送信対象が見つかりませんでした")
    return None

  # 最高スコアのユーザーへ移動
  results.sort(key=lambda x: x['score'], reverse=True)
  best = results[0]
  print(f"  [{name}] 最高スコア: {best['name']} ({best['score']}点) → メッセージ送信")

  driver.get(best['url'])
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(1.5)

  try:
    # メッセージボタンをクリック（ds_profile_target_btn）
    mail_btn = driver.find_elements(By.CLASS_NAME, 'ds_profile_target_btn')
    if not mail_btn:
      print(f"  [{name}] メッセージボタンが見つかりません")
      return None
    driver.execute_script('arguments[0].click();', mail_btn[0])
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1.5)
    # メッセージ入力
    text_area = driver.find_elements(By.ID, 'text-message')
    if not text_area:
      print(f"  [{name}] テキストエリアが見つかりません")
      return None
    message = fst_message.format(name=best['name']) if '{name}' in fst_message else fst_message
    text_area[0].send_keys(message)
    time.sleep(0.5)

    # テキスト送信
    send_btn = driver.find_elements(By.ID, 'submit_button')
    if not send_btn:
      print(f"  [{name}] 送信ボタンが見つかりません")
      return None
    driver.execute_script('arguments[0].scrollIntoView({block:"center"});', send_btn[0])
    driver.execute_script('arguments[0].click();', send_btn[0])
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
    reload_cnt = 0
    most_recent_msg = send_msg_elem[-1]  
    script = """
      var element = arguments[0];

      // 除外するクラスを持つ子要素を取得
      var elementsToRemove = element.querySelectorAll('.transit_info, .message__block__body__time');

      // 一時的に削除
      elementsToRemove.forEach(el => el.remove());

      // 要素Aのテキストを取得
      var textContent = element.textContent.trim();

      // 削除した子要素を元に戻す
      elementsToRemove.forEach(el => element.appendChild(el));

      return textContent;
      """
      
    most_recent_msg = driver.execute_script(script, most_recent_msg) 
    most_recent_msg_clean = func.normalize_text(most_recent_msg)
    fst_message_clean = func.normalize_text(message)
    while most_recent_msg_clean != fst_message_clean:
      # print(most_recent_msg)
      # print("~~~~~~~~~~~~~~~~~~~~")
      # print(return_foot_message)
      driver.refresh()
      wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
      time.sleep(wait_time)
      send_msg_elem = driver.find_elements(By.CLASS_NAME, value="message__block__body__text--female")
      reload_cnt += 1
      if reload_cnt == 1:
        driver.refresh()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(wait_time)
        break
    print(f"  [{name}] → {best['name']} にテキスト送信完了")

    # 画像送信
    local_img_path = None
    if image_path:
      try:
        local_img_path = f"{name}_fst_img.png"
        img_response = requests.get(image_path)
        with open(local_img_path, 'wb') as f:
          f.write(img_response.content)
        local_img_path = os.path.abspath(local_img_path)

        # +アイコンをクリックして画像アップロード
        plus_icon = driver.find_elements(By.CLASS_NAME, 'icon-message_plus')
        if plus_icon:
          driver.execute_script('arguments[0].click();', plus_icon[0])
          time.sleep(1)
        upload_file = driver.find_elements(By.ID, 'upload_file')
        if upload_file:
          upload_file[0].send_keys(local_img_path)
          time.sleep(2)
          img_submit = driver.find_elements(By.ID, 'submit_button')
          if img_submit:
            driver.execute_script('arguments[0].scrollIntoView({block:"center"});', img_submit[0])
            driver.execute_script('arguments[0].click();', img_submit[0])
            time.sleep(2)
            print(f"  [{name}] 画像送信完了")
      except Exception as e:
        print(f"  [{name}] 画像送信エラー: {e}")
      finally:
        if local_img_path and os.path.exists(local_img_path):
          os.remove(local_img_path)

    return best['name']
  except Exception as e:
    print(f"  [{name}] メッセージ送信エラー: {e}")
    return None


def return_foot_message_roll(name, driver, wait, login_id, password, return_foot_message, return_foot_img):
  warning_pop = catch_warning_screen(driver)
  daily_limit = 111

  if return_foot_img:
    # 画像データを取得してBase64にエンコード
    image_response = requests.get(return_foot_img)
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
  nav_item_click("マイページ", driver, wait)
  # 足あとをクリック
  return_footpoint = driver.find_element(By.CLASS_NAME, value="icon-ico_footprint")
  driver.execute_script("arguments[0].click();", return_footpoint)
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(1.5)

  
     




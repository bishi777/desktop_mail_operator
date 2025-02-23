import time
from selenium.webdriver.common.by import By
import random
from selenium.common.exceptions import ElementNotInteractableException
import re
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from widget import func

def login(driver, wait, login_mail_address, login_pass):
  if login_mail_address == None or login_pass == None:
    print(f"ログインに必要な情報がありません。メールアドレスとパスワードを確認してください。")
    return
  driver.delete_all_cookies()
  driver.get("https://www.194964.com/")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  wait_time = random.uniform(2, 3)
  time.sleep(2)
  login_button = driver.find_element(By.CLASS_NAME, value="btn-login")
  login_button.click()
  time.sleep(2)
  mail_address_tab = driver.find_elements(By.CLASS_NAME, value="lstTab")
  mail_address_tab = mail_address_tab[0].find_elements(By.CLASS_NAME, value="tab")
  mail_address_tab = mail_address_tab[1].find_elements(By.TAG_NAME, value="a")
  mail_address_tab[0].click()
  mail_addres_input_form = driver.find_elements(By.NAME, value="mailAddressForward")
  mail_addres_input_form[0].send_keys(login_mail_address)
  time.sleep(1)
  password_input_form = driver.find_elements(By.NAME, value="password")
  password_input_form[0].send_keys(login_pass)
  time.sleep(1)
  login_button = driver.find_elements(By.CLASS_NAME, value="greenButton")
  login_button[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  driver.refresh()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  popup_content = driver.find_elements(By.ID, value="popupContent")
  while len(popup_content):
    driver.refresh()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(wait_time)
    popup_content = driver.find_elements(By.ID, value="popupContent")
  
def set_search_filter(driver, wait):
  wait_time = random.uniform(2, 3)
  search_user = driver.find_elements(By.CLASS_NAME, value="bottom-nav-item-txt")
  search_user = search_user[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  search_link = driver.find_elements(By.CLASS_NAME, value="searchlink")
  search_link = search_link[0].find_elements(By.TAG_NAME, value="a")  
  search_link[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  footer_link_title = driver.find_elements(By.CLASS_NAME, value="footerLinkTitle")
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", footer_link_title[0])
  time.sleep(1)
  footer_link_title[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  green_button = driver.find_elements(By.CLASS_NAME, value="greenButton")
  if green_button[0].text != "検索":
    print("検索フィルターが見つかりません")
    return
  green_button[0].click()

def send_fst_message(driver, wait, fst_message, name,send_cnt):
  wait_time = random.uniform(1, 6)
  user_link_list = []
  prof_Look_btns = driver.find_elements(By.CLASS_NAME, value="profLookBtn")
  for prof_Look_btn in prof_Look_btns:
    user_link = prof_Look_btn.get_attribute("href")
    user_link_list.append(user_link)
  print(len(user_link_list))
  send_cnt = 0
  for i in user_link_list:
    driver.get(i)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
    # 自己紹介NGワードチェック
    introduction = driver.find_elements(By.CLASS_NAME, value="block-introduction-slide")
    introduction_text = introduction[0].text
    if '通報' in introduction_text or '業者' in introduction_text:
      print('イククル：自己紹介文に危険なワードが含まれていました')
      continue
    message_btn_parent = driver.find_elements(By.CLASS_NAME, value="user-profile-btn-message")
    display_value = message_btn_parent[0].value_of_css_property("display")
    if display_value == "none":
      print("履歴あり")
      continue 
    message_btn = driver.find_elements(By.ID, value="messageBtn")
    message_btn[0].click()
    time.sleep(wait_time)
    send_textarea = driver.find_elements(By.ID, value="send-message")
    try:
      send_textarea[0].send_keys(fst_message)
    except ElementNotInteractableException:
      print("年齢確認ができていないユーザーの可能性があります")
      continue
    time.sleep(1)
    submit_message_btn = driver.find_elements(By.CLASS_NAME, value="submitMessageBtn")
    submit_message_btn[0].click()
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    history_btn = driver.find_elements(By.ID, value="historyBtn")
    while not len(history_btn):
      time.sleep(wait_time)
      history_btn = driver.find_elements(By.ID, value="historyBtn")
    send_cnt += 1
    print(f"イククル:{name} fstメール送信  ~{send_cnt}~ 件")

def check_mail(driver, wait, ikukuru_data, gmail_account, gmail_account_password, recieve_mailaddress):
  return_list = []
  login_address = ikukuru_data["login_mail_address"]
  login_password = ikukuru_data["password"]
  fst_message = ikukuru_data["fst_message"]
  second_message = ikukuru_data["second_message"]
  gmail_address = ikukuru_data["gmail_address"]
  gmail_pass = ikukuru_data["gmail_password"]
  condition_message = ikukuru_data["condition_message"]
  mail_img = ""
  print(f"{gmail_account} {gmail_account_password} {recieve_mailaddress}")

  wait_time = random.uniform(2, 3)
  messages_icon = driver.find_elements(By.CLASS_NAME, value="bottom-nav-item")
  new_icon = messages_icon[2].find_elements(By.CLASS_NAME, value="caution")
  if not len(new_icon):
    print('新着なし')
    return  
  messages_button = messages_icon[2].find_elements(By.CLASS_NAME, value="bottom-nav-item-txt")
  messages_button[0].click()
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  # ユーザーやりとりリスト
  users_list = driver.find_elements(By.CLASS_NAME, value="bgMiddle")
  for i in range(len(users_list)):
    new_icon = users_list[i].find_elements(By.CLASS_NAME, value="icon-new-box")
    if len(new_icon):
      print("new!!")
      # 時間チェック　timeContribute
      arrival_date = users_list[i].find_elements(By.CLASS_NAME, value="timeContribute")
      arrival_date_text = arrival_date[0].text
      if "今話せるかも " in arrival_date_text:
        arrival_date_text = arrival_date_text.replace("今話せるかも", "")
      arrival_date_text = arrival_date_text.lstrip()
      print(arrival_date_text)
      # datetime型を作成
      datetime_object = datetime.strptime(arrival_date_text, "%m/%d %H:%M")
      current_time = datetime.now()
      # 現在の日付より未来の時間が設定されている場合は「昨日」と判定
      if datetime_object > current_time:
        datetime_object = datetime_object - timedelta(days=1)
      if current_time - datetime_object > timedelta(minutes=4):
        print("4分以上経過しています")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", users_list[i])
        users_list[i].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
        # bubble_owner
        chara_send = driver.find_elements(By.CLASS_NAME, value="bubble_owner")
        send_message = ""
        # bubble_other
        user_message = driver.find_elements(By.CLASS_NAME, value="bubble_other")
        if len(user_message):
          received_mail = user_message[-1].text
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
          print("メールアドレスが含まれています")
          # icloudの場合
          if "icloud.com" in received_mail:
            print("icloud.comが含まれています")
            icloud_text = "メール送ったんですけど、ブロックされちゃって届かないのでこちらのアドレスにお名前添えて送ってもらえますか？"
            icloud_text = icloud_text + "\n" + gmail_address
            send_message = icloud_text
          else:
            user_name = driver.find_elements(By.CLASS_NAME, value="w60")
            user_name = user_name[0].text
            print(user_name)
            for user_address in email_list:
              site = "イククル"
              try:
                func.send_conditional(user_name, user_address, gmail_address, gmail_pass, condition_message, site)
                print("アドレス内1stメールを送信しました")
                time.sleep(2)
                driver.get("https://sp.194964.com/mail/inbox/show_mailbox.html")
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(1)
                users_list = driver.find_elements(By.CLASS_NAME, value="bgMiddle")

              except Exception:
                print(f"{user_name} アドレス内1stメールの送信に失敗しました")
                time.sleep(2)
                driver.get("https://sp.194964.com/mail/inbox/show_mailbox.html")
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(1)
                users_list = driver.find_elements(By.CLASS_NAME, value="bgMiddle")
          continue
        elif len(chara_send) == 2: #通知
          print('やり取り中')
          user_name = driver.find_elements(By.CLASS_NAME, value="w60")
          user_name = user_name[0].text
          print(user_name)
          return_message = f"{user_name}イククル,{login_address}:{login_password}\n{user_name}「{received_mail}」"
          return_list.append(return_message) 
        elif len(chara_send) == 0: #fst
          send_message = fst_message
          print("fst")
        elif len(chara_send) == 1: #second
          print("second")
          send_message = second_message
        text_area = driver.find_elements(By.NAME, value="body")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area[0])
        text_area[0].send_keys(send_message)
        time.sleep(1)
        send_button = driver.find_elements(By.ID, value="sendButton")
        send_button[0].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        submit_button = driver.find_elements(By.ID, value="submitBtn")
        submit_button[0].click()
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        popup_text = driver.find_elements(By.CLASS_NAME, value="popupText")
        popup_text_cnt = 0
        while not len(popup_text):
          time.sleep(2)
          popup_text = driver.find_elements(By.CLASS_NAME, value="popupText")
          popup_text_cnt += 1
          if popup_text_cnt == 3:
            break
        check_sent_text_1 = "お相手がメッセージを送信されてから3日間以上経過している為、送信ポイントは付きません"
        check_sent_text_2 = "お返事のない方へ2通以上続けて送信した場合は送信ポイントはつきません"
        print(popup_text[-1].text)
        if "メッセージを送信しました" in popup_text[-1].text or check_sent_text_1 in popup_text[-1].text or check_sent_text_2 in popup_text[-1].text:
          print("メッセージを送信しました")
          time.sleep(2)
          driver.get("https://sp.194964.com/mail/inbox/show_mailbox.html")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
        else:
          print("メッセージ送信に失敗しました")
          time.sleep(2)
          driver.get("https://sp.194964.com/mail/inbox/show_mailbox.html")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
        users_list = driver.find_elements(By.CLASS_NAME, value="bgMiddle")
        
  if len(return_list):
    return return_list
  else:
    return 0
        
        
        


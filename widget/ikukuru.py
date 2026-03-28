import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import random
from selenium.common.exceptions import ElementNotInteractableException
import re
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from widget import func

# 検索フィルターのフォーム name 属性マッピング（Select要素のみ）
# age_from/age_to の値は visible text: "18-19歳","20代前半","20代後半","30代前半","30代後半" 等
# area（地域）は別ボタン経由のため自動設定不可 → ブラウザ側で設定しておく
FILTER_SELECT_MAP = {
  "age_from":    "ageFrom",    # 年齢（下限）
  "age_to":      "ageTo",      # 年齢（上限）
  "height_from": "heightFrom", # 身長（下限）
  "height_to":   "heightTo",   # 身長（上限）
  "income":      "income",     # 年収
  "child":       "child",      # 子供
}

def _apply_filters(driver, filters):
  """検索フォームにフィルターを適用する"""
  for key, value in filters.items():
    name_attr = FILTER_SELECT_MAP.get(key)
    if not name_attr:
      continue
    try:
      if isinstance(value, list):
        # チェックボックス / 複数選択
        for v in value:
          checkboxes = driver.find_elements(By.CSS_SELECTOR, f"input[name='{name_attr}']")
          for cb in checkboxes:
            if cb.get_attribute("value") == v:
              if not cb.is_selected():
                driver.execute_script("arguments[0].click();", cb)
      else:
        sel_elem = driver.find_element(By.NAME, name_attr)
        sel = Select(sel_elem)
        sel.select_by_visible_text(str(value))
    except Exception as e:
      print(f"フィルター設定スキップ [{key}={value}]: {e}")

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

def set_search_filter(driver, wait, filters=None):
  wait_time = random.uniform(2, 3)
  driver.get("https://pc.194964.com/profile/profilesearch/show_profile_search.html")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  if filters:
    _apply_filters(driver, filters)
  # 検索ボタン（class: input_search）
  search_btns = driver.find_elements(By.CLASS_NAME, value="input_search")
  if not search_btns:
    print("検索ボタンが見つかりません")
    return
  driver.execute_script("arguments[0].click();", search_btns[0])
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)

def send_fst_message(driver, wait, fst_message, name, send_cnt):
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
      _input_text(driver, send_textarea[0], fst_message)
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
  check_first = 0
  check_second = 0
  gmail_condition = 0
  login_address = ikukuru_data["login_mail_address"]
  login_password = ikukuru_data["password"]
  fst_message = ikukuru_data["fst_message"]
  second_message = ikukuru_data["second_message"]
  gmail_address = ikukuru_data["gmail_address"]
  gmail_pass = ikukuru_data["gmail_password"]
  condition_message = ikukuru_data["condition_message"]

  wait_time = random.uniform(2, 3)
  driver.get("https://pc.194964.com/mail/inbox/show_mailbox.html")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  # ユーザーやりとりリスト
  users_list = driver.find_elements(By.CLASS_NAME, value="bgMiddle")
  has_new = any(u.find_elements(By.CLASS_NAME, value="icon-new-box") for u in users_list)
  if not has_new:
    print('新着なし')
    return check_first, check_second, gmail_condition, return_list
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
                gmail_condition += 1
                time.sleep(2)
                driver.get("https://pc.194964.com/mail/inbox/show_mailbox.html")
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(1)
                users_list = driver.find_elements(By.CLASS_NAME, value="bgMiddle")
              except Exception:
                print(f"{user_name} アドレス内1stメールの送信に失敗しました")
                time.sleep(2)
                driver.get("https://pc.194964.com/mail/inbox/show_mailbox.html")
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
        _input_text(driver, text_area[0], send_message)
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
          if len(chara_send) == 0:
            check_first += 1
          elif len(chara_send) == 1:
            check_second += 1
          time.sleep(2)
          driver.get("https://pc.194964.com/mail/inbox/show_mailbox.html")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
        else:
          print("メッセージ送信に失敗しました")
          time.sleep(2)
          driver.get("https://pc.194964.com/mail/inbox/show_mailbox.html")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
          time.sleep(1)
        users_list = driver.find_elements(By.CLASS_NAME, value="bgMiddle")

  return check_first, check_second, gmail_condition, return_list

def _input_text(driver, element, text):
  """絵文字などBMP外文字を含むテキストをJavaScript経由で入力する"""
  driver.execute_script(
    "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles:true}));",
    element, text
  )

def _collect_profile_links(driver, wait, list_url, max_next=3):
  """足跡・タイプリストページからプロフィール/遷移URLを収集して返す"""
  driver.get(list_url)
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(random.uniform(2, 3))
  hrefs = []
  next_cnt = 0
  while True:
    links = driver.find_elements(By.CLASS_NAME, value="type-list-link")
    for link in links:
      href = link.get_attribute("href")
      if href and href not in hrefs:
        hrefs.append(href)
    # 次のページへ
    next_btn = driver.find_elements(By.CLASS_NAME, value="nextBtn")
    if not next_btn or "gray555" in (next_btn[0].get_attribute("class") or "") or next_cnt >= max_next:
      break
    driver.execute_script("arguments[0].click();", next_btn[0])
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    next_cnt += 1
  return hrefs

def _send_message_on_profile(driver, wait, message, name, label):
  """プロフページからfooter-btn-sendmail経由でメッセージ履歴ページへ遷移し送信。成功したらTrue"""
  wait_time = random.uniform(2, 3)
  # footer-btn-sendmail のhref = 会話履歴ページURL
  send_mail_btn = driver.find_elements(By.CLASS_NAME, value="footer-btn-sendmail")
  if not send_mail_btn:
    print(f"イククル:{name} {label} footer-btn-sendmailが見つかりません")
    return False
  history_url = send_mail_btn[0].get_attribute("href")
  if not history_url:
    return False
  driver.get(history_url)
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  # 既送信チェック（bubble_owner が存在 = すでにメッセージ送信済み）
  already_sent = driver.find_elements(By.CLASS_NAME, value="bubble_owner")
  if already_sent:
    print(f"イククル:{name} {label} 履歴あり スキップ")
    return False
  # メッセージ送信（check_mailと同じ仕組み）
  text_area = driver.find_elements(By.NAME, value="body")
  if not text_area:
    print(f"イククル:{name} {label} bodyテキストエリアが見つかりません")
    return False
  driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", text_area[0])
  _input_text(driver, text_area[0], message)
  time.sleep(1)
  send_button = driver.find_elements(By.ID, value="sendButton")
  if not send_button:
    return False
  send_button[0].click()
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(1)
  submit_button = driver.find_elements(By.ID, value="submitBtn")
  if submit_button:
    submit_button[0].click()
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1)
  popup_text = driver.find_elements(By.CLASS_NAME, value="popupText")
  wait_cnt = 0
  while not popup_text and wait_cnt < 3:
    time.sleep(2)
    popup_text = driver.find_elements(By.CLASS_NAME, value="popupText")
    wait_cnt += 1
  if popup_text:
    print(f"イククル:{name} {label} {popup_text[-1].text[:40]}")
  return True

def return_foot(driver, wait, return_foot_message, name, send_cnt=1):
  """足跡リストのユーザーにreturn_foot_messageを送る"""
  FOOT_LIST_URL = "https://pc.194964.com/sns/snsashiato/show.html"
  rf_cnt = 0
  hrefs = _collect_profile_links(driver, wait, FOOT_LIST_URL)
  print(f"イククル:{name} 足跡リスト {len(hrefs)}件")
  for href in hrefs:
    if rf_cnt >= send_cnt:
      break
    try:
      driver.get(href)
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(random.uniform(1.5, 2.5))
      sent = _send_message_on_profile(driver, wait, return_foot_message, name, "足跡返し")
      if sent:
        rf_cnt += 1
        print(f"イククル:{name} 足跡返しメッセージ送信 {rf_cnt}件")
    except Exception as e:
      print(f"イククル:{name} 足跡返しエラー: {e}")
  return rf_cnt

def return_type(driver, wait, fst_message, name, send_cnt=1):
  """タイプリストのユーザーにタイプを返してfst_messageを送る"""
  TYPE_LIST_URL = "https://pc.194964.com/sns/snstype/show_typed_list.html"
  rt_cnt = 0
  hrefs = _collect_profile_links(driver, wait, TYPE_LIST_URL)
  print(f"イククル:{name} タイプリスト {len(hrefs)}件")
  for href in hrefs:
    if rt_cnt >= send_cnt:
      break
    try:
      driver.get(href)
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(random.uniform(1.5, 2.5))
      # PC版: send-like-message + submitLikeMessageBtn でタイプ返し+fst同時送信
      like_textarea = driver.find_elements(By.ID, value="send-like-message")
      like_btn = driver.find_elements(By.ID, value="submitLikeMessageBtn")
      if like_textarea and like_btn:
        try:
          _input_text(driver, like_textarea[0], fst_message)
          time.sleep(1)
          driver.execute_script("arguments[0].click();", like_btn[0])
          wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
          rt_cnt += 1
          print(f"イククル:{name} タイプ返し+fst送信 {rt_cnt}件")
        except Exception as e:
          print(f"イククル:{name} タイプ返し操作エラー: {e}")
          rt_cnt += 1
      else:
        # フォールバック: footer-btn-sendmail 経由でメッセージ送信
        sent = _send_message_on_profile(driver, wait, fst_message, name, "タイプ返しfst")
        if sent:
          rt_cnt += 1
          print(f"イククル:{name} タイプ返し+fst送信(履歴経由) {rt_cnt}件")
    except Exception as e:
      print(f"イククル:{name} タイプ返しエラー: {e}")
  return rt_cnt

def make_footprint(driver, wait, name, footprint_count, filters=None):
  """詳細フィルターでプロフ検索してfootprint_count件の足跡をつける"""
  set_search_filter(driver, wait, filters)
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(random.uniform(2, 3))
  visited = 0
  current_step = 0
  prev_count = 0
  while visited < footprint_count:
    prof_links = driver.find_elements(By.CLASS_NAME, value="profLookBtn")
    if current_step >= len(prof_links):
      driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(3)
      prof_links = driver.find_elements(By.CLASS_NAME, value="profLookBtn")
      if len(prof_links) == prev_count:
        print(f"イククル:{name} 足跡付け終了（追加ユーザーなし） {visited}件")
        break
      prev_count = len(prof_links)
      continue
    href = prof_links[current_step].get_attribute("href")
    current_step += 1
    if not href:
      continue
    try:
      driver.get(href)
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(random.uniform(0.8, 2.0))
      visited += 1
      now_str = datetime.now().strftime('%m/%d %H:%M:%S')
      print(f"イククル:{name} 足跡付け {visited}件 {now_str}")
      driver.back()
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(random.uniform(0.5, 1.5))
    except Exception as e:
      print(f"イククル:{name} 足跡付けエラー: {e}")
  return visited

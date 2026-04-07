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

# area（地域）は別ボタン経由のため自動設定不可 → ブラウザ側で設定しておく
# 全キャラ共通の固定検索フィルター
# 全キャラ共通の固定フィルター（ランダム項目は除く）
FIXED_SEARCH_FILTER = {
  "age_from": "18-19歳",        # 年齢下限（固定）
  "child":    "いない",          # 子供なし（固定）
  "married":  ["1", "5", "6"], # 独身 / 彼氏募集中 / 恋愛相談（固定）
}

# ランダム選択肢
_AGE_TO_CHOICES    = ["20代後半", "30代前半"]
_HEIGHT_TO_CHOICES = ["165～169", "170～174"]
_INCOME_CHOICES    = ["100万円以下", "100～300万円", "指定なし"]
_AREA_POOL = {   # 東京は必須、残り2つをここからランダム選択
  "東京都":  "21-10021",
  "栃木県":  "18-10018",
  "静岡県":  "23-10023",
  "千葉県":  "20-10020",
  "神奈川県": "15-10015",
  "埼玉県":  "16-10016",
}

FILTER_SELECT_MAP = {
  "age_from":    "ageFrom",
  "age_to":      "ageTo",
  "height_from": "heightFrom",
  "height_to":   "heightTo",
  "income":      "income",
  "child":       "child",
  "married":     "married[]",
}

def _set_area_filter(driver, wait, area_values):
  """地域フィルターを設定する。area_values = prefAndCity[]のvalue文字列リスト（東京を先頭に）"""
  PREF_NAMES = {v: k for k, v in _AREA_POOL.items()}

  # 地域変更ボタンをクリック → show_selected_area.html
  area_btn = driver.find_element(By.CSS_SELECTOR, "input[value*='地域']")
  area_btn.click()
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(1.5)

  # 既存の選択を全削除
  existing = driver.find_elements(By.CSS_SELECTOR, "input[name='prefAndCity[]']")
  if existing:
    for cb in existing:
      if not cb.is_selected():
        driver.execute_script("arguments[0].click();", cb)
    del_btn = driver.find_element(By.XPATH, "//*[contains(text(),'チェックを削除')]")
    del_btn.click()
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1.5)
    # 削除後は show_profile_search.html にリダイレクトされるため再度クリック
    area_btn = driver.find_element(By.CSS_SELECTOR, "input[value*='地域']")
    area_btn.click()
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1.5)

  # 1件ずつ地域を追加（追加後は show_profile_search.html に戻る）
  for i, area_val in enumerate(area_values):
    if i > 0:
      # 前の追加後は show_profile_search.html に戻るため再度クリック
      area_btn = driver.find_element(By.CSS_SELECTOR, "input[value*='地域']")
      area_btn.click()
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(1.5)
    add_btn = driver.find_element(By.XPATH, "//button[contains(text(),'地域を追加する')]")
    add_btn.click()
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1.5)
    pref_name = PREF_NAMES[area_val]
    pref_link = driver.find_element(By.XPATH, f"//a[.//p[text()='{pref_name}']]")
    pref_link.click()
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1.5)
    cb = driver.find_element(By.CSS_SELECTOR, f"input[value='{area_val}']")
    driver.execute_script("arguments[0].click();", cb)
    time.sleep(0.5)
    select_btn = driver.find_element(By.CSS_SELECTOR, "button.greenButton")
    driver.execute_script("arguments[0].click();", select_btn)
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(1.5)
    # 各 選択する 後は show_profile_search.html に戻る
  random_area_names = [PREF_NAMES[v] for v in area_values]
  print(f"地域設定: {', '.join(random_area_names)}")

def _apply_filters(driver, filters):
  """検索フォームにフィルターを適用する"""
  for key, value in filters.items():
    name_attr = FILTER_SELECT_MAP.get(key)
    if not name_attr:
      continue
    try:
      if isinstance(value, list):
        # チェックボックス（married[] など）
        checkboxes = driver.find_elements(By.CSS_SELECTOR, f"input[name='{name_attr}']")
        for cb in checkboxes:
          should_check = cb.get_attribute("value") in value
          if should_check and not cb.is_selected():
            driver.execute_script("arguments[0].click();", cb)
          elif not should_check and cb.is_selected():
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

  # 地域フィルター: 東京固定 + ランダム2件
  extra_areas = random.sample([v for k, v in _AREA_POOL.items() if k != "東京都"], 2)
  area_values = [_AREA_POOL["東京都"]] + extra_areas
  _set_area_filter(driver, wait, area_values)

  # ランダムフィルター生成
  random_filters = {
    "age_to":    random.choice(_AGE_TO_CHOICES),
    "height_to": random.choice(_HEIGHT_TO_CHOICES),
    "income":    random.choice(_INCOME_CHOICES),
  }

  # 固定 + ランダム + 追加フィルターをマージして適用
  merged = dict(FIXED_SEARCH_FILTER)
  merged.update(random_filters)
  if filters:
    merged.update(filters)
  print(f"検索フィルター: 年齢上限={merged['age_to']} 身長上限={merged['height_to']} 年収={merged['income']}")
  _apply_filters(driver, merged)
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
        if submit_button:
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
  """足跡・タイプリストページからプロフィール/遷移URLとユーザー名を収集して返す"""
  driver.get(list_url)
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(random.uniform(2, 3))
  items = []  # (href, username) のリスト
  seen_hrefs = set()
  next_cnt = 0
  while True:
    links = driver.find_elements(By.CLASS_NAME, value="type-list-link")
    for link in links:
      href = link.get_attribute("href")
      if href and href not in seen_hrefs:
        seen_hrefs.add(href)
        name_els = link.find_elements(By.CLASS_NAME, value="type-list-name")
        username = name_els[0].text.strip() if name_els else ""
        # リストアイテムのテキストから年齢を抽出（例: "22歳"）
        link_text = link.text
        age_match = re.search(r'(\d+)歳', link_text)
        age = int(age_match.group(1)) if age_match else None
        items.append((href, username, age))
    # 次のページへ
    next_btn = driver.find_elements(By.CLASS_NAME, value="nextBtn")
    if not next_btn or "gray555" in (next_btn[0].get_attribute("class") or "") or next_cnt >= max_next:
      break
    driver.execute_script("arguments[0].click();", next_btn[0])
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    next_cnt += 1
  return items

def _send_message_on_profile(driver, wait, message, name, label, opponent_name=""):
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
  # 相手の名前を履歴ページから取得（リスト側で取れなかった場合のフォールバック）
  if not opponent_name:
    w60_els = driver.find_elements(By.CLASS_NAME, value="w60")
    if w60_els:
      opponent_name = w60_els[0].text.strip()
  # {name} プレースホルダーを相手の名前に置換
  if opponent_name:
    message = message.replace("{name}", opponent_name)
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
  items = _collect_profile_links(driver, wait, FOOT_LIST_URL)
  print(f"イククル:{name} 足跡リスト {len(items)}件")
  for href, opponent_name, age in items:
    if rf_cnt >= send_cnt:
      break
    if age is not None and age > 34:
      print(f"イククル:{name} 足跡返し スキップ（{opponent_name} {age}歳 > 34歳）")
      continue
    try:
      driver.get(href)
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(random.uniform(1.5, 2.5))
      msg = return_foot_message.replace("{name}", opponent_name) if opponent_name else return_foot_message
      sent = _send_message_on_profile(driver, wait, msg, name, "足跡返し", opponent_name)
      if sent:
        rf_cnt += 1
        print(f"イククル:{name} 足跡返しメッセージ送信 {rf_cnt}件")
    except Exception as e:
      print(f"イククル:{name} 足跡返しエラー: {e}")
  return rf_cnt

def return_type(driver, wait, fst_message, name, send_cnt=1):
  """タイプリスト(35歳以下)にタイプを返し、両思いリストにfst_messageを送る"""
  TYPE_LIST_URL   = "https://pc.194964.com/sns/snstype/show_typed_list.html"
  MUTUAL_LIST_URL = "https://pc.194964.com/sns/snstype/show_mutual_list.html"
  type_cnt = 0

  # --- Step1: タイプリスト → 35歳以下にタイプを返す ---
  items = _collect_profile_links(driver, wait, TYPE_LIST_URL)
  print(f"イククル:{name} タイプリスト {len(items)}件")
  for href, opponent_name, age in items:
    if age is not None and age < 55:
      print(f"イククル:{name} タイプ返しスキップ（{opponent_name} {age}歳）")
      continue
    try:
      driver.get(href)
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(random.uniform(1.5, 2.5))
      # タイプ返しボタンをクリック（メッセージなし）
      like_btn = driver.find_elements(By.ID, value="submitLikeMessageBtn")
      if like_btn:
        driver.execute_script("arguments[0].click();", like_btn[0])
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
        type_cnt += 1
        print(f"イククル:{name} タイプ返し {type_cnt}件（{opponent_name} {age}歳）")
      else:
        print(f"イククル:{name} タイプ返しボタンなし（{opponent_name}）")
    except Exception as e:
      print(f"イククル:{name} タイプ返しエラー: {e}")
    if type_cnt == 1:
      break

  # --- Step2: 両思いリスト → fst_messageを送る ---
  mutual_items = _collect_profile_links(driver, wait, MUTUAL_LIST_URL)
  print(f"イククル:{name} 両思いリスト {len(mutual_items)}件")
  fst_cnt = 0
  for href, opponent_name, age in mutual_items:
    if fst_cnt >= send_cnt:
      break
    try:
      driver.get(href)
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(random.uniform(1.5, 2.5))
      msg = fst_message.replace("{name}", opponent_name) if opponent_name else fst_message
      sent = _send_message_on_profile(driver, wait, msg, name, "両思いfst", opponent_name)
      if sent:
        fst_cnt += 1
        print(f"イククル:{name} 両思いfst送信 {fst_cnt}件（{opponent_name}）")
    except Exception as e:
      print(f"イククル:{name} 両思いfstエラー: {e}")

  return type_cnt

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


def profile_edit(chara_data, driver, wait):
  """イククルのプロフィールを編集する"""
  import re
  name = chara_data['name']

  def _val(key):
    v = chara_data.get(key)
    return None if (v is None or str(v).strip() in ('None', '')) else str(v).strip()

  # 地域確認・東京以外なら引越し
  detail_area = _val('detail_activity_area')
  try:
    driver.get('https://pc.194964.com/mypage.html')
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    age_el = driver.find_element(By.CLASS_NAME, 'profile-age')
    area_text = age_el.text.strip()
    print(f'  現在の地域: {area_text}')
    if '東京' not in area_text:
      print(f'  東京以外のため引越し処理を実行')
      driver.get('https://pc.194964.com/other/area/show_pref_setting_list.html')
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(2)
      driver.find_element(By.LINK_TEXT, '東京都').click()
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(2)
      city_links = [l for l in driver.find_elements(By.TAG_NAME, 'a')
                    if 'show_complete_move_pref_and_city' in (l.get_attribute('href') or '')]
      # detail_activity_areaと一致する市区町村を探す、なければ先頭
      target = None
      if detail_area:
        target = next((l for l in city_links if l.text.strip() == detail_area), None)
      if target is None:
        target = city_links[0] if city_links else None
      if target:
        city_name = target.text.strip()
        target.click()
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
        print(f'  引越し完了: {city_name}')
      else:
        print('  市区町村リンクが見つかりません')
    else:
      print('  地域は東京のためスキップ')
  except Exception as e:
    print(f'  地域確認・引越しエラー: {e}')

  def set_select(sel_name, value):
    if value is None:
      return
    try:
      el = driver.find_element(By.NAME, sel_name)
      Select(el).select_by_visible_text(value)
      print(f'  {sel_name} = {value} ✓')
    except Exception as e:
      print(f'  {sel_name} = {value} ✗ ({e})')

  # 1. ニックネーム・年齢設定
  from datetime import datetime
  chara_name_val = _val('name') or name
  age_val = _val('age')
  driver.get('https://pc.194964.com/config/settingprof/show_profile_setting.html')
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(3)
  try:
    name_input = driver.find_element(By.CSS_SELECTOR, 'input[name="name"]')
    name_input.clear()
    name_input.send_keys(chara_name_val)
    print(f'  name = {chara_name_val} ✓')
  except Exception as e:
    print(f'  name 設定エラー: {e}')
  if age_val:
    try:
      birth_year = datetime.now().year - int(age_val)
      birth_date_str = f'{birth_year}-01'
      select_date_str = f'{birth_year}年01月'
      driver.execute_script("""
        var sd = document.querySelector('input[name="selectdate"]');
        var bd = document.querySelector('input[name="birthDate"]');
        if (sd) sd.value = arguments[0];
        if (bd) bd.value = arguments[1];
      """, select_date_str, birth_date_str)
      print(f'  age = {age_val} → birthDate = {birth_date_str} ✓')
    except Exception as e:
      print(f'  age 設定エラー: {e}')
  set_select('height',  _val('height'))
  set_select('style',   _val('body_shape'))
  set_select('blood',   _val('blood_type'))
  set_select('looks',   _val('_type'))
  # relationship_status の値をページ選択肢に合わせてマッピング
  _married_map = {'独身': '未婚'}
  _married_val = _val('relationship_status')
  if _married_val:
    _married_val = _married_map.get(_married_val, _married_val)
  set_select('married', _married_val)
  set_select('city',    _val('detail_activity_area'))
  try:
    btn = driver.find_element(By.CSS_SELECTOR, 'button.greenButton')
    btn.click()
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    print(f'  ニックネーム・年齢更新完了')
  except Exception as e:
    print(f'  更新ボタンエラー: {e}')

  # 2. プロフィール編集（基本情報）
  driver.get('https://pc.194964.com/sns/snssetting/show_edit_profile.html')
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(3)

  set_select('occupation',   _val('job'))
  set_select('income',       _val('annual_income'))
  set_select('cigarette',    _val('tobacco'))
  set_select('alcohol',      _val('alcohol'))
  set_select('child',        _val('children'))
  set_select('constellation', _val('constellation'))
  set_select('freeTime',     _val('free_time'))
  set_select('fStyle',       _val('favorite_body_shape'))
  set_select('cup',          _val('cup'))

  try:
    btn = driver.find_element(By.CSS_SELECTOR, 'button.greenButton')
    btn.click()
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    print(f'  プロフィール更新完了: {driver.current_url}')
  except Exception as e:
    print(f'  更新ボタンエラー: {e}')

  # 2. 自己紹介編集
  intro = _val('self_promotion')
  if intro:
    driver.get('https://pc.194964.com/sns/snssetting/show_edit_profile_intro.html')
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
    time.sleep(3)
    try:
      ta = driver.find_element(By.NAME, 'introduction')
      ta.clear()
      ta.send_keys(intro)
      btn = driver.find_element(By.CSS_SELECTOR, 'button.greenButton')
      btn.click()
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(2)
      print(f'  自己紹介更新完了: {driver.current_url}')
    except Exception as e:
      print(f'  自己紹介更新エラー: {e}')

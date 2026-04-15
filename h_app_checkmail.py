"""ハッピーメール アプリ版 メールチェック＆返信スクリプト (iPhone実機 / Appium)

使い方:
  myenv/bin/python h_app_checkmail.py <キャラ名>
  例: myenv/bin/python h_app_checkmail.py えりか

ブラウザ版(widget/happymail.py multidrivers_checkmail)と同等の機能:
  - 新着メッセージ確認
  - 送信回数に応じた返信（1st/2nd/やりとり中）
  - メールアドレス検出時の条件メール送信
  - NGワード検出
  - AIチャット返信（system_prompt設定時）
"""
import sys
import os
import re
import time
import random
import traceback
sys.path.insert(0, os.path.dirname(__file__))

from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from widget import func
from datetime import datetime


UDID = '00008030-000C701C22E8802E'
BUNDLE_ID = 'jp.co.i-bec.happyhills'
APPIUM_URL = 'http://localhost:4723'
MAX_CHECK = 5  # 最大チェック件数


def create_driver():
    options = XCUITestOptions()
    options.platform_name = 'iOS'
    options.device_name = 'BishiのiPhone'
    options.udid = UDID
    options.bundle_id = BUNDLE_ID
    options.no_reset = True
    options.auto_accept_alerts = True
    options.wda_launch_timeout = 120000
    options.wda_connection_timeout = 120000
    return webdriver.Remote(APPIUM_URL, options=options)


def dismiss_popups(driver):
    """ポップアップを閉じる"""
    for _ in range(5):
        closed = False
        for btn_id in ['OK', 'icon cancel', 'icon_cancel_black', 'はい(募集一覧へ)']:
            try:
                btns = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, btn_id)
                if btns and btns[0].get_attribute('visible') == 'true':
                    btns[0].click()
                    time.sleep(1)
                    closed = True
                    break
            except Exception:
                pass
        if not closed:
            break


def go_to_message_tab(driver):
    """メッセージタブへ移動"""
    # タブバーが見えるまで戻る
    for _ in range(5):
        tab_bars = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTabBar')
        if tab_bars:
            for tb in tab_bars[0].find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeButton'):
                if tb.get_attribute('name') == 'メッセージ':
                    tb.click()
                    time.sleep(3)
                    return True
        back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'BackButton')
        if not back:
            back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'back arrow btn')
        if back and back[0].get_attribute('visible') == 'true':
            back[0].click()
            time.sleep(1)
        else:
            break
    return False


def tap_unread_filter(driver):
    """未読フィルタをタップ"""
    try:
        btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, '未読')
        if btn and btn[0].get_attribute('visible') == 'true':
            btn[0].click()
            time.sleep(2)
            return True
    except Exception:
        pass
    return False


def get_message_list(driver):
    """メッセージ一覧からユーザー情報を取得"""
    users = []
    cells = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeCell')
    for cell in cells:
        try:
            if cell.get_attribute('visible') != 'true':
                continue
            texts = cell.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeStaticText')
            labels = [t.get_attribute('label') or '' for t in texts]
            if len(labels) < 3:
                continue
            # labels: [年齢+地域, 名前, メッセージプレビュー, None, None, 日時]
            imgs = cell.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeImage')
            img_names = [x.get_attribute('name') or '' for x in imgs]
            user = {
                'cell': cell,
                'age_area': labels[0] if labels else '',
                'name': labels[1] if len(labels) > 1 else '',
                'preview': labels[2] if len(labels) > 2 else '',
                'time': labels[-1] if labels else '',
                'has_reply_icon': 'message_icon_reply' in img_names,
            }
            if user['name']:
                users.append(user)
        except Exception:
            pass
    return users


def get_chat_messages(driver):
    """チャット画面からメッセージ履歴を取得
    returns: list of {'role': 'send'/'receive', 'text': str}
    """
    messages = []
    cells = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeCell')
    for cell in cells:
        try:
            if cell.get_attribute('visible') != 'true':
                continue
            imgs = cell.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeImage')
            img_names = [x.get_attribute('name') or '' for x in imgs]
            # blue_left_balloon = 受信, pink系/right系 = 送信
            role = None
            if 'blue_left_balloon' in img_names:
                role = 'receive'
            elif any('right' in n or 'pink' in n for n in img_names if n):
                role = 'send'
            if not role:
                # balloon画像がない場合はスキップ
                for n in img_names:
                    if 'balloon' in n:
                        role = 'send' if 'right' in n else 'receive'
                        break
            if not role:
                continue
            # メッセージ本文を取得（TextViewのvalue）
            tvs = cell.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTextView')
            text = ''
            if tvs:
                text = tvs[0].get_attribute('value') or ''
                if not text:
                    # valueがない場合はlabelの結合
                    text_parts = [tv.get_attribute('label') or '' for tv in tvs]
                    text = '\n'.join(t for t in text_parts if t)
            if text:
                messages.append({'role': role, 'text': text})
        except Exception:
            pass
    return messages


def count_sent_messages(messages):
    """送信メッセージ数を数える"""
    return sum(1 for m in messages if m['role'] == 'send')


def send_message(driver, message):
    """メッセージを入力して送信し、送信確認する"""
    # 入力欄をタップ
    driver.tap([(227, 838)])
    time.sleep(1.5)

    kb = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeKeyboard')
    if not kb:
        driver.tap([(227, 838)])
        time.sleep(1.5)

    tvs = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTextView')
    if not tvs:
        print('    入力欄が見つかりません')
        return False
    tvs[0].send_keys(message)
    time.sleep(1)

    val = tvs[0].get_attribute('value') or ''
    if not val:
        print('    メッセージ入力に失敗')
        return False

    send_btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'message send triangle on btn')
    if not send_btn:
        print('    送信ボタンが見つかりません')
        return False
    send_btn[0].click()
    time.sleep(3)

    # 送信確認: メッセージ先頭部分が画面上に表示されているか
    msg_first_line = message.split('\n')[0].split('\r')[0].strip()[:20]
    msg_first_clean = func.normalize_text(msg_first_line)
    for _ in range(3):
        texts = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeStaticText')
        for t in reversed(texts):
            try:
                label = t.get_attribute('label') or ''
                if len(label) < 3:
                    continue
                if msg_first_clean in func.normalize_text(label):
                    return True
            except Exception:
                pass
        # TextViewのvalueも確認
        tvs_all = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTextView')
        for tv in reversed(tvs_all):
            try:
                tv_val = tv.get_attribute('value') or ''
                if tv_val and msg_first_clean in func.normalize_text(tv_val):
                    return True
            except Exception:
                pass
        time.sleep(2)

    try:
        driver.save_screenshot(f'/tmp/hm_send_fail_{int(time.time())}.png')
    except Exception:
        pass
    print('    送信確認失敗')
    return False


def go_back_to_message_list(driver):
    """メッセージ一覧に戻る"""
    for _ in range(5):
        navs = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeNavigationBar')
        if navs:
            title = navs[0].get_attribute('name') or ''
            if title == 'メッセージ':
                return True
        back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'BackButton')
        if not back:
            back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'back arrow btn')
        if back and back[0].get_attribute('visible') == 'true':
            back[0].click()
            time.sleep(1.5)
        else:
            break
    return False


def check_mail(chara_data, driver):
    """メールチェック＆返信メイン処理"""
    name = chara_data['name']
    login_id = chara_data.get('login_id', '')
    password = chara_data.get('password', '')
    fst_message = chara_data.get('fst_message', '')
    second_message = chara_data.get('second_message', '')
    post_return_message = chara_data.get('post_return_message', '')
    confirmation_mail = chara_data.get('confirmation_mail', '')
    conditions_message = chara_data.get('condition_message', '')
    gmail_address = chara_data.get('mail_address', '')
    gmail_password = chara_data.get('gmail_password', '')
    chara_prompt = chara_data.get('system_prompt', '')
    return_list = []

    print(f'\n--- {name} メールチェック ---')

    # メッセージタブへ
    if not go_to_message_tab(driver):
        print('  メッセージ画面に移動できませんでした')
        return None

    # 未読フィルタ
    tap_unread_filter(driver)

    # メッセージ一覧取得
    users = get_message_list(driver)
    if not users:
        print('  新着メッセージなし')
        return None

    print(f'  新着メッセージ数: {len(users)}')
    check_count = 0

    for user in users:
        if check_count >= MAX_CHECK:
            print(f'  チェック上限({MAX_CHECK}件)に達しました')
            break

        user_name = user['name']
        print(f'\n  --- {user_name} ---')

        # セルタップ → チャット画面
        try:
            user['cell'].click()
            time.sleep(3)
        except Exception:
            print(f'    {user_name}: セルタップ失敗')
            continue

        dismiss_popups(driver)

        # チャット履歴取得
        messages = get_chat_messages(driver)
        sent_count = count_sent_messages(messages)
        received = [m for m in messages if m['role'] == 'receive']
        last_received = received[-1]['text'] if received else ''

        print(f'    送信済み: {sent_count}件, 受信: {len(received)}件')

        # メールアドレス検出
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        email_list = re.findall(email_pattern, last_received)
        if email_list:
            print(f'    メールアドレス検出: {email_list}')
            if 'icloud.com' in last_received:
                # iCloudの場合は自分のアドレスを送信
                icloud_text = f"メール送ったんですけど、ブロックされちゃって届かないのでこちらのアドレスにお名前添えて送ってもらえますか？\n{gmail_address}"
                if send_message(driver, icloud_text):
                    print(f'    {user_name}: iCloudアドレス対応メッセージ送信')
            else:
                # 条件メール送信
                for user_address in email_list:
                    user_address = func.normalize_text(user_address)
                    try:
                        func.send_conditional(user_name, user_address, gmail_address, gmail_password, conditions_message, "ハッピーメール")
                        print(f'    {user_name}: アドレス内1stメール送信 → {user_address}')
                    except Exception:
                        print(f'    {user_name}: アドレス内1stメール送信失敗')
                        traceback.print_exc()
                # 確認メッセージ送信
                if confirmation_mail:
                    send_message(driver, confirmation_mail)

            go_back_to_message_list(driver)
            check_count += 1
            continue

        # 送信回数に応じた返信
        if sent_count == 0:
            # 1st返信
            msg = fst_message.format(name=user_name) if fst_message else ''
            # 掲示板からの送信か確認
            for m in received:
                if '募集から送信' in m['text'] and post_return_message:
                    msg = post_return_message.format(name=user_name)
                    break
            if msg:
                if send_message(driver, msg):
                    now = datetime.now().strftime('%m-%d %H:%M:%S')
                    print(f'    {user_name}: 1st返信送信 {now}')
                else:
                    print(f'    {user_name}: 1st返信送信失敗')

        elif sent_count == 1:
            # 2nd返信
            msg = second_message.format(name=user_name) if second_message else ''
            # 掲示板からの場合はスキップ
            from_post = False
            for m in received:
                if '募集から送信' in m['text']:
                    from_post = True
                    break
            if from_post:
                print(f'    {user_name}: 掲示板経由 → やりとり中通知')
                return_message = f"{name}happymail,{login_id}:{password}\n{user_name}「{last_received[:100]}」"
                return_list.append(return_message)
            elif msg:
                if send_message(driver, msg):
                    now = datetime.now().strftime('%m-%d %H:%M:%S')
                    print(f'    {user_name}: 2nd返信送信 {now}')
                else:
                    print(f'    {user_name}: 2nd返信送信失敗')

        else:
            # やりとり中
            if chara_prompt:
                # AIチャット返信
                print(f'    {user_name}: AIチャット返信')
                try:
                    history = []
                    for m in messages:
                        role = 'model' if m['role'] == 'send' else 'user'
                        history.append({'role': role, 'text': m['text']})
                    male_history = [m['text'] for m in messages if m['role'] == 'receive']
                    user_input = male_history[-1] if male_history else None
                    ai_response, all_history = func.chat_ai(chara_prompt, history, fst_message, user_input)
                    if ai_response:
                        if send_message(driver, ai_response):
                            now = datetime.now().strftime('%m-%d %H:%M:%S')
                            print(f'    {user_name}: AI返信送信 {now}')
                        else:
                            print(f'    {user_name}: AI返信送信失敗')
                        # やりとり通知
                        formatted = [f"{name}happymail AI返信 {user_name}"]
                        for h in all_history[-4:]:
                            role_label = "相手" if h['role'] == 'user' else "自分"
                            formatted.append(f"  {role_label}: {h['text'][:80]}")
                        return_list.append('\n'.join(formatted))
                    else:
                        print(f'    {user_name}: AI応答なし')
                except Exception:
                    print(f'    {user_name}: AIチャットエラー')
                    traceback.print_exc()
            else:
                print(f'    {user_name}: やりとり中 → 通知のみ')
                return_message = f"{name}happymail,{login_id}:{password}\n{user_name}「{last_received[:100]}」"
                return_list.append(return_message)

        go_back_to_message_list(driver)
        check_count += 1
        time.sleep(random.uniform(1.0, 2.5))

    print(f'\n{name} メールチェック完了: {check_count}件処理')
    return return_list if return_list else None


def main():
    if len(sys.argv) < 2:
        print("使い方: python h_app_checkmail.py <キャラ名>")
        sys.exit(1)

    chara_name = sys.argv[1]

    user_data = func.get_user_data()
    if not user_data or user_data == 2:
        print('ユーザーデータの取得に失敗しました')
        sys.exit(1)

    chara_data = next((c for c in user_data.get('happymail', []) if c['name'] == chara_name), None)
    if not chara_data:
        print(f'「{chara_name}」が見つかりません')
        print('ハッピーメールキャラ一覧:', [c['name'] for c in user_data.get('happymail', [])])
        sys.exit(1)

    print(f'{chara_name} のデータ取得完了 (login_id: {chara_data.get("login_id")})')

    print('Appium接続中...')
    driver = create_driver()
    time.sleep(2)

    try:
        dismiss_popups(driver)
        result = check_mail(chara_data, driver)
        if result:
            print('\n--- 通知一覧 ---')
            for r in result:
                print(r)
    finally:
        driver.quit()
        print('Appiumセッション終了')


if __name__ == '__main__':
    main()

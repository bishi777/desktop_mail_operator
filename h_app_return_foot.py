"""ハッピーメール アプリ版 足跡返しスクリプト (iPhone実機 / Appium)

使い方:
  myenv/bin/python h_app_return_foot.py <キャラ名>
  例: myenv/bin/python h_app_return_foot.py えりか

ブラウザ版(widget/happymail.py return_footpoint)と同等の機能:
  - 足あとリストを巡回
  - 送信済み(メール履歴あり)はスキップ
  - 年齢が20代/18-19以外はスキップ
  - 自己紹介にNGワードがあればスキップ
  - 条件OKならメッセージ送信
"""
import sys
import os
import time
import random
import re
sys.path.insert(0, os.path.dirname(__file__))

from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from widget import func
from datetime import datetime


UDID = '00008030-000C701C22E8802E'
BUNDLE_ID = 'jp.co.i-bec.happyhills'
APPIUM_URL = 'http://localhost:4723'
NGWORDS = ["通報", "業者", "金銭", "条件"]
MAX_RETURN_FOOT = 3  # 1回の足跡返し上限
MAX_SKIP = 20  # 連続スキップ上限


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


def go_to_mypage(driver):
    """タブバーからマイページへ"""
    for _ in range(5):
        tab_bars = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTabBar')
        if tab_bars:
            for tb in tab_bars[0].find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeButton'):
                if tb.get_attribute('name') == 'マイページ':
                    tb.click()
                    time.sleep(2)
                    return True
        # タブバーが見えない → 戻る
        for back_id in ['BackButton', 'back arrow btn']:
            try:
                back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, back_id)
                if back and back[0].get_attribute('visible') == 'true':
                    back[0].click()
                    time.sleep(1)
                    break
            except Exception:
                pass
    return False


def go_to_footprints(driver):
    """マイページから足あと画面へ"""
    cells = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeCell')
    for c in cells:
        try:
            imgs = c.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeImage')
            for img in imgs:
                if img.get_attribute('name') == 'mypage_footprints_btn':
                    c.click()
                    time.sleep(3)
                    return True
        except Exception:
            pass
    return False


def get_footprint_users(driver):
    """足あとリストからユーザー情報を取得"""
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
            # labels構造: ['プロフィールより', '自己紹介...', '名前', '職業:... 身長:...', '日時', '年齢  地域']
            user = {
                'cell': cell,
                'labels': labels,
                'name': '',
                'age_text': '',
            }
            # 名前と年齢を探す
            for label in labels:
                if re.match(r'^\d{2}代', label) or '18~19' in label:
                    user['age_text'] = label
                elif label not in ['プロフィールより', ''] and not label.startswith('職業') and not label.startswith('身長') and not re.match(r'\d{2}/\d{2}', label) and len(label) < 20:
                    if not user['name']:
                        user['name'] = label
            if user['name']:
                users.append(user)
        except Exception:
            pass
    return users


def is_valid_age(age_text):
    """年齢が20代または18-19か"""
    return '20代' in age_text or '18~19' in age_text


def check_profile_ngwords(driver):
    """プロフィール画面の自己紹介にNGワードがあるか"""
    texts = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeStaticText')
    for t in texts:
        try:
            label = (t.get_attribute('label') or '').replace(' ', '').replace('\n', '')
            if any(ng in label for ng in NGWORDS):
                return True
        except Exception:
            pass
    return False


def has_mail_history(driver):
    """メッセージ送信画面でメール履歴があるか確認
    送信画面にメッセージ履歴があればTrueを返す"""
    # メッセージ送信画面に遷移した時点で、既にメッセージ履歴がある場合は
    # チャット画面(メッセージ一覧)が表示される
    # 初回の場合は「初回メッセージ定型文」画面が出るか、プロフ+入力欄が表示される
    # 既にやりとりがある場合は過去メッセージが表示されるはず

    # 「初回メッセージ定型文の利用はこちら」が見えたら初回=履歴なし
    texts = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeStaticText')
    for t in texts:
        try:
            label = t.get_attribute('label') or ''
            if '初回メッセージ定型文' in label:
                return False
        except Exception:
            pass

    # NavBarが「初回メッセージ定型文」なら初回画面が出ている→戻る
    navs = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeNavigationBar')
    for n in navs:
        try:
            title = n.get_attribute('name') or ''
            if '定型文' in title:
                back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, '戻る')
                if not back:
                    back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'BackButton')
                if back:
                    back[0].click()
                    time.sleep(1)
                return False
        except Exception:
            pass

    # message__block系の既読メッセージが見えたら履歴あり
    # アプリではStaticTextに過去メッセージが表示される
    # → 送信ボタンがあって入力欄がある画面 = メッセージ画面
    # 簡易判定: 「お相手の自己紹介」テキストがあれば初回メッセージ画面=履歴なし
    for t in texts:
        try:
            label = t.get_attribute('label') or ''
            if 'お相手の自己紹介' in label or '興味あることに触れて' in label:
                return False
        except Exception:
            pass

    return True


def send_message(driver, message):
    """メッセージを入力して送信"""
    # 入力欄をタップ (座標: TextViewのrect x=78, y=822, w=298, h=32)
    driver.tap([(227, 838)])
    time.sleep(1.5)

    # キーボードが出ているか確認
    kb = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeKeyboard')
    if not kb:
        # リトライ
        driver.tap([(227, 838)])
        time.sleep(1.5)

    # TextViewに入力
    tvs = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTextView')
    if not tvs:
        print('    入力欄が見つかりません')
        return False
    tvs[0].send_keys(message)
    time.sleep(1)

    # 入力確認
    val = tvs[0].get_attribute('value') or ''
    if not val:
        print('    メッセージ入力に失敗')
        return False

    # 送信ボタンをタップ
    send_btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'message send triangle on btn')
    if not send_btn:
        print('    送信ボタンが見つかりません')
        return False
    send_btn[0].click()
    time.sleep(3)

    # 送信確認: メッセージ先頭部分が画面上に表示されているか
    # 長文メッセージは複数行に分割されるため、先頭の一部で部分一致
    msg_first_line = message.split('\n')[0].split('\r')[0].strip()[:20]
    msg_first_clean = func.normalize_text(msg_first_line)
    for retry in range(3):
        texts = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeStaticText')
        for t in reversed(texts):
            try:
                label = t.get_attribute('label') or ''
                if not label or len(label) < 5:
                    continue
                label_clean = func.normalize_text(label)
                if msg_first_clean and msg_first_clean in label_clean:
                    return True
            except Exception:
                pass
        time.sleep(2)

    # スクリーンショットで確認用に保存
    try:
        driver.save_screenshot(f'/tmp/hm_send_fail_{int(time.time())}.png')
    except Exception:
        pass
    print('    送信確認失敗: 画面上にメッセージが見つかりません')
    return False


def go_back_to_footprints(driver):
    """足あと画面まで戻る"""
    for _ in range(5):
        navs = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeNavigationBar')
        if navs:
            title = navs[0].get_attribute('name') or ''
            if title == '足あと':
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


def return_footprint(chara_data, driver):
    """足跡返しメイン処理"""
    name = chara_data['name']
    return_foot_message = chara_data.get('return_foot_message', '')
    if not return_foot_message:
        print(f'  {name}: return_foot_messageが未設定')
        return 0

    print(f'\n--- {name} 足跡返し ---')

    # マイページ → 足あと画面
    go_to_mypage(driver)
    dismiss_popups(driver)

    if not go_to_footprints(driver):
        print('  足あと画面に移動できませんでした')
        return 0

    return_cnt = 0
    skip_cnt = 0
    processed_names = []

    for round_num in range(MAX_RETURN_FOOT + MAX_SKIP):
        if return_cnt >= MAX_RETURN_FOOT:
            break
        if skip_cnt >= MAX_SKIP:
            print('  連続スキップ上限')
            break

        # 足あとユーザー取得
        users = get_footprint_users(driver)
        if not users:
            print('  足あとユーザーがいません')
            break

        # 未処理のユーザーを探す
        target = None
        for u in users:
            if u['name'] not in processed_names:
                target = u
                break
        if not target:
            # スクロールして追加読み込み
            try:
                driver.execute_script('mobile: scroll', {'direction': 'down'})
                time.sleep(1)
            except Exception:
                pass
            users = get_footprint_users(driver)
            for u in users:
                if u['name'] not in processed_names:
                    target = u
                    break
            if not target:
                print('  未処理ユーザーなし')
                break

        user_name = target['name']
        processed_names.append(user_name)

        # 年齢チェック
        if not is_valid_age(target['age_text']):
            skip_cnt += 1
            continue

        # プロフィール画面へ
        try:
            target['cell'].click()
            time.sleep(3)
        except Exception:
            skip_cnt += 1
            continue

        # NGワードチェック
        if check_profile_ngwords(driver):
            print(f'    {user_name}: NGワード検出 → スキップ')
            go_back_to_footprints(driver)
            skip_cnt += 1
            continue

        # メール送信ボタンをタップ
        mail_btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'prof_rounded_mail_send_btn')
        if not mail_btn:
            print(f'    {user_name}: メール送信ボタンなし')
            go_back_to_footprints(driver)
            skip_cnt += 1
            continue
        mail_btn[0].click()
        time.sleep(3)

        # 初回メッセージ定型文画面が出たら戻る
        navs = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeNavigationBar')
        if navs:
            title = navs[0].get_attribute('name') or ''
            if '定型文' in title:
                back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, '戻る')
                if not back:
                    back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'BackButton')
                if back:
                    back[0].click()
                    time.sleep(2)

        # メール履歴チェック
        if has_mail_history(driver):
            go_back_to_footprints(driver)
            skip_cnt += 1
            continue

        # メッセージ送信
        msg = return_foot_message.format(name=user_name)
        if send_message(driver, msg):
            return_cnt += 1
            skip_cnt = 0
            now = datetime.now().strftime('%m-%d %H:%M:%S')
            print(f'  {name}:足跡返し  ~ {return_cnt} ~ {user_name} {now}')
        else:
            print(f'    {user_name}: 送信失敗')

        # 足あと画面に戻る
        go_back_to_footprints(driver)
        time.sleep(random.uniform(1.5, 3.0))

    print(f'\n{name} 足跡返し完了: {return_cnt}件')
    return return_cnt


def main():
    if len(sys.argv) < 2:
        print("使い方: python h_app_return_foot.py <キャラ名>")
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
        return_footprint(chara_data, driver)
    finally:
        driver.quit()
        print('Appiumセッション終了')


if __name__ == '__main__':
    main()

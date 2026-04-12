"""ハッピーメール アプリ版 プロフィール編集スクリプト (iPhone実機 / Appium)

使い方:
  myenv/bin/python h_app_profile_edit.py <キャラ名>
  例: myenv/bin/python h_app_profile_edit.py いおり

前提:
  - iPhoneがUSB接続済み・デベロッパモードON・WDAビルド済み
  - Appiumサーバーが localhost:4723 で起動中
  - ハッピーメールアプリにログイン済み
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
import time
from widget import func


UDID = '00008030-000C701C22E8802E'
BUNDLE_ID = 'jp.co.i-bec.happyhills'
APPIUM_URL = 'http://localhost:4723'


def create_driver():
    options = XCUITestOptions()
    options.platform_name = 'iOS'
    options.device_name = 'BishiのiPhone'
    options.udid = UDID
    options.bundle_id = BUNDLE_ID
    options.no_reset = True
    options.auto_accept_alerts = True
    options.wda_launch_timeout = 120000
    return webdriver.Remote(APPIUM_URL, options=options)


def dismiss_popups(driver):
    """起動時のポップアップを閉じ、途中画面から戻る"""
    for _ in range(10):
        closed = False
        # 戻るボタン（ナビゲーション途中）
        for back_id in ['back arrow btn', 'BackButton']:
            try:
                back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, back_id)
                if back and back[0].get_attribute('visible') == 'true':
                    back[0].click()
                    time.sleep(1)
                    closed = True
                    break
            except Exception:
                pass
        if closed:
            continue
        # OKボタン
        try:
            ok = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'OK')
            if ok and ok[0].get_attribute('visible') == 'true':
                ok[0].click()
                time.sleep(1)
                continue
        except Exception:
            pass
        # ×ボタン各種
        for cancel_id in ['icon cancel', 'order icon cancel old']:
            try:
                cancel = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, cancel_id)
                if cancel and cancel[0].get_attribute('visible') == 'true':
                    cancel[0].click()
                    time.sleep(1)
                    closed = True
                    break
            except Exception:
                pass
        if closed:
            continue
        # タブバーが見えていれば完了
        try:
            tab_bars = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTabBar')
            if tab_bars:
                tabs = tab_bars[0].find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeButton')
                visible_tabs = [t for t in tabs if t.get_attribute('visible') == 'true']
                if visible_tabs:
                    break
        except Exception:
            pass
        break


def go_to_mypage(driver):
    """マイページタブへ移動"""
    tab_bars = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTabBar')
    if tab_bars:
        for tb in tab_bars[0].find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeButton'):
            if tb.get_attribute('name') == 'マイページ':
                tb.click()
                time.sleep(3)
                return True
    return False


def get_member_number(driver):
    """マイページから会員番号を取得"""
    texts = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeStaticText')
    for t in texts:
        try:
            label = (t.get_attribute('label') or '').strip()
            if '会員番号' in label:
                return label.replace('会員番号：', '').strip()
        except Exception:
            pass
    return None


def go_to_profile_edit(driver):
    """マイページからプロフィール編集画面へ"""
    cells = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeCell')
    for c in cells:
        try:
            imgs = c.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeImage')
            for img in imgs:
                if img.get_attribute('name') == 'mypage_prof_btn':
                    c.click()
                    time.sleep(3)
                    return True
        except Exception:
            pass
    return False


def scroll_to_field(driver, field_label):
    """指定フィールドが表示されるまでスクロール"""
    for _ in range(8):
        cells = driver.find_elements(AppiumBy.XPATH,
            f'//XCUIElementTypeCell[.//XCUIElementTypeStaticText[@label="{field_label}"]]')
        if cells:
            try:
                if cells[0].get_attribute('visible') == 'true':
                    return cells[0]
            except Exception:
                pass
        driver.execute_script('mobile: scroll', {'direction': 'down'})
        time.sleep(0.5)
    return None


def scroll_to_top(driver):
    """画面最上部へスクロール"""
    for _ in range(5):
        driver.execute_script('mobile: scroll', {'direction': 'up'})
        time.sleep(0.3)


def edit_nickname(driver, name):
    """ニックネームを編集"""
    scroll_to_top(driver)
    driver.execute_script('mobile: scroll', {'direction': 'down'})
    time.sleep(0.5)
    cell = scroll_to_field(driver, 'ニックネーム')
    if not cell:
        print('  ニックネーム: セルが見つかりません')
        return
    # 現在の値を確認
    inner_texts = cell.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeStaticText')
    current_name = None
    for t in inner_texts:
        label = (t.get_attribute('label') or '').strip()
        if label and label != 'ニックネーム':
            current_name = label
            break
    if current_name == name:
        print(f'  ニックネーム: 変更なし ({name})')
        return
    cell.click()
    time.sleep(2)
    tf = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTextField')
    if not tf:
        print('  ニックネーム: TextFieldが見つかりません')
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'back arrow btn').click()
        time.sleep(1)
        return
    tf[0].clear()
    tf[0].send_keys(name)
    time.sleep(0.5)
    save = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, '保存')
    if save:
        save[0].click()
        time.sleep(2)
    print(f'  ニックネーム: {name}')
    # 自動で戻る場合もある、戻るボタンがあれば押す
    back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'back arrow btn')
    if back and back[0].get_attribute('visible') == 'true':
        back[0].click()
        time.sleep(1)


def edit_list_field(driver, field_label, target_value):
    """リスト選択形式のフィールドを編集（居住地・出身地・血液型等）"""
    if not target_value:
        return
    scroll_to_top(driver)
    cell = scroll_to_field(driver, field_label)
    if not cell:
        print(f'  {field_label}: セルが見つかりません')
        return
    # 現在の値を確認
    inner_texts = cell.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeStaticText')
    current_value = None
    for t in inner_texts:
        label = (t.get_attribute('label') or '').strip()
        if label and label != field_label:
            current_value = label
            break
    if current_value == target_value:
        print(f'  {field_label}: 変更なし ({target_value})')
        return
    cell.click()
    time.sleep(2)
    # リストからtarget_valueを探してタップ
    for _ in range(8):
        target_cells = driver.find_elements(AppiumBy.XPATH,
            f'//XCUIElementTypeCell[.//XCUIElementTypeStaticText[@label="{target_value}"]]')
        if target_cells:
            target_cells[0].click()
            time.sleep(1)
            print(f'  {field_label}: {target_value}')
            # 戻るボタン
            back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'back arrow btn')
            if back and back[0].get_attribute('visible') == 'true':
                back[0].click()
                time.sleep(1)
            return
        driver.execute_script('mobile: scroll', {'direction': 'down'})
        time.sleep(0.5)
    print(f'  {field_label}: 「{target_value}」が見つかりません')
    back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'back arrow btn')
    if back and back[0].get_attribute('visible') == 'true':
        back[0].click()
        time.sleep(1)


def edit_self_introduction(driver, text):
    """自己紹介を編集"""
    if not text:
        return
    scroll_to_top(driver)
    cell = scroll_to_field(driver, '自己紹介')
    if not cell:
        print('  自己紹介: セルが見つかりません')
        return
    cell.click()
    time.sleep(2)
    tv = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTextView')
    if not tv:
        print('  自己紹介: TextViewが見つかりません')
        back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'back arrow btn')
        if back:
            back[0].click()
            time.sleep(1)
        return
    tv[0].clear()
    tv[0].send_keys(text)
    time.sleep(0.5)
    # 保存/提出ボタン
    save = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, '保存')
    if not save:
        save = driver.find_elements(AppiumBy.XPATH, '//*[contains(@label, "提出") or contains(@label, "保存") or contains(@label, "審査")]')
    if save:
        save[0].click()
        time.sleep(2)
    print(f'  自己紹介: 設定完了')
    back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'back arrow btn')
    if back and back[0].get_attribute('visible') == 'true':
        back[0].click()
        time.sleep(1)


def edit_pr_comment(driver, text):
    """PRコメントを編集"""
    if not text:
        return
    scroll_to_top(driver)
    cell = scroll_to_field(driver, 'PRコメント')
    if not cell:
        print('  PRコメント: セルが見つかりません')
        return
    cell.click()
    time.sleep(2)
    tv = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTextView')
    if not tv:
        tv = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTextField')
    if not tv:
        print('  PRコメント: 入力欄が見つかりません')
        back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'back arrow btn')
        if back:
            back[0].click()
            time.sleep(1)
        return
    tv[0].clear()
    tv[0].send_keys(text)
    time.sleep(0.5)
    save = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, '保存')
    if save:
        save[0].click()
        time.sleep(2)
    print(f'  PRコメント: 設定完了')
    back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'back arrow btn')
    if back and back[0].get_attribute('visible') == 'true':
        back[0].click()
        time.sleep(1)


def profile_edit(chara_data, driver):
    """プロフィール全体を編集"""
    print(f'\n--- {chara_data["name"]} プロフィール編集 ---')

    # ニックネーム
    edit_nickname(driver, chara_data['name'])

    # リスト選択フィールド
    field_mappings = [
        ('居住地', 'activity_area'),
        ('詳細エリア', 'detail_activity_area'),
        ('出身地', 'birth_place'),
        ('血液型', 'blood_type'),
        ('星座', 'constellation'),
        ('身長', 'height'),
        ('スタイル', 'style'),
        ('ルックス', 'looks'),
        ('職業', 'job'),
        ('学歴', 'education'),
        ('休日', 'holiday'),
        ('子ども', 'having_children'),
        ('タバコ', 'smoking'),
        ('お酒', 'sake'),
        ('クルマ', 'car_ownership'),
        ('同居人', 'roommate'),
        ('兄弟姉妹', 'brothers_and_sisters'),
        ('出会うまでの希望', 'until_we_met'),
        ('初回デート費用', 'date_expenses'),
    ]
    for field_label, data_key in field_mappings:
        value = chara_data.get(data_key)
        if value:
            edit_list_field(driver, field_label, str(value))

    # PRコメント
    edit_pr_comment(driver, chara_data.get('pr_comment'))

    # 自己紹介
    edit_self_introduction(driver, chara_data.get('self_promotion'))

    print(f'\n{chara_data["name"]} のプロフィール編集が完了しました')


def main():
    if len(sys.argv) < 2:
        print("使い方: python h_app_profile_edit.py <キャラ名>")
        print("例: python h_app_profile_edit.py いおり")
        sys.exit(1)

    chara_name = sys.argv[1]

    # ユーザーデータ取得
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

    # Appium接続
    print('Appium接続中...')
    driver = create_driver()
    time.sleep(5)

    try:
        # ポップアップ閉じる
        dismiss_popups(driver)

        # マイページへ
        go_to_mypage(driver)

        # 会員番号で照合確認
        member_no = get_member_number(driver)
        if not member_no:
            dismiss_popups(driver)
            go_to_mypage(driver)
            time.sleep(2)
            member_no = get_member_number(driver)

        login_id = str(chara_data.get('login_id', ''))
        if member_no and member_no != login_id:
            print(f'会員番号が一致しません: 画面={member_no}, データ={login_id}')
            print('正しいアカウントでログインしてください')
            sys.exit(1)
        if member_no:
            print(f'会員番号照合OK: {member_no}')
        else:
            print('会員番号取得スキップ（マイページ未到達）')

        # プロフィール編集画面へ
        if not go_to_profile_edit(driver):
            print('プロフィール編集画面に移動できませんでした')
            sys.exit(1)

        # プロフィール編集
        profile_edit(chara_data, driver)

    finally:
        driver.quit()
        print('Appiumセッション終了')


if __name__ == '__main__':
    main()

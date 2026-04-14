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
    options.wda_connection_timeout = 120000
    return webdriver.Remote(APPIUM_URL, options=options)


def dismiss_popups(driver):
    """起動時のポップアップ・ダイアログを閉じる"""
    for _ in range(5):
        closed = False
        # OKボタン
        try:
            ok = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'OK')
            if ok and ok[0].get_attribute('visible') == 'true':
                ok[0].click()
                time.sleep(1)
                closed = True
        except Exception:
            pass
        if closed:
            continue
        # ×ボタン各種
        for cancel_id in ['icon cancel', 'icon_cancel_black', 'order icon cancel old']:
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
        # 年齢確認ダイアログ
        try:
            yes = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'はい(募集一覧へ)')
            if yes and yes[0].get_attribute('visible') == 'true':
                yes[0].click()
                time.sleep(1)
                continue
        except Exception:
            pass
        break


def go_to_mypage(driver):
    """タブバーが見えるTOP階層まで戻ってからマイページタブへ移動"""
    # タブバーが見えるまで戻る
    for _ in range(10):
        tab_bars = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTabBar')
        if tab_bars:
            try:
                tabs = tab_bars[0].find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeButton')
                visible = [t for t in tabs if t.get_attribute('visible') == 'true']
                if visible:
                    break
            except Exception:
                pass
        # タブバーが見えない → 戻るボタンで階層を上がる
        backed = False
        for back_id in ['back arrow btn', 'BackButton']:
            try:
                back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, back_id)
                if back and back[0].get_attribute('visible') == 'true':
                    back[0].click()
                    time.sleep(1)
                    backed = True
                    break
            except Exception:
                pass
        if not backed:
            break
    # マイページタブをタップ
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


def _safe_scroll(driver, direction):
    """スクロール（失敗しても無視）"""
    try:
        driver.execute_script('mobile: scroll', {'direction': direction})
        time.sleep(0.5)
    except Exception:
        pass


def _ensure_on_profile_edit(driver):
    """プロフィール編集画面にいることを確認。リスト選択画面にいたら戻る"""
    for _ in range(5):
        nav = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeNavigationBar')
        if nav:
            try:
                title = nav[0].get_attribute('name') or ''
                if title == 'マイプロフィール':
                    return True
            except Exception:
                pass
        # マイプロフィール以外 → 戻る
        back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'back arrow btn')
        if back:
            try:
                if back[0].get_attribute('visible') == 'true':
                    back[0].click()
                    time.sleep(1)
                    continue
            except Exception:
                pass
        break
    return False


def _is_profile_field_cell(cell, field_label):
    """プロフィール編集画面のフィールドセルか判定（ラベル+値の2つのStaticTextを持つ）"""
    try:
        texts = cell.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeStaticText')
        labels = [t.get_attribute('label') or '' for t in texts]
        # field_labelが含まれ、かつ値テキストもある（2つ以上のStaticText）
        if field_label in labels and len(labels) >= 2:
            return True
    except Exception:
        pass
    return False


def scroll_to_field(driver, field_label):
    """指定フィールドが表示されるまで下にスクロールして探す"""
    _ensure_on_profile_edit(driver)
    for _ in range(8):
        cells = driver.find_elements(AppiumBy.XPATH,
            f'//XCUIElementTypeCell[.//XCUIElementTypeStaticText[@label="{field_label}"]]')
        for cell in cells:
            try:
                if cell.get_attribute('visible') == 'true' and _is_profile_field_cell(cell, field_label):
                    return cell
            except Exception:
                pass
        _safe_scroll(driver, 'down')
    return None


def edit_nickname(driver, name):
    """ニックネームを編集"""
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
    # リスト選択画面に入れたか確認（ナビバータイトルが変わるはず）
    nav = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeNavigationBar')
    if not nav:
        print(f'  {field_label}: リスト画面に遷移できませんでした')
        return
    # リストからtarget_valueを探してタップ
    found = False
    for _ in range(8):
        target_cells = driver.find_elements(AppiumBy.XPATH,
            f'//XCUIElementTypeCell[.//XCUIElementTypeStaticText[@label="{target_value}"]]')
        if target_cells:
            target_cells[0].click()
            time.sleep(1)
            print(f'  {field_label}: {target_value}')
            found = True
            break
        _safe_scroll(driver, 'down')
    if not found:
        print(f'  {field_label}: 「{target_value}」が見つかりません')
    # リスト選択画面にいる場合は戻る
    nav = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeNavigationBar')
    nav_title = ''
    if nav:
        try:
            nav_title = nav[0].get_attribute('name') or ''
        except Exception:
            pass
    if nav_title != 'マイプロフィール':
        back = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, 'back arrow btn')
        if back:
            try:
                back[0].click()
                time.sleep(1)
            except Exception:
                pass


def edit_tag_field(driver, field_label, target_value):
    """タグ/チップボタン形式のフィールドを編集（スタイル・ルックス等の外見セクション）
    セルをタップするとインラインオーバーレイが開き、ボタンで選択する形式。
    """
    if not target_value:
        return
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
    # オーバーレイ内のボタンを探す
    found = False
    for _ in range(3):
        buttons = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeButton')
        for btn in buttons:
            try:
                btn_label = (btn.get_attribute('label') or '').strip()
                if btn_label == target_value and btn.get_attribute('visible') == 'true':
                    btn.click()
                    time.sleep(1)
                    print(f'  {field_label}: {target_value}')
                    found = True
                    break
            except Exception:
                pass
        if found:
            break
        _safe_scroll(driver, 'down')
        time.sleep(0.5)
    if not found:
        print(f'  {field_label}: 「{target_value}」ボタンが見つかりません')
        # オーバーレイを閉じる試み（×ボタンやオーバーレイ外タップ）
        for close_id in ['icon cancel', 'icon_cancel_black', 'order icon cancel old', '閉じる']:
            try:
                close_btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, close_id)
                if close_btn and close_btn[0].get_attribute('visible') == 'true':
                    close_btn[0].click()
                    time.sleep(1)
                    return
            except Exception:
                pass
        # 戻るボタンで閉じる
        _ensure_on_profile_edit(driver)


def edit_self_introduction(driver, text):
    """自己紹介を編集"""
    if not text:
        return
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

    # プロフィール編集画面のトップへ
    for _ in range(3):
        _safe_scroll(driver, 'up')

    # ニックネーム
    edit_nickname(driver, chara_data['name'])

    # フィールド編集（画面表示順）
    # type: 'list' = リスト選択画面遷移, 'tag' = インラインオーバーレイのタグボタン
    field_mappings = [
        ('居住地', 'activity_area', 'list'),
        ('詳細エリア', 'detail_activity_area', 'list'),
        ('出身地', 'birth_place', 'list'),
        ('血液型', 'blood_type', 'list'),
        ('星座', 'constellation', 'list'),
        ('身長', 'height', 'list'),
        ('スタイル', 'style', 'tag'),
        ('ルックス', 'looks', 'tag'),
        ('職業', 'job', 'list'),
        ('学歴', 'education', 'list'),
        ('休日', 'holiday', 'list'),
        ('子ども', 'having_children', 'list'),
        ('タバコ', 'smoking', 'list'),
        ('お酒', 'sake', 'list'),
        ('クルマ', 'car_ownership', 'list'),
        ('同居人', 'roommate', 'list'),
        ('兄弟姉妹', 'brothers_and_sisters', 'list'),
        ('出会うまでの希望', 'until_we_met', 'list'),
        ('初回デート費用', 'date_expenses', 'list'),
    ]
    for field_label, data_key, field_type in field_mappings:
        value = chara_data.get(data_key)
        if value:
            if field_type == 'tag':
                edit_tag_field(driver, field_label, str(value))
            else:
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
    time.sleep(2)

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

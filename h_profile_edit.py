import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from widget import func, happymail


def find_matching_tab(driver, login_id, wait):
    """login_idと一致するタブを探してswitchする（マイページの会員番号で照合）"""
    for handle in driver.window_handles:
        try:
            driver.switch_to.window(handle)
            driver.get("https://happymail.co.jp/app/html/mypage.php")
            wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
            elements = driver.find_elements(By.CLASS_NAME, 'ds_mypage_member_item')
            for e in elements:
                text = e.text.strip()
                if '会員番号' in text:
                    member_no = text.replace('会員番号：', '').strip()
                    if member_no == str(login_id):
                        print(f'  対象タブ発見: 会員番号={member_no} (handle={handle})')
                        return True
        except Exception:
            continue
    return False


def main():
    if len(sys.argv) < 3:
        print("使い方: python h_profile_edit.py <デバッグポート> <キャラ名>")
        print("例: python h_profile_edit.py 9222 いおり")
        sys.exit(1)

    port = sys.argv[1]
    chara_name = sys.argv[2]

    # デバッグ用Chromeに接続
    options = Options()
    options.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    # ユーザーデータ取得
    user_data = func.get_user_data()
    if not user_data or user_data == 2:
        print('ユーザーデータの取得に失敗しました')
        sys.exit(1)

    # キャラデータを探す
    chara_data = next((c for c in user_data.get('happymail', []) if c['name'] == chara_name), None)
    if not chara_data:
        print(f'{chara_name} が見つかりません')
        print('ハッピーメールキャラ一覧:', [c['name'] for c in user_data.get('happymail', [])])
        sys.exit(1)

    print(f'{chara_name} のデータ取得完了')

    # 会員番号と一致するタブに切り替え
    if not find_matching_tab(driver, chara_data['login_id'], wait):
        print(f'login_id={chara_data["login_id"]} と一致するタブが見つかりません')
        sys.exit(1)

    happymail.profile_edit_without_login(chara_data, driver, wait)

    # 検索条件設定
    print(f'\n--- 検索条件設定 ---')
    happymail.set_search_conditions(chara_data, driver, wait)

    # 足あと設定
    print(f'\n--- 足あと設定 ---')
    happymail.set_footprint_settings(driver, wait)


if __name__ == '__main__':
    main()

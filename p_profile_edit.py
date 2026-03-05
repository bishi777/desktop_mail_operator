import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from widget import func, pcmax_2


def main():
    if len(sys.argv) < 3:
        print("使い方: python p_profile_edit.py <デバッグポート> <キャラ名>")
        print("例: python p_profile_edit.py 9222 あゆ")
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
    chara_data = next((c for c in user_data.get('pcmax', []) if c['name'] == chara_name), None)
    if not chara_data:
        print(f'{chara_name} が見つかりません')
        print('PCMAXキャラ一覧:', [c['name'] for c in user_data.get('pcmax', [])])
        sys.exit(1)

    print(f'{chara_name} のデータ取得完了')
    pcmax_2.pcmax_profile_edit(chara_data, driver, wait)


if __name__ == '__main__':
    main()

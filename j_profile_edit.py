"""
Jmail プロフィール編集スクリプト
シークレットブラウザを起動してキャラのID/PASSでログインし、プロフ設定する。

使い方: python j_profile_edit.py <キャラ名>
例:     python j_profile_edit.py いおり
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from widget import func, jmail


def main():
  if len(sys.argv) < 2:
    print("使い方: python j_profile_edit.py <キャラ名>")
    print("例:     python j_profile_edit.py いおり")
    sys.exit(1)

  chara_name = sys.argv[1]

  user_data = func.get_user_data()
  if not user_data:
    print('ユーザーデータの取得に失敗しました')
    sys.exit(1)

  chara_data = next((c for c in user_data.get('jmail', []) if c['name'] == chara_name), None)
  if not chara_data:
    print(f'「{chara_name}」が見つかりません')
    print('Jmailキャラ一覧:', [c['name'] for c in user_data.get('jmail', [])])
    sys.exit(1)

  login_id = chara_data.get('login_id')
  password = chara_data.get('password')
  if not login_id or not password:
    print(f'「{chara_name}」のlogin_idまたはpasswordが未設定です')
    sys.exit(1)

  print(f'キャラ: {chara_name}  login_id: {login_id}')

  # シークレットモードでChrome起動
  options = Options()
  options.add_argument('--incognito')
  options.add_argument('--window-size=640,900')
  options.add_experimental_option('detach', True)
  service = Service(ChromeDriverManager().install())
  driver = webdriver.Chrome(service=service, options=options)
  wait = WebDriverWait(driver, 15)

  # ログイン
  print('ログイン中...')
  result = jmail.login_jmail(driver, wait, login_id, password)
  if not result:
    print('ログインに失敗しました')
    sys.exit(1)
  print('ログイン完了')

  # プロフィール編集
  jmail.profile_edit(chara_data, driver, wait)
  print('完了。ブラウザは手動で閉じてください。')


if __name__ == '__main__':
  main()

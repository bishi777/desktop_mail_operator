"""
Jmail プロフィール編集スクリプト
既存のデバッグChromeに接続して、指定キャラのタブでプロフ編集する。

使い方: python j_profile_edit.py <デバッグポート> <キャラ名>
例:     python j_profile_edit.py 9225 いおり
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from widget import func, jmail


def find_matching_tab(driver, wait, chara_name):
  """mintj.comのタブからニックネームが一致するタブを探してswitchする"""
  for handle in driver.window_handles:
    try:
      driver.switch_to.window(handle)
      if 'mintj.com' not in driver.current_url:
        continue
      driver.get('https://mintj.com/msm/MyProf/EditNickName/')
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      nick_input = driver.find_elements(By.NAME, 'EditedNickNameText')
      if not nick_input:
        continue
      nick = (nick_input[0].get_attribute('value') or '').strip()
      print(f'  タブ確認: {nick}')
      if nick == chara_name:
        print(f'  対象タブ発見: {nick} (handle={handle})')
        return True
    except Exception:
      continue
  return False


def main():
  if len(sys.argv) < 3:
    print("使い方: python j_profile_edit.py <デバッグポート> <キャラ名>")
    print("例: python j_profile_edit.py 9225 いおり")
    sys.exit(1)

  port = sys.argv[1]
  chara_name = sys.argv[2]

  options = Options()
  options.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')
  driver = webdriver.Chrome(options=options)
  wait = WebDriverWait(driver, 15)

  user_data = func.get_user_data()
  if not user_data:
    print('ユーザーデータの取得に失敗しました')
    sys.exit(1)

  chara_data = next((c for c in user_data.get('jmail', []) if c['name'] == chara_name), None)
  if not chara_data:
    print(f'「{chara_name}」が見つかりません')
    print('Jmailキャラ一覧:', [c['name'] for c in user_data.get('jmail', [])])
    sys.exit(1)

  print(f'キャラ: {chara_name}  login_id: {chara_data.get("login_id")}')

  if not find_matching_tab(driver, wait, chara_name):
    print(f'「{chara_name}」と一致するタブが見つかりません')
    sys.exit(1)

  jmail.profile_edit(chara_data, driver, wait)
  print('完了')


if __name__ == '__main__':
  main()

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


def find_matching_tab(driver, wait, login_id):
  """mintj.comのタブからマイページの会員IDが一致するタブを探してswitchする"""
  import re
  for handle in driver.window_handles:
    try:
      driver.switch_to.window(handle)
      if 'mintj.com' not in driver.current_url:
        continue
      driver.get('https://mintj.com/msm/mainmenu/M.aspx?sid=&pn=51')
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(1)
      body_text = driver.find_element(By.TAG_NAME, 'body').text
      match = re.search(r'会員ID[\s【\[:：]+(\d+)', body_text)
      page_id = match.group(1).strip() if match else ''
      print(f'  タブ確認: 会員ID={page_id}')
      if page_id == str(login_id):
        print(f'  対象タブ発見: {page_id} (handle={handle})')
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

  login_id = chara_data.get('login_id')
  print(f'キャラ: {chara_name}  login_id: {login_id}')

  if not find_matching_tab(driver, wait, login_id):
    print(f'「{chara_name}」(会員ID={login_id}) と一致するタブが見つかりません')
    sys.exit(1)

  jmail.profile_edit(chara_data, driver, wait)
  print('完了')


if __name__ == '__main__':
  main()

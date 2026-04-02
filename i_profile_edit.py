import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from widget import func, ikukuru


def find_matching_tab(driver, wait, chara_name):
  """イククルのタブからキャラ名と一致するタブを探してswitchする"""
  for handle in driver.window_handles:
    try:
      driver.switch_to.window(handle)
      if '194964' not in driver.current_url:
        continue
      driver.get('https://pc.194964.com/mypage.html')
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      import time; time.sleep(2)
      elements = driver.find_elements(By.CLASS_NAME, 'profile-name')
      if elements:
        page_name = elements[0].text.strip()
        if page_name == chara_name:
          print(f'  対象タブ発見: {page_name} (handle={handle})')
          return True
    except Exception:
      continue
  return False


def main():
  if len(sys.argv) < 3:
    print("使い方: python i_profile_edit.py <デバッグポート> <キャラ名>")
    print("例: python i_profile_edit.py 9222 えりか")
    print()
    sys.exit(1)

  port = sys.argv[1]
  chara_name = sys.argv[2]

  options = Options()
  options.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')
  driver = webdriver.Chrome(options=options)
  wait = WebDriverWait(driver, 10)

  user_data = func.get_user_data()
  if not user_data:
    print('ユーザーデータの取得に失敗しました')
    sys.exit(1)

  chara_data = next((c for c in user_data.get('ikukuru', []) if c['name'] == chara_name), None)
  if not chara_data:
    print(f'「{chara_name}」が見つかりません')
    print('イククルキャラ一覧:', [c['name'] for c in user_data.get('ikukuru', [])])
    sys.exit(1)

  print(f'{chara_name} のデータ取得完了')

  if not find_matching_tab(driver, wait, chara_name):
    print(f'「{chara_name}」と一致するタブが見つかりません')
    sys.exit(1)

  ikukuru.profile_edit(chara_data, driver, wait)
  print('完了')


if __name__ == '__main__':
  main()

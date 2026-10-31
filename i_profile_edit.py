import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from widget import func, ikukuru
from widget.human_input import make_driver


def find_matching_tab(driver, wait, login_mail_address):
  """イククルのタブからメールアドレスが一致するタブを探してswitchする"""
  import re, time
  for handle in driver.window_handles:
    try:
      driver.switch_to.window(handle)
      if '194964' not in driver.current_url:
        continue
      driver.get('https://pc.194964.com/config/settingregist/show_setting_mailaddress.html')
      wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
      time.sleep(2)
      body_text = driver.find_element(By.TAG_NAME, 'body').text
      match = re.search(r'ご登録のメールアドレス\s*\n\s*(\S+@\S+)', body_text)
      if match:
        page_mail = match.group(1).strip()
        print(f'  タブ確認: {page_mail}')
        if page_mail == login_mail_address:
          print(f'  対象タブ発見: {page_mail} (handle={handle})')
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
  if not str(port).isdigit():
    # 引数の順番を間違えると "port must be > 0" という分かりにくい例外になるため、
    # ここで止めて正しい使い方を示す（ポートが先、キャラ名が後）
    print(f"ポート番号が不正です: {port!r}")
    print("引数の順番は <デバッグポート> <キャラ名> です")
    print("例: python i_profile_edit.py 9222 えりか")
    sys.exit(1)

  options = Options()
  options.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')
  driver = make_driver(options, port=port)
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

  login_mail = chara_data.get('login_mail_address', '')
  print(f'{chara_name} のデータ取得完了 (mail: {login_mail})')

  if not find_matching_tab(driver, wait, login_mail):
    print(f'「{chara_name}」({login_mail}) と一致するタブが見つかりません')
    sys.exit(1)

  ikukuru.profile_edit(chara_data, driver, wait)
  print('完了')


if __name__ == '__main__':
  main()

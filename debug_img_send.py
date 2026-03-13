"""
score_and_send_fst_message の画像送信部分のデバッグスクリプト
前提: デバッグ用Chromeが9224で起動済み、かつメッセージ画面（チャット画面）を開いている
"""
import sys, os, time, requests
sys.path.insert(0, os.path.dirname(__file__))
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import settings

PORT = sys.argv[1] if len(sys.argv) > 1 else settings.happymail_drivers_port
NAME = "debug"

# image_path: コマンド引数2で指定、なければデフォルト
from widget import func
d = func.get_user_data()
IMAGE_URL = sys.argv[2] if len(sys.argv) > 2 else d['happymail'][0].get('chara_image', '')

print(f"=== 画像送信デバッグ ===")
print(f"PORT: {PORT}")
print(f"IMAGE_URL: {IMAGE_URL}")

service = Service(ChromeDriverManager().install())
options = Options()
options.add_experimental_option("debuggerAddress", f"127.0.0.1:{PORT}")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

print(f"現在のURL: {driver.current_url}")

# 画像をローカルに保存
local_img_path = None
try:
    local_img_path = os.path.abspath(f"{NAME}_fst_img.png")
    print(f"画像ダウンロード中: {IMAGE_URL}")
    img_response = requests.get(IMAGE_URL, timeout=10)
    img_response.raise_for_status()
    with open(local_img_path, 'wb') as f:
        f.write(img_response.content)
    print(f"画像保存完了: {local_img_path} ({os.path.getsize(local_img_path)} bytes)")

    # +アイコン確認
    plus_icon = driver.find_elements(By.CLASS_NAME, 'icon-message_plus')
    print(f"icon-message_plus: {len(plus_icon)}個見つかった")
    if not plus_icon:
        print("ERROR: +アイコンが見つかりません。メッセージ画面を開いているか確認してください。")
        sys.exit(1)

    driver.execute_script('arguments[0].click();', plus_icon[0])
    print("+アイコンクリック完了")
    time.sleep(1)

    # upload_file確認
    upload_file = driver.find_elements(By.ID, 'upload_file')
    print(f"upload_file: {len(upload_file)}個見つかった")
    if not upload_file:
        print("ERROR: upload_fileが見つかりません")
        sys.exit(1)

    upload_file[0].send_keys(local_img_path)
    print("画像パスをセット完了")
    time.sleep(2)

    # submit_button確認
    img_submit = driver.find_elements(By.ID, 'submit_button')
    print(f"submit_button: {len(img_submit)}個見つかった")
    if not img_submit:
        print("ERROR: submit_buttonが見つかりません")
        sys.exit(1)

    driver.execute_script('arguments[0].scrollIntoView({block:"center"});', img_submit[0])
    driver.execute_script('arguments[0].click();', img_submit[0])
    print("submit_buttonクリック完了")
    time.sleep(2)
    print("=== 画像送信完了（ブラウザを確認してください）===")

except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()
finally:
    if local_img_path and os.path.exists(local_img_path):
        os.remove(local_img_path)
        print(f"ローカル画像削除: {local_img_path}")

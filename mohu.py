import time
from widget import happymail, func, pcmax
from DrissionPage import ChromiumPage
import time
import random
from DrissionPage import ChromiumPage
from DrissionPage.errors import ElementNotFoundError
import os
import time
from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage.errors import BrowserConnectError
from selenium.webdriver.support.ui import WebDriverWait
from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage.errors import BrowserConnectError, PageDisconnectedError
import os
import time

user_data = func.get_user_data()

# driver,wait = func.test_get_driver(None, False)
wait_time = 1.5
pcmax_data = user_data["pcmax"][4]
happy_data = user_data["happymail"][4]
name = pcmax_data["name"]
login_id = pcmax_data["login_id"]
login_pass = pcmax_data["password"]

h_name = happy_data["name"]
h_login_id = happy_data["login_id"]
h_login_pass = happy_data["password"]


def test_get_DrissionPage(tmp_dir=None, headless_flag=False, max_retries=3):
    """DrissionPage を使って ChromiumPage をセットアップする関数"""
    if tmp_dir:
        temp_dir = os.path.join(tmp_dir, f"temp_cache_{os.getpid()}")  
        os.environ["WDM_CACHE"] = temp_dir
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
    for attempt in range(max_retries):
        try:
            options = ChromiumOptions()
            if headless_flag:
                options.headless(True)
            options.set_argument("--disable-gpu")
            options.set_argument("--disable-software-rasterizer")
            options.set_argument("--disable-dev-shm-usage")
            options.set_argument("--incognito")
            options.set_argument("--enable-unsafe-swiftshader")
            options.set_argument("--log-level=3")
            options.set_argument("--disable-web-security")
            options.set_argument("--disable-extensions")
            options.set_argument("--no-sandbox")
            options.set_argument("--window-size=456,912")
            options.set_argument("--disable-cache")
            options.set_argument("--disable-blink-features=AutomationControlled")
            options.set_argument("--disable-background-timer-throttling")  # 🔹 追加
            options.set_argument("--disable-renderer-backgrounding")  # 🔹 追加
            options.set_argument("--disable-backgrounding-occluded-windows")  # 🔹 追加

            page = ChromiumPage(options)
            # ページが正しく開けるか確認
            page.get("about:blank")
            print("✅ ChromiumPage 起動成功")

            return page

        except BrowserConnectError as e:
            print(f"BrowserConnectError発生: {e}")
            print(f"再試行します ({attempt + 1}/{max_retries})")
            time.sleep(5)
            if attempt == max_retries - 1:
                raise

        except ConnectionError as e:
            print(f"⚠️ ネットワークエラーが発生しました: {e}")
            print("3分後に再接続します...")
            time.sleep(180)
            if attempt == max_retries - 1:
                raise

def pcmax_login(name, login_id, login_pass, page: ChromiumPage):
    try:
        # 🔹 ページの接続が切れていないかチェック
        if not page.driver:
            print("⚠️ ChromiumPage が切断されています。再起動します。")
            return "ページ切断エラー"

        page.get("https://pcmax.jp/pcm/file.php?f=login_form")
        time.sleep(3)

        print("📌 ログインページタイトル:", page.title)

        page.ele('#login_id').input(login_id)
        page.ele('#login_pw').input(login_pass)
        time.sleep(1)
        page.ele('@name=login').click()
        time.sleep(3)

        # 利用制限チェック
        if page.eles('.suspend-title'):
            print(f"{name} pcmax利用制限中です")
            return f"{name} pcmax利用制限中です"

        print("✅ ログイン成功")
        return ""

    except PageDisconnectedError:
        print("⚠️ DrissionPage が Chrome との接続を失いました。再起動してください。")
        return "ページ切断エラー"

    except Exception as e:
        print(f"❌ ログイン中にエラーが発生: {e}")
        return "ログインエラー"


# func.change_tor_ip()
profile_path = '/Users/yamamotokenta/Library/Application Support/Google/Chrome/Profile 74'
driver, wait = func.test_get_driver(None, False, 3, profile_path)
# time.sleep(100)
happymail.login(name, h_login_id, h_login_pass, driver, wait)

"""make_footprint_keyword をえりかでデバッグ実行"""
import sys
import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from widget import pcmax_2


def main():
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    for h in driver.window_handles:
        driver.switch_to.window(h)
        if "pcmax" in driver.current_url or "linkleweb" in driver.current_url:
            break

    if "/pcm/index.php" not in driver.current_url:
        driver.get("https://pcmax.jp/mobile/index.php")
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(1.5)

    name_els = driver.find_elements(By.CLASS_NAME, "mydata_name")
    if not name_els or "えりか" not in name_els[0].text:
        print(f"❌ えりかでログインしていません: {name_els[0].text if name_els else '(未ログイン)'}")
        sys.exit(1)
    print(f"✅ ログイン中: {name_els[0].text}")

    try:
        pcmax_2.make_footprint_keyword("えりか", driver, footprint_count=5, iikamo_count=1)
        print("✅ make_footprint_keyword 完了")
    except Exception as e:
        print(f"❌ 失敗: {type(e).__name__} → {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()

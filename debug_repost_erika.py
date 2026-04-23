"""えりかで re_post を単体デバッグするスクリプト。
前提: ポート9222でChromeを debug 起動済み、えりかでログイン済み。
使い方: myenv/bin/python debug_repost_erika.py
"""
import sys
import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from widget import func, pcmax_2


def main():
    PORT = 9222
    user_data = func.get_user_data()
    pcmax_datas = user_data["pcmax"]

    target = None
    for i in pcmax_datas:
        if i["name"] == "えりか":
            target = i
            break
    if target is None:
        print("❌ user_data['pcmax'] に えりか が見つかりません")
        sys.exit(1)

    post_title = target.get("post_title", "")
    post_content = target.get("post_content", "")
    print(f"post_title: {post_title!r}")
    print(f"post_content (先頭80): {post_content[:80]!r}")
    if not post_title or not post_content:
        print("❌ post_title / post_content が未設定のため中止")
        sys.exit(1)

    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{PORT}")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    # PCMAXの該当タブを特定。index.phpに移動して mydata_name を確認
    handles = driver.window_handles
    print(f"タブ数: {len(handles)}")
    chosen = None
    for idx, h in enumerate(handles):
        driver.switch_to.window(h)
        url = driver.current_url
        print(f"  [{idx}] url={url}")
        if "pcmax" in url or "linkleweb" in url:
            chosen = h
            break
    if chosen is None:
        print("❌ PCMAX/linkleweb のタブがありません")
        sys.exit(1)

    driver.switch_to.window(chosen)
    if "/pcm/index.php" not in driver.current_url:
        print("index.php に移動します")
        if "linkleweb" in driver.current_url:
            driver.get("https://linkleweb.jp/mobile/index.php")
        else:
            driver.get("https://pcmax.jp/mobile/index.php")
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(1.5)

    pcmax_2.catch_warning_pop("", driver)
    name_els = driver.find_elements(By.CLASS_NAME, "mydata_name")
    if not name_els:
        print("❌ mydata_name が見つからない（未ログイン？）")
        sys.exit(1)
    login_name = name_els[0].text.strip()
    print(f"ログイン中: {login_name}")
    if "えりか" not in login_name:
        print(f"❌ 対象(えりか)ではありません: {login_name}")
        sys.exit(1)

    try:
        print("📝 re_post 開始")
        pcmax_2.re_post(driver, wait, post_title, post_content)
        print("✅ re_post 完了")
    except Exception as e:
        print(f"❌ re_post 失敗: {type(e).__name__} → {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()

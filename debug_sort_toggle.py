"""profile_search の検索順トグルが動作するか、2回呼んで検証"""
import sys
import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from widget import pcmax_2


def main():
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    for h in driver.window_handles:
        driver.switch_to.window(h)
        if "pcmax" in driver.current_url:
            break

    if "/pcm/index.php" not in driver.current_url:
        driver.get("https://pcmax.jp/mobile/index.php")
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(1.5)

    name_els = driver.find_elements(By.CLASS_NAME, "mydata_name")
    print(f"ログイン中: {name_els[0].text if name_els else '(不明)'}")

    search_edit = {
        "y_age": [18],
        "o_age": [34],
        "m_height": [165, 170, 175],
        "area_flug": 2,
        "search_target": ["送信歴無し"],
        "exclude_words": ["不倫・浮気", "エロトーク・TELH", "SMパートナー", "写真・動画撮影", "同性愛", "アブノーマル"],
        "search_body_type": ["スリム", "やや細め", "普通", "ふくよか", "太め"],
        "annual_income": ["200万円未満", "200万円以上〜400万円未満", "指定なし"],
    }

    for i in range(2):
        print(f"\n=== {i+1}回目 profile_search ===")
        # 検索メニューに戻る
        driver.get("https://pcmax.jp/mobile/profile_reference.php")
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(1)
        # 送信前の so1 現在値を取得
        try:
            sel_before = driver.find_element(By.ID, "so1")
            before_val = Select(sel_before).first_selected_option.get_attribute("value")
            before_txt = Select(sel_before).first_selected_option.text
            print(f"  送信前 so1: value={before_val} text={before_txt!r}")
        except Exception as e:
            print(f"  so1取得エラー: {e}")

        try:
            ok = pcmax_2.profile_search(driver, search_edit)
            print(f"  profile_search 戻り値: {ok}")
        except Exception as e:
            print(f"❌ profile_search 失敗: {type(e).__name__} → {e}")
            traceback.print_exc()
            break
        time.sleep(2)
        print(f"  検索後URL: {driver.current_url}")

        # 結果ページからフォームに戻り、so1が次回どう表示されるか見る（サーバーが状態記憶してるか）
        driver.get("https://pcmax.jp/mobile/profile_reference.php")
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(1)
        try:
            sel_after = driver.find_element(By.ID, "so1")
            after_val = Select(sel_after).first_selected_option.get_attribute("value")
            after_txt = Select(sel_after).first_selected_option.text
            print(f"  検索フォーム再表示時の so1: value={after_val} text={after_txt!r}")
        except Exception as e:
            print(f"  so1取得エラー: {e}")


if __name__ == "__main__":
    main()

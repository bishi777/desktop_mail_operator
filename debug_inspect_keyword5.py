"""送信後のページに何が表示されているか確認（エラーメッセージ/警告の有無）"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select


def main():
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    for h in driver.window_handles:
        driver.switch_to.window(h)
        if "pcmax" in driver.current_url:
            break

    driver.get("https://pcmax.jp/mobile/profile_reference.php")
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(1.5)

    TARGET_PREF_VALUES = {"22", "23", "24", "25", "19", "20", "21"}
    for cb in driver.find_elements(By.CSS_SELECTOR, "input[name='pref[]']"):
        v = cb.get_attribute("value")
        want = v in TARGET_PREF_VALUES
        if cb.is_selected() != want:
            driver.execute_script("arguments[0].click();", cb)

    Select(driver.find_element(By.NAME, "from_age")).select_by_visible_text("18歳")
    Select(driver.find_element(By.NAME, "to_age")).select_by_visible_text("34歳")

    # 送信前に警告あるか
    body_before = driver.find_element(By.TAG_NAME, "body").text
    print("=== 送信前 body に 警告/制限 系テキスト ===")
    for kw in ["制限", "エラー", "もう一度", "再度", "ご利用", "しばらく", "混雑"]:
        if kw in body_before:
            print(f"  含む: {kw}")

    # 「この条件 で 検索 する」
    for btn in driver.find_elements(By.TAG_NAME, "button"):
        if "条件" in btn.text and "検索" in btn.text:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.4)
            btn.click()
            time.sleep(3)
            break

    print(f"\n送信後URL: {driver.current_url}")
    print("\n=== 送信後 body 先頭1500文字 ===")
    body_after = driver.find_element(By.TAG_NAME, "body").text
    print(body_after[:1500])

    # 「検索結果」や件数表示があるか
    print("\n=== '検索結果' 等の表示 ===")
    for line in body_after.split("\n"):
        if any(k in line for k in ["件", "結果", "該当", "見つかりません"]):
            print(f"  {line.strip()}")


if __name__ == "__main__":
    main()

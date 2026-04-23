"""phrase入力 + 都道府県チェック → 「この条件で検索する」ボタンで検索し、
結果のURLと地域分布を確認する"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select


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
    time.sleep(1.2)

    TARGET_PREF_VALUES = {"22", "23", "24", "25", "19", "20", "21"}

    # 都道府県チェック（東京+近隣6県のみ）
    for cb in driver.find_elements(By.CSS_SELECTOR, "input[name='pref[]']"):
        v = cb.get_attribute("value")
        want = v in TARGET_PREF_VALUES
        if cb.is_selected() != want:
            driver.execute_script("arguments[0].click();", cb)

    # 年齢
    Select(driver.find_element(By.NAME, "from_age")).select_by_visible_text("18歳")
    Select(driver.find_element(By.NAME, "to_age")).select_by_visible_text("34歳")

    # 送信歴無し
    nt = driver.find_elements(By.CSS_SELECTOR, "input[name='no_transmit']")
    if nt and not nt[0].is_selected():
        driver.execute_script("arguments[0].click();", nt[0])

    # phrase入力
    phrase = driver.find_element(By.CSS_SELECTOR, "input[name='phrase']")
    phrase.clear()
    phrase.send_keys("童貞")

    # phraseがどのformに属するか確認
    phrase_form = driver.execute_script(
        "var el = arguments[0].closest('form');"
        "return el ? (el.getAttribute('action') + ' / ' + el.getAttribute('method')) : null;",
        phrase,
    )
    print(f"phrase が属するform: {phrase_form}")

    # 「この条件 で 検索 する」ボタンをクリック
    clicked = False
    for btn in driver.find_elements(By.TAG_NAME, "button"):
        if "条件" in btn.text and "検索" in btn.text:
            btn_form = driver.execute_script(
                "var el = arguments[0].closest('form');"
                "return el ? (el.getAttribute('action') + ' / ' + el.getAttribute('method')) : null;",
                btn,
            )
            print(f"'{btn.text.strip()}' ボタンが属するform: {btn_form}")
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.4)
            btn.click()
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            time.sleep(2)
            clicked = True
            break
    if not clicked:
        print("❌ 「この条件で検索する」ボタンが見つからず")
        return

    print(f"\n検索後URL: {driver.current_url}")

    cards = driver.find_elements(By.CLASS_NAME, "profile_card")
    print(f"結果カード数: {len(cards)}")
    print("\n--- 上位20件の地域 ---")
    for i, c in enumerate(cards[:20]):
        name_els = c.find_elements(By.CLASS_NAME, "name")
        age_els = c.find_elements(By.CLASS_NAME, "age")
        conf_els = c.find_elements(By.CLASS_NAME, "conf")
        nm = name_els[0].text if name_els else ""
        ag = age_els[0].text if age_els else ""
        ar = conf_els[0].text.replace("登録地域", "").strip() if conf_els else ""
        print(f"  [{i}] {nm} {ag} / {ar}")


if __name__ == "__main__":
    main()

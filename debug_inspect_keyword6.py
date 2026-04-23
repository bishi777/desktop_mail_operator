"""phrase入り/空 の2回検索で結果が違うか比較（キーワードが効いているかの検証）"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select


def run_search(driver, wait, phrase_text):
    driver.get("https://pcmax.jp/mobile/profile_reference.php")
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(1.2)

    TARGET_PREF_VALUES = {"22", "23", "24", "20"}  # 東京+神奈川+埼玉+栃木 (4県)
    for cb in driver.find_elements(By.CSS_SELECTOR, "input[name='pref[]']"):
        v = cb.get_attribute("value")
        want = v in TARGET_PREF_VALUES
        if cb.is_selected() != want:
            driver.execute_script("arguments[0].click();", cb)

    Select(driver.find_element(By.NAME, "from_age")).select_by_visible_text("18歳")
    Select(driver.find_element(By.NAME, "to_age")).select_by_visible_text("34歳")

    nt = driver.find_elements(By.CSS_SELECTOR, "input[name='no_transmit']")
    if nt and not nt[0].is_selected():
        driver.execute_script("arguments[0].click();", nt[0])

    if phrase_text:
        phrase = driver.find_element(By.CSS_SELECTOR, "input[name='phrase']")
        phrase.clear()
        phrase.send_keys(phrase_text)

    for btn in driver.find_elements(By.TAG_NAME, "button"):
        if "条件" in btn.text and "検索" in btn.text:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.4)
            btn.click()
            break
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(2)

    url = driver.current_url
    cards = driver.find_elements(By.CLASS_NAME, "profile_card")
    names = []
    self_prs = []
    for c in cards[:10]:
        n = c.find_elements(By.CLASS_NAME, "name")
        p = c.find_elements(By.CLASS_NAME, "self_pr")
        names.append(n[0].text if n else "")
        self_prs.append(p[0].text if p else "")
    return url, len(cards), names, self_prs


def main():
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    for h in driver.window_handles:
        driver.switch_to.window(h)
        if "pcmax" in driver.current_url:
            break

    print("=== phrase=童貞 で検索 ===")
    url1, n1, names1, prs1 = run_search(driver, wait, "童貞")
    print(f"URL: {url1}")
    print(f"件数: {n1}")
    print(f"上位10 names: {names1}")
    hit1 = sum(1 for p in prs1 if "童貞" in p)
    print(f"self_pr に '童貞' 含む件数: {hit1}/10")

    time.sleep(2)

    print("\n=== phrase 空 で検索 ===")
    url2, n2, names2, prs2 = run_search(driver, wait, "")
    print(f"URL: {url2}")
    print(f"件数: {n2}")
    print(f"上位10 names: {names2}")
    hit2 = sum(1 for p in prs2 if "童貞" in p)
    print(f"self_pr に '童貞' 含む件数: {hit2}/10")

    print("\n=== 判定 ===")
    if names1 == names2:
        print("❌ 両者の結果が完全一致 → キーワードは無視されている")
    elif hit1 > hit2:
        print(f"✅ phrase入りの方が '童貞' 含む件数が多い ({hit1} vs {hit2}) → 効いている可能性")
    else:
        print(f"⚠️ 結果は異なるが '童貞' hit数は同程度 → ランダム性/時系列差の可能性")


if __name__ == "__main__":
    main()

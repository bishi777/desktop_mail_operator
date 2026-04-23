"""phraseを profile_reference.php フォームに hidden injection して送信 →
サーバーが phrase を認識してくれるかテスト"""
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
    time.sleep(1.2)

    TARGET_PREF_VALUES = {"22", "23", "24", "25", "19", "20", "21"}

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

    # profile_reference.php form に phrase=童貞 を hidden注入
    injected = driver.execute_script(
        """
        var forms = document.querySelectorAll('form');
        for (var i=0; i<forms.length; i++) {
          var f = forms[i];
          if (f.action && f.action.indexOf('profile_reference') >= 0) {
            var inp = document.createElement('input');
            inp.type = 'hidden';
            inp.name = 'phrase';
            inp.value = '童貞';
            f.appendChild(inp);
            return f.action;
          }
        }
        return null;
        """
    )
    print(f"phrase注入先 form: {injected}")

    # 「この条件 で 検索 する」ボタンクリック
    for btn in driver.find_elements(By.TAG_NAME, "button"):
        if "条件" in btn.text and "検索" in btn.text:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.4)
            btn.click()
            break
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(2)

    print(f"\n検索後URL: {driver.current_url}")
    cards = driver.find_elements(By.CLASS_NAME, "profile_card")
    print(f"結果カード数: {len(cards)}")

    # 上位5件の self_pr を確認（キーワード 童貞 が含まれているか検証）
    print("\n--- 上位5件の self_pr ---")
    for i, c in enumerate(cards[:5]):
        name_els = c.find_elements(By.CLASS_NAME, "name")
        ar_els = c.find_elements(By.CLASS_NAME, "conf")
        pr_els = c.find_elements(By.CLASS_NAME, "self_pr")
        nm = name_els[0].text if name_els else ""
        ar = ar_els[0].text.replace("登録地域", "").strip() if ar_els else ""
        pr = pr_els[0].text if pr_els else ""
        has_kw = "童貞" in pr
        print(f"  [{i}] {nm} / {ar} / 童貞含む={has_kw}")
        print(f"      self_pr={pr[:100]!r}")


if __name__ == "__main__":
    main()

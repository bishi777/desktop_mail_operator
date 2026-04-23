"""profile_reference.php の フォーム詳細 + 試しに検索して結果カード構造を調査"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


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

    print(f"URL: {driver.current_url}")

    # pref チェックボックス: ラベル文字列とvalue対応
    print("\n=== pref[] チェックボックス: value → ラベル ===")
    pref_boxes = driver.find_elements(By.CSS_SELECTOR, "input[name='pref[]']")
    for cb in pref_boxes:
        val = cb.get_attribute("value")
        # 親ラベルか隣接テキストを取得
        label = driver.execute_script(
            """
            var el = arguments[0];
            // まずlabel for=id
            var id = el.getAttribute('id');
            if (id) {
              var lbl = document.querySelector('label[for=\"' + id + '\"]');
              if (lbl) return lbl.textContent.trim();
            }
            // 親要素のlabel
            var p = el.closest('label');
            if (p) return p.textContent.trim();
            // 次の兄弟のtextContent
            var sib = el.nextSibling;
            while (sib && sib.nodeType === 3 && !sib.textContent.trim()) sib = sib.nextSibling;
            if (sib && sib.nodeType === 3) return sib.textContent.trim();
            if (sib && sib.nodeType === 1) return sib.textContent.trim();
            // 親のtextContentから他の内容を除外
            return (el.parentElement ? el.parentElement.textContent.trim() : '').slice(0, 20);
            """,
            cb,
        )
        print(f"  value={val} label={label!r}")

    # 年齢フィールド
    print("\n=== 年齢フィールド（selectなど） ===")
    for sel in driver.find_elements(By.TAG_NAME, "select"):
        n = sel.get_attribute("name")
        if n and ("age" in n.lower()):
            opts = [o.text.strip() for o in sel.find_elements(By.TAG_NAME, "option")]
            print(f"  select name={n} options={opts}")
        else:
            print(f"  select name={n}")

    # 送信歴無し (no_transmit)
    print("\n=== no_transmit 確認 ===")
    nt = driver.find_elements(By.CSS_SELECTOR, "input[name='no_transmit']")
    for cb in nt:
        print(f"  no_transmit value={cb.get_attribute('value')} checked={cb.is_selected()}")

    # 試しに検索 — 「童貞」 をpostして結果ページを見る
    print("\n=== 試しに phrase=童貞 で検索 ===")
    phrase = driver.find_element(By.CSS_SELECTOR, "input[name='phrase']")
    phrase.clear()
    phrase.send_keys("童貞")
    # submit
    submit = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='検索']")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit)
    time.sleep(0.5)
    submit.click()
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(2)

    print(f"結果URL: {driver.current_url}")
    print("\n--- profile_card 要素数 ---")
    cards = driver.find_elements(By.CLASS_NAME, "profile_card")
    print(f"  {len(cards)}件")
    if cards:
        print("\n--- 1枚目のHTML（先頭2000文字） ---")
        html = cards[0].get_attribute("outerHTML")
        print(html[:2000])
        print("\n--- 1枚目の主要class要素 ---")
        for c in ["name", "age", "conf", "exchange", "profile_link_btn", "user_info"]:
            els = cards[0].find_elements(By.CLASS_NAME, c)
            if els:
                print(f"  .{c}: {els[0].text!r}")
            else:
                print(f"  .{c}: (なし)")


if __name__ == "__main__":
    main()

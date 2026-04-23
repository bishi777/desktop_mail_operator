"""キーワード検索ページのDOMを調査する"""
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
        if "pcmax" in driver.current_url or "linkleweb" in driver.current_url:
            break

    print(f"現在URL: {driver.current_url}")
    driver.get("https://pcmax.jp/mobile/index.php")
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(1)

    print("\n=== TOP: キーワード検索 候補リンク ===")
    for a in driver.find_elements(By.TAG_NAME, "a"):
        t = a.text.strip()
        if "キーワード" in t:
            print(f"  text={t!r} href={a.get_attribute('href')}")

    # 「キーワード検索」をクリック
    clicked = False
    for a in driver.find_elements(By.TAG_NAME, "a"):
        if "キーワード検索" in a.text:
            a.click()
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            time.sleep(1.5)
            clicked = True
            break
    if not clicked:
        print("❌ キーワード検索リンクがTOPに無い")
        return

    print(f"\n=== キーワード検索ページ: {driver.current_url} ===")
    print("\n--- タブ候補（プロフィール） ---")
    for a in driver.find_elements(By.TAG_NAME, "a"):
        t = a.text.strip()
        if "プロフィール" in t or "掲示板" in t or "日記" in t:
            print(f"  text={t!r} href={a.get_attribute('href')}")

    # プロフィールタブをクリック
    for a in driver.find_elements(By.TAG_NAME, "a"):
        if a.text.strip() == "プロフィール" or "プロフィール" in a.text.strip():
            a.click()
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            time.sleep(1.5)
            break

    print(f"\n=== プロフィールタブ後: {driver.current_url} ===")
    print("\n--- 入力フォーム要素 ---")
    for inp in driver.find_elements(By.TAG_NAME, "input"):
        t = inp.get_attribute("type")
        n = inp.get_attribute("name")
        p = inp.get_attribute("placeholder")
        v = inp.get_attribute("value")
        print(f"  input type={t!r} name={n!r} placeholder={p!r} value={v!r}")
    for btn in driver.find_elements(By.TAG_NAME, "button"):
        print(f"  button text={btn.text!r}")

    print("\n--- form一覧 ---")
    for f in driver.find_elements(By.TAG_NAME, "form"):
        print(f"  form action={f.get_attribute('action')!r} method={f.get_attribute('method')!r}")


if __name__ == "__main__":
    main()

"""so1 (検索順) の option value と text を調査"""
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

    try:
        sel = driver.find_element(By.ID, "so1")
    except Exception:
        # 別のページかも
        for s in driver.find_elements(By.TAG_NAME, "select"):
            n = s.get_attribute("name")
            i = s.get_attribute("id")
            if n == "sort" or (i and "so" in i):
                print(f"候補select id={i} name={n}")
        return

    print(f"so1 name={sel.get_attribute('name')}")
    for o in sel.find_elements(By.TAG_NAME, "option"):
        print(f"  value={o.get_attribute('value')!r} text={o.text!r} selected={o.is_selected()}")


if __name__ == "__main__":
    main()

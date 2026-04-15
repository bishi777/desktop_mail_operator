"""タイプリストのHTML構造を確認するデバッグスクリプト"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import re
import settings

PORT = getattr(settings, "ikukuru_port", 9222)
TYPE_LIST_URL = "https://pc.194964.com/sns/snstype/show_typed_list.html"

options = Options()
options.add_experimental_option("debuggerAddress", f"127.0.0.1:{PORT}")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# 現在のタブを記憶してイククルのタブを探す
original_handle = driver.current_handle
found = False
for handle in driver.window_handles:
    driver.switch_to.window(handle)
    if "194964" in driver.current_url:
        found = True
        break

if not found:
    print("イククルのタブが見つかりません")
    exit()

print(f"現在のURL: {driver.current_url}")

# タイプリストページへ
driver.get(TYPE_LIST_URL)
wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
time.sleep(2)

# ページ全体のチェックボックスを確認
all_checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
print(f"\n=== チェックボックス数: {len(all_checkboxes)} ===")
for i, cb in enumerate(all_checkboxes):
    print(f"  [{i}] name={cb.get_attribute('name')}, value={cb.get_attribute('value')}, id={cb.get_attribute('id')}")

# 削除ボタンを確認
del_btns = driver.find_elements(By.XPATH, "//*[contains(text(),'削除')]")
print(f"\n=== 削除ボタン数: {len(del_btns)} ===")
for i, btn in enumerate(del_btns):
    print(f"  [{i}] tag={btn.tag_name}, text={btn.text}, class={btn.get_attribute('class')}")

# type-list-link の構造を確認
links = driver.find_elements(By.CLASS_NAME, value="type-list-link")
print(f"\n=== type-list-link数: {len(links)} ===")
for i, link in enumerate(links[:5]):  # 最初の5件
    link_text = link.text.replace('\n', ' | ')
    age_match = re.search(r'(\d+)歳', link.text)
    age = int(age_match.group(1)) if age_match else None
    print(f"\n  [{i}] age={age}, text={link_text[:80]}")

    # 親要素の構造を確認
    parent_html = driver.execute_script("""
        var el = arguments[0].parentElement;
        var html = el.outerHTML;
        // HTMLが長すぎる場合は最初の500文字
        return html.substring(0, 500);
    """, link)
    print(f"  親HTML: {parent_html[:300]}")

    # 親・祖父のチェックボックスを探す
    parent = link.find_element(By.XPATH, './..')
    cb_parent = parent.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
    print(f"  親のチェックボックス: {len(cb_parent)}")

    try:
        grandparent = parent.find_element(By.XPATH, './..')
        cb_grand = grandparent.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        print(f"  祖父のチェックボックス: {len(cb_grand)}")
    except:
        print(f"  祖父なし")

print("\n=== デバッグ完了 ===")

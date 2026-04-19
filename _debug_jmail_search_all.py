"""
Jmail 詳しく検索ページの全フィルタ項目を列挙するデバッグスクリプト。
使い方: python _debug_jmail_search_all.py <port>
"""
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def main():
  port = sys.argv[1] if len(sys.argv) > 1 else "9222"
  options = Options()
  options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
  driver = webdriver.Chrome(options=options)

  # mintj.comのタブに切り替え
  for h in driver.window_handles:
    driver.switch_to.window(h)
    if "mintj.com" in driver.current_url:
      break

  driver.get("https://mintj.com/msm/PfSearch/Search/?sid=")
  time.sleep(2)

  # 詳しく検索を展開
  ac2h2 = driver.find_elements(By.ID, "ac2h2")
  if ac2h2:
    driver.execute_script("arguments[0].click();", ac2h2[0])
    time.sleep(1)

  # すべてのアコーディオンヘッダ
  print("===== すべてのアコーディオン =====")
  acs = driver.find_elements(By.CSS_SELECTOR, "[id^='ac'],[id^='accordion']")
  for a in acs:
    aid = a.get_attribute("id")
    txt = (a.text or "").strip().replace("\n", " / ")[:80]
    tag = a.tag_name
    print(f"  [{aid}] <{tag}> {txt}")

  # すべてのアコーディオンを展開
  for a in acs:
    try:
      driver.execute_script("arguments[0].click();", a)
      time.sleep(0.2)
    except Exception:
      pass
  time.sleep(1)

  # すべてのcheckboxを列挙
  print("\n===== すべての checkbox input =====")
  cbs = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
  for cb in cbs:
    cid = cb.get_attribute("id") or ""
    name = cb.get_attribute("name") or ""
    value = cb.get_attribute("value") or ""
    # 近くのlabelテキスト
    label_txt = ""
    try:
      if cid:
        lbls = driver.find_elements(By.CSS_SELECTOR, f"label[for='{cid}']")
        if lbls:
          label_txt = (lbls[0].text or "").strip()
      if not label_txt:
        parent = cb.find_element(By.XPATH, "./..")
        label_txt = (parent.text or "").strip()[:40]
    except Exception:
      pass
    print(f"  id={cid!r:25} name={name!r:20} value={value!r:10} label={label_txt!r}")

  # すべてのselect
  print("\n===== すべての select =====")
  sels = driver.find_elements(By.CSS_SELECTOR, "select")
  for s in sels:
    sid = s.get_attribute("id") or ""
    name = s.get_attribute("name") or ""
    opts = s.find_elements(By.TAG_NAME, "option")
    opt_preview = " | ".join([f"{o.get_attribute('value')}:{(o.text or '').strip()}" for o in opts[:6]])
    print(f"  id={sid!r:25} name={name!r:20} options=[{opt_preview}]")

  # すべてのtext input (身長等の数値入力欄)
  print("\n===== すべての text/number input =====")
  txts = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='number']")
  for t in txts:
    tid = t.get_attribute("id") or ""
    name = t.get_attribute("name") or ""
    ph = t.get_attribute("placeholder") or ""
    parent_txt = ""
    try:
      parent = t.find_element(By.XPATH, "./../..")
      parent_txt = (parent.text or "").strip()[:60]
    except Exception:
      pass
    print(f"  id={tid!r:25} name={name!r:20} ph={ph!r:15} ctx={parent_txt!r}")


if __name__ == "__main__":
  main()

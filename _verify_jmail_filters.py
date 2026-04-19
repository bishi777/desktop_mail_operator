"""新しいfst検索フィルタロジックが動くか確認する検証スクリプト。"""
import sys
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def main():
  port = sys.argv[1] if len(sys.argv) > 1 else "9222"
  options = Options()
  options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
  driver = webdriver.Chrome(options=options)
  wait = WebDriverWait(driver, 10)

  for h in driver.window_handles:
    driver.switch_to.window(h)
    if "mintj.com" in driver.current_url:
      break

  name = "verify"
  driver.get("https://mintj.com/msm/PfSearch/Search/?sid=")
  wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
  time.sleep(1.5)

  detail_query = driver.find_elements(By.ID, 'ac2h2')
  if detail_query:
    driver.execute_script('arguments[0].click();', detail_query[0])
    time.sleep(1.5)

  def _check_ids(ids, label_for_log=None):
    selected_values = []
    for cid in ids:
      cbs = driver.find_elements(By.ID, cid)
      if not cbs:
        print(f"    [WARN] id={cid} NOT FOUND")
        continue
      cb = cbs[0]
      if not cb.is_selected():
        driver.execute_script('arguments[0].click();', cb)
        time.sleep(0.2)
      if cb.is_selected():
        selected_values.append(cb.get_attribute('value'))
      else:
        print(f"    [WARN] id={cid} click did not register selection")
    if label_for_log:
      print(f"  [{name}] {label_for_log}: {selected_values}")

  def _open_accordion(acc_id):
    els = driver.find_elements(By.ID, acc_id)
    if els:
      driver.execute_script('arguments[0].click();', els[0])
      time.sleep(0.6)

  _check_ids(['CheckAge1', 'CheckAge2', 'CheckAge3', 'CheckAge4'], '年齢')
  _check_ids(
    ['CheckHeight1', 'CheckHeight2', 'CheckHeight3', 'CheckHeight4', 'CheckHeight5'],
    '身長'
  )
  _check_ids(['f01'], '写真あり')
  _check_ids(['o01'], 'リッチ度')

  _open_accordion('accordion03')
  state_cbs = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][name='state']")
  for scb in state_cbs:
    if scb.is_selected():
      driver.execute_script('arguments[0].click();', scb)
      time.sleep(0.1)
  extra_area_id = random.choice([
    'CheckState-9', 'CheckState-10', 'CheckState-11',
    'CheckState-24', 'CheckState-14', 'CheckState-13',
  ])
  _check_ids(['CheckState-8', extra_area_id], '地域')

  _open_accordion('accordion04')
  _check_ids(
    ['CheckLooksType1', 'CheckLooksType4', 'CheckLooksType6',
     'CheckLooksType16', 'CheckLooksType17', 'CheckLooksType18'],
    'ルックス'
  )

  _open_accordion('accordion05')
  _check_ids(
    ['CheckCharacter1', 'CheckCharacter2', 'CheckCharacter5', 'CheckCharacter6',
     'CheckCharacter7', 'CheckCharacter10', 'CheckCharacter11'],
    '性格'
  )

  _open_accordion('accordion06')
  _occupation_exclude = {2, 14, 19, 31, 33}
  _check_ids(
    [f'CheckOccupation{n}' for n in range(1, 38) if n not in _occupation_exclude],
    '職業'
  )

  _open_accordion('accordion07')
  _purpose_exclude = {10, 14, 15, 19, 22, 24, 25, 27}
  _check_ids(
    [f'CheckPurpose{n}' for n in range(0, 28) if n not in _purpose_exclude],
    '目的'
  )

  print("\n===== 最終的にselected=Trueなcheckbox一覧 =====")
  all_cbs = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
  for cb in all_cbs:
    if cb.is_selected():
      print(f"  id={cb.get_attribute('id')!r:25} name={cb.get_attribute('name')!r:20} value={cb.get_attribute('value')!r}")


if __name__ == "__main__":
  main()

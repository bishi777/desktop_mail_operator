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
  _check_ids(['CheckHeight6', 'CheckHeight7', 'CheckHeight8'], '身長')
  _check_ids(
    ['CheckFigureStyle1', 'CheckFigureStyle2', 'CheckFigureStyle3',
     'CheckFigureStyle4', 'CheckFigureStyle5'],
    '体型'
  )
  _check_ids(['f01'], '写真あり')
  _check_ids(['o01'], 'リッチ度')

  _open_accordion('accordion03')
  area_id = random.choice(['CheckState-8', 'CheckState-9'])
  _check_ids([area_id], '地域')

  _open_accordion('accordion06')
  _check_ids(
    ['CheckOccupation1', 'CheckOccupation2', 'CheckOccupation3', 'CheckOccupation4',
     'CheckOccupation27', 'CheckOccupation29', 'CheckOccupation30',
     'CheckOccupation15', 'CheckOccupation31', 'CheckOccupation25'],
    '職業'
  )

  _open_accordion('accordion07')
  _check_ids(['CheckPurpose0', 'CheckPurpose1', 'CheckPurpose3'], '目的')

  print("\n===== 最終的にselected=Trueなcheckbox一覧 =====")
  all_cbs = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
  for cb in all_cbs:
    if cb.is_selected():
      print(f"  id={cb.get_attribute('id')!r:25} name={cb.get_attribute('name')!r:20} value={cb.get_attribute('value')!r}")


if __name__ == "__main__":
  main()

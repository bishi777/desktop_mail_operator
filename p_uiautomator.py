from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from appium.options.ios import SafariOptions
import time
import subprocess
from widget import func
import os
import settings
import traceback

user_data = func.get_user_data()
pcmax_datas = user_data["pcmax"]

for i in pcmax_datas:
  name = i["name"]
  if "haru" != name:
    continue
  login_id = i["login_id"]
  login_pass = i["password"]
  # Appium Safari Options 設定
  options = SafariOptions()
  options.set_capability("safariInitialUrl", "https://linkleweb.jp/pcm/login.php")
  # options.set_capability("safariInitialUrl", "https://pcmax.jp/pcm/?ad_id=unknown")
  options.set_capability("platformName", "iOS")
  options.set_capability("platformVersion", "18.5")
  options.set_capability("udid", settings.udid)
  options.set_capability("browserName", "Safari")
  options.set_capability("automationName", "XCUITest")

  # Appium 接続
  driver = webdriver.Remote("http://localhost:4723", options=options)
  wait = WebDriverWait(driver, 10)

  try:
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    print(777)
    time.sleep(10)
    # 「ログイン（登録済みの方）」ボタンをクリック
    login_form = driver.find_element(By.CLASS_NAME, 'login-sub')
    login_link = login_form.find_element(By.TAG_NAME, 'a')
    login_link.click()
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(3)
    # フォーム入力
    id_form = driver.find_element(By.ID, "login_id")
    id_form.send_keys(login_id)
    time.sleep(3)
    pass_form = driver.find_element(By.ID, "login_pw")
    pass_form.send_keys(login_pass)
    time.sleep(3)
    send_form = driver.find_element(By.NAME, "login")
    send_form.click()
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    print(f"{name} ✅ ログイン成功")
    time.sleep(5)
  except Exception as e:
    print(f"{name} ❌ ログイン処理でエラー:", e)
    traceback.print_exc()

  finally:
    # Appiumセッション終了
    driver.quit()
    # Simulator停止＋初期化
    print(f"{name} ⏹ Simulatorシャットダウン中...")
    subprocess.run(["xcrun", "simctl", "shutdown", settings.udid])
    print(f"{name} ♻️ Simulator初期化中...")
    subprocess.run(["xcrun", "simctl", "erase", settings.udid])
    subprocess.run(["osascript", "-e", 'quit app "Simulator"'])
    print(f"{name} ✅ 完了")

os.system("pkill -f appium")

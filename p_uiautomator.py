from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from appium.options.ios import SafariOptions
import time
import subprocess
from widget import func, pcmax_2, pcmax
import os
import settings
import traceback

user_data = func.get_user_data()
pcmax_datas = user_data["pcmax"]
linkle_chara = ["きりこ"]
# 地域選択（3つまで選択可能）
select_areas = [
    "東京都",
    # "千葉県",
    "埼玉県",
    "神奈川県",
    # "静岡県",
    # "新潟県",
    # "山梨県",
    # "長野県",
    # "茨城県",
    # "栃木県",
    # "群馬県",
]
youngest_age = 18
oldest_age = 31  
foot_cnt = 5

# === ① シミュレータをGUIなしで事前ブート（★追加） =========================
subprocess.run(["xcrun", "simctl", "boot", settings.udid], check=False)
# 任意: 万一 Simulator.app が開いてしまってもすぐ閉じる（★追加・任意）
subprocess.run(["osascript", "-e", 'tell application "Simulator" to quit'], check=False)
time.sleep(2)

try:
  while True:
    for i in pcmax_datas:
      name = i["name"]
      
      # if name not in ("ゆかり", "いおり"):
      #   continue
      login_id = i["login_id"]
      login_pass = i["password"]
      # Appium Safari Options 設定
      options = SafariOptions()
      if name in linkle_chara:
        options.set_capability("safariInitialUrl", "https://linkleweb.jp/pcm/login.php")
      else:
        options.set_capability("safariInitialUrl", "https://pcmax.jp/pcm/file.php?f=login_form")
      options.set_capability("platformName", "iOS")
      options.set_capability("udid", settings.udid)
      options.set_capability("browserName", "Safari")
      options.set_capability("automationName", "XCUITest")
      options.set_capability("autoDismissAlerts", True)   # ←自動で「閉じる」側を選ぶ


      # Appium 接続
      driver = webdriver.Remote("http://localhost:4723", options=options)
      wait = WebDriverWait(driver, 10)

      try:
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(1)
        # 「ログイン（登録済みの方）」ボタンをクリック
        login_form = driver.find_element(By.ID, 'login_id')
        login_form.send_keys(login_id)
        time.sleep(1)
        pass_form = driver.find_element(By.ID, 'login_pw')
        pass_form.send_keys(login_pass)
        time.sleep(6)
        send_form = driver.find_element(By.NAME, 'login')
        send_form.click()
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(2)
        if "member.php"in driver.current_url:
          print(f"{name} ✅ ログイン成功")
        pcmax.catch_warning_pop(name, driver,wait)
        my_menu = driver.find_element(By.CLASS_NAME, "sp-fl-mymenu")
        my_menu.click()
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(3)
        imahima_icon = driver.find_element(By.ID, "my_today_free")
        if 'free_off' in imahima_icon.get_attribute("style"):
          print("❌ いまヒマアイコンがオフになっています")
          imahima_icon.click()
          print("❌ いまヒマアイコンおんにしました")
          wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)
        # prof_serch_menu = driver.find_element(By.CLASS_NAME, "sp-fl-prof")
        # prof_serch_menu.click()
        # wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        # time.sleep(3)
        # pcmax.make_footprints(i, driver, wait, select_areas, youngest_age, oldest_age, foot_cnt)
        
      except Exception as e:
        print(f"{name} ❌ ログイン処理でエラー:", e)
        traceback.print_exc()
      
      finally:
        # Appiumセッション終了
        driver.delete_all_cookies()  # そのドメインの Cookie 全削除
        driver.execute_script("""
          try { localStorage.clear(); } catch(e) {}
          try { sessionStorage.clear(); } catch(e) {}
          try {
            if (window.indexedDB && indexedDB.databases) {
              indexedDB.databases().then(dbs => dbs.forEach(db => indexedDB.deleteDatabase(db.name)));
            }
          } catch(e) {}
        """)
        # driver.quit()
        # # Simulator停止＋初期化
        # print(f"{name} ⏹ Simulatorシャットダウン中...")
        # subprocess.run(["xcrun", "simctl", "shutdown", settings.udid])
        # print(f"{name} ♻️ Simulator初期化中...")
        # subprocess.run(["xcrun", "simctl", "erase", settings.udid])
        # subprocess.run(["osascript", "-e", 'quit app "Simulator"'])
        print(f"{name} ✅ 完了")
finally:
  # === ③ 終了時にシミュレータ停止＆初期化（★追加） =========================
    subprocess.run(["xcrun", "simctl", "shutdown", settings.udid], check=False)
    subprocess.run(["xcrun", "simctl", "erase", settings.udid], check=False)
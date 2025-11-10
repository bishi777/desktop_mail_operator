from appium import webdriver
from appium.options.ios import XCUITestOptions
import time

APPIUM_SERVER = "http://127.0.0.1:4723"

# --- ここにあなたの実機情報を設定 ---
device_name = "BishiのiPhone"        # xcrunで確認したデバイス名
udid = "00008130-0016682128A1401C"    # 実際のUDID
platform_version = "18.1"             # 実際のiOSバージョン
team_id = "2SG5GJJYNH"          # あなたのTeam ID
# --------------------------------------

# XCUITest用オプション
options = XCUITestOptions()
options.platform_name = "iOS"
options.device_name = device_name
options.udid = udid
options.platform_version = platform_version
options.automation_name = "XCUITest"
options.xcode_org_id = team_id
options.xcode_signing_id = "iPhone Developer"
options.bundle_id = "com.apple.mobilesafari"
options.set_capability("startIWDP", True)
options.set_capability("showXcodeLog", True)

# ドライバー起動
driver = webdriver.Remote(APPIUM_SERVER, options=options)

try:
    print("🚀 Safariを起動中...")
    driver.get("https://www.google.com")
    print("🌐 Googleを開きました！")
    time.sleep(5)

finally:
    print("🧹 終了処理中...")
    driver.quit()
    print("✅ 完了！")

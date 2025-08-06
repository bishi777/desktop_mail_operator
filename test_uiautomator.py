import subprocess
import re
import time
from appium import webdriver
from selenium.webdriver.common.by import By
from appium.options.ios import SafariOptions

# === ① iPhone 16 のUDIDを取得 ===
print("🔍 iPhone 16 のUDIDを探しています...")
output = subprocess.run(["xcrun", "simctl", "list", "devices"], capture_output=True, text=True).stdout
devices = re.findall(r"(iPhone 16.*) \(([-A-F0-9]+)\) \((Shutdown|Booted)\)", output)

if not devices:
    print("❌ iPhone 16 のシミュレータが見つかりません。Xcodeで追加してください。")
    exit(1)

device_name, udid, state = devices[0]
print(f"✅ {device_name} を使用します（UDID: {udid}）")

# === ② Simulator 起動 ===
if state != "Booted":
    print("🚀 シミュレータを起動中...")
    subprocess.run(["xcrun", "simctl", "boot", udid])
    time.sleep(5)  # Boot待ち

print("🖥 Simulator.app を起動中...")
subprocess.run(["open", "-a", "Simulator"])
time.sleep(5)

# === ③ Safari を開いて URL にアクセス ===
url = "https://pcmax.jp/pcm/?ad_id=unknown"
print(f"🌐 Safariを起動してアクセス中: {url}")
subprocess.run(["xcrun", "simctl", "openurl", udid, url])
time.sleep(5)  # ページ読み込み待ち

# === ④ Appiumでログインボタンをクリック ===

# === Desired Capabilities の設定 ===
options = SafariOptions()
options.set_platform_name("iOS")
options.set_platform_version("17.4")  # あなたの環境に合わせて
options.set_device_name("iPhone 16 Pro")
options.set_browser_name("Safari")
options.set_capability("automationName", "XCUITest")

# === Appium接続 ===
driver = webdriver.Remote(
    command_executor='http://localhost:4723',
    options=options
)

print("⌛ ページを待機中...")
time.sleep(5)

try:
    print("🔍 ログインボタンを探しています...")
    # ログインボタンを XPath またはテキストから特定（適宜調整）
    login_button = driver.find_element(By.XPATH, '//button[contains(., "ログイン")]')
    login_button.click()
    print("✅ ログインボタンをクリックしました！")
except Exception as e:
    print(f"❌ ログインボタンが見つかりませんでした: {e}")

driver.quit()

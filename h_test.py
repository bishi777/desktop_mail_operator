# windows_iphone_perfect.py  ← Windowsでだけ動かす用
import undetected_chromedriver as uc
import os

def iphone():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1")
    options.add_argument("--window-size=390,844")
    
    # Windowsではこれだけで自動ノイズが完璧に効く
    driver = uc.Chrome(options=options, version_main=None)
    
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
        "mobile": True,
        "width": 390,
        "height": 844,
        "deviceScaleFactor": 3,
        "fitWindow": False
    })
    
    return driver

driver = iphone()
driver.get("https://browserleaks.com/canvas")
input("見てみて！完璧なiPhone指紋が出てるはず！")
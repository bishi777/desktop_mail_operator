from appium.options.ios import SafariOptions
from appium import webdriver
from widget import happymail
from appium.options.ios import XCUITestOptions
import time

bishi_16 = "00008130-0016682128A1401C"
iphone7 = "3d67d84e9b8cd6c7a0a6ab93b5f984da5f1307e7"
name_ihone7 = "山本健太のiPhone7"
options = SafariOptions()

# caps = {
#     'platformName': 'iOS',
#     'automationName': 'XCUITest',
#     'deviceName': name_ihone7,
#     'udid': iphone7,
#     'bundleId': 'com.apple.mobilesafari',
#     "showXcodeLog": True,
#     'updatedWDABundleId': 'com.kenta.WebDriverAgentRunner'
# }

# options = XCUITestOptions().load_capabilities(caps)
options = SafariOptions()
options.set_capability("platformName", "iOS")
options.set_capability("deviceName", "山本健太のiPhone7")
options.set_capability("udid", "3d67d84e9b8cd6c7a0a6ab93b5f984da5f1307e7")
options.set_capability("automationName", "XCUITest")
options.set_capability("browserName", "Safari")
options.set_capability("safariAllowPopups", True)
options.set_capability("startIWDP", True)  # ←必要に応じて
options.set_capability("useNewWDA", True)  # ←初回はこれも有効に
options.set_capability("updatedWDABundleId", "com.kenta.WebDriverAgentRunner")
options.set_capability("xcodeOrgId", "2SG5GJJYNH")
options.set_capability("xcodeSigningId", "Apple Development")
options.set_capability("noReset", True)

driver = webdriver.Remote('http://localhost:4723', options=options)

# driver.get("https://www.google.co.jp")
# title = driver.execute_script("return document.title")


# driver.get('https://happymail.co.jp/')

# print("ページタイトル:", title)

# driver.find_element("xpath", "//header[@id='sp_header']/div/p[1]/a").click()
# password_field = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, "//input[@placeholder='パスワード']"))
# )

# # テスト用に値を入力
# password_field.send_keys("your_password_here")
# driver.find_element("xpath", "//input[@placeholder='電話番号／会員番号／メールアドレス']").send_keys("08028377704")
# driver.find_element("xpath", "//input[@placeholder='パスワード']").send_keys("ad3642")
# driver.find_element("xpath", "//input[@value='ログイン']").click()
# driver.quit()
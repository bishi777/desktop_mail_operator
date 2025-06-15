from appium.options.ios import SafariOptions
from appium import webdriver

options = SafariOptions()
options.set_capability("platformName", "iOS")
options.set_capability("platformVersion", "16.2")
options.set_capability("deviceName", "iPhone 14")
options.set_capability("automationName", "XCUITest")
options.set_capability("browserName", "Safari")

driver = webdriver.Remote("http://localhost:4723", options=options)

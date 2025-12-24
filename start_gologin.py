import requests
import time
from gologin import GoLogin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OTI2OTRjMjExODY3MzExN2Y3M2ZjMjYiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2OTI2YTJhNjZhMWI0NGE3OTEzM2NlYzcifQ.F8VKng9UTpAyVE7maKDSbaiFFCfoRGim2qQhyIlQME4"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

url = "https://api.gologin.com/browser/v2"
res = requests.get(url, headers=headers)
data = res.json()

for p in data["profiles"]:
    # print(p["name"], p["id"])
    # if p["name"] == "レイナ":
    #     print("Found profile ID:", p["id"])
    #     PROFILE_ID = p["id"]

    gl = GoLogin({
        "token": TOKEN,
        "profile_id": p["id"],
        # "port": 35000,  # 固定したい場合（競合するなら別ポート）
    })

    # GoLoginプロファイル起動（ローカルにデバッグポートが開く）
    debugger_address = gl.start()  # 例: "127.0.0.1:xxxxx" が返る想定
    print("debugger_address =", debugger_address)

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", debugger_address)
    service = Service(ChromeDriverManager(driver_version="141.0.7390.54").install())
    driver = webdriver.Chrome(service=service, options=chrome_options)


    driver.get("https://example.com")
    time.sleep(3)

# driver.quit()
# gl.stop()
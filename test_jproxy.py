import requests

proxy_user = "1erwovu4"
proxy_pass = "43zoykmw"
proxy_host = "210.48.225.248"
proxy_port = "3126"

proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"

proxies = {
    "http": proxy_url,
    "https": proxy_url,
}

try:
    r = requests.get(
        "https://api.ipify.org?format=json",
        proxies=proxies,
        timeout=15
    )
    print("接続成功")
    print("IP:", r.text)

except Exception as e:
    print("接続失敗")
    print(e)

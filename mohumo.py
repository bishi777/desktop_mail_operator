import cloudscraper
import time
scraper = cloudscraper.create_scraper()  # Cloudflareを回避するためのスクレイパーを作成
url = "https://pcmax.jp/pcm/file.php?f=login_form"

response = scraper.get(url)

if response.status_code == 200:
    print("Cloudflareを突破してページの取得に成功しました！")
else:
    print("アクセスに失敗しました。ステータスコード:", response.status_code)
time.sleep(10)
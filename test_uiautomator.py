import uiautomator2 as u2
import time

# d = u2.connect("a02aca5e")
d = u2.connect("e2448c60")
# d.app_start("jp.co.i_bec.suteki_happy")

# # ログインボタンをクリック
# d(resourceId="jp.co.i_bec.suteki_happy:id/fragment_start_btn_login").wait(timeout=5.0)
# d(resourceId="jp.co.i_bec.suteki_happy:id/fragment_start_btn_login").click()
# # ログインボタン2をクリック
# d(resourceId="jp.co.i_bec.suteki_happy:id/fragment_login_btn_login").wait(timeout=5.0)
# d(resourceId="jp.co.i_bec.suteki_happy:id/fragment_login_btn_login").click()

# ページのロードが終わる待て待機
loading_flug_ele = "jp.co.i_bec.suteki_happy:id/maintab_footer_image_message_off"
if d(resourceId=loading_flug_ele).wait(timeout=10.0):
  print("✅ ログイン後の画面が表示されました")
else:
  print("❌ ログイン後の画面が表示されませんでした（タイムアウト）")
loading_flug_ele = "jp.co.i_bec.suteki_happy:id/activity_maintab_loading_normal"
start = time.time()
while time.time() - start < 10:
  if not d(resourceId=loading_flug_ele).exists:
    print("✅ ログイン完了")
    break
  time.sleep(0.5)

# 新着メッセージはあるか
new_message_xpath = "jp.co.i_bec.suteki_happy:id/maintab_footer_badge_message"
if d.xpath(new_message_xpath).exists:
  print("✅ 新着メッセージは存在します")
else:
  print("❌ 新着メッセージは存在しません")
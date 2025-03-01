import time
from widget import happymail, func
import traceback

user_data = func.get_user_data()["happymail"][4]
driver,wait = func.test_get_driver(None, False)
wait_time = 1.5
happymail.login(user_data["name"], user_data["login_id"], user_data["password"], driver, wait,)

return_cnt = 0
mail_icon_cnt = 0
duplication_user = False
user_name_list = []
user_icon = 0
return_foot_img = ""
# if return_foot_img:
#   # 画像データを取得してBase64にエンコード
#   image_response = requests.get(return_foot_img)
#   image_base64 = base64.b64encode(image_response.content).decode('utf-8')
#   # ローカルに一時的に画像ファイルとして保存
#   image_filename = f"{name}_image.png"
#   with open(image_filename, 'wb') as f:
#       f.write(base64.b64decode(image_base64))
#   # 画像の保存パスを取得
#   image_path = os.path.abspath(image_filename)
# else:
#   image_path = ""
#   image_filename = None 
# # マッチング返し
matching_counted = 0
matching_cnt = 3
type_cnt = 3
image_path = ""
try:
  matching_counted = happymail.return_matching(user_data["name"], wait, wait_time, driver, user_name_list, duplication_user, user_data["fst_message"], image_path, matching_cnt)
  print(f"マッチング返し総数 {matching_counted}")
except Exception as e:  
  print("マッチング返しエラー")
  # print(traceback.format_exc())
  driver.get("https://happymail.co.jp/sp/app/html/mbmenu.php")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
  
# タイプ返し
type_counted = 0
try:
  type_counted = happymail.return_type(user_data["name"], wait, wait_time, driver, user_name_list, duplication_user, user_data["fst_message"], image_path, type_cnt)
  print(f"タイプ返し総数 {type_counted}")
except Exception as e:  
  print("タイプ返しエラー")
  print(traceback.format_exc())
  
finally:
  print(777)
  driver.get("https://happymail.co.jp/sp/app/html/mbmenu.php")
  wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
  time.sleep(wait_time)
      
print(f"メッセージ送信数　{return_cnt} {matching_counted} {type_counted}")
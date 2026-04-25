from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from widget import func, jmail
import settings
import time
import random
import requests
import traceback
import argparse
from datetime import datetime


user_data = func.get_user_data()
user_mail_info = [
  user_data['user'][0]['user_email'],
  user_data['user'][0]['gmail_account'],
  user_data['user'][0]['gmail_account_password'],
]
spare_mail_info = [
  "gifopeho@kmail.li",
  "siliboco68@gmail.com",
  "akkcxweqzdplcymh",
]
api_url = "https://meruopetyan.com/api/update-submitted-users/"


def _get_fst_time_slot(hour):
  if 6 <= hour < 8:
    return "morning"
  elif 18 <= hour < 20:
    return "evening"
  elif 20 <= hour < 22:
    return "night"
  return None


def _is_send_day(send_on="even"):
  yday = datetime.now().timetuple().tm_yday
  if send_on == "odd":
    return yday % 2 == 1
  return yday % 2 == 0


def _build_chara_info(i):
  """jmail_datasの1件から、check_mailが期待する辞書形式に変換"""
  return {
    "name": i["name"],
    "login_id": i["login_id"],
    "password": i["password"],
    "post_title": i.get("post_title", ""),
    "post_contents": i.get("post_contents", ""),
    "fst_message": i.get("fst_message", ""),
    "return_foot_message": i.get("return_foot_message", ""),
    "second_message": i.get("second_message", ""),
    "conditions_message": i.get("conditions_message", ""),
    "mail_img": i.get("chara_image", ""),
    "chara_image": i.get("chara_image", ""),
    "mail_address_image": i.get("mail_address_image", ""),
    "submitted_users": i.get("submitted_users", []),
    "young_submitted_users": i.get("young_submitted_users", []),
    "mail_address": i.get("mail_address", ""),
    "gmail_password": i.get("gmail_password", ""),
  }


def parse_args():
  p = argparse.ArgumentParser()
  p.add_argument("port", nargs="?", type=int, help="remote debugging port")
  p.add_argument("send_on", nargs="?", type=int, default=0, choices=[0, 1],
                 help="0=偶数日に送信, 1=奇数日に送信")
  args = p.parse_args()
  port = args.port if args.port is not None else getattr(settings, "jmail_port", None)
  send_on = "odd" if args.send_on == 1 else "even"
  return port, send_on


def main_syori():
  PORT, send_on = parse_args()
  jmail_datas = user_data["jmail"]

  options = Options()
  if PORT is not None:
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{PORT}")
  else:
    print("[INFO] No remote-debugging port provided. Launching Chrome normally.")
  driver = webdriver.Chrome(options=options)
  wait = WebDriverWait(driver, 10)

  loop_cnt = 0
  fst_sent_today = {}  # {name: {slot: date_str}}
  handle_chara_map = {}  # タブhandle → jmail_datasの1件

  while True:
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")

    if not (7 <= now.hour <= 23):
      time.sleep(60)
      continue

    mail_info = random.choice([user_mail_info, spare_mail_info])
    start_loop_time = time.time()
    handles = driver.window_handles
    print(f"タブ数:{len(handles)}")
    print("<<<<<<<ループスタート🏃‍♀️>>>>>>>")

    # アクティブキャラのリスト（tab順）
    tab_chara_list = []
    for handle in handles:
      try:
        driver.switch_to.window(handle)
        current_url = driver.current_url
      except WebDriverException as e:
        print(f"⚠️ タブクラッシュ検知、リロード試行: {e}")
        try:
          driver.refresh()
          time.sleep(3)
          current_url = driver.current_url
          print(f"  リロード成功: {current_url}")
        except Exception as e2:
          print(f"  リロード失敗、タブを閉じてスキップ: {e2}")
          try:
            driver.close()
          except Exception:
            pass
          continue
      except Exception:
        continue
      if "mintj.com" not in current_url:
        continue

      # キャラ名取得（ニックネーム編集ページから）
      matched_data = None
      try:
        driver.get("https://mintj.com/msm/MyProf/EditNickName/")
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(0.8)
        nick_input = driver.find_elements(By.NAME, "EditedNickNameText")
        if nick_input:
          nick = nick_input[0].get_attribute("value") or ""
          for ik in jmail_datas:
            if ik["name"] == nick.strip():
              matched_data = ik
              handle_chara_map[handle] = ik
              break
      except Exception as e:
        print(f"❌ キャラ名取得エラー: {e}")

      # 取得失敗時はhandle_chara_mapから復元
      if matched_data is None:
        matched_data = handle_chara_map.get(handle)
      if matched_data is None:
        # 再ログインを試みる
        try:
          name_candidates = [ik for ik in jmail_datas if ik["name"] not in [c["name"] for c in tab_chara_list]]
          if name_candidates:
            cand = name_candidates[0]
            print(f"  再ログイン試行: {cand['name']}")
            if jmail.login_jmail(driver, wait, cand["login_id"], cand["password"]):
              matched_data = cand
              handle_chara_map[handle] = cand
        except Exception as e:
          print(f"  再ログイン失敗: {e}")
      if matched_data is None:
        continue
      tab_chara_list.append(matched_data)

    # 各キャラ処理
    for chara_idx, i in enumerate(tab_chara_list):
      # 該当handleに切替
      target_handle = None
      for h, d in handle_chara_map.items():
        if d["name"] == i["name"] and h in handles:
          target_handle = h
          break
      if target_handle is None:
        continue
      try:
        driver.switch_to.window(target_handle)
      except Exception:
        continue

      name = i["name"]
      data = _build_chara_info(i)
      now = datetime.now()
      print(f"  📄 ---------- {name} ------------{now.strftime('%Y-%m-%d %H:%M:%S')}")

      # 1. 新着メールチェック
      young_submitted_users = data["young_submitted_users"]
      submitted_users = data["submitted_users"]
      try:
        check_start = time.time()
        young_submitted_users, submitted_users = jmail.check_mail(name, data, driver, wait, mail_info)
        print(f"  [{name}] check_mail完了 ({time.time()-check_start:.0f}秒)")
      except TimeoutException:
        print(f"  [{name}] check_mail TimeoutException")
        traceback.print_exc()
        try:
          driver.refresh()
          wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
          time.sleep(2)
        except Exception:
          pass
      except Exception as e:
        print(f"❌ {name} check_mailエラー: {e}")
        traceback.print_exc()
        # check_mail失敗でもfst送信処理は継続

      print(f"ループ回数: {loop_cnt}")

      # 2. fst送信判定（1日おき・時間帯別・各キャラそのスロット1回）
      time_slot = _get_fst_time_slot(now.hour)
      should_send_fst = False
      print(f"  [{name}] fst判定 hour={now.hour} slot={time_slot} send_day={_is_send_day(send_on)} sent_today={fst_sent_today.get(name, {})}")
      if _is_send_day(send_on) and time_slot:
        if name not in fst_sent_today:
          fst_sent_today[name] = {}
        for slot in list(fst_sent_today[name].keys()):
          if fst_sent_today[name][slot] != today_str:
            del fst_sent_today[name][slot]
        if time_slot not in fst_sent_today[name]:
          should_send_fst = True

      if should_send_fst:
        try:
          fst_message = i.get("fst_message", "")
          image_path = i.get("chara_image", "")
          sent_to, submitted_users = jmail.score_and_send_fst_message(
            name, driver, wait, fst_message, image_path,
            submitted_users=submitted_users,
            user_check_cnt=random.randint(7, 11)
          )
          if sent_to:
            print(f"  [{name}] fst送信完了: {sent_to}")
          fst_sent_today[name][time_slot] = today_str
        except Exception as e:
          print(f"  [{name}] fst送信エラー: {e}")
          traceback.print_exc()

      # 3. 送信履歴ユーザー更新
      payload = {
        "login_id": i["login_id"],
        "password": i["password"],
        "submitted_users": submitted_users,
        "young_submitted_users": young_submitted_users,
      }
      try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
          print(f"✅ {name} 送信済ユーザー更新成功")
        else:
          print(f"❌ {name} 送信済ユーザー更新失敗（{response.status_code}）")
      except requests.exceptions.RequestException as e:
        print("⚠️ 通信エラー:", e)
        traceback.print_exc()

    loop_cnt += 1
    elapsed_time = time.time() - start_loop_time
    wait_cnt = 0
    target_wait = random.randint(580, 860)
    while elapsed_time < target_wait:
      time.sleep(20)
      elapsed_time = time.time() - start_loop_time
      if wait_cnt % 3 == 0:
        print(f"待機中~~ {elapsed_time:.0f}s")
      wait_cnt += 1
    print("<<<<<<<<<<<<<ループ折り返し>>>>>>>>>>>>>>>>>>>>>")
    minutes, seconds = divmod(int(time.time() - start_loop_time), 60)
    print(f"タイム: {minutes}分{seconds}秒")


if __name__ == "__main__":
  try:
    main_syori()
  except KeyboardInterrupt:
    print("\n🛑 手動終了 (Ctrl + C) により処理を中断しました。")
  except Exception as e:
    print(f"\n❌ 予期せぬエラーが発生しました: {e}")
    traceback.print_exc()

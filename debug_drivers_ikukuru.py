from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import time
from widget import func, ikukuru
import settings
import random
import traceback
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import argparse


def reset_metrics_keep_check_date(d: dict) -> dict:
  metric_keys = ["fst", "rf", "check_first", "check_second", "gmail_condition", "check_more"]
  new_d = {}
  for name, v in (d or {}).items():
    if isinstance(v, dict):
      cd = v.get("check_date", None)
    else:
      cd = None
    new_d[name] = {k: 0 for k in metric_keys}
    new_d[name]["check_date"] = cd
  return new_d


# 検索フィルターはikukuru.py内のFIXED_SEARCH_FILTERで固定
# area（地域）のみブラウザ側で設定しておく
SEARCH_FILTER = None

# 掲示板投稿の時間帯スロット
BBS_SLOTS = [(6, 9), (9, 12), (14, 17), (17, 20), (20, 22)]

def get_bbs_slot(hour):
  for idx, (start, end) in enumerate(BBS_SLOTS):
    if start <= hour < end:
      return idx
  return None


def parse_args():
  p = argparse.ArgumentParser()
  p.add_argument("port", nargs="?", type=int, help="remote debugging port")
  p.add_argument("chara", nargs="?", type=str, help="対象キャラ名（指定時はそのタブのみ実行）")
  args = p.parse_args()
  port = args.port if args.port is not None else getattr(settings, "ikukuru_port", None)
  return port, args.chara


def main_syori():
  PORT, CHARA_FILTER = parse_args()
  if CHARA_FILTER:
    print(f"[INFO] 対象キャラを限定: {CHARA_FILTER}")
  user_data = func.get_user_data()
  user_mail_info = [
    user_data['user'][0]['user_email'],
    user_data['user'][0]['gmail_account'],
    user_data['user'][0]['gmail_account_password'],
  ]
  gmail_account = user_data['user'][0]['gmail_account']
  gmail_account_password = user_data['user'][0]['gmail_account_password']
  recieve_mailaddress = user_data['user'][0]['user_email']

  ikukuru_datas = user_data["ikukuru"]
  options = Options()

  if PORT is not None:
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{PORT}")
  else:
    print("[INFO] No remote-debugging port provided. Launching Chrome normally.")
  driver = webdriver.Chrome(options=options)
  wait = WebDriverWait(driver, 10)
  report_dict = {}
  send_flug = False
  roll_cnt = 1
  start_time = datetime.now()
  active_chara_list = []
  handle_chara_map = {}  # タブhandle → キャラデータのマッピング
  bbs_posted = {}  # {name: set(slot_idx)} 掲示板投稿済みスロット
  bbs_date = datetime.now().date()  # 日付変更検知用

  while True:
    start_loop_time = time.time()
    now = datetime.now()
    # 日付が変わったら掲示板投稿済みをリセット
    if now.date() != bbs_date:
      bbs_posted = {}
      bbs_date = now.date()
    try:
      handles = driver.window_handles
    except WebDriverException as e:
      print(f"❌ タブ列挙エラー（セッション切断？）: {e}")
      time.sleep(60)
      continue
    print(f"タブ数:{len(handles)}")
    print("<<<<<<<ループスタート🏃‍♀️🏃‍♀️🏃‍♀️🏃‍♀️🏃‍♀️>>>>>>>>>>>>>>>>>>>>>>>>>")

    net_down = False
    for idx, handle in enumerate(handles):
      try:
        driver.switch_to.window(handle)
        if "194964" not in driver.current_url:
          continue

        # PC版メニューページに移動して状態をリセット
        if driver.current_url != "https://pc.194964.com/menu.html":
          driver.get("https://pc.194964.com/menu.html")
          wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
          time.sleep(1.5)
      except WebDriverException as e:
        msg = str(e)
        if 'ERR_INTERNET_DISCONNECTED' in msg or 'ERR_NAME_NOT_RESOLVED' in msg or 'ERR_CONNECTION' in msg:
          print(f"⚠️ ネット切断検知 → 60秒待機して次ループへ: {msg.splitlines()[0]}")
          net_down = True
          break
        print(f"❌ タブ初期化エラー（スキップ）: {msg.splitlines()[0]}")
        continue

      # キャラ名取得（マイページから）
      try:
        driver.get("https://pc.194964.com/mypage.html")
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(1)
        name_elements = driver.find_elements(By.CLASS_NAME, value="profile-name")
        if not name_elements:
          print("イククル: キャラ名が取得できません → 再ログイン処理開始")
          try:
            # 再ログインリンクを探してクリック
            relogin_links = [el for el in driver.find_elements(By.TAG_NAME, 'a') if '再ログイン' in el.text]
            if not relogin_links:
              driver.get('https://pc.194964.com/other/error/show_nosession.html')
              wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
              time.sleep(1)
              relogin_links = [el for el in driver.find_elements(By.TAG_NAME, 'a') if '再ログイン' in el.text]
            if not relogin_links:
              print("  再ログインリンクが見つかりません")
              continue
            relogin_links[0].click()
            wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
            time.sleep(1.5)
            # タブマッピングからキャラを特定、なければメールアドレスで照合
            matched_data = handle_chara_map.get(handle)
            if matched_data is None:
              body_text = driver.find_element(By.TAG_NAME, 'body').text
              for ik in ikukuru_datas:
                if ik.get('login_mail_address', '') in body_text:
                  matched_data = ik
                  break
            if matched_data is None:
              print("  対象キャラを特定できません")
              continue
            print(f"  対象キャラ: {matched_data['name']}")
            pw_input = driver.find_element(By.ID, 'txtPassword')
            pw_input.clear()
            pw_input.send_keys(matched_data['password'])
            submit_btn = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"], button[type="submit"]')
            submit_btn.click()
            wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
            time.sleep(2)
            print(f"  再ログイン完了: {matched_data['name']}")
          except Exception as re_e:
            print(f"  再ログインエラー: {re_e}")
          continue
        name_on_ikukuru = name_elements[0].text.strip()
        # キャラ名フィルターが指定されていれば、それ以外はスキップ
        if CHARA_FILTER and name_on_ikukuru != CHARA_FILTER:
          print(f"  スキップ（対象外キャラ: {name_on_ikukuru}）")
          continue
        # タブhandle → キャラデータのマッピングを保存
        for ik in ikukuru_datas:
          if ik['name'] == name_on_ikukuru:
            handle_chara_map[handle] = ik
            break
        now = datetime.now()
        print(f"~~~~~~~~~~~{idx+1}キャラ目:{name_on_ikukuru}~~~~~{now.strftime('%m-%d %H:%M:%S')}~~~~~~~~~~")
      except Exception as e:
        print(f"❌ キャラ名取得エラー: {e}")
        traceback.print_exc()
        continue

      # キャラデータと照合
      for i in ikukuru_datas:
        if name_on_ikukuru != i['name']:
          continue

        if name_on_ikukuru not in active_chara_list:
          active_chara_list.append(name_on_ikukuru)
        if name_on_ikukuru not in report_dict:
          report_dict[name_on_ikukuru] = {
            "fst": 0, "rf": 0, "check_first": 0, "check_second": 0,
            "gmail_condition": 0, "check_more": 0, "check_date": None
          }

        name = i["name"]
        fst_message = i["fst_message"]
        return_foot_message = i.get("return_foot_message", "")
        chara_image = i.get("chara_image", "")
        footprint_count = random.randint(7, 12)

        if 6 <= now.hour < 24:
          # 1. 新着メールチェック
          try:
            print("✅新着メールチェック開始")
            check_first, check_second, gmail_condition, _ = ikukuru.check_mail(
              driver, wait, i, gmail_account, gmail_account_password, recieve_mailaddress
            )
            print("新着メールチェック終了✅")
            report_dict[name]["check_first"] += check_first
            report_dict[name]["check_second"] += check_second
            report_dict[name]["gmail_condition"] += gmail_condition
          except Exception as e:
            print(f"{name}❌ メールチェックエラー: {e}")
            traceback.print_exc()

          # 2. 足跡返し
          if return_foot_message:
            try:
              print("🐾足跡返し開始")
              rf_cnt = ikukuru.return_foot(driver, wait, return_foot_message, name, send_cnt=1, chara_image=chara_image)
              report_dict[name]["rf"] += rf_cnt
              print(f"足跡返し終了 {rf_cnt}件🐾")
            except Exception as e:
              print(f"{name}❌ 足跡返しエラー: {e}")
              traceback.print_exc()

          # 3. タイプ返し + fst
          try:
            print("💕タイプ返し+fst開始")
            rt_cnt = ikukuru.return_type(driver, wait, fst_message, name, send_cnt=1, chara_image=chara_image)
            report_dict[name]["fst"] += rt_cnt
            print(f"タイプ返し+fst終了 {rt_cnt}件💕")
          except Exception as e:
            print(f"{name}❌ タイプ返しエラー: {e}")
            traceback.print_exc()

          # 4. 足跡付け
          try:
            print(f"🐾🐾足跡付け開始 {footprint_count}件🐾🐾")
            ikukuru.make_footprint(driver, wait, name, footprint_count, SEARCH_FILTER)
          except Exception as e:
            print(f"{name}❌ 足跡付けエラー: {e}")
            traceback.print_exc()

          # 5. 掲示板投稿（時間帯スロットごとに1回）
          slot_idx = get_bbs_slot(now.hour)
          if slot_idx is not None:
            if name not in bbs_posted:
              bbs_posted[name] = set()
            if slot_idx not in bbs_posted[name]:
              try:
                print("📝掲示板投稿開始")
                result = ikukuru.post_bbs(i, driver, wait)
                if result:
                  bbs_posted[name].add(slot_idx)
                print("掲示板投稿終了📝")
              except Exception as e:
                print(f"{name}❌ 掲示板投稿エラー: {e}")
                traceback.print_exc()

        # 進捗報告
        if now.hour in (10, 14, 18, 22):
          if send_flug:
            try:
              body = func.format_progress_mail(report_dict, now)
              func.send_mail(
                body,
                user_mail_info,
                f"イククル 6時間の進捗報告  開始時間：{start_time.strftime('%Y-%m-%d %H:%M:%S')}",
              )
              send_flug = False
              report_dict = reset_metrics_keep_check_date(report_dict)
              start_time = datetime.now()
            except Exception as e:
              print(f"{name}❌ 進捗報告エラー: {e}")
              traceback.print_exc()
        else:
          send_flug = True

    if net_down:
      time.sleep(60)
      continue

    elapsed_time = time.time() - start_loop_time
    wait_cnt = 0
    while elapsed_time < 600:
      time.sleep(10)
      elapsed_time = time.time() - start_loop_time
      if wait_cnt % 6 == 0:
        print(f"待機中~~ {elapsed_time:.0f}s ")
      wait_cnt += 1
    print("🎉🎉🎉<<<<<<<<<<<<<ループ終了>>>>>>>>>>>>>>>>>>>>>🎉🎉🎉")
    elapsed_time = time.time() - start_loop_time
    minutes, seconds = divmod(int(elapsed_time), 60)
    print(f"🏁🏁🏁タイム: {minutes}分{seconds}秒　🏁🏁🏁")
    roll_cnt += 1


if __name__ == "__main__":
  try:
    main_syori()
  except KeyboardInterrupt:
    print("\n🛑 手動終了 (Ctrl + C) により処理を中断しました。安全に終了します。")
  except Exception as e:
    print(f"\n❌ 予期せぬエラーが発生しました: {e}")
    traceback.print_exc()

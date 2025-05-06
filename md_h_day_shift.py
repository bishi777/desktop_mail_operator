from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import random
import time
from selenium.webdriver.common.by import By
import os
import sys
from widget import pcmax, happymail, func
from selenium.webdriver.support.ui import WebDriverWait
import traceback
from datetime import timedelta
# from sb_p_repost import pcmax_repost


def md_h_all_do(matching_cnt, type_cnt, return_foot_cnt,  mail_info, drivers):
  verification_flug = func.get_user_data()
  if not verification_flug:
    return
  def timer(sec, functions):
    start_time = time.time() 
    for func in functions:
      try:
        return_func = func()
      except Exception as e:
        print(e)
        return_func = 0
    elapsed_time = time.time() - start_time  # 経過時間を計算する
    while elapsed_time < sec:
      time.sleep(30)
      elapsed_time = time.time() - start_time  # 経過時間を計算する
      # print(f"待機中~~ {elapsed_time} ")
    return return_func
  
  wait_cnt = 7200 / len(drivers)
  start_one_rap_time = time.time() 
  return_cnt_list = []
  rollong_flug = False
  try:
    for name, data in drivers.items():
      driver = drivers[name]["driver"]
      wait = drivers[name]["wait"]
      fst_message = drivers[name]["fst_message"]
      return_foot_message = drivers[name]["return_foot_message"]
      mail_img = drivers[name]["mail_img"]
      post_title = drivers[name]["post_title"]
      post_contents = drivers[name]["post_contents"]
      # repost
      try:
        repost_flug = happymail.re_post(name, driver, wait, post_title, post_contents, rollong_flug)
      except Exception as e:
        print(f"ハッピーメール掲示板エラー{name}")
        print(traceback.format_exc())
        func.send_error(f"ハッピーメール掲示板エラー{name}", traceback.format_exc())
      return_func = timer(wait_cnt, [lambda: happymail.return_footpoint(name, driver, wait, return_foot_message, matching_cnt, type_cnt, return_foot_cnt, mail_img, fst_message, rollong_flug)])
      if isinstance(return_func, str):
          return_cnt_list.append(f"{name}: {return_func}")
      elif isinstance(return_func, list):
          return_cnt_list.append(f"{name}: {return_func}")
      if repost_flug:
        return_cnt_list.append(repost_flug)
  except Exception as e:
    print(f"エラー{name}")
    print(traceback.format_exc())
    func.send_error(f"足跡返しエラー{name}", traceback.format_exc())
  except KeyError:
    print(f"⚠️'{name}'のブラウザが見つかりませんでした。処理をスキップします。")
  # finally:
  #   # 正常終了時・エラー終了時を問わず、最後に WebDriver を閉じる
  #   print('finaly----------------------------')
  #   print(drivers)
  #   func.close_all_drivers(drivers)
  #   os._exit(0)

  elapsed_time = time.time() - start_one_rap_time  
  elapsed_timedelta = timedelta(seconds=elapsed_time)
  elapsed_time_formatted = str(elapsed_timedelta)
  print(f"<<<<<<<<<<<<<サイト回し一周タイム： {elapsed_time_formatted}>>>>>>>>>>>>>>>>>>")
  return_cnt_list.append(f"サイト回し一周タイム： {elapsed_time_formatted}")
 
  # リストをフラットにする関数
  def flatten(lst):
    for item in lst:
      if isinstance(item, list):
        yield from flatten(item)
      else:
        yield item
  str_return_cnt_list = ",\n".join([str(item) for item in flatten(return_cnt_list)])
  
  if len(mail_info) and mail_info[0] != "" and mail_info[1] != "" and mail_info[2] != "":
    title = "ハッピーメールサイト回し件数"
    func.send_mail(str_return_cnt_list, mail_info, title)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    return_foot_cnt = 18
  elif len(sys.argv) >= 2:
    return_foot_cnt = int(sys.argv[1])
  user_data =   func.get_user_data()
  mailaddress = user_data['user'][0]['gmail_account']
  gmail_password = user_data['user'][0]['gmail_account_password']
  receiving_address = user_data['user'][0]['user_email']
  mail_info = None
  if mailaddress and gmail_password and receiving_address:
    mail_info = [
      receiving_address, mailaddress, gmail_password, 
    ]
  happy_chara_list = user_data["happymail"]
  headless = False
  base_path = "./chrome_profiles/h_scheduler"
  drivers = happymail.start_the_drivers_login(mail_info, user_data["happymail"], headless, base_path, False)
  md_h_all_do(3, 3, return_foot_cnt,  mail_info, drivers)
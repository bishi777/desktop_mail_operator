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


def md_h_all_do(matching_cnt, type_cnt, return_foot_cnt, happy_chara_list, headless, mail_info, drivers):
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
  
  wait_cnt = 7200 / len(happy_chara_list)

  start_one_rap_time = time.time() 
  return_cnt_list = []

  for happy_chara in happy_chara_list:
    if happy_chara['name'] != "めあり" and happy_chara['name'] != "きりこ":
      continue
    name = happy_chara['name']
    driver = drivers[name]["driver"]
    wait = drivers[name]["wait"]
    fst_message = drivers[name]["fst_message"]
    return_foot_message = drivers[name]["return_foot_message"]
    mail_img = drivers[name]["mail_img"]
    try:
      return_func = timer(wait_cnt, [lambda: happymail.return_footpoint(name, driver, wait, return_foot_message, matching_cnt, type_cnt, return_foot_cnt, mail_img, fst_message)])
      if isinstance(return_func, str):
          return_cnt_list.append(f"{happy_chara['name']}: {return_func}")
      elif isinstance(return_func, list):
          return_cnt_list.append(f"{happy_chara['name']}: {return_func}")
    except Exception as e:
      print(f"エラー{happy_chara[0]}")
      print(traceback.format_exc())
      func.send_error(f"足跡返しエラー{name}", traceback.format_exc())
    
     
  elapsed_time = time.time() - start_one_rap_time  
  elapsed_timedelta = timedelta(seconds=elapsed_time)
  elapsed_time_formatted = str(elapsed_timedelta)
  print(f"<<<<<<<<<<<<<サイト回し一周タイム： {elapsed_time_formatted}>>>>>>>>>>>>>>>>>>")
  return_cnt_list.append(f"サイト回し一周タイム： {elapsed_time_formatted}")
  str_return_cnt_list = ",\n".join(return_cnt_list)
  
  if len(mail_info) and mail_info[0] != "" and mail_info[1] != "" and mail_info[2] != "":
    title = "ハッピーメールサイト回し件数"
    func.send_mail(str_return_cnt_list, mail_info, title)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    return_foot_cnt = 18
  elif len(sys.argv) >= 2:
    return_foot_cnt = int(sys.argv[1])
  happy_chara_list = func.get_user_data()["happymail"]
  headless = True
  drivers = {}
  md_h_all_do(return_foot_cnt, happy_chara_list, headless, drivers)
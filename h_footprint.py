import tkinter as tk
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import random
import time
from selenium.webdriver.common.by import By
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from selenium.webdriver.support.ui import WebDriverWait
import traceback
from widget import happymail, func
import sqlite3
from selenium.webdriver.chrome.service import Service
from datetime import timedelta
from tkinter import messagebox
from selenium.common.exceptions import NoSuchWindowException
import signal

def signal_handler(signum, frame):
    print("SIGINT")
    sys.exit()


def happymail_footprints(headless, foot_cnt):
    user_data = func.get_user_data()
    happy_user_list = []
    if not user_data:
        return
    if user_data == 2:
        print("ユーザーデータを登録してください。")
        return
    for h_chara_data in user_data["happymail"]:
        happy_user_list.append([h_chara_data['name'], h_chara_data['login_id'], h_chara_data['password']])
   
    for i in range(9999):
        driver,wait = func.get_driver(headless)
        verification_flug = func.get_user_data()
        if not verification_flug:
            return
        if len(driver.window_handles) == 0:  # ウィンドウが閉じられたか確認
            print("ブラウザウィンドウが閉じられました。プロセスを終了します。")
            driver.quit()
            sys.exit(0)
            
        start_time = time.time()
        for user_list in happy_user_list:
            if user_list[1] is None or user_list[1] == "":
                print(f"{user_list[0]}:ログインIDが正しくありません")
                continue
            try:
                
                happymail.make_footprints(user_list[0], user_list[1], user_list[2], driver, wait, foot_cnt)
            except NoSuchWindowException:
                pass
            
            except Exception as e:
                print(f"{user_list[0]}:")
                print(traceback.format_exc())
            finally:
                if len(driver.window_handles) == 0:  # ウィンドウが閉じられたか確認
                    print("ブラウザウィンドウが閉じられました。プロセスを終了します。")
                    driver.quit()
                    sys.exit(0)
        driver.quit()
        time.sleep(1)        
        elapsed_time = time.time() - start_time
        elapsed_timedelta = timedelta(seconds=elapsed_time)
        elapsed_time_formatted = str(elapsed_timedelta)
        print(f"<<<<<<<<<<<<<経過時間 {elapsed_time_formatted}>>>>>>>>>>>>>>>>>>")

def run_script():
    foot_cnt = int(entry.get())
    headless = check_var.get()
    
    root.withdraw()  # 実行ボタンを押した時にウィンドウを非表示にする
    root.update()  # Tkinterのイベントループを更新
    happymail_footprints(headless, foot_cnt)

def populate_user_listbox():
    user_data = func.get_user_data()
    if user_data == 2:
        return
    happy_user_list = []
    if not user_data:
        return
    for h_chara_data in user_data["happymail"]:
        happy_user_list.append(f"{h_chara_data['name']}")
    
    listbox.delete(0, tk.END)
    for user in happy_user_list:
        listbox.insert(tk.END, user)


# Tkinter ウィンドウの設定
root = tk.Tk()
root.title("ハピメ足跡付け")

# キャラリストの表示
listbox_label = tk.Label(root, text="キャラリスト:")
listbox_label.pack()

listbox = tk.Listbox(root, height=10)
listbox.pack()

# 入力フォーム
entry_label = tk.Label(root, text="一度につける足跡数:")
entry_label.pack()
entry = tk.Entry(root, width=5)  
entry.pack()

# フレームの作成
frame = tk.Frame(root)
frame.pack()

# チェックボックスとラベルをフレーム内に配置
check_label = tk.Label(frame, text="ウィンドウを表示しない")
check_label.pack(side="left")

check_var = tk.BooleanVar(value=True)
check_button = tk.Checkbutton(frame, variable=check_var)
check_button.pack(side="left")

# 実行ボタン
run_button = tk.Button(root, text="実行", command=run_script)
run_button.pack()

# ユーザーリストの読み込み
populate_user_listbox()


try:
    root.mainloop()
except KeyboardInterrupt:
    print("\nKeyboardInterrupt in mainloop. Exiting...")
    root.quit()
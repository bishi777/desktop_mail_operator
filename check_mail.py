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
import s_check_mail_hp2
import sqlite3
from selenium.webdriver.chrome.service import Service
from datetime import timedelta
from tkinter import messagebox
from selenium.common.exceptions import NoSuchWindowException
import signal

def signal_handler(signum, frame):
    print("SIGINT")
    sys.exit()

global user_data 
user_data = func.get_user_data()

def check_mail_hpj(headless): 
    check_mail_flug = user_data["user"][0]['check_mail']
    if not check_mail_flug:
        print("有効期限が切れています。")
        return
    if not user_data:
        return
    if user_data == 2:
        print("ユーザーデータを登録してください。")
        return
    s_check_mail_hp2.check_mail(user_data, headless)
        
def run_script():
    headless = check_var.get()
    root.withdraw()  # 実行ボタンを押した時にウィンドウを非表示にする
    root.update()  # Tkinterのイベントループを更新
    check_mail_hpj(headless)

def populate_user_listbox():
    
    if user_data == 2:
        return
    happy_user_list = []
    pcmax_user_list = []

    if not user_data:
        return
   
    for p_chara_data in user_data["pcmax"]:
        pcmax_user_list.append(f"{p_chara_data['name']}")
    for h_chara_data in user_data["happymail"]:
        happy_user_list.append(f"{h_chara_data['name']}")

    happy_listbox.delete(0, tk.END)
    pcmax_listbox.delete(0, tk.END)
    
    # ハッピーキャラリストにデータを追加
    for user in happy_user_list:
        happy_listbox.insert(tk.END, user)

    # PCMAXキャラリストにデータを追加
    for user in pcmax_user_list:
        pcmax_listbox.insert(tk.END, user)
    

# Tkinter ウィンドウの設定
root = tk.Tk()
root.title("新着メールチェック")

# ハッピーキャラリストの表示
happy_listbox_label = tk.Label(root, text="ハッピーキャラリスト:")
happy_listbox_label.pack()

happy_listbox = tk.Listbox(root, height=8)  
happy_listbox.pack(padx=10, pady=(0, 10))  # 最後のキャラの下に少し余白

# PCMAXキャラリストの表示
pcmax_listbox_label = tk.Label(root, text="PCMAXキャラリスト:")
pcmax_listbox_label.pack()

pcmax_listbox = tk.Listbox(root, height=8)  
pcmax_listbox.pack(padx=10, pady=(0, 10))  # 少し余白

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

# Tkinter メインループの開始
root.mainloop()

import tkinter as tk
from tkinter import messagebox
from apscheduler.schedulers.blocking import BlockingScheduler
import os
import sys
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sb_h_day_shift import sb_h_all_do
from widget import func, pcmax
from sb_h_day_shift import sb_h_all_do
import sqlite3
from selenium.common.exceptions import WebDriverException
import requests
from requests.exceptions import HTTPError
import signal

def signal_handler(signum, frame):
    print("SIGINT")
    sys.exit()

global user_data
user_data = func.get_user_data()

# Tkinter ウィンドウの設定
root = tk.Tk()
root.title("スケジューラ設定")

def run_scheduler():
    global user_data  
    mail_info = [
        user_data["user"][0]["user_email"],
        user_data["user"][0]["gmail_account"],
        user_data["user"][0]["gmail_account_password"],
    ]
    pcmax_chara_list = [listbox.get(i) for i in range(listbox.size())]  # リストボックスからキャラリストを取得
    headless = check_var.get()  # チェックボックスの値を取得
    one_four_flug = one_hour_var.get()
    send_limit = send_count_var.get()
    if int(send_limit) > 20:
        print("送信の上限は20件以内に設定してください")
        return
    
    # pcmax_chara_list の順番に基づいて user_data["pcmax"] を並べ替える
    sorted_pcmax = []
    for chara_name in pcmax_chara_list:
        for p_chara_data in user_data["pcmax"]:
            if p_chara_data['name'] == chara_name:
                sorted_pcmax.append(p_chara_data)
                break    
    
    root.withdraw()  # 実行ボタンを押した時にウィンドウを非表示にする
    root.update()  # Tkinterのイベントループを更新
    # root.quit()
    pcmax.returnfoot_fst_one_rap(sorted_pcmax, headless, send_limit, one_four_flug, mail_info)
    
def populate_user_listbox():
    global user_data  # グローバル変数に代入
    pcmax_chara_list = []
    
    if not user_data:
        return
    for p_chara_data in user_data["pcmax"]:
        pcmax_chara_list.append(f"{p_chara_data['name']}")
    
    listbox.delete(0, tk.END)
    for user in pcmax_chara_list:
        listbox.insert(tk.END, user)

def on_drag_start(event):
    widget = event.widget
    widget.start_index = widget.nearest(event.y)

def on_drag_motion(event):
    widget = event.widget
    widget.activate(widget.nearest(event.y))

def on_drag_end(event):
    widget = event.widget
    end_index = widget.nearest(event.y)
    if end_index != widget.start_index:
        # 元の位置と新しい位置のアイテムを入れ替える
        item = widget.get(widget.start_index)
        widget.delete(widget.start_index)
        widget.insert(end_index, item)

# ユーザーリストの表示
listbox_label = tk.Label(root, text="キャラリスト:")
listbox_label.grid(row=0, column=0, columnspan=6)

listbox = tk.Listbox(root, height=10)
listbox.grid(row=1, column=0, columnspan=6)

# リストボックスでドラッグアンドドロップを有効にする
listbox.bind('<Button-1>', on_drag_start)
listbox.bind('<B1-Motion>', on_drag_motion)
listbox.bind('<ButtonRelease-1>', on_drag_end)


pcmax_times = user_data["user"][0]["p_schedule_time"]
user_info_list = [["", "",] for _ in range(6)]  
if pcmax_times is not None:
    for i in range(len(pcmax_times)):
        split_data = pcmax_times[i].split(":")  # ":"で分割
        for j in range(len(split_data)):
            user_info_list[i][j] = split_data[j]  # 分割されたデータを正しい位置に挿入


# 新しいフレームに「1時間の送信数」を追加
send_count_frame = tk.Frame(root)
send_count_frame.grid(row=6, column=0, columnspan=6, pady=10)

send_count_label = tk.Label(send_count_frame, text="1時間の送信上限:")
send_count_label.pack(side="left")

# Spinboxで数値入力 (0から20まで)
send_count_var = tk.IntVar(value=0)
send_count_spinbox = tk.Spinbox(send_count_frame, from_=0, to=20, textvariable=send_count_var, width=5)
send_count_spinbox.pack(side="left")

# 新しいフレームにチェックボックスとラベルを配置
check_frame = tk.Frame(root)
check_frame.grid(row=7, column=0, columnspan=6, pady=10)
check_label = tk.Label(check_frame, text="１時間後に実行")
check_label.pack(side="left")

one_hour_var = tk.BooleanVar(value=True)
check_button = tk.Checkbutton(check_frame, variable=one_hour_var)
check_button.pack(side="left")

# 新しいフレームにチェックボックスとラベルを配置
check_frame = tk.Frame(root)
check_frame.grid(row=8, column=0, columnspan=6, pady=10)
check_label = tk.Label(check_frame, text="ウィンドウを表示しない")
check_label.pack(side="left")

check_var = tk.BooleanVar(value=True)
check_button = tk.Checkbutton(check_frame, variable=check_var)
check_button.pack(side="left")

# 実行ボタン
run_button = tk.Button(root, text="実行", command=run_scheduler)
run_button.grid(row=9, column=0, columnspan=6, pady=10)

# ユーザーリストの読み込み
populate_user_listbox()

# Tkinter メインループの開始
root.mainloop()

import tkinter as tk
from tkinter import messagebox
from apscheduler.schedulers.blocking import BlockingScheduler
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from widget import func
from sb_h_day_shift import sb_h_all_do
import sqlite3
from selenium.common.exceptions import WebDriverException
import requests
from requests.exceptions import HTTPError


conn = sqlite3.connect('user_data.db')
c = conn.cursor()
global user_data
user_data = func.get_user_data()

# フォームを追加するためのカウンタ
form_count = 0
max_forms = 6

# Tkinter ウィンドウの設定
root = tk.Tk()
root.title("スケジューラ設定")

driver = None  # グローバルにドライバを定義

def start_scheduler(schedule_data, happy_chara_list, headless):
    if not user_data:
        return
    global driver
    
    mail_info = [
        user_data["user"][0]["user_email"],
        user_data["user"][0]["gmail_account"],
        user_data["user"][0]["gmail_account_password"],
    ]
    scheduler = BlockingScheduler()
    
    api_url = "https://meruopetyan.com/api/user-data/"
    # DEBUG
    # api_url = "http://127.0.0.1:8000/api/user-data/"
    # スケジュールデータを文字列に変換して保存
    schedule_strings = [f"{hour}:{minute}:{match_args}:{type_args}:{args}" for (hour, minute, match_args, type_args, args) in schedule_data]
    try:
        user_id = user_data["user"][0]["user"]
        update_data = {
            "h_schedule_time": schedule_strings
        }

        response = requests.patch(f"{api_url}{user_id}/", json=update_data)
        response.raise_for_status()
        # print(f"UserProfileが更新されました: {response.json()}")
    
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    
    for data in schedule_data:
        hour, minute, match_args, type_args, args = data
        scheduler.add_job(
            sb_h_all_do, 
            'cron', 
            hour=int(hour), 
            minute=int(minute), 
            args=[int(match_args), int(type_args), int(args), happy_chara_list, headless, mail_info], 
            max_instances=2, 
            misfire_grace_time=60*60
        )
        print(f"スケジュール設定: {hour}時{minute}分, マッチング返し{match_args}件, タイプ返し{type_args}件, 足跡返し件数{args}件")

    print("Ctrl+{0} を押すと終了します。".format('Break' if os.name == 'nt' else 'C'))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    except WebDriverException as e:
        error_message = str(e)
        if "unexpectedly exited. Status code was: -9" in error_message:
            print("Chromedriverが予期せず終了しました。再起動して起動してください。")
            driver.quit()
    finally:
        if driver:
            driver.quit()
            print("Chromedriver has been closed.")

def run_scheduler():
    global user_data  
    schedule_data = []
    happy_chara_list = [listbox.get(i) for i in range(listbox.size())]  # リストボックスからキャラリストを取得
    headless = check_var.get()  # チェックボックスの値を取得
    
    # happy_chara_list の順番に基づいて user_data["happymail"] を並べ替える
    sorted_happymail = []
    for chara_name in happy_chara_list:
        for h_chara_data in user_data["happymail"]:
            if h_chara_data['name'] == chara_name:
                sorted_happymail.append(h_chara_data)
                break    
    for i in range(form_count):
        hour = hour_vars[i].get()
        minute = minute_vars[i].get()
        match_args = match_vars[i].get()
        type_args = type_vars[i].get() 
        args = args_vars[i].get()

        schedule_data.append((hour, minute, match_args, type_args, args))

    root.withdraw()  # 実行ボタンを押した時にウィンドウを非表示にする
    root.update()  # Tkinterのイベントループを更新
    # root.quit()
    start_scheduler(schedule_data, sorted_happymail, headless)

def add_form(user_info_list):
    global form_count
    if form_count >= max_forms:
        return  

    # 新しい入力フォームを追加
    hour_var = tk.IntVar()
    hour_menu = tk.OptionMenu(frame, hour_var, *range(24))  # 時間0〜23
    hour_menu.grid(row=form_count, column=0, pady=2)
    hour_entries.append(hour_menu)
    hour_vars.append(hour_var)  # IntVarをリストに追加    print(999)
    hour_label = tk.Label(frame, text="時")
    hour_label.grid(row=form_count, column=1, pady=2)
    hour_labels.append(hour_label)

    minute_var = tk.IntVar()
    minute_menu = tk.OptionMenu(frame, minute_var, *range(60))  # 分0〜59
    minute_menu.grid(row=form_count, column=2)
    minute_entries.append(minute_menu)
    minute_vars.append(minute_var)
    minute_label = tk.Label(frame, text="分")
    minute_label.grid(row=form_count, column=3)
    minute_labels.append(minute_label)

    match_left_label = tk.Label(frame, text="(マッチング返し)")
    match_left_label.grid(row=form_count, column=4)
    match_labels.append(match_left_label)  
    match_var = tk.IntVar()
    match_menu = tk.OptionMenu(frame, match_var, *range(6))  # マッチング返し0〜5
    match_menu.grid(row=form_count, column=5)
    match_entries.append(match_menu)
    match_vars.append(match_var)
    match_right_label = tk.Label(frame, text="件")
    match_right_label.grid(row=form_count, column=6)
    match_labels.append(match_right_label)

    type_left_label = tk.Label(frame, text="（タイプ返し)")
    type_left_label.grid(row=form_count, column=7)
    type_labels.append(type_left_label)
    type_var = tk.IntVar()
    type_menu = tk.OptionMenu(frame, type_var, *range(6))  # タイプ返し0〜5
    type_menu.grid(row=form_count, column=8)
    type_entries.append(type_menu)
    type_vars.append(type_var)
    type_right_label = tk.Label(frame, text="件")
    type_right_label.grid(row=form_count, column=9)
    type_labels.append(type_right_label)


    args_left_label = tk.Label(frame, text="（足跡返し）")
    args_left_label.grid(row=form_count, column=10)
    args_labels.append(args_left_label)
    args_var = tk.IntVar()
    args_menu = tk.OptionMenu(frame, args_var, *range(31))  # 足跡返し0〜30
    args_menu.grid(row=form_count, column=11)
    args_entries.append(args_menu)
    args_vars.append(args_var)
    args_right_label = tk.Label(frame, text="件")
    args_right_label.grid(row=form_count, column=12)
    args_labels.append(args_right_label)


    # 初期値を設定（空文字列に対応）
    hour_value = int(user_info_list[form_count][0]) if user_info_list[form_count][0].isdigit() else 0
    minute_value = int(user_info_list[form_count][1]) if user_info_list[form_count][1].isdigit() else 0
    match_value = int(user_info_list[form_count][2]) if user_info_list[form_count][2].isdigit() else 0
    type_value = int(user_info_list[form_count][3]) if user_info_list[form_count][3].isdigit() else 0
    args_value = int(user_info_list[form_count][4]) if user_info_list[form_count][4].isdigit() else 0

    hour_var.set(hour_value)   
    minute_var.set(minute_value)  
    match_var.set(match_value) 
    type_var.set(type_value) 
    args_var.set(args_value)

    form_count += 1  # カウンタを更新

def remove_form():
    global form_count

    if form_count <= 1:
        return
    form_count -= 1  # カウンタを更新
    
    # 最後のフォームを削除
    hour_entries.pop().grid_forget()
    minute_entries.pop().grid_forget()
    args_entries.pop().grid_forget()
    type_entries.pop().grid_forget()
    match_entries.pop().grid_forget()

    # 最後のラベルを削除
    hour_labels.pop().grid_forget()
    minute_labels.pop().grid_forget()
    args_labels.pop().grid_forget()
    args_labels.pop().grid_forget()
    type_labels.pop().grid_forget()
    type_labels.pop().grid_forget()
    match_labels.pop().grid_forget()
    match_labels.pop().grid_forget()
    
def populate_user_listbox():
    global user_data  # グローバル変数に代入
    
    happy_chara_list = []
    
    if not user_data:
        return
    for h_chara_data in user_data["happymail"]:
        happy_chara_list.append(f"{h_chara_data['name']}")
    
    listbox.delete(0, tk.END)
    for user in happy_chara_list:
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

# 入力フォームとラベルを横に並べるフレーム
frame = tk.Frame(root)
frame.grid(row=2, column=0, columnspan=6, pady=10)

hour_entries = []
minute_entries = []
match_entries = []  
type_entries = []  
args_entries = []

hour_labels = []
minute_labels = []
match_labels = []
type_labels = []  
args_labels = []

hour_vars = []
minute_vars = []
match_vars = []
type_vars = []
args_vars = []


happy_times = user_data["user"][0]["h_schedule_time"]
user_info_list = [["", "", "", "", ""] for _ in range(6)]  
if happy_times is not None:
    for i in range(len(happy_times)):
        split_data = happy_times[i].split(":")  # ":"で分割
        for j in range(len(split_data)):
            user_info_list[i][j] = split_data[j]  # 分割されたデータを正しい位置に挿入

# 最初の入力フォームを作成
add_form(user_info_list)

# プラスボタンとマイナスボタンを中央揃えにするためのフレームを作成
button_frame = tk.Frame(root)
button_frame.grid(row=3, column=0, columnspan=6, pady=10)

# プラスボタンを追加
add_button = tk.Button(button_frame, text="+", command=lambda: add_form(user_info_list))
add_button.grid(row=0, column=0, padx=10)

# マイナスボタンを追加
remove_button = tk.Button(button_frame, text="-", command=remove_form)
remove_button.grid(row=0, column=1, padx=10)

# 新しいフレームにチェックボックスとラベルを配置
check_frame = tk.Frame(root)
check_frame.grid(row=4, column=0, columnspan=6, pady=10)

check_label = tk.Label(check_frame, text="ウィンドウを表示しない")
check_label.pack(side="left")

check_var = tk.BooleanVar(value=True)
check_button = tk.Checkbutton(check_frame, variable=check_var)
check_button.pack(side="left")

# 実行ボタン
run_button = tk.Button(root, text="実行", command=run_scheduler)
run_button.grid(row=5, column=0, columnspan=6, pady=10)

# ユーザーリストの読み込み
populate_user_listbox()

# Tkinter メインループの開始
root.mainloop()

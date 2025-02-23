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


conn = sqlite3.connect('user_data.db')
c = conn.cursor()
global user_data
form_label_added = False 
user_data = func.get_user_data()

# フォームを追加するためのカウンタ
form_count = 0
max_forms = 2

# Tkinter ウィンドウの設定
root = tk.Tk()
root.title("スケジューラ設定")

driver = None  # グローバルにドライバを定義

def start_scheduler(schedule_data, sorted_pcmax, headless, detail_area_flug):
    if not user_data:
        return
    global driver
    scheduler = BlockingScheduler()
    
    api_url = "https://meruopetyan.com/api/user-data/"
    # DEBUG
    # api_url = "http://127.0.0.1:8000/api/user-data/"
    # スケジュールデータを文字列に変換して保存
    schedule_strings = [f"{hour}:{minute}" for (hour, minute) in schedule_data]
    # print(schedule_data)
    schedule_data = [(6, 0), (20, 0)]
    pcmax.repost_30minute(schedule_data, sorted_pcmax, headless, detail_area_flug)
    

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
    pcmax_chara_list = [listbox.get(i) for i in range(listbox.size())]  # リストボックスからキャラリストを取得
    headless = check_var.get()  # チェックボックスの値を取得
    detail_area_flug = radio_var.get()
    
    
    # pcmax_chara_list の順番に基づいて user_data["pcmax"] を並べ替える
    sorted_pcmax = []
    for chara_name in pcmax_chara_list:
        for p_chara_data in user_data["pcmax"]:
            if p_chara_data['name'] == chara_name:
                sorted_pcmax.append(p_chara_data)
                break    
    for i in range(form_count):
        hour = hour_vars[i].get()
        minute = minute_vars[i].get()

        schedule_data.append((hour, minute, ))

    root.withdraw()  # 実行ボタンを押した時にウィンドウを非表示にする
    root.update()  # Tkinterのイベントループを更新
    # root.quit()
    start_scheduler(schedule_data, sorted_pcmax, headless, detail_area_flug)

def add_form(user_info_list):
    global form_count, form_label_added
    if form_count >= max_forms:
        return  
    # 掲示板予約時間のラベルがまだ追加されていなければ追加
    if not form_label_added:
        form_label = tk.Label(frame, text="掲示板予約時間", font=("Arial", 12, "bold"))
        form_label.grid(row=0, column=0, columnspan=4, pady=(0, 10))
        form_label_added = True
    
    # 新しい入力フォームを追加
    hour_var = tk.IntVar()
    hour_menu = tk.OptionMenu(frame, hour_var, *range(24))  # 時間0〜23
    hour_menu.grid(row=form_count, column=0, pady=2)
    hour_entries.append(hour_menu)
    hour_vars.append(hour_var)  # IntVarをリストに追加   
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

    
    
   

    form_count += 1  # カウンタを更新

def remove_form():
    global form_count

    if form_count <= 1:
        return
    form_count -= 1  # カウンタを更新
    
    # 最後のフォームを削除
    hour_entries.pop().grid_forget()
    minute_entries.pop().grid_forget()
    

    # 最後のラベルを削除
    hour_labels.pop().grid_forget()
    minute_labels.pop().grid_forget()
    
    
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


# 掲示板予約時間ラベル用の新しいフレームを作成し、フォームの上に配置
label_frame = tk.Frame(root)
label_frame.grid(row=2, column=0, columnspan=6, pady=(10, 5))
form_label = tk.Label(label_frame, text="掲示板予約時間", font=("Arial", 12, "bold"))
form_label.pack()

# 入力フォームとラベルを横に並べるフレーム
frame = tk.Frame(root)
frame.grid(row=3, column=0, columnspan=6, pady=10)



hour_entries = []
minute_entries = []

hour_labels = []
minute_labels = []


hour_vars = []
minute_vars = []


pcmax_times = user_data["user"][0]["p_schedule_time"]
user_info_list = [["", "",] for _ in range(6)]  
if pcmax_times is not None:
    for i in range(len(pcmax_times)):
        split_data = pcmax_times[i].split(":")  # ":"で分割
        for j in range(len(split_data)):
            user_info_list[i][j] = split_data[j]  # 分割されたデータを正しい位置に挿入

# 最初の入力フォームを作成
add_form(user_info_list)

# プラスボタンとマイナスボタンを中央揃えにするためのフレームを作成
button_frame = tk.Frame(root)
button_frame.grid(row=5, column=0, columnspan=6, pady=10)
# プラスボタンを追加
add_button = tk.Button(button_frame, text="+", command=lambda: add_form(user_info_list))
add_button.grid(row=0, column=0, padx=10)
# マイナスボタンを追加
remove_button = tk.Button(button_frame, text="-", command=remove_form)
remove_button.grid(row=0, column=1, padx=10)

# ラジオボタンを追加するフレーム
radio_frame = tk.Frame(root)
radio_frame.grid(row=6, column=0, columnspan=6, pady=10)

# ラジオボタンの変数
radio_var = tk.StringVar(value="random")
# ラジオボタン1
radio_button1 = tk.Radiobutton(radio_frame, text="前回と同じ詳細地域", variable=radio_var, value="same")
radio_button1.pack(side="left", padx=10)
# ラジオボタン2
radio_button2 = tk.Radiobutton(radio_frame, text="ランダム", variable=radio_var, value="random")
radio_button2.pack(side="left", padx=10)

# # 新しいフレームにチェックボックスとラベルを配置
# check_frame = tk.Frame(root)
# check_frame.grid(row=7, column=0, columnspan=6, pady=10)
# check_label = tk.Label(check_frame, text="１時間後に実行")
# check_label.pack(side="left")

# one_hour_var = tk.BooleanVar(value=True)
# check_button = tk.Checkbutton(check_frame, variable=one_hour_var)
# check_button.pack(side="left")


# 新しいフレームにチェックボックスとラベルを配置
check_frame = tk.Frame(root)
check_frame.grid(row=7, column=0, columnspan=6, pady=10)
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

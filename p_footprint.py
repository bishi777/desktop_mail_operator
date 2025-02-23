import tkinter as tk
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from widget import func, pcmax
import sqlite3
from requests.exceptions import HTTPError
import traceback
import time
import shutil

def signal_handler(signum, frame):
    print("SIGINT")
    sys.exit()

conn = sqlite3.connect('user_data.db')
c = conn.cursor()
global user_data
form_label_added = False 
user_data = func.get_user_data()

# Tkinter ウィンドウの設定
root = tk.Tk()


def start_scheduler(sorted_pcmax, headless, foot_cnt):
    if not user_data:
        return
    # 地域選択（3つまで選択可能）
    select_areas = [
        "東京都",
        # "千葉県",
        "埼玉県",
        "神奈川県",
        # "静岡県",
        # "新潟県",
        # "山梨県",
        # "長野県",
        # "茨城県",
        # "栃木県",
        # "群馬県",
    ]
    youngest_age = 18
    oldest_age = 31  
    api_url = "https://meruopetyan.com/api/user-data/"
    # DEBUG
    # api_url = "http://127.0.0.1:8000/api/user-data/"

    while True:
        temp_dir = func.get_the_temporary_folder("p_footprint")
        driver,wait = func.test_get_driver(temp_dir, headless)
        for chara_data in sorted_pcmax:
            # print(chara_data['name'])
            func.change_tor_ip()
            try:
                # if chara_data['name'] == "つむぎ":
                    pcmax.make_footprints(chara_data, driver, wait, select_areas, youngest_age, oldest_age, foot_cnt,)
            
            except Exception as e:
                print(traceback.format_exc())
            finally:
                if len(driver.window_handles) == 0:  # ウィンドウが閉じられたか確認
                    print("ブラウザウィンドウが閉じられました。プロセスを終了します。")
                    driver.quit()
                    sys.exit(0)
        driver.quit()
        shutil.rmtree(temp_dir)
        time.sleep(1)
    
def run_scheduler():
    global user_data  
    schedule_data = []
    pcmax_chara_list = [listbox.get(i) for i in range(listbox.size())]  # リストボックスからキャラリストを取得
    headless = check_var.get()  # チェックボックスの値を取得
    foot_cnt = entry.get()
    
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
    start_scheduler(sorted_pcmax, headless, foot_cnt)


    
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

# 新しいフレームにチェックボックスとラベルを配置
check_frame = tk.Frame(root)
check_frame.pack()
check_label = tk.Label(check_frame, text="ウィンドウを表示しない")
check_label.pack(side="left")

check_var = tk.BooleanVar(value=True)
check_button = tk.Checkbutton(check_frame, variable=check_var)
check_button.pack(side="left")


# 実行ボタン
run_button = tk.Button(root, text="実行", command=run_scheduler)
run_button.pack()

# ユーザーリストの読み込み
populate_user_listbox()

# Tkinter メインループの開始
root.mainloop()

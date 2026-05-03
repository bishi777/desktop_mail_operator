# h_app_drivers_android.py 設計メモ

ハッピーメール **Androidネイティブアプリ** 巡回ドライバの設計書。
[h_ch_ma_fm.py](h_ch_ma_fm.py) (モバイルWeb版) のAndroid版を、
[h_app_profile_edit_android.py](h_app_profile_edit_android.py) と
[widget/happymail_android.py](widget/happymail_android.py) の上に構築する。

最終更新: 2026-05-02

---

## 1. ゴール

- 1端末1アカウントで、ハッピーメールAndroidネイティブアプリを24時間運用ベースで自動操作する
- PCからAppium経由で操作（端末側は対象アプリのみ稼働）
- 将来モバイルファーム化（端末数を増やすだけで横展開）を想定し、最初から端末識別をパラメータ化

## 2. アーキテクチャ

```
[Mac サーバ]                           [Android端末1]
 Python (myenv)                         HappyMailアプリ
  ├ h_app_drivers_android.py 端末1用 ──── ADB/USB ──>  (アカウント A)
  │   └ Appium :4723 (system_port=8200)
  ├ h_app_drivers_android.py 端末2用 ────────────── [Android端末2]
  │   └ Appium :4724 (system_port=8201)              (アカウント B)
  ├ widget/happymail_android.py
  ├ widget/func.py
  └ device_mapping.yaml
```

- **案A採用** (1プロセス＝1端末＝1アカウント) — 障害分離・離席タイミングの非同期性・launchdでの水平拡張のしやすさから
- Appium サーバは端末ごとにポート分離。`system_port` / `mjpeg_server_port` も明示分離
- スクショ・ログは Mac 側の `logs_android/<udid>/` に集約

## 3. ファイル構成

新規・追記が必要なファイル一覧。

```
desktop_mail_operator/
├ h_app_drivers_android.py         ← 新規。本ドキュメントの主題
├ device_mapping.yaml              ← 新規
├ widget/
│  └ happymail_android.py          ← 既存。以下を追記
│      - return_footpoint          (フェーズ2)
│      - detect_ban_screen         (フェーズ3)
│      - score_and_send_fst_message (フェーズ4)
└ logs_android/                    ← 新規ディレクトリ
   └ <udid>/
      ├ daily_<YYYYMMDD>.log
      ├ ban_<YYYYMMDD>_<HHMMSS>.png
      └ crash_<YYYYMMDD>_<HHMMSS>.png
```

## 4. 既存資産の棚卸し

### 4.1 既に使えるもの (流用)

| 機能 | 既存実装 | 元コード対応 |
|---|---|---|
| Appium起動・接続・recovery | [h_app_profile_edit_android.py:39-94](h_app_profile_edit_android.py#L39-L94) | — |
| `_appium_alive` / `start_appium_if_needed` / `create_driver` / `recover_driver` | 同上 | — |
| `edit_chara_with_retry` のリトライパターン | [h_app_profile_edit_android.py:97-132](h_app_profile_edit_android.py#L97-L132) | — |
| ポップアップ消去 | [happymail_android.py:137 `dismiss_popups`](widget/happymail_android.py#L137) | — |
| 未読バッジ検出 | [happymail_android.py:196,216](widget/happymail_android.py#L196) | — |
| **新着メール処理 (受動)** | [happymail_android.py:816 `check_mail`](widget/happymail_android.py#L816) | `multidrivers_checkmail` |
| 画像送信 | [happymail_android.py:510 `send_image`](widget/happymail_android.py#L510) | — |
| 見ちゃいや登録 | [happymail_android.py:661 `register_micha_iya`](widget/happymail_android.py#L661) | — |
| プロフィール編集・検証 | [happymail_android.py:1874,1943](widget/happymail_android.py#L1874) | — |

### 4.2 元コードから流用するロジック (Python関数として移植)

[h_ch_ma_fm.py](h_ch_ma_fm.py) の以下はネイティブアプリでもそのまま有効:

- `_human_round_interval()` ([h_ch_ma_fm.py:52-57](h_ch_ma_fm.py#L52-L57)) — 周回間隔の正規分布ランダム化
- `_should_take_break()` ([h_ch_ma_fm.py:60-65](h_ch_ma_fm.py#L60-L65)) — 8〜12周ごとの離席模倣
- 7:00±30分 〜 22:00±30分 の稼働時間管理
- `run_today = not run_today` の隔日運用
- 20%の確率で能動タスクをスキップ

### 4.3 削除するロジック

| 元コード | 理由 |
|---|---|
| `driver.window_handles` 巡回 | 1端末1アカウントなのでタブ概念不要 |
| `ds_user_display_name` でのタブ識別 | 同上 |
| `shuffled_handles` ループ | 同上 |
| `happymail.stealth_setup` | ネイティブには `navigator.webdriver` 概念なし |
| `driver.get(URL)` でのメニュー遷移 | アプリにURL概念無し → `driver.activate_app(APP_PACKAGE)` + タブタップに置換 |

### 4.4 未実装 (新規追加が必要)

| 機能 | 既存元コード | 優先度 |
|---|---|---|
| **巡回ループ本体** (`h_app_drivers_android.py`) | `h_ch_ma_fm.py` | **フェーズ1** |
| **足跡返し / マッチング返し** (`return_footpoint` のAndroid版) | `widget.happymail.return_footpoint` | **フェーズ2** |
| **BAN/利用停止画面検出** (`detect_ban_screen`) | `check_mail` 内の警告検出 | **フェーズ3** |
| **検索→スコアリング→FST送信** (`score_and_send_fst_message` のAndroid版) | `widget.happymail.score_and_send_fst_message` | **フェーズ4** |

## 5. 重要な運用制約 (Q-D 由来)

> **能動的送信 (return_foot / fst) は 1ループ1通まで**
> check_mail の受動的返信は何通連続でもOK。

連続して複数ユーザーへ能動送信するとBANリスクが上がるため、周回内で
能動送信を行うのは最大1件 (return_foot か fst のどちらか) に制限する。

### 元コードからの変更点

[h_ch_ma_fm.py:103-194 _process_chara](h_ch_ma_fm.py#L103-L194) は
`tasks = ["checkmail", "return_foot", "fst"]` を順序シャッフルで全部試行していた
(20%でランダムに片方スキップ)。**これを以下に変更**:

```python
# 元: checkmail → return_foot → fst を全部試行 (20%で片方スキップ)
# 新: checkmail を必ず実行、能動送信は return_foot or fst を 1つだけ抽選

passive_task = "checkmail"
active_candidates = []
if daily_done < daily_limit:
    active_candidates.append("return_foot")
if fst_daily_done < fst_daily_limit and elapsed_since_fst >= fst_interval:
    active_candidates.append("fst")

# 能動送信は最大1件、20%は完全スキップ (純粧checkmailのみの周)
active_task = None
if active_candidates and random.random() >= 0.2:
    active_task = random.choice(active_candidates)

execute(passive_task)         # check_mail (受動: 連続OK)
if active_task:
    execute(active_task)      # return_foot xor fst (能動: 1件)
```

## 6. 数値スペック (Q5 反映)

```python
# h_app_drivers_android.py 冒頭定数
DAILY_LIMIT_RANGE       = (8, 10)        # 元1-2 → 8-10 に変更 (return_foot)
FST_DAILY_LIMIT_RANGE   = (1, 2)         # FSTはキャラごとに1-2件
ROUND_INTERVAL_MEAN_SEC = 15 * 60
ROUND_INTERVAL_STD_SEC  = 5 * 60
ROUND_INTERVAL_MIN_SEC  = 8 * 60
ROUND_INTERVAL_MAX_SEC  = 30 * 60
BREAK_EVERY_ROUNDS      = (8, 12)
BREAK_DURATION_MIN      = (20, 40)
DAILY_START_HOUR        = 7
DAILY_END_HOUR          = 22
DAILY_OFFSET_MIN        = 30             # ±30分のランダム
RUN_EVERY_OTHER_DAY     = True           # 隔日運用
ACTIVE_SKIP_PROB        = 0.2            # 周回内で能動送信を完全スキップする確率
FST_INTERVAL_MIN_SEC    = 50 * 60        # FST間隔 50-70分
FST_INTERVAL_MAX_SEC    = 70 * 60
```

### 想定処理量 (理論値)

- 稼働時間: 15時間 × 0.6 (休憩等を引いた稼働率) ≒ 9時間
- 1周15分 → 1日 約36周
- 1周あたり能動送信 0.8件 (20%スキップ込み) → **約29件/日 が上限**
- 設定 daily_limit (8-10) + fst (1-2) = 9-12件/日 → 上限内に収まる

## 7. デバイス管理 (Q-C 反映: login_id で一意紐付け)

### 7.1 `device_mapping.yaml`

```yaml
# login_id ごとの端末割り当て
# get_user_data() の happymail[].login_id と紐付け
mappings:
  - login_id: chara_a_login_id_string
    udid: a02aca5e
    appium_port: 4723
    system_port: 8200          # uiautomator2-server用、衝突回避
    mjpeg_server_port: 7810
  - login_id: chara_b_login_id_string
    udid: b12bcd6f
    appium_port: 4724
    system_port: 8201
    mjpeg_server_port: 7811
```

### 7.2 起動コマンド

```bash
# 引数: login_id 1つだけ。残りは device_mapping.yaml から解決
myenv/bin/python h_app_drivers_android.py <login_id>

# 例
myenv/bin/python h_app_drivers_android.py chara_a_login_id_string
```

スクリプトは:
1. `device_mapping.yaml` を読み込み、引数の `login_id` から `udid` / ポート群を解決
2. `func.get_user_data()` の `happymail[]` から該当キャラ情報を取得
3. 該当 `udid` の Appium サーバが立っていなければ起動
4. driver作成→巡回開始

### 7.3 並列起動 (将来のファーム化)

```bash
# launchd plist or 単純なシェルスクリプトで端末分起動
nohup myenv/bin/python h_app_drivers_android.py chara_a_login_id &
nohup myenv/bin/python h_app_drivers_android.py chara_b_login_id &
nohup myenv/bin/python h_app_drivers_android.py chara_c_login_id &
```

## 8. h_app_drivers_android.py の構造案

```python
"""ハッピーメール Androidネイティブアプリ 巡回ドライバ

使い方:
  myenv/bin/python h_app_drivers_android.py <login_id>

device_mapping.yaml で login_id ↔ UDID/ポート を解決し、
1端末1アカウント前提で 7:00-22:00 に巡回ループを回す (隔日運用)。
"""
import argparse
import os
import random
import socket
import subprocess
import sys
import time
import traceback
from datetime import datetime, timedelta

import yaml
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import WebDriverException

sys.path.insert(0, os.path.dirname(__file__))
from widget import func, happymail_android


# ---------- 定数 ----------
APP_PACKAGE = "jp.co.i_bec.suteki_happy"
APP_ACTIVITY = "jp.co.i_bec.happymailapp.activity.SplashActivity"
APPIUM_BIN = "/Users/yamamotokenta/.nodebrew/current/bin/appium"
MAPPING_FILE = os.path.join(os.path.dirname(__file__), "device_mapping.yaml")

DAILY_LIMIT_RANGE = (8, 10)
FST_DAILY_LIMIT_RANGE = (1, 2)
ROUND_INTERVAL_MEAN_SEC = 15 * 60
ROUND_INTERVAL_STD_SEC = 5 * 60
ROUND_INTERVAL_MIN_SEC = 8 * 60
ROUND_INTERVAL_MAX_SEC = 30 * 60
BREAK_EVERY_ROUNDS = (8, 12)
BREAK_DURATION_MIN = (20, 40)
DAILY_START_HOUR = 7
DAILY_END_HOUR = 22
DAILY_OFFSET_MIN = 30
RUN_EVERY_OTHER_DAY = True
ACTIVE_SKIP_PROB = 0.2
FST_INTERVAL_MIN_SEC = 50 * 60
FST_INTERVAL_MAX_SEC = 70 * 60


# ---------- 人間らしさ (h_ch_ma_fm.py から移植) ----------
def _human_round_interval(): ...
def _should_take_break(round_cnt): ...


# ---------- デバイスマッピング ----------
def load_device_mapping(login_id):
    """device_mapping.yaml から login_id に対応する UDID/ポート群を返す。"""
    with open(MAPPING_FILE) as f:
        data = yaml.safe_load(f)
    for m in data.get("mappings", []):
        if m["login_id"] == login_id:
            return m
    raise ValueError(f"login_id={login_id} が device_mapping.yaml に未登録")


# ---------- Appium 制御 (h_app_profile_edit_android.py から移植) ----------
def _appium_alive(port): ...
def start_appium_if_needed(port, system_port): ...
def create_driver(udid, appium_port, system_port, mjpeg_server_port): ...
def recover_driver(holder, device_cfg): ...


# ---------- 1キャラ分の周回 ----------
def _process_chara(chara_data, holder, mail_info, state, device_cfg):
    """1周分の処理: check_mail (受動) + return_foot xor fst (能動1件)."""
    name = chara_data["name"]
    happymail_android.dismiss_popups(holder["driver"])
    # アプリが裏に回っている可能性があるので必ず前面化
    holder["driver"].activate_app(APP_PACKAGE)
    time.sleep(2)
    happymail_android.dismiss_popups(holder["driver"])

    # ── 1. 能動送信タスクの抽選 (1ループ1通制約) ──
    active_candidates = []
    if state["daily_done"] < state["daily_limit"]:
        active_candidates.append("return_foot")
    elapsed_since_fst = (
        (datetime.now() - state["last_fst_sent"]).total_seconds()
        if state["last_fst_sent"] else float("inf")
    )
    fst_interval = random.randint(FST_INTERVAL_MIN_SEC, FST_INTERVAL_MAX_SEC)
    if (state["fst_daily_done"] < state["fst_daily_limit"]
        and elapsed_since_fst >= fst_interval):
        active_candidates.append("fst")

    active_task = None
    if active_candidates and random.random() >= ACTIVE_SKIP_PROB:
        active_task = random.choice(active_candidates)

    # ── 2. check_mail (受動: 連続OK) ──
    try:
        return_list = happymail_android.check_mail(
            name, holder["driver"],
            chara_data["login_id"], chara_data["password"],
            chara_data["fst_message"], chara_data["second_message"],
            chara_data["post_return_message"], chara_data["condition_message"],
            chara_data["confirmation_mail"], chara_data["chara_image"],
            chara_data["mail_address"], chara_data["gmail_password"],
            return_check_cnt=10,
            chara_prompt=chara_data["system_prompt"],
        )
        if return_list:
            _send_check_report(name, return_list, mail_info, holder["driver"], chara_data)
    except WebDriverException as e:
        _handle_crash(holder, device_cfg, name, "check_mail", e)
        return
    except Exception:
        print(traceback.format_exc())

    # ── 3. 能動送信1件 (return_foot か fst のどちらか1つだけ) ──
    happymail_android.human_sleep(1.5, 4.0)  # ※後述
    if active_task == "return_foot":
        _do_return_foot(chara_data, holder, state, device_cfg)
    elif active_task == "fst":
        _do_fst(chara_data, holder, state, device_cfg)


def _do_return_foot(chara_data, holder, state, device_cfg):
    """フェーズ2で実装。今は noop or 簡易ログのみ。"""
    name = chara_data["name"]
    try:
        sent = happymail_android.return_footpoint(  # ★フェーズ2で追加
            holder["driver"], chara_data,
            send_cnt=1,                              # 1ループ1通
        )
        if sent:
            state["daily_done"] += sent
            print(f"[{name}] return_foot +{sent} 累計 {state['daily_done']}/{state['daily_limit']}")
    except WebDriverException as e:
        _handle_crash(holder, device_cfg, name, "return_foot", e)
    except Exception:
        print(traceback.format_exc())


def _do_fst(chara_data, holder, state, device_cfg):
    """フェーズ4で実装。"""
    name = chara_data["name"]
    try:
        sent_to = happymail_android.score_and_send_fst_message(  # ★フェーズ4で追加
            holder["driver"], chara_data,
        )
        if sent_to:
            state["fst_daily_done"] += 1
            state["last_fst_sent"] = datetime.now()
            print(f"[{name}] fst送信 {state['fst_daily_done']}/{state['fst_daily_limit']}")
    except WebDriverException as e:
        _handle_crash(holder, device_cfg, name, "fst", e)
    except Exception:
        print(traceback.format_exc())


def _handle_crash(holder, device_cfg, name, task, exc):
    print(f"[CRASH:{name}] {task}: {str(exc)[:200]}")
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(
            os.path.dirname(__file__), "logs_android", device_cfg["udid"],
            f"crash_{ts}.png",
        )
        os.makedirs(os.path.dirname(path), exist_ok=True)
        holder["driver"].save_screenshot(path)
    except Exception:
        pass
    recover_driver(holder, device_cfg)


# ---------- 通報メール (元 h_ch_ma_fm.py の挙動を流用) ----------
def _send_check_report(name, return_list, mail_info, driver, chara_data):
    title = f"happy新着 {name}"
    text = ""
    img_path = None
    for m in return_list:
        text += m + ",\n"
        if "警告" in text or "NoImage" in text or "利用" in text:
            if mail_info:
                img_path = f"{chara_data['name']}_ban.png"
                driver.save_screenshot(img_path)
                img_path = func.compress_image(img_path)
                title = "メッセージ"
                text = (f"ハッピーメール {chara_data['name']}:"
                        f"{chara_data['login_id']}:{chara_data['password']}: {text}")
    if mail_info:
        func.send_mail(text, mail_info, title, img_path)


# ---------- 1日のループ ----------
def run_one_day(chara_data, holder, device_cfg):
    now = datetime.now()
    today_start = now.replace(hour=DAILY_START_HOUR, minute=0, second=0, microsecond=0) \
                  + timedelta(minutes=random.randint(-DAILY_OFFSET_MIN, DAILY_OFFSET_MIN))
    today_end = now.replace(hour=DAILY_END_HOUR, minute=0, second=0, microsecond=0) \
                + timedelta(minutes=random.randint(-DAILY_OFFSET_MIN, DAILY_OFFSET_MIN))

    if now < today_start:
        wait_sec = (today_start - now).total_seconds()
        print(f"開始時刻まで待機 {wait_sec/60:.0f}分")
        time.sleep(wait_sec)

    if datetime.now() >= today_end:
        print(f"終了時刻過ぎたためスキップ")
        return

    state = {
        "daily_limit": random.randint(*DAILY_LIMIT_RANGE),
        "daily_done": 0,
        "fst_daily_limit": random.randint(*FST_DAILY_LIMIT_RANGE),
        "fst_daily_done": 0,
        "last_fst_sent": None,
    }
    print(f"本日上限 daily={state['daily_limit']} fst={state['fst_daily_limit']}")

    user_mail_info = _build_user_mail_info()
    spare_mail_info = _build_spare_mail_info()
    round_cnt = 1
    while datetime.now() < today_end:
        round_start = datetime.now()
        print(f"\n--- {round_cnt}周目 ({round_start.strftime('%H:%M:%S')}) ---")

        if _should_take_break(round_cnt):
            break_min = random.randint(*BREAK_DURATION_MIN)
            print(f"離席模倣 {break_min}分")
            time.sleep(break_min * 60)
            if datetime.now() >= today_end:
                break

        mail_info = random.choice([user_mail_info, spare_mail_info])
        try:
            _process_chara(chara_data, holder, mail_info, state, device_cfg)
        except Exception:
            print(traceback.format_exc())

        elapsed = (datetime.now() - round_start).total_seconds()
        wait_sec = _human_round_interval() - elapsed
        if wait_sec > 0 and datetime.now() < today_end:
            print(f"次の周まで {wait_sec/60:.0f}分待機")
            time.sleep(wait_sec)
        round_cnt += 1


# ---------- main ----------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("login_id", help="device_mapping.yaml に登録済みのlogin_id")
    args = parser.parse_args()

    device_cfg = load_device_mapping(args.login_id)
    user_data = func.get_user_data()
    if not user_data or user_data == 2:
        print("[ERROR] ユーザーデータ取得失敗")
        sys.exit(1)
    chara_data = next((c for c in user_data["happymail"]
                       if c["login_id"] == args.login_id), None)
    if not chara_data:
        print(f"[ERROR] login_id={args.login_id} がuser_dataに無い")
        sys.exit(1)

    appium_proc = start_appium_if_needed(
        device_cfg["appium_port"], device_cfg["system_port"],
    )
    holder = {"driver": None}

    # 端末画面ONを維持
    subprocess.run(
        ["adb", "-s", device_cfg["udid"], "shell", "svc", "power", "stayon", "true"],
        check=False,
    )

    run_today = True
    try:
        holder["driver"] = create_driver(
            device_cfg["udid"], device_cfg["appium_port"],
            device_cfg["system_port"], device_cfg["mjpeg_server_port"],
        )
        time.sleep(3)
        happymail_android.dismiss_popups(holder["driver"])

        while True:
            if run_today:
                run_one_day(chara_data, holder, device_cfg)
            run_today = not run_today
            # 翌7:00±30分まで待機
            next_start = (datetime.now() + timedelta(days=1)).replace(
                hour=DAILY_START_HOUR, minute=0, second=0, microsecond=0,
            ) + timedelta(minutes=random.randint(-DAILY_OFFSET_MIN, DAILY_OFFSET_MIN))
            wait_sec = (next_start - datetime.now()).total_seconds()
            status = "実行" if run_today else "スキップ"
            print(f"翌日【{status}】 次回: {next_start.strftime('%Y-%m-%d %H:%M')}")
            time.sleep(wait_sec)
    except KeyboardInterrupt:
        print("Ctrl+C 中断")
    except Exception:
        traceback.print_exc()
    finally:
        if holder["driver"]:
            try:
                holder["driver"].quit()
            except Exception:
                pass
        if appium_proc:
            appium_proc.terminate()


if __name__ == "__main__":
    main()
```

> 上記は構造提案。`happymail_android.human_sleep` は元 [widget/happymail.py](widget/happymail.py) の同名関数を `widget/happymail_android.py` にも置く想定 (なければ実装時に追加)。

## 9. Appium 並列起動時のポート割り当て表

| 端末 | UDID | appium | system_port | mjpeg_server_port |
|---|---|---|---|---|
| 端末1 | a02aca5e | 4723 | 8200 | 7810 |
| 端末2 | b12bcd6f | 4724 | 8201 | 7811 |
| 端末3 | c23def7a | 4725 | 8202 | 7812 |

`UiAutomator2Options` で **必ず明示**:
- `system_port` (uiautomator2-server)
- `mjpeg_server_port` (画面ストリーミング)

デフォルト値だと並列実行時に確実に衝突する。

## 10. フェーズ別ロードマップ (Q-A 順)

### フェーズ1: 巡回ループの最小実装 ✅ 実装完了 (2026-05-02)

- [x] [h_app_drivers_android.py](h_app_drivers_android.py) を作成
- [x] [device_mapping.json](device_mapping.json) を作成 (4キャラ x UDID a02aca5e)
- [x] `check_mail` (既実装) を呼ぶ巡回ループ
- [x] `return_foot` / `fst` は `getattr` で動的呼び出し (未実装時はノーオペ)
- 完了基準: **1端末で7:00-22:00、隔日、新着メール返信が回る状態**
- **未検証**: 実機での1日通し動作 (帰宅後の確認待ち)

### フェーズ2: 足跡返し / タイプ返し / マッチング返し ✅ 実装完了 (2026-05-02)

`return_footpoint` は **3 種のオーケストレーター** に拡張。実行順は固定:
**タイプ返し → マッチング返し → 足跡返し**。

#### 実行ルール

1. **タイプ返し** は常に実行 (タップのみで「通」扱いではないため戻り値カウントには **含めない**)
2. **マッチング返し** を試行。**1 件送れたら 足跡返しはスキップ** (1 ループ 1 通制約)
3. マッチング返しが 0 件のときだけ **足跡返し** へフォールバック

戻り値はマッチング返し + 足跡返しの件数 (0 or 1)。タイプ返しは含まれない。
daemon 側 (`_do_return_foot`) はこの戻り値を `state["daily_done"]` に加算する。

#### 共通

- [x] [widget/happymail_android.py](widget/happymail_android.py) に公開 API `return_footpoint(driver, chara_data, send_cnt=1)` を実装
- [x] 内部で `_return_type_only` / `_return_matching_only` / `_return_footprint_only` を順次試行
- **`send_cnt=1` 固定** (1ループ1通制約)
- **未検証**: 実機で 3 種のフローを順番に動作確認

#### 足跡返し (`_return_footprint_only`)

- [x] マイページ → 足あとグリッド (5 番目) → リストの 20代/18-19歳 の最初の未送信ユーザー → 送信
- [x] サブヘルパー: `_open_footprint_list` / `_back_to_footprint_list` /
      `_profile_has_ng_words` / `_register_micha_iya_from_user_detail` / `_scroll_footprint_list`
- [x] 「既存スレッドあり」判定: `frame_first_message` 不在で判定
- [x] 年齢フィルタ: `txt_age` に "20代" / "18~19" 含むか
- [x] NG ワード検出: `txt_comment` 群結合で「通報/業者/金銭/条件」→ 見ちゃいや登録
- [x] 画像送信: 既存 `send_image` 流用
- メッセージ本文: `chara_data["return_foot_message"]`

#### タイプ返し (`_return_type_only`)

- [x] typelist タブ → 相手から フィルタ → 現在カードの `btn_send_type` をタップ
- [x] 確認ダイアログ (`common_yesnodialog_tv_yes`) を `_confirm_yes_dialog` で自動承認
- [x] 年齢が 20代/18-19 でないカードはスキップ (誤送信回避)
- [x] 空状態 (`layout_empty_state`) で 0 件返却
- メッセージ送信なし、ワンタップアクションのみ (元コード `return_type` 踏襲)

#### マッチング返し (`_return_matching_only`)

- [x] typelist タブ → マッチング フィルタ → リスト先頭の 20代 ユーザー → 送信
- [x] 空状態 (`layout_empty_state`) で 0 件返却
- [x] NG ワード検出 → 見ちゃいや登録 (足跡返しと共通)
- [x] 既存スレッド検出 → スキップ
- [x] `_back_to_typelist` で typelist 画面に復帰
- [x] 画像送信あり
- メッセージ本文: `chara_data["fst_message"]` (元コード `return_matching` 踏襲)

#### サブヘルパー (typelist 共通)

- `_open_typelist_tab` / `_select_typelist_filter` / `_back_to_typelist` /
  `_confirm_yes_dialog`

### フェーズ3: BAN/利用停止画面検出 ✅ 実装完了 (2026-05-02)

- [x] [widget/happymail_android.py](widget/happymail_android.py) に `detect_ban_screen(driver) -> Optional[str]` を追加
- [x] `BAN_TEXT_PATTERNS` 定数で 16 個の検出文言を定義 (誤検知低めに調整)
  - "ご利用いただけません", "アカウント停止", "規約違反", "登録は利用できません", "強制ログアウト" 等
- [x] [h_app_drivers_android.py](h_app_drivers_android.py) `_process_chara` 冒頭で BAN チェック
- [x] 検出時挙動: スクショ保存 → 緊急通報メール (`_send_ban_report`) → 周回スキップ
- [x] **スロットリング**: `state["ban_reported_today"]` で 1 日 1 回までに制限 (毎周回スパムしない)
- 戻り値: BAN画面ならその種別文字列、正常なら None
- **未検証**: 実BAN画面でのフォールス陽性/陰性確認 (BAN になるまで待たないと検証不可)

### フェーズ4: FST送信 (`score_and_send_fst_message` Android移植) — 調査完了・実装未着手

#### 調査結果 (2026-05-02)

**検索タブ (プロフ検索画面) のリソースID**:
| リソースID | 役割 |
|---|---|
| `maintab_profsearch_window` | 検索結果のメインコンテナ |
| `maintab_profsearch_gv_big_profilelist` | 2列グリッドのプロフィール一覧 (GridView) |
| `maintab_profsearch_frame_search` | 上部「検索条件を設定する」ボタン |
| `maintab_profsearchbtn_view_group` | 表示切替 (1列/2列等) |
| `layout_profile_info` | 各プロフィールカードの情報部分 (年齢・都道府県含む) |

**プロフカード構造** (例: `layout_profile_info bounds=[21,925][519,992]: ['30代前半', '東京都']`):
- 上半分: サムネイル画像
- 下半分: 年齢・都道府県・自己紹介スニペット

**Phase 4 実装方針**:
1. **検索タブに遷移**: `ID_SEARCH_TAB` をタップ
2. **プロフィールカードを順番にタップ → 詳細画面へ → 戻る、を繰り返してスコアリング**
   - フェーズ2の `_open_footprint_list` と同じパターンで `frame_swipe` 行 or `layout_profile_info` をループ
   - 各ユーザー詳細画面で `_profile_has_ng_words` 流用
   - メール履歴チェック: `btn_send_msg` をタップ → `frame_first_message` の有無で判定
3. **最高スコアのユーザーへ FST 送信**: フェーズ2の送信フローを再利用
4. **画像送信**: `send_image` 流用

**設計上の判断ポイント (ユーザーへ要相談)**:
- (a) **AI スコアリング** (`score_user` + `analyze_image_with_claude` + `generate_fst_message_with_ai`)
  をAndroid版でも踏襲するか、シンプルな heuristic スコアリング (年齢・都道府県・コメント長 等) に置き換えるか?
  - 元コードは Claude API を呼ぶため、コスト・レイテンシが増える
  - Android 版では「足跡返しと同じテンプレートメッセージで送信」が低リスク
- (b) **scoring対象の探索範囲**: 元は `idx=1〜14` まで巡回。Android 版では何件まで見るか? (リスト中の `frame_swipe` 行を上から N 個)
- (c) **AIメッセージ生成** (`generate_fst_message_with_ai`) を使うか、固定テンプレ (`fst_message`) を `.format(name=user_name)` で送るか
  - return_footpoint は固定テンプレなので、FST も固定テンプレが整合的

**推奨ミニマム実装**: AIなしで、検索リストから NG ワード/メール履歴をフィルタした最初のユーザーに `fst_message.format(name=...)` で送信。これで Phase 4 完了基準 (1日1-2件 FST) を満たせる。AIスコアリングは将来拡張。

**完了基準**: fst_daily_limit (1-2件/日) のFSTが配信できる

## 11. Android 特有の運用上の注意

| 項目 | 対策 |
|---|---|
| アプリが裏に回る・Force Stopされる | 周回頭で `driver.activate_app(APP_PACKAGE)` |
| 画面OFF・自動ロック | 起動時に `adb shell svc power stayon true`、開発者オプションで「スリープしない」 |
| OS / アプリのアップデート | resource-id が変わると `re_registration` 等が壊れる。**自動更新OFF推奨**、バージョン固定 |
| 新規キャンペーンモーダル | 既存 `dismiss_popups` の `_DISMISS_TEXTS` / `_DISMISS_IDS` に随時追加 |
| `system_port` 衝突 | 並列実行時は端末ごとに必ず別ポート |
| Wi-Fi/USB切断 | `recover_driver` で driver作り直し、Appiumも `pkill` → 再起動 |

## 12. 通報・ログ (Q4 / Q6 反映)

### 既存活用 (Q4)

- 新着メール+警告系 → 既存 `func.send_mail` で Gmail通報 (既に `check_mail` 内にロジックあり)
- BAN検出 (フェーズ3) → 同 Gmail通報

### Mac側保存 (Q6)

- スクショ・周回ログは `logs_android/<udid>/` 配下に Mac 側保存
- `driver.save_screenshot(path)` は Appium が自動的に Mac側へ保存するので追加実装不要
- 周回ログは Python 標準 `logging` で 日次ローテート (`daily_<YYYYMMDD>.log`)

## 13. 残タスク / 未確定事項

### 解決済み
- [x] ~~ネイティブアプリの足跡画面の動線調査~~ → フェーズ2で解決 (FootMarkActivity / `frame_swipe` 行 / `btn_send_msg` 経路)
- [x] ~~`human_sleep` ヘルパ~~ → `widget/happymail_android.py:human_sleep` に追加済み
- [x] ~~`func.compress_image` / `send_mail` の利用可否~~ → 使えることを確認
- [x] ~~ネイティブアプリの検索画面の動線~~ → フェーズ4調査で `maintab_profsearch_*` ID 群を特定

### 未着手
- [ ] **実機 1 周通し動作確認** (帰宅後)
  - フェーズ1: `myenv/bin/python h_app_drivers_android.py 50022949331` で 7:00-22:00 巡回が安定するか
  - フェーズ2: 1 件 return_foot を実送信して、フローが完走するか (return_foot_message が user_data に設定されている前提)
  - フェーズ3: BAN画面に当たった時の通報動作 (人為的に検証困難なので運用中の自然発生待ち)
- [x] ~~**マッチング返し** (元 `return_matching` 相当)~~ → 2026-05-02 実装完了 (`_return_matching_only`)
- [x] ~~**タイプ返し** (元 `return_type` 相当)~~ → 2026-05-02 実装完了 (`_return_type_only`)
  - daily_limit は 3 種共通カウンタ (return_footpoint で 1 件成功すれば daily_done +1)
- [ ] **フェーズ4 (FST送信) の設計判断** → 上記 §10 フェーズ4 「設計上の判断ポイント」参照
- [ ] launchd plist (フェーズ1の安定動作確認後)
- [ ] モバイルファーム拡張時の手順書 (端末追加時の `device_mapping.json` 更新と `system_port` 採番)

## 14. 用語整理

| 用語 | 意味 |
|---|---|
| FST | First message。新規ユーザーへの初メール送信 |
| RF | Return Footpoint。足跡返し |
| 受動送信 | 届いたメールへの返信 (check_mail内) — 連続OK |
| 能動送信 | こちらから新規送信 (return_foot / fst) — 1ループ1通 |
| 1ループ | 周回1周。平均15分間隔 |
| 1キャラ | 1アカウント。本設計では 1端末＝1キャラ |

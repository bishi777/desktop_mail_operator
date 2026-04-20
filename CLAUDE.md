# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 概要

複数の婚活・マッチングプラットフォーム（PCMAX、ハッピーメール、イククル、Jメール）のアカウントを自動操作するシステム。プロフィール管理・メールチェック・メッセージ送信・足跡付けなどをSelenium/Appiumで自動化する。

## 実行環境

```bash
# 仮想環境を使う
myenv/bin/python <スクリプト名>.py

# デバッグ用Chrome起動（ポート指定）
./start_debug_chrome_mac.sh 9222

# iKukuru自動処理
myenv/bin/python debug_drivers_ikukuru.py 9222

# PCMAX自動処理
myenv/bin/python debug_drivers_p_ch_fm.py 9223

# プロフィール編集
myenv/bin/python i_profile_edit.py <port> <キャラ名>
myenv/bin/python p_profile_edit.py
myenv/bin/python h_profile_edit.py
```

## アーキテクチャ

### データフロー

```
meruopetyan.com API
    ↓ get_user_data() (widget/func.py)
各エントリスクリプト（p_*, h_*, i_*, j_*）
    ↓ Chrome remote debugging / Appium
widget/ のプラットフォーム別モジュール
    ↓
PCMAX / ハッピーメール / イククル / Jメール
```

### ユーザーデータ取得

すべてのスクリプトは `widget/func.py` の `get_user_data()` でリモートAPIからアカウント情報を取得する。ローカルの `user_data.db`（SQLite）に認証情報を保存し、`https://meruopetyan.com/api/user-data/` へリクエストする。接続失敗時は5分リトライ。

### ブラウザ接続方式

- **Chrome remote debugging**: `options.add_experimental_option("debuggerAddress", "127.0.0.1:<port>")` で起動済みChromeに接続
- **Appium（iOS）**: `p_uiautomator.py` でiOSシミュレータのSafariを操作
- **GoLogin**: `gologin_*.py` が `ps` コマンドでOrbita プロセスのデバッグポートを自動検出

### メトリクス管理

各スクリプトは `report_dict` でキャラ別のFST（初メール送信数）・RF（足跡返し数）・check数を追跡し、定時にGmail経由でレポートを送信する。

## widget/ モジュール構成

| ファイル | 役割 |
|---|---|
| `func.py` | 共通ユーティリティ（API取得・メール送信・Gemini呼び出し等） |
| `pcmax.py` / `pcmax_2.py` | PCMAX自動化（pcmax_2がより新しい） |
| `happymail.py` | ハッピーメール自動化（Appium対応のCSSセレクタ変換含む） |
| `ikukuru.py` | イククル自動化（検索フィルタ・足跡・タイプ返し・プロフィール編集） |
| `jmail.py` | Jメール自動化 |
| `human_scheduler.py` | 人間らしい活動時間スケジューラ（偶数日/奇数日で異なるパターン） |

## 設定ファイル

**`settings.py`**: Chromeデバッグポート・プロキシ・APIキー（Gemini・Anthropic・2Captcha）を管理。

```python
ikukuru_port = 9222
pcmax_mf_port = 9222
pcmax_ch_port = 9223
happymail_port = 9224
```

**`.env`**: CapSolver APIキー（Cloudflare Turnstile解決用）。

## スクリプト命名規則

- `p_*` → PCMAX
- `h_*` → ハッピーメール
- `i_*` → イククル
- `j_*` → Jメール
- `debug_drivers_*.py` → Chrome接続して無限ループで自動処理するメインドライバ
- `gologin_*.py` → GoLoginプロファイル経由の処理

## launchd スケジューラ

`com.pcmax.uiautomator.plist`（`~/Library/LaunchAgents/`）で毎朝7時にAppium + `p_uiautomator.py` を1時間実行。`run_uiautomator.sh` が実体。

## イククル固有の仕様

- 検索フィルタは `widget/ikukuru.py` の `FIXED_SEARCH_FILTER` と `_AREA_POOL` で定義
- タイプ返しは `btn-type-on{id}` 内の `[onclick]` 要素の `setTypeStatusPc()` を直接JS実行
- プロフィール編集は3ページ（`show_profile_setting.html` / `show_edit_profile.html` / `show_edit_profile_intro.html`）
- お引越し: `show_pref_setting_list.html` → `show_city_setting_list.html`
- タブ識別: `show_setting_mailaddress.html` のメールアドレスで照合
- スタンプ不使用キャラ（`make_chara_image.py`）: yukko / erika / tumugi

あなたの作業が完了したら、Codexが出力をレビューします。
指定された時以外は必ず日本語で答えてください。
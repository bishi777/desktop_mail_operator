#!/bin/bash
# launchdから呼ばれるスクリプト（8時に実行される）

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$SCRIPT_DIR/myenv/bin/python3"
APPIUM="/Users/yamamotokenta/.nodebrew/current/bin/appium"
DURATION=1800  # 30分（秒）

echo "===== $(date '+%Y-%m-%d %H:%M:%S') Appium起動 =====" >> "$SCRIPT_DIR/appium_launchd.log"

# Appium起動（バックグラウンド）
$APPIUM >> "$SCRIPT_DIR/appium.log" 2>&1 &
APPIUM_PID=$!
echo "Appium PID: $APPIUM_PID" >> "$SCRIPT_DIR/appium_launchd.log"
sleep 3

# p_uiautomator.py起動（バックグラウンド）
cd "$SCRIPT_DIR"
$PYTHON p_uiautomator.py >> "$SCRIPT_DIR/p_uiautomator.log" 2>&1 &
PY_PID=$!
echo "p_uiautomator.py PID: $PY_PID" >> "$SCRIPT_DIR/appium_launchd.log"

# 30分待機
sleep $DURATION

# プロセス終了
echo "===== $(date '+%Y-%m-%d %H:%M:%S') 終了処理 =====" >> "$SCRIPT_DIR/appium_launchd.log"
kill $PY_PID 2>/dev/null
sleep 2
kill -9 $PY_PID 2>/dev/null
kill $APPIUM_PID 2>/dev/null
sleep 2
kill -9 $APPIUM_PID 2>/dev/null
echo "完了" >> "$SCRIPT_DIR/appium_launchd.log"

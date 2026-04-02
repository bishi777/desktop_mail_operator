#!/bin/bash

PROJECT_DIR="/Users/yamamotokenta/Desktop/myprojects/desktop_mail_operator"
PYTHON="$PROJECT_DIR/myenv/bin/python"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/uiautomator_$(date +%Y%m%d).log"
APPIUM="/Users/yamamotokenta/.nodebrew/current/bin/appium"

mkdir -p "$LOG_DIR"

echo "=== 起動 $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"

# Appium起動
"$APPIUM" >> "$LOG_FILE" 2>&1 &
APPIUM_PID=$!
echo "Appium PID: $APPIUM_PID" >> "$LOG_FILE"

# Appium起動待ち
sleep 5

# p_uiautomator.pyを1時間（3600秒）実行して強制終了
cd "$PROJECT_DIR"
"$PYTHON" -u p_uiautomator.py >> "$LOG_FILE" 2>&1 &
SCRIPT_PID=$!
echo "Script PID: $SCRIPT_PID" >> "$LOG_FILE"

sleep 3600

# 終了処理
kill "$SCRIPT_PID" 2>/dev/null
wait "$SCRIPT_PID" 2>/dev/null
kill "$APPIUM_PID" 2>/dev/null
wait "$APPIUM_PID" 2>/dev/null

echo "=== 終了 $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"

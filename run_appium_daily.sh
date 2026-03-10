#!/bin/bash
# 毎日8時にAppiumを起動してp_uiautomator.pyを30分だけ実行するスクリプト

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$SCRIPT_DIR/myenv/bin/python3"
APPIUM="/Users/yamamotokenta/.nodebrew/current/bin/appium"
DURATION=1800  # 30分（秒）

while true; do
  # 次の8:00 AMまで待機
  NOW=$(date +%s)
  TODAY_8=$(date -v8H -v0M -v0S +%s)

  if [ "$NOW" -ge "$TODAY_8" ]; then
    # 今日の8時を過ぎていたら翌日の8時を計算
    NEXT_8=$(( TODAY_8 + 86400 ))
  else
    NEXT_8=$TODAY_8
  fi

  WAIT=$(( NEXT_8 - NOW ))
  echo "次の実行: $(date -r $NEXT_8 '+%Y-%m-%d %H:%M:%S') (${WAIT}秒後)"
  sleep $WAIT

  echo "===== $(date '+%Y-%m-%d %H:%M:%S') Appium起動 ====="

  # Appium起動（バックグラウンド）
  $APPIUM >> "$SCRIPT_DIR/appium.log" 2>&1 &
  APPIUM_PID=$!
  echo "Appium PID: $APPIUM_PID"
  sleep 3  # Appiumの起動を待つ

  # p_uiautomator.py起動（バックグラウンド）
  cd "$SCRIPT_DIR"
  $PYTHON p_uiautomator.py >> "$SCRIPT_DIR/p_uiautomator.log" 2>&1 &
  PY_PID=$!
  echo "p_uiautomator.py PID: $PY_PID"

  # 30分待機
  echo "30分間実行中... (終了予定: $(date -v+30M '+%H:%M:%S'))"
  sleep $DURATION

  # プロセス終了
  echo "===== $(date '+%Y-%m-%d %H:%M:%S') 終了処理 ====="
  kill $PY_PID 2>/dev/null && echo "p_uiautomator.py 終了 (PID: $PY_PID)"
  kill $APPIUM_PID 2>/dev/null && echo "Appium 終了 (PID: $APPIUM_PID)"

  # 念のため残存プロセスも終了
  sleep 2
  kill -9 $PY_PID 2>/dev/null
  kill -9 $APPIUM_PID 2>/dev/null

  echo "===== 完了 ====="
done

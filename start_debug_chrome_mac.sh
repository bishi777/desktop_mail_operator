#!/bin/bash
# デバッグ用Chrome起動スクリプト
# 使い方: ./start_debug_chrome.sh [ポート番号]
# 例: ./start_debug_chrome.sh 9222

PORT=${1:-9222}

echo "デバッグ用Chromeを起動します (port: $PORT)"

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=$PORT \
  --user-data-dir="$HOME/Library/Application Support/Google/Chrome/DebugProfile_$PORT" \
  --disable-popup-blocking

#!/bin/bash
# デバッグ用Chrome起動スクリプト
# 使い方: ./start_debug_chrome.sh [ポート番号]
# 例: ./start_debug_chrome.sh 9222
#
# 2026-07-19修正: Chromeを open 経由（launchd管理下）で起動する。
# 以前はシェルの子プロセスとして起動していたため、起動元のClaude Code
# セッションが終了するとChromeが道連れで終了していた。

PORT=${1:-9222}

# 既に同ポートで起動済みなら二重起動しない
if curl -s -m 2 "http://localhost:${PORT}/json/version" >/dev/null 2>&1; then
  echo "port ${PORT} のデバッグChromeは既に起動しています"
  exit 0
fi

echo "デバッグ用Chromeを起動します (port: $PORT)"

open -na "Google Chrome" --args \
  --remote-debugging-port=$PORT \
  --user-data-dir="$HOME/Library/Application Support/Google/Chrome/DebugProfile_$PORT" \
  --disable-popup-blocking \
  --disk-cache-size=104857600 \
  --media-cache-size=52428800

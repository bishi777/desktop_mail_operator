#!/bin/bash
# デバッグ用Chrome起動スクリプト
# 使い方: ./start_debug_chrome_mac.sh [ポート番号] [UAプリセット]
# 例:     ./start_debug_chrome_mac.sh 9222 iphone14
#         ./start_debug_chrome_mac.sh 9222 mac
#         ./start_debug_chrome_mac.sh 9222 "Mozilla/5.0 (...任意のUA文字列...)"
#
# UAプリセット (第2引数):
#   iphone14 (デフォルト) → iPhone14 相当のUA
#   mac                   → UA上書きなし (Chrome標準のMac UA)
#   それ以外の文字列       → その文字列をそのままUAとして使用
#
# ※ PCMAX は UA とログインセッションを紐付けているため、ログイン後にUAを
#   変えるとセッションが切れる。UAごとに別プロファイルを使い、その UA の
#   ままログインすること。プロファイルは DebugProfile_<port>_<uaタグ>。
#
# 2026-07-19修正: Chromeを open 経由（launchd管理下）で起動する。
# 以前はシェルの子プロセスとして起動していたため、起動元のClaude Code
# セッションが終了するとChromeが道連れで終了していた。

PORT=${1:-9222}
UA_PRESET=${2:-iphone14}

# iPhone14 相当UA（widget/jmail.py・happymail.py と同一文字列で統一）
IPHONE14_UA="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/537.36"

# UAプリセットを解決
case "$UA_PRESET" in
  iphone14)
    USER_AGENT="$IPHONE14_UA"
    UA_TAG="iphone14"
    ;;
  mac|"")
    USER_AGENT=""
    UA_TAG="mac"
    ;;
  *)
    # 任意のUA文字列
    USER_AGENT="$UA_PRESET"
    UA_TAG="custom"
    ;;
esac

# 既に同ポートで起動済みなら二重起動しない
if curl -s -m 2 "http://localhost:${PORT}/json/version" >/dev/null 2>&1; then
  echo "port ${PORT} のデバッグChromeは既に起動しています"
  exit 0
fi

PROFILE_DIR="$HOME/Library/Application Support/Google/Chrome/DebugProfile_${PORT}_${UA_TAG}"

if [ -n "$USER_AGENT" ]; then
  echo "デバッグ用Chromeを起動します (port: $PORT, UA: $UA_TAG)"
  echo "  UA: $USER_AGENT"
  open -na "Google Chrome" --args \
    --remote-debugging-port=$PORT \
    --user-data-dir="$PROFILE_DIR" \
    --user-agent="$USER_AGENT" \
    --disable-popup-blocking \
    --disk-cache-size=104857600 \
    --media-cache-size=52428800
else
  echo "デバッグ用Chromeを起動します (port: $PORT, UA: 標準Mac)"
  open -na "Google Chrome" --args \
    --remote-debugging-port=$PORT \
    --user-data-dir="$PROFILE_DIR" \
    --disable-popup-blocking \
    --disk-cache-size=104857600 \
    --media-cache-size=52428800
fi

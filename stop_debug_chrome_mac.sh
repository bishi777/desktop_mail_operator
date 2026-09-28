#!/bin/bash
# ============================================================
#  デバッグ用Chrome終了スクリプト (Mac版)
#  start_debug_chrome_mac.sh で起動したポート指定のChromeだけを安全に終了する
#  (普段使いのChromeには影響しない)
#  使い方: ./stop_debug_chrome_mac.sh [ポート番号]
#  例:     ./stop_debug_chrome_mac.sh 9223
#
#  動作:
#    1) コマンドラインに --remote-debugging-port=<PORT> を持つ Chrome プロセスだけを特定
#       (普段使いChromeや別ポートのデバッグChromeには触らない)
#    2) まず graceful に TERM を送りセッション/プロファイルを正しく保存させる
#    3) 5秒待って残っていたら KILL で強制終了
# ============================================================

PORT=${1:-9222}

echo "デバッグ用Chromeを終了します (port: $PORT)"

# --remote-debugging-port=<PORT> を持つプロセスの PID を取得する関数。
# 末尾に数字が続かない( =9222 が 92223 に部分マッチしない )ようパターンで縛る。
find_pids() {
  # pgrep -f はコマンドライン全体を対象にする。Chrome のメイン/子プロセス両方が拾える。
  pgrep -f -- "--remote-debugging-port=${PORT}([^0-9]|$)"
}

PIDS="$(find_pids)"
if [ -z "$PIDS" ]; then
  echo "port ${PORT} のデバッグ用Chromeは見つかりません"
  exit 0
fi

# 1) graceful に TERM
for pid in $PIDS; do
  echo "PID $pid へ終了要求を送信 (graceful TERM)"
  kill -TERM "$pid" 2>/dev/null
done

# 2) 5秒待つ
sleep 5

# 3) まだ残っていたら KILL
REST="$(find_pids)"
if [ -n "$REST" ]; then
  echo "終了しないため強制終了します (KILL)"
  for pid in $REST; do
    kill -KILL "$pid" 2>/dev/null
  done
  echo "強制終了しました"
else
  echo "正常に終了しました"
fi

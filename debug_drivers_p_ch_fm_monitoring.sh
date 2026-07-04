#!/bin/bash
# debug_drivers_p_ch_fm.py を無限リスタートで回す監視スクリプト
# 使い方: ./debug_drivers_p_ch_fm_monitoring.sh [ポート番号]
# 例:     ./debug_drivers_p_ch_fm_monitoring.sh 9223

PORT=${1:-9223}
SLEEP_SEC=${2:-600}

echo "======================================="
echo " debug_drivers_p_ch_fm 監視スクリプト起動"
echo " port      : $PORT"
echo " restart間隔 : $SLEEP_SEC 秒"
echo "======================================="

while true; do
    python debug_drivers_p_ch_fm.py "$PORT"
    echo "スクリプトが終了しました。${SLEEP_SEC}秒後に再起動します..."
    sleep "$SLEEP_SEC"
done

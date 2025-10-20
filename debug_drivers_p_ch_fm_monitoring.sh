#!/bin/bash

while true; do
    python debug_drivers_p_fm.py 
    echo "スクリプトが終了しました。再起動します..."
    sleep 600  # 少し待機してから再起動
done
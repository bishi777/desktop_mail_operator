#!/bin/bash

while true; do
    python h_ch_ma_rf_mf.py
    echo "スクリプトが終了しました。再起動します..."
    sleep 600  # 少し待機してから再起動
done
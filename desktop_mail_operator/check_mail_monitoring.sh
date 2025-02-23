#!/bin/bash

while true; do
    python check_mail.py
    echo "スクリプトが終了しました。再起動します..."
    sleep 5  # 少し待機してから再起動
done
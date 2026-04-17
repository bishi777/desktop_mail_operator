#!/bin/bash

PORT="${1:-9222}"

while true; do
    myenv/bin/python debug_drivers_ikukuru.py "$PORT"
    echo "スクリプトが終了しました。再起動します... (port: $PORT)"
    sleep 600
done

#!/bin/bash

PORT="${1:-9225}"
SEND_ON="${2:-0}"

while true; do
    myenv/bin/python debug_drivers_jmail.py "$PORT" "$SEND_ON"
    echo "スクリプトが終了しました。再起動します... (port: $PORT, send_on: $SEND_ON)"
    sleep 600
done

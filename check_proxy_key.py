#!/usr/bin/env python3
"""プロキシキーが settings.py の JPROXY_PROXYS に存在するか確認する。

存在すれば終了コード 0、無ければ 1 を返して利用可能なキー一覧を出す。

キー名はローマ字（erika, ema など）で、キャラ名の日本語表記ではない。
日本語名を渡すと proxy_auth_relay.py が起動直後に sys.exit するため、
Chrome だけがプロキシを向いて立ち上がり
net::ERR_PROXY_CONNECTION_FAILED になる。
原因が分かりにくいので、Chrome を起動する前にここで止める。

start_debug_chrome_win.bat / start_debug_chrome_mac.sh から呼ばれる。
"""

import os
import sys

# Windows のコンソールは既定が cp932 のため、bat 側で chcp 65001 にしていても
# Python 側の標準出力が cp932 だと日本語が化ける。UTF-8 に寄せる。
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    if len(sys.argv) < 2 or not sys.argv[1]:
        print("使い方: python check_proxy_key.py <プロキシキー>")
        return 1

    key = sys.argv[1]

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import settings
    except Exception as e:
        print(f"settings.py を読めません: {e}")
        return 1

    table = getattr(settings, "JPROXY_PROXYS", {}) or {}
    if key in table:
        return 0

    avail = ", ".join(sorted(table)) or "(空)"
    print(f"プロキシキー '{key}' は JPROXY_PROXYS にありません (settings.py)")
    print(f"  利用可能なキー: {avail}")
    print("  キー名はローマ字です（キャラ名の日本語表記ではありません）")
    return 1


if __name__ == "__main__":
    sys.exit(main())

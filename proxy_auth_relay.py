#!/usr/bin/env python3
"""認証付き上流プロキシへの認証を肩代わりするローカル中継。

Chrome の --proxy-server は user:pass 付きURLを受け付けず、認証ダイアログが
出てしまう。そこで「認証なしで繋げるローカルプロキシ」を 127.0.0.1 に立て、
上流への転送時に Proxy-Authorization を自動付与する。

  Chrome --proxy-server=127.0.0.1:<listen>
      → 本スクリプト（認証を付与）
          → 上流プロキシ (settings.py の JPROXY_PROXYS)
              → インターネット

使い方:
  # settings.py の JPROXY_PROXYS のキー名で指定
  python proxy_auth_relay.py --key erika --listen 18222

  # 直接指定
  python proxy_auth_relay.py --host 1.2.3.4 --port 8080 \
      --user someuser --password somepass --listen 18222

start_debug_chrome_mac.sh から自動起動されるため、通常は直接叩かない。
"""

import argparse
import base64
import os
import select
import socket
import sys
import threading

BUFSIZE = 65536
# 上流プロキシへの接続タイムアウト（秒）
CONNECT_TIMEOUT = 20


def _recv_headers(sock):
    """ヘッダ終端(\r\n\r\n)までを読み切って返す。

    ボディが先読みされるとCONNECT前の取りこぼしになるため、
    終端までしか読まないよう1バイトずつではなく都度チェックする。
    """
    data = b""
    while b"\r\n\r\n" not in data:
        try:
            chunk = sock.recv(BUFSIZE)
        except OSError:
            return b""
        if not chunk:
            break
        data += chunk
        # ヘッダが異常に大きい場合は打ち切る（不正リクエスト対策）
        if len(data) > 262144:
            break
    return data


def _pump(src, dst):
    """src → dst へ一方向に転送し続ける。"""
    try:
        while True:
            data = src.recv(BUFSIZE)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    finally:
        # 相手側の pump にも終了を伝える
        for s in (src, dst):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


def _relay_both(a, b):
    """双方向に転送し、どちらかが閉じるまで待つ。"""
    t = threading.Thread(target=_pump, args=(a, b), daemon=True)
    t.start()
    _pump(b, a)
    t.join(timeout=5)


class Relay:
    def __init__(self, up_host, up_port, auth_header):
        self.up_host = up_host
        self.up_port = up_port
        self.auth_header = auth_header

    def _connect_upstream(self):
        s = socket.create_connection((self.up_host, self.up_port), CONNECT_TIMEOUT)
        s.settimeout(None)
        return s

    def handle(self, client):
        upstream = None
        try:
            head = _recv_headers(client)
            if not head:
                return

            # ヘッダとボディ(先読み分)を分離
            sep = head.find(b"\r\n\r\n")
            if sep == -1:
                return
            header_blob = head[: sep + 4]
            body_prefix = head[sep + 4 :]

            lines = header_blob.split(b"\r\n")
            request_line = lines[0]

            # 既存の Proxy-Authorization / Proxy-Connection は捨てて付け直す
            kept = [request_line]
            for ln in lines[1:]:
                if not ln:
                    continue
                low = ln.lower()
                if low.startswith(b"proxy-authorization:"):
                    continue
                if low.startswith(b"proxy-connection:"):
                    continue
                kept.append(ln)
            kept.append(self.auth_header)

            rebuilt = b"\r\n".join(kept) + b"\r\n\r\n"

            upstream = self._connect_upstream()

            if request_line.upper().startswith(b"CONNECT "):
                # HTTPS: 上流に CONNECT を投げ、200 が返ったら素通しトンネルにする
                upstream.sendall(rebuilt)
                resp = _recv_headers(upstream)
                if not resp:
                    return
                status_line = resp.split(b"\r\n", 1)[0]
                client.sendall(resp)
                if b" 200" not in status_line:
                    # 認証失敗などはそのままクライアントへ返して終了
                    return
                _relay_both(client, upstream)
            else:
                # 平文 HTTP: ヘッダを書き換えて流し、以後は双方向中継
                upstream.sendall(rebuilt)
                if body_prefix:
                    upstream.sendall(body_prefix)
                _relay_both(client, upstream)
        except Exception:
            # 個別接続の失敗で中継全体を落とさない
            pass
        finally:
            for s in (client, upstream):
                if s is not None:
                    try:
                        s.close()
                    except OSError:
                        pass

    def serve(self, listen_host, listen_port):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((listen_host, listen_port))
        srv.listen(128)
        print(
            f"[proxy-relay] {listen_host}:{listen_port} → "
            f"{self.up_host}:{self.up_port} (認証付与) で待受開始",
            flush=True,
        )
        while True:
            try:
                client, _ = srv.accept()
            except OSError:
                break
            threading.Thread(target=self.handle, args=(client,), daemon=True).start()


def resolve_proxy(args):
    """引数または settings.py から上流プロキシ情報を解決する。"""
    if args.key:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        try:
            import settings
        except Exception as e:
            sys.exit(f"[proxy-relay] settings.py を読めません: {e}")
        table = getattr(settings, "JPROXY_PROXYS", {}) or {}
        if args.key not in table:
            avail = ", ".join(sorted(table)) or "(空)"
            sys.exit(
                f"[proxy-relay] JPROXY_PROXYS にキー '{args.key}' がありません。"
                f" 利用可能: {avail}"
            )
        p = table[args.key]
        return str(p["HOST"]), int(p["PORT"]), str(p["USER"]), str(p["PASS"])

    if not (args.host and args.port):
        sys.exit("[proxy-relay] --key か --host/--port のどちらかを指定してください")
    return args.host, int(args.port), args.user or "", args.password or ""


def main():
    ap = argparse.ArgumentParser(description="認証付きプロキシへのローカル中継")
    ap.add_argument("--key", help="settings.py の JPROXY_PROXYS のキー名")
    ap.add_argument("--host", help="上流プロキシのホスト")
    ap.add_argument("--port", help="上流プロキシのポート")
    ap.add_argument("--user", help="上流プロキシのユーザー名")
    ap.add_argument("--password", help="上流プロキシのパスワード")
    ap.add_argument("--listen", type=int, required=True, help="待受ポート")
    ap.add_argument(
        "--listen-host", default="127.0.0.1", help="待受アドレス(既定: 127.0.0.1)"
    )
    args = ap.parse_args()

    host, port, user, password = resolve_proxy(args)
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    auth_header = f"Proxy-Authorization: Basic {token}".encode()

    Relay(host, port, auth_header).serve(args.listen_host, args.listen)


if __name__ == "__main__":
    main()

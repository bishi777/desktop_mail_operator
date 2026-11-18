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

通信量の記録:
  直近 STATS_INTERVAL 秒に STATS_MIN_BYTES 以上流れたときだけ、相手ホスト別の
  内訳をログ (logs/proxy_relay_<port>.log) に [stats] 行として1行出す。
  「Chrome が遅い」ときに、Chrome が裏で大きなダウンロードをして回線を
  食っていないか、上流プロキシが接続を断っていないかを後から確かめるため。
"""

import argparse
import base64
import os
import select
import socket
import sys
import threading
import time
from urllib.parse import urlsplit

BUFSIZE = 65536
# 上流プロキシへの接続タイムアウト（秒）
CONNECT_TIMEOUT = 20
# 通信量をログに出す間隔（秒）と、出す下限（これ未満の分は黙って捨てる）。
# JPROXY は絞られると 0.1〜0.2Mbps (= 1分で 0.75〜1.5MB) になるので、
# その状態で張り付いていても拾えるよう下限は低めにしておく。
STATS_INTERVAL = 60
STATS_MIN_BYTES = 200_000
# 内訳に出す相手ホストの数
STATS_TOP = 5


class TrafficStats:
    """直近の通信量を相手ホスト別に数える（ログ出力用）。"""

    def __init__(self):
        self._lock = threading.Lock()
        self._bytes = {}  # host -> [下り, 上り]
        self._errors = {}  # 失敗内容 -> 回数
        self._active = 0

    def add(self, host, down=0, up=0):
        with self._lock:
            v = self._bytes.setdefault(host, [0, 0])
            v[0] += down
            v[1] += up

    def error(self, what):
        with self._lock:
            self._errors[what] = self._errors.get(what, 0) + 1

    def opened(self):
        with self._lock:
            self._active += 1

    def closed(self):
        with self._lock:
            self._active -= 1

    def take(self):
        """ここまでの集計を取り出してリセットする。"""
        with self._lock:
            by_host, errors = self._bytes, self._errors
            self._bytes, self._errors = {}, {}
            return by_host, errors, self._active


def _report_loop(stats, interval):
    while True:
        time.sleep(interval)
        by_host, errors, active = stats.take()
        down = sum(v[0] for v in by_host.values())
        up = sum(v[1] for v in by_host.values())
        if down + up < STATS_MIN_BYTES and not errors:
            continue
        top = sorted(by_host.items(), key=lambda kv: kv[1][0] + kv[1][1], reverse=True)
        parts = [
            f"[stats {time.strftime('%m/%d %H:%M:%S')}] 中継中 {active}本",
            f"直近{interval}秒 下り {down / 1e6:.1f}MB (平均 {down * 8 / interval / 1e6:.2f}Mbps)"
            f" 上り {up / 1e6:.1f}MB",
        ]
        if top:
            parts.append(
                "内訳: "
                + ", ".join(f"{h} {(d + u) / 1e6:.1f}MB" for h, (d, u) in top[:STATS_TOP])
            )
        if errors:
            parts.append("失敗: " + ", ".join(f"{k} x{n}" for k, n in errors.items()))
        print(" / ".join(parts), flush=True)


def _target_host(request_line):
    """リクエスト行から相手ホスト名を取り出す（統計用）。

    平文 HTTP の keep-alive で1本の接続が別ホストへ使い回された場合は
    最初のホストに計上される（統計用なので厳密さは求めない）。
    """
    try:
        target = request_line.split()[1].decode("latin-1")
    except IndexError:
        return "?"
    if "://" in target:
        return urlsplit(target).hostname or "?"
    return target.rsplit(":", 1)[0]


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


def _pump(src, dst, on_bytes=None):
    """src → dst へ一方向に転送し続ける。on_bytes には転送したバイト数を渡す。"""
    try:
        while True:
            data = src.recv(BUFSIZE)
            if not data:
                break
            dst.sendall(data)
            if on_bytes is not None:
                on_bytes(len(data))
    except OSError:
        pass
    finally:
        # 相手側の pump にも終了を伝える
        for s in (src, dst):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


def _relay_both(a, b, on_a_to_b=None, on_b_to_a=None):
    """双方向に転送し、どちらかが閉じるまで待つ。"""
    t = threading.Thread(target=_pump, args=(a, b, on_a_to_b), daemon=True)
    t.start()
    _pump(b, a, on_b_to_a)
    t.join(timeout=5)


class Relay:
    def __init__(self, up_host, up_port, auth_header):
        self.up_host = up_host
        self.up_port = up_port
        self.auth_header = auth_header
        self.stats = TrafficStats()

    def _connect_upstream(self):
        try:
            s = socket.create_connection((self.up_host, self.up_port), CONNECT_TIMEOUT)
        except OSError as e:
            self.stats.error(f"上流に接続できない({type(e).__name__})")
            raise
        s.settimeout(None)
        return s

    def _tunnel(self, client, upstream, host):
        """client(Chrome) ⇔ upstream を中継し、通信量を host 宛てとして数える。"""
        self.stats.opened()
        try:
            _relay_both(
                client,
                upstream,
                on_a_to_b=lambda n: self.stats.add(host, up=n),
                on_b_to_a=lambda n: self.stats.add(host, down=n),
            )
        finally:
            self.stats.closed()

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
            host = _target_host(request_line)

            upstream = self._connect_upstream()

            if request_line.upper().startswith(b"CONNECT "):
                # HTTPS: 上流に CONNECT を投げ、200 が返ったら素通しトンネルにする
                upstream.sendall(rebuilt)
                resp = _recv_headers(upstream)
                if not resp:
                    self.stats.error("上流が CONNECT に無応答で切断")
                    return
                status_line = resp.split(b"\r\n", 1)[0]
                client.sendall(resp)
                if b" 200" not in status_line:
                    # 認証失敗などはそのままクライアントへ返して終了
                    self.stats.error(status_line.decode("latin-1", "replace")[:60])
                    return
                self._tunnel(client, upstream, host)
            else:
                # 平文 HTTP: ヘッダを書き換えて流し、以後は双方向中継
                upstream.sendall(rebuilt)
                if body_prefix:
                    upstream.sendall(body_prefix)
                self._tunnel(client, upstream, host)
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

    def serve(self, listen_host, listen_port, stats_interval=STATS_INTERVAL):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((listen_host, listen_port))
        srv.listen(128)
        print(
            f"[proxy-relay {time.strftime('%m/%d %H:%M:%S')}] {listen_host}:{listen_port} → "
            f"{self.up_host}:{self.up_port} (認証付与) で待受開始",
            flush=True,
        )
        threading.Thread(
            target=_report_loop, args=(self.stats, stats_interval), daemon=True
        ).start()
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
    ap.add_argument(
        "--stats-interval",
        type=int,
        default=STATS_INTERVAL,
        help=f"通信量をログに出す間隔・秒(既定: {STATS_INTERVAL})",
    )
    args = ap.parse_args()

    host, port, user, password = resolve_proxy(args)
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    auth_header = f"Proxy-Authorization: Basic {token}".encode()

    Relay(host, port, auth_header).serve(
        args.listen_host, args.listen, args.stats_interval
    )


if __name__ == "__main__":
    main()

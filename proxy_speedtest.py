#!/usr/bin/env python3
"""プロキシ経路の速度を区間ごとに測り、どこで遅くなっているかを切り分ける。

Chrome が遅いとき、原因は次のどこかにある:
  [直接]       この PC の回線そのもの
  [上流に直接] JPROXY のプロキシ（proxy_auth_relay.py を通さずにつなぐ）
  [中継経由]   proxy_auth_relay.py 経由（= Chrome と同じ経路）
3つを順に測って比べれば、遅い区間がわかる。

使い方（Chrome は止めずに、遅いと感じている状態のまま実行する）:
  python proxy_speedtest.py              # 起動中の中継すべて
  python proxy_speedtest.py erika reina  # キーを指定
  python proxy_speedtest.py --all        # settings.py の全キー（中継が無いキーは上流だけ）

計測は軽くしてある（1経路 2MB まで・1本だけ）。
JPROXY は 15〜20MB ほど流すと 0.1〜0.2Mbps に絞られることを確認済みで
(2026-11-18)、重い計測をすると計測そのものが制限を発動させて、
運用中のキャラまで遅くしてしまうため。
"""

import argparse
import os
import re
import subprocess
import sys
import threading
import time

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import settings  # noqa: E402

DOWN_URL = "https://speed.cloudflare.com/__down?bytes=25000000"
PING_URL = "https://www.gstatic.com/generate_204"
TEST_SEC = 10  # 1回の計測時間の上限（秒）
BYTE_BUDGET = 2_000_000  # 1回の計測で落とす上限（多いと計測が制限を発動させる）
SLOW_MBPS = 3.0  # これ未満を「遅い」とみなす


def find_relays():
    """起動中の proxy_auth_relay.py を探し、[(key, listen_port)] を返す。"""
    if os.name == "nt":
        # 自分自身(powershell)のコマンドラインは 'relay\.py' を含むだけで
        # 'relay.py' には一致しないので拾わない
        ps = (
            "Get-CimInstance Win32_Process"
            " | Where-Object { $_.CommandLine -match 'proxy_auth_relay\\.py' }"
            " | ForEach-Object { '' + $_.ProcessId + [char]9 + $_.CommandLine }"
        )
        cmd = ["powershell", "-NoProfile", "-Command", ps]
    else:
        cmd = ["ps", "-axo", "pid=,command="]
    out = subprocess.run(cmd, capture_output=True, text=True, errors="replace").stdout
    found = []
    for line in out.splitlines():
        if "proxy_auth_relay.py" not in line:
            continue
        m_key = re.search(r"--key\s+\"?([\w-]+)", line)
        m_port = re.search(r"--listen\s+(\d+)", line)
        if not m_port:
            continue
        item = (m_key.group(1) if m_key else None, int(m_port.group(1)))
        # Windows の venv は python.exe が本体を子プロセスで起動するので、
        # 同じ中継が2プロセス見える。重複は1つにまとめる
        if item not in found:
            found.append(item)
    return found


def netstat_lines():
    out = subprocess.run(
        ["netstat", "-an"], capture_output=True, text=True, errors="replace"
    ).stdout
    return out.splitlines()


def count_states(lines, host, port):
    """この PC から host:port への TCP 接続を状態ごとに数える。"""
    targets = {f"{host}:{port}", f"{host}.{port}"}  # Windows / macOS の表記
    counts = {}
    for ln in lines:
        tok = ln.split()
        if not any(t in targets for t in tok):
            continue
        state = tok[-1] if re.fullmatch(r"[A-Z_0-9]+", tok[-1]) else "?"
        counts[state] = counts.get(state, 0) + 1
    return counts


def _session(proxy):
    s = requests.Session()
    s.trust_env = False  # 環境変数のプロキシ設定を無視し、指定どおりの経路で測る
    if proxy:
        s.proxies = {"http": proxy, "https": proxy}
    return s


def ping(proxy):
    """新しい接続で小さなページを取るまでの秒数（接続+TLS+応答）。2回のうち速いほう。"""
    best = None
    for _ in range(2):
        s = _session(proxy)
        t0 = time.monotonic()
        try:
            s.get(PING_URL, timeout=15)
            dt = time.monotonic() - t0
            best = dt if best is None else min(best, dt)
        except requests.RequestException:
            pass
        finally:
            s.close()
    return best


def speed(proxy, streams):
    """streams 本を並列にダウンロードし、(合計 Mbps, 失敗の種類リスト) を返す。"""
    got = [0]
    lock = threading.Lock()
    errors = []
    start = time.monotonic()
    deadline = start + TEST_SEC

    def worker():
        s = _session(proxy)
        try:
            with s.get(DOWN_URL, stream=True, timeout=(15, 15)) as r:
                r.raise_for_status()
                for chunk in r.iter_content(16384):
                    with lock:
                        got[0] += len(chunk)
                        enough = got[0] >= BYTE_BUDGET
                    if enough or time.monotonic() >= deadline:
                        break
        except requests.RequestException as e:
            errors.append(type(e).__name__)
        finally:
            s.close()

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(streams)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(TEST_SEC + 35)
    elapsed = time.monotonic() - start
    return got[0] * 8 / elapsed / 1e6, errors


def measure(label, proxy):
    """1本で測って表示し、Mbps を返す。"""
    p = ping(proxy)
    mbps, errs = speed(proxy, 1)
    txt = f"{mbps:6.2f} Mbps"
    if errs:
        txt += f" (失敗: {', '.join(sorted(set(errs)))})"
    p_txt = f"{p:.2f}秒" if p is not None else "失敗"
    print(f"  {label}: {txt} | 応答 {p_txt}", flush=True)
    return mbps


def verdict(base, up, rel):
    if base < SLOW_MBPS:
        return "この PC の回線そのものが遅い（プロキシ以前の問題）"
    if up < SLOW_MBPS:
        return (
            "JPROXY 側で絞られている（中継の問題ではない）。"
            "何が通信量を使ったかは中継ログ logs/proxy_relay_<port>.log の [stats] 行で確認"
        )
    if rel is None:
        return "上流は速い（中継が起動していないので、Chrome と同じ経路は測っていない）"
    if rel < SLOW_MBPS or rel < up * 0.3:
        return "中継 (proxy_auth_relay.py) で詰まっている。stop → start で中継を起動し直して再計測"
    return "今はどの区間も速い"


def main():
    ap = argparse.ArgumentParser(description="プロキシ経路の区間ごとの速度チェック")
    ap.add_argument("keys", nargs="*", help="JPROXY_PROXYS のキー（省略時は起動中の中継）")
    ap.add_argument("--all", action="store_true", help="settings.py の全キーを測る")
    args = ap.parse_args()

    table = getattr(settings, "JPROXY_PROXYS", {}) or {}
    relays = find_relays()

    if args.keys:
        keys = args.keys
    elif args.all:
        keys = list(table)
    else:
        keys = []
        for k, _ in relays:
            if k and k not in keys:
                keys.append(k)
    unknown = [k for k in keys if k not in table]
    if unknown:
        sys.exit(f"JPROXY_PROXYS に無いキー: {', '.join(unknown)} / 利用可能: {', '.join(table)}")
    if not keys:
        sys.exit("起動中の中継が見つかりません。キーを指定してください（例: python proxy_speedtest.py erika）")

    # 同じ待受ポートに別キーの中継が2つ居ると、Chrome がどちらの IP を使うか定まらない
    by_port = {}
    for k, port in relays:
        by_port.setdefault(port, set()).add(k)
    for port, ks in by_port.items():
        if len(ks) > 1:
            print(f"⚠️ 127.0.0.1:{port} に別キーの中継が重複しています: {', '.join(sorted(map(str, ks)))}")

    print(f"=== プロキシ速度チェック {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    print("（Chrome は止めずに、遅いと感じている状態のまま測ってください）\n")
    print("[直接] この PC の回線（プロキシなし）")
    base = measure("直接", None)
    lines = netstat_lines()

    for key in keys:
        p = table[key]
        host, port = str(p["HOST"]), int(p["PORT"])
        upstream = f"http://{p['USER']}:{p['PASS']}@{host}:{port}"
        mine = [lp for k, lp in relays if k == key]
        relay_txt = ", ".join(f"127.0.0.1:{lp} (Chrome port {lp - 10000})" for lp in mine) or "起動していない"
        print(f"\n[{key}] 上流 {host}:{port} / 中継 {relay_txt}")
        # Chrome と同じ経路（中継経由）を先に測る。後に回すと、先の計測で
        # 使った通信量のせいで絞られた値を拾いかねないため
        rel = None
        for lp in mine:
            r = measure(f"中継経由 {lp}", f"http://127.0.0.1:{lp}")
            rel = r if rel is None else min(rel, r)
        up = measure("上流に直接", upstream)
        states = count_states(lines, host, port)
        st_txt = ", ".join(f"{s} {n}" for s, n in sorted(states.items())) or "なし"
        print(f"  上流への接続数（計測前・この PC 全体）: {st_txt}")
        print(f"  → {verdict(base, up, rel)}")


if __name__ == "__main__":
    main()

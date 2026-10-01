#!/usr/bin/env python3
"""インストール済み Chrome に合う chromedriver を取得して配置する。

Chrome は自動更新で頻繁にメジャーバージョンが上がるが、chromedriver は
追従しないため "This version of ChromeDriver only supports Chrome version N"
で動かなくなる。Homebrew の chromedriver cask は Gatekeeper を通らず
2026-09-01 に無効化されたので brew upgrade でも直せない。

このスクリプトは Chrome のバージョンを調べ、Chrome for Testing から
対応する chromedriver を取得して配置し、macOS で必要な後処理
(quarantine 除去 / ad-hoc 署名) までを一括で行う。

使い方:
  python update_chromedriver.py           # 必要なときだけ更新
  python update_chromedriver.py --force   # 一致していても入れ直す
  python update_chromedriver.py --dry-run # 何をするか表示するだけ

配置先は PATH 上の既存 chromedriver。無ければ /opt/homebrew/bin を使う。
"""

import argparse
import json
import os
import platform
import plistlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

CFT_ENDPOINT = (
    "https://googlechromelabs.github.io/chrome-for-testing/"
    "known-good-versions-with-downloads.json"
)
CHROME_APP = "/Applications/Google Chrome.app"
DEFAULT_DEST_DIR = "/opt/homebrew/bin"


def detect_chrome_version():
    """インストール済み Chrome のバージョンを返す（例: '154.0.8037.58'）。"""
    plist = os.path.join(CHROME_APP, "Contents", "Info.plist")
    if os.path.exists(plist):
        try:
            with open(plist, "rb") as f:
                v = plistlib.load(f).get("CFBundleShortVersionString")
            if v:
                return v
        except Exception:
            pass
    # plist が読めないときは実行ファイルに聞く
    exe = os.path.join(CHROME_APP, "Contents", "MacOS", "Google Chrome")
    if os.path.exists(exe):
        try:
            out = subprocess.run(
                [exe, "--version"], capture_output=True, text=True, timeout=30
            ).stdout
            m = re.search(r"(\d+\.\d+\.\d+\.\d+)", out)
            if m:
                return m.group(1)
        except Exception:
            pass
    return None


def detect_driver_version(path):
    """chromedriver のバージョンを返す。取得できなければ None。"""
    if not path or not os.path.exists(path):
        return None
    try:
        out = subprocess.run(
            [path, "--version"], capture_output=True, text=True, timeout=30
        ).stdout
        m = re.search(r"(\d+\.\d+\.\d+\.\d+)", out)
        return m.group(1) if m else None
    except Exception:
        return None


def platform_key():
    """Chrome for Testing のプラットフォーム名を返す。"""
    if sys.platform != "darwin":
        sys.exit("このスクリプトは macOS 専用です")
    return "mac-arm64" if platform.machine() == "arm64" else "mac-x64"


def pick_driver_url(chrome_version, plat):
    """Chrome のバージョンに最も近い chromedriver の URL を選ぶ。

    ビルド番号まで一致するとは限らない (Chrome 154.0.8037.58 に対して
    driver は 154.0.8037.92 しか無い等) ので、同じ major.minor.build の中から
    patch が最も近いものを選び、無ければ同じ major の最新を使う。
    """
    with urllib.request.urlopen(CFT_ENDPOINT, timeout=60) as r:
        data = json.load(r)

    def parts(v):
        try:
            return tuple(int(x) for x in v.split("."))
        except ValueError:
            return (0, 0, 0, 0)

    want = parts(chrome_version)
    cands = []
    for v in data.get("versions", []):
        url = next(
            (
                d["url"]
                for d in v.get("downloads", {}).get("chromedriver", [])
                if d.get("platform") == plat
            ),
            None,
        )
        if url:
            cands.append((parts(v["version"]), v["version"], url))
    if not cands:
        sys.exit(f"{plat} 向けの chromedriver が見つかりません")

    # 1) major.minor.build が一致するものを優先。
    #    patch は Chrome 以上の中で最小（= 直近の対応版）を選ぶ。
    #    Chrome 側の patch の方が新しい場合は、同じ build の最新で代用する。
    same_build = [c for c in cands if c[0][:3] == want[:3]]
    if same_build:
        newer = [c for c in same_build if c[0][3] >= want[3]]
        best = min(newer, key=lambda c: c[0]) if newer else max(same_build, key=lambda c: c[0])
        return best[1], best[2]

    # 2) major が一致する中で最新
    same_major = [c for c in cands if c[0][0] == want[0]]
    if same_major:
        best = max(same_major, key=lambda c: c[0])
        return best[1], best[2]

    sys.exit(
        f"Chrome {chrome_version} に対応する chromedriver が見つかりません"
        "（Chrome が新しすぎる可能性があります）"
    )


def resolve_dest():
    """配置先のパスを決める。PATH 上の既存を優先。"""
    found = shutil.which("chromedriver")
    if found:
        return found
    return os.path.join(DEFAULT_DEST_DIR, "chromedriver")


def install(url, dest, dry_run=False):
    """ダウンロードして dest に配置し、macOS 用の後処理まで行う。"""
    if dry_run:
        print(f"[dry-run] {url}\n[dry-run]   → {dest}")
        return

    with tempfile.TemporaryDirectory() as tmp:
        zpath = os.path.join(tmp, "chromedriver.zip")
        print(f"ダウンロード中: {url}")
        urllib.request.urlretrieve(url, zpath)
        with zipfile.ZipFile(zpath) as z:
            z.extractall(tmp)

        src = None
        for root, _, files in os.walk(tmp):
            if "chromedriver" in files:
                src = os.path.join(root, "chromedriver")
                break
        if not src:
            sys.exit("zip の中に chromedriver が見つかりません")

        os.makedirs(os.path.dirname(dest), exist_ok=True)
        # 使用中だと Text file busy になるので一度どける
        if os.path.exists(dest):
            try:
                os.remove(dest)
            except OSError as e:
                sys.exit(f"既存の {dest} を置き換えられません: {e}")
        shutil.move(src, dest)
        os.chmod(dest, os.stat(dest).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    # Gatekeeper 対策: 隔離属性を外し、ad-hoc 署名を付け直す
    subprocess.run(["xattr", "-d", "com.apple.quarantine", dest],
                   capture_output=True)
    r = subprocess.run(["codesign", "--force", "--sign", "-", dest],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  [警告] 署名に失敗: {r.stderr.strip()[:200]}")
    print(f"配置しました: {dest}")


def main():
    ap = argparse.ArgumentParser(
        description="Chrome に合う chromedriver を取得して配置する"
    )
    ap.add_argument("--force", action="store_true",
                    help="バージョンが合っていても入れ直す")
    ap.add_argument("--dry-run", action="store_true",
                    help="実際には変更せず、何をするかだけ表示")
    ap.add_argument("--dest", help="配置先のパス（既定: PATH 上の chromedriver）")
    args = ap.parse_args()

    chrome = detect_chrome_version()
    if not chrome:
        sys.exit("Chrome のバージョンを特定できません（Chrome 未インストール?）")

    dest = args.dest or resolve_dest()
    current = detect_driver_version(dest)

    print(f"Chrome       : {chrome}")
    print(f"chromedriver : {current or '(なし)'}  @ {dest}")

    # major が一致していれば基本的に動くので、既定ではそれを「一致」とみなす
    if current and not args.force:
        if current.split(".")[0] == chrome.split(".")[0]:
            print("メジャーバージョンが一致しています。更新は不要です。")
            print("（入れ直す場合は --force）")
            return

    version, url = pick_driver_url(chrome, platform_key())
    print(f"取得する版   : {version}")
    install(url, dest, dry_run=args.dry_run)

    if not args.dry_run:
        after = detect_driver_version(dest)
        print(f"確認         : chromedriver {after or '取得失敗'}")
        if after and after.split(".")[0] != chrome.split(".")[0]:
            print("  [警告] まだメジャーバージョンが一致していません")
        else:
            print("完了。デバッグ用 Chrome を起動し直してください:")
            print("  ./stop_debug_chrome_mac.sh <port>")
            print("  ./start_debug_chrome_mac.sh <port> [プロキシキー]")


if __name__ == "__main__":
    main()

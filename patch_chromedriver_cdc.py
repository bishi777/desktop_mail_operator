"""
chromedriver の cdc_ 痕跡を除去するパッチスクリプト（方法A）。

■ 何をするか
  chromedriver(.exe) のバイナリ内にハードコードされている固定文字列
  "cdc_adoQpoasnfa76pfcZLmcfl" を、同じ長さのランダム英数字に書き換える。
  検知側は固定の "cdc_" 名前空間を探すため、名前が変われば
  window.cdc_... ベースの自動化検知をすり抜けられる。
  （undetected-chromedriver が内部でやっているのと同じ手法）

■ 安全設計
  - パッチ前に必ず .bak バックアップを作成（--restore で復元可能）
  - バイナリ長は不変（同じ長さのランダム文字列に置換するだけ）
  - 冪等: 既にパッチ済み(cdc_が無い)なら何もしない
  - webdriver_manager(~/.wdm) と Selenium Manager キャッシュの両方を自動探索

■ 使い方（Windows / Mac 共通、プロジェクトの venv で実行）
  # パッチを当てる（cdc_ を持つ全ドライバを検出して置換）
  myenv\Scripts\python patch_chromedriver_cdc.py          (Windows)
  myenv/bin/python patch_chromedriver_cdc.py              (Mac)

  # 特定のドライバだけパッチ
  python patch_chromedriver_cdc.py --path "C:\path\to\chromedriver.exe"

  # 元に戻す（.bak から復元）
  python patch_chromedriver_cdc.py --restore

■ 注意
  - Chrome を更新すると webdriver_manager が新しい chromedriver を落とすので、
    その都度このスクリプトを再実行する必要がある。
  - cdc_ を消しても platform(実OS) や WebGL レンダラ等の痕跡は残るため、
    Cloudflare Turnstile 級の検知を完全に突破できる保証はない。
  - パッチ対象のドライバを使っている Chrome/ChromeDriver は事前に終了しておくこと
    （実行中だとファイルロックで書き込めない場合がある）。
"""
import os
import sys
import glob
import random
import string
import shutil
import argparse

# 検知される固定の cdc_ 名前空間（ChromeDriver にハードコードされている）
CDC_TARGET = b"cdc_adoQpoasnfa76pfcZLmcfl"


def find_chromedrivers():
    """webdriver_manager と Selenium のキャッシュから chromedriver(.exe) を全部探す。"""
    home = os.path.expanduser("~")
    patterns = [
        # webdriver_manager (~/.wdm)
        os.path.join(home, ".wdm", "**", "chromedriver.exe"),
        os.path.join(home, ".wdm", "**", "chromedriver"),
        # Selenium Manager キャッシュ
        os.path.join(home, ".cache", "selenium", "chromedriver", "**", "chromedriver.exe"),
        os.path.join(home, ".cache", "selenium", "chromedriver", "**", "chromedriver"),
    ]
    found = set()
    for pat in patterns:
        for p in glob.glob(pat, recursive=True):
            # .bak や THIRD_PARTY 等の非バイナリを除外
            base = os.path.basename(p)
            if base in ("chromedriver", "chromedriver.exe") and os.path.isfile(p):
                found.add(os.path.abspath(p))
    return sorted(found)


def random_namespace(length):
    """同じ長さのランダム置換名（先頭は英字にして念のため妥当性を保つ）。"""
    first = random.choice(string.ascii_lowercase)
    rest = "".join(random.choices(string.ascii_lowercase + string.digits, k=length - 1))
    return (first + rest).encode()


def patch_one(path, quiet=False):
    """1つの chromedriver をパッチ。パッチした→True / 不要(既に無い)→False。"""
    with open(path, "rb") as f:
        data = f.read()
    cnt = data.count(CDC_TARGET)
    if cnt == 0:
        if not quiet:
            print(f"  [skip] cdc_ なし（パッチ済みか対象外）: {path}")
        return False
    # バックアップ（既にあれば上書きしない = 最初の未パッチ状態を保持）
    bak = path + ".bak"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        if not quiet:
            print(f"  [backup] {bak}")
    repl = random_namespace(len(CDC_TARGET))
    assert len(repl) == len(CDC_TARGET), "置換文字列の長さが不一致"
    data2 = data.replace(CDC_TARGET, repl)
    assert len(data2) == len(data), "バイナリ長が変わった（異常）"
    # 書き込み（実行権限を保持）
    mode = os.stat(path).st_mode
    with open(path, "wb") as f:
        f.write(data2)
    os.chmod(path, mode)
    if not quiet:
        print(f"  [patched] cdc_ {cnt}箇所 → '{repl.decode()}' : {path}")
    return True


def restore_one(path):
    """.bak から復元。"""
    bak = path + ".bak"
    if not os.path.exists(bak):
        print(f"  [skip] バックアップなし: {path}")
        return False
    shutil.copy2(bak, path)
    print(f"  [restored] {path}  ← {bak}")
    return True


def patch_all(quiet=True):
    """外部モジュールから呼ぶ用: 見つかった全 chromedriver をパッチする。
    debug_drivers 等の起動処理から接続前に呼ぶことを想定。
    戻り値: パッチした個数。例外は握りつぶして 0 を返す（起動を止めない）。"""
    try:
        targets = find_chromedrivers()
        if not targets:
            return 0
        done = 0
        for t in targets:
            try:
                if patch_one(t, quiet=quiet):
                    done += 1
            except PermissionError:
                if not quiet:
                    print(f"  [cdc_パッチ] 書き込み不可(使用中?): {t}")
            except Exception as e:
                if not quiet:
                    print(f"  [cdc_パッチ] {type(e).__name__}: {e} : {t}")
        return done
    except Exception as e:
        if not quiet:
            print(f"  [cdc_パッチ] 探索失敗: {e}")
        return 0


def main():
    ap = argparse.ArgumentParser(description="chromedriver の cdc_ 痕跡を除去するパッチ")
    ap.add_argument("--path", help="特定の chromedriver(.exe) だけを対象にする")
    ap.add_argument("--restore", action="store_true", help=".bak から元に戻す")
    args = ap.parse_args()

    if args.path:
        targets = [os.path.abspath(args.path)]
    else:
        targets = find_chromedrivers()

    if not targets:
        print("chromedriver が見つかりませんでした。")
        print("--path で明示的に指定してください（例: --path chromedriver.exe のフルパス）")
        sys.exit(1)

    print(f"対象 chromedriver: {len(targets)}個")
    for t in targets:
        print(f"  - {t}")
    print()

    action = restore_one if args.restore else patch_one
    label = "復元" if args.restore else "パッチ"
    done = 0
    for t in targets:
        try:
            if action(t):
                done += 1
        except PermissionError:
            print(f"  [error] 書き込み不可（Chrome/ChromeDriver 実行中の可能性）: {t}")
        except Exception as e:
            print(f"  [error] {type(e).__name__}: {e} : {t}")

    print(f"\n{label}完了: {done}個")
    if not args.restore and done:
        print("※ Chrome を更新するとドライバが再取得されるので、その都度再実行してください。")


if __name__ == "__main__":
    main()

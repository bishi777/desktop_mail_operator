"""
Nano Banana Pro (gemini-3-pro-image-preview) でキャラ画像を加工するスクリプト。

使い方:
    myenv/bin/python make_chara_image.py <キャラ名> [プレフィックス]

例:
    myenv/bin/python make_chara_image.py reina        # → reina/80420.jpg
    myenv/bin/python make_chara_image.py reina p      # → reina/p80420.jpg
    myenv/bin/python make_chara_image.py yukko h      # → yukko_yuki/h80420.jpg

仕様:
    - Google Drive のキャラフォルダ内 original.{jpg,png} を元画像とする
    - 微細変形（±0.5〜1度回転、±1〜2% 色調）
    - キャラ別スタンプ処理:
        * yukko / yuki / erika : スタンプなし（微細変形のみ）
        * reina : 鼻 or 鼻+口（必ず鼻を隠す）
        * iori : 元画像のピンクハート3つを選択スタンプで完全置換
        * その他 : 鼻 / 口 / 鼻+口 のランダム
    - 保存名: 令和年(1桁)+月(2桁)+日(2桁) （例 80420）
        プレフィックスがあれば先頭に付与（p80420 等）
"""

import sys
import random
import mimetypes
from datetime import date
from pathlib import Path

from google import genai
from google.genai import types

from settings import Gemini_API_KEY


CHARA_BASE = Path(
    "/Users/yamamotokenta/Library/CloudStorage/"
    "GoogleDrive-kenta.bishi777@gmail.com/マイドライブ/キャラ画像"
)
STAMPS_DIR = CHARA_BASE / "アクセサリ" / "stamps"

NO_STAMP_CHARS = {"yukko", "yuki", "erika", "ayu", "tumugi"}
FOLDER_ALIAS = {
    "yukko": "yukko_yuki",
    "yuki": "yukko_yuki",
}

MODEL = "gemini-3-pro-image-preview"


def reiwa_filename_base(today: date) -> str:
    """令和年(1桁)+月(2桁)+日(2桁) の文字列を返す。"""
    reiwa_year = today.year - 2018  # 2019 = 令和元年
    return f"{reiwa_year}{today.month:02d}{today.day:02d}"


def find_original(folder: Path) -> Path:
    for ext in ("jpg", "jpeg", "png", "JPG", "JPEG", "PNG"):
        p = folder / f"original.{ext}"
        if p.exists():
            return p
    raise FileNotFoundError(
        f"original.(jpg|png) が見つかりません: {folder}"
    )


def load_image_part(path: Path) -> types.Part:
    mime, _ = mimetypes.guess_type(str(path))
    if mime is None:
        mime = "image/jpeg"
    return types.Part.from_bytes(data=path.read_bytes(), mime_type=mime)


def pick_random_stamp() -> Path:
    candidates = sorted(
        p for p in STAMPS_DIR.glob("*")
        if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
    )
    if not candidates:
        raise FileNotFoundError(f"スタンプ画像が見つかりません: {STAMPS_DIR}")
    return random.choice(candidates)


def build_prompt(chara: str) -> tuple[str, str]:
    """(プロンプト本文, 選択されたスタンプパターン) を返す。"""
    base_transform = (
        "【出力形式（厳守）】\n"
        "  - 出力は編集後の画像【1枚のみ】。\n"
        "  - 比較画像・before/after・左右分割・グリッド・コラージュ等は絶対に作らないこと。\n"
        "  - 出力画像のキャンバス・アスペクト比・構図・背景は【1枚目の人物画像と完全に同一】にすること。\n"
        "  - 1枚目の画像にない要素（白フチ・余白・枠・他の素材）を周囲に追加しないこと。\n"
        "\n"
        "【微細変形（必須）】\n"
        "  - 画像全体を ±0.5〜1度 のごく僅かな角度で回転（回転で出る隙間は元画像の内容を引き伸ばして埋め、白フチや枠を絶対に出さない）\n"
        "  - 明るさ・コントラスト・色調を ±1〜2% 程度ごく僅かに変化\n"
        "  - 変化はごく僅か（パッと見では気づかないレベル）に留めること\n"
        "  - 人物の表情・髪・服装・背景・構図・ポーズは一切変更しないこと\n"
    )

    if chara in NO_STAMP_CHARS:
        prompt = (
            "1枚目の人物画像に対し、以下を行ってください。\n\n"
            + base_transform
            + "\nスタンプ等の合成は行わないでください。"
        )
        return prompt, "no_stamp"

    if chara == "iori":
        prompt = (
            "1枚目: 人物の元画像（顔の上にピンクのハートが3つ配置されている）\n"
            "2枚目: 使用するスタンプ画像（このデザインのみ使用）\n\n"
            + base_transform
            + "\n【スタンプ合成】\n"
            "  - 元画像にある3つのピンクハートそれぞれを、2枚目のスタンプで完全に上書きする\n"
            "  - 元のピンクハートが一切見えなくなるよう、各スタンプはハートをやや大きめに覆うサイズにする\n"
            "  - 3箇所すべて同じスタンプを使うこと\n"
            "  - 出力画像には【1枚目の人物画像 + そのスタンプ3個】以外を一切描かない。\n"
        )
        return prompt, "iori_hearts"

    if chara == "reina":
        pattern = random.choice(["nose", "nose_mouth"])
        if pattern == "nose":
            target = "鼻のみ"
            detail = "鼻が完全に隠れる位置・サイズで配置。スタンプは1個。"
        else:
            target = "鼻と口の両方"
            detail = (
                "鼻と口の両方が確実に隠れるよう配置。"
                "1個のスタンプで両方を覆ってもよいし、必要なら2個使ってもよい。"
            )
        prompt = (
            "1枚目: 人物の元画像\n"
            "2枚目: 使用するスタンプ画像（このデザインのみ使用）\n\n"
            + base_transform
            + f"\n【スタンプ合成】\n"
            f"  - 2枚目のスタンプを使って人物の【{target}】を隠す\n"
            f"  - 配置: {detail}\n"
            f"  - スタンプのサイズ感: 該当パーツの1.2倍程度（パーツが確実に隠れる）\n"
            f"  - 元画像に既に口や鼻を覆う別のスタンプがある場合、それが完全に見えなくなるよう上書きすること\n"
            f"  - 出力画像には【1枚目の人物画像 + 2枚目のスタンプ】以外を一切描かない。\n"
        )
        return prompt, f"reina_{pattern}"

    # その他のキャラ
    pattern = random.choice(["nose", "mouth", "nose_mouth"])
    target_label = {
        "nose": "鼻のみ",
        "mouth": "口のみ",
        "nose_mouth": "鼻と口の両方",
    }[pattern]
    prompt = (
        "1枚目: 人物の元画像\n"
        "2枚目: 使用するスタンプ画像（このデザインのみ使用）\n\n"
        + base_transform
        + f"\n【スタンプ合成】\n"
        f"  - 2枚目のスタンプ1個を使って人物の【{target_label}】を隠す\n"
        f"  - スタンプは1個だけ使用すること\n"
        f"  - スタンプのサイズ感: 該当パーツの1.2倍程度（パーツが確実に隠れる）\n"
        f"  - 元画像に既に口や鼻を覆う別のスタンプがある場合、それが完全に見えなくなるよう上書きすること\n"
        f"  - 出力画像には【1枚目の人物画像 + 2枚目のスタンプ1個】以外を一切描かない。\n"
    )
    return prompt, pattern


def extract_image(response) -> tuple[bytes, str]:
    for part in response.candidates[0].content.parts:
        inline = getattr(part, "inline_data", None)
        if inline and inline.data:
            mime = inline.mime_type or "image/jpeg"
            return inline.data, mime
    raise RuntimeError("レスポンスに画像が含まれていません")


def mime_to_ext(mime: str) -> str:
    mapping = {
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }
    return mapping.get(mime, "jpg")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: make_chara_image.py <キャラ名> [プレフィックス]")
        return 1

    chara = sys.argv[1].strip().lower()
    prefix = sys.argv[2].strip() if len(sys.argv) >= 3 else ""

    folder_name = FOLDER_ALIAS.get(chara, chara)
    folder = CHARA_BASE / folder_name
    if not folder.is_dir():
        print(f"キャラフォルダが存在しません: {folder}")
        return 1

    original_path = find_original(folder)
    print(f"元画像: {original_path}")

    contents: list = []
    contents.append(load_image_part(original_path))

    stamp_path: Path | None = None
    if chara not in NO_STAMP_CHARS:
        try:
            stamp_path = pick_random_stamp()
        except FileNotFoundError as e:
            print(e)
            return 1
        contents.append(load_image_part(stamp_path))
        print(f"スタンプ: {stamp_path.name}")

    prompt, pattern = build_prompt(chara)
    contents.append(prompt)
    print(f"パターン: {pattern}")

    client = genai.Client(api_key=Gemini_API_KEY)
    print(f"Nano Banana Pro 呼び出し中... (model={MODEL})")
    response = client.models.generate_content(model=MODEL, contents=contents)

    img_bytes, mime = extract_image(response)
    ext = mime_to_ext(mime)

    base = reiwa_filename_base(date.today())
    fname = f"{prefix}{base}.{ext}" if prefix else f"{base}.{ext}"
    save_path = folder / fname

    if save_path.exists():
        i = 2
        while True:
            alt = folder / (
                f"{prefix}{base}-{i}.{ext}" if prefix else f"{base}-{i}.{ext}"
            )
            if not alt.exists():
                save_path = alt
                break
            i += 1

    save_path.write_bytes(img_bytes)
    print(f"保存しました: {save_path}")
    print(f"サイズ: {len(img_bytes)} bytes / pattern: {pattern}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

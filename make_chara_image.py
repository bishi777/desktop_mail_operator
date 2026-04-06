#!/usr/bin/env python3
"""
キャラ画像を微妙に変えてスタンプを貼った画像を生成する
usage: python make_chara_image.py <キャラ名>
"""

import sys
import os
import random
import math
from datetime import datetime
from PIL import Image, ImageEnhance
import cv2
import numpy as np

DRIVE_BASE = "/Users/yamamotokenta/Library/CloudStorage/GoogleDrive-kenta.bishi777@gmail.com/マイドライブ/キャラ画像"
STAMPS_PATH = os.path.join(DRIVE_BASE, "アクセサリ", "stamps.jpg")

# スタンプ不使用キャラ
NO_STAMP_CHARAS = ["yukko", "yuki", "yukko_yuki", "erika", "tumugi"]

# キャラ名 → フォルダ名マッピング（そのままの名前で見つからない場合）
CHARA_FOLDER_MAP = {
    "yukko": "yukko_yuki",
    "yuki":  "yukko_yuki",
}

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

FACE_MODEL_PATH = "/tmp/face_landmarker.task"


def find_chara_folder(chara_name):
    """キャラ名からフォルダパスを返す"""
    candidates = [
        CHARA_FOLDER_MAP.get(chara_name, chara_name),
        chara_name,
    ]
    for c in candidates:
        p = os.path.join(DRIVE_BASE, c)
        if os.path.isdir(p):
            return p
    # 部分一致
    for d in os.listdir(DRIVE_BASE):
        if chara_name.lower() in d.lower() and os.path.isdir(os.path.join(DRIVE_BASE, d)):
            return os.path.join(DRIVE_BASE, d)
    return None


def apply_subtle_changes(img):
    """目視でほぼ気づかない微妙な変化を加える"""
    # 色調: ±3%
    img = ImageEnhance.Color(img).enhance(random.uniform(0.97, 1.03))
    # 明るさ: ±3%
    img = ImageEnhance.Brightness(img).enhance(random.uniform(0.97, 1.03))
    # コントラスト: ±2%
    img = ImageEnhance.Contrast(img).enhance(random.uniform(0.98, 1.02))
    # 回転: ±1.5度（expand=Falseでサイズ維持）
    angle = random.uniform(-1.5, 1.5)
    img = img.rotate(angle, resample=Image.BICUBIC, expand=False)
    return img


def get_nose_mouth_regions(pil_img):
    """
    MediaPipeで顔ランドマークを検出し、鼻と口の領域を返す。
    返り値: (nose_box, mouth_box) それぞれ (x1, y1, x2, y2)、検出失敗時は (None, None)
    """
    if not os.path.exists(FACE_MODEL_PATH):
        print(f"  顔モデルが見つかりません: {FACE_MODEL_PATH}")
        return None, None
    arr = np.array(pil_img.convert("RGB"))
    w, h = pil_img.size
    base_opts = mp_python.BaseOptions(model_asset_path=FACE_MODEL_PATH)
    opts = mp_vision.FaceLandmarkerOptions(base_options=base_opts, num_faces=1)
    detector = mp_vision.FaceLandmarker.create_from_options(opts)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=arr)
    result = detector.detect(mp_img)
    if not result.face_landmarks:
        return None, None
    lm = result.face_landmarks[0]

    def px(idx):
        return int(lm[idx].x * w), int(lm[idx].y * h)

    # 鼻: 鼻先周辺ランドマーク（1=鼻先, 129=鼻左, 358=鼻右, 2=鼻下）
    nose_pts = [px(i) for i in [1, 2, 48, 129, 275, 358]]
    # 口: 口周辺ランドマーク（61=左端, 291=右端, 0=上唇上, 17=下唇下）
    mouth_pts = [px(i) for i in [61, 291, 0, 17, 40, 270, 91, 321]]

    def bbox(pts, pad=20):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)

    return bbox(nose_pts), bbox(mouth_pts)


def load_stamps(stamps_path):
    """
    白背景のスタンプ画像から個別スタンプを輪郭検出で切り出してリストで返す。
    """
    if not os.path.exists(stamps_path):
        print(f"  スタンプ画像が見つかりません: {stamps_path}")
        return []
    img = Image.open(stamps_path).convert("RGB")
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(cv_img, 240, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((20, 20), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 面積50000以上の輪郭のみ（ノイズ除外）
    boxes = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > 50000]
    boxes.sort(key=lambda b: (b[1] // 500, b[0]))
    if not boxes:
        print("  スタンプ検出なし")
        return []
    stamps = [img.crop((x, y, x + w, y + h)).convert("RGBA") for x, y, w, h in boxes]
    print(f"  スタンプ: {len(stamps)}個検出")
    return stamps


def make_transparent(stamp):
    """白背景を透過にする"""
    stamp = stamp.convert("RGBA")
    data = np.array(stamp)
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    # RGB全て230以上 = ほぼ白 → 透明にする
    white_mask = (r > 230) & (g > 230) & (b > 230)
    data[:,:,3] = np.where(white_mask, 0, a)
    return Image.fromarray(data, "RGBA")


def paste_stamp(base_img, stamp, region, fit_to_region=False):
    """
    regionの中心にstampを貼り付ける。
    fit_to_region=Trueのときは領域サイズに合わせてリサイズ（iori以外）。
    fit_to_region=Falseのときは短辺を領域の短辺に合わせる（iori）。
    """
    x1, y1, x2, y2 = region
    rw, rh = x2 - x1, y2 - y1
    if rw <= 0 or rh <= 0:
        return base_img
    stamp = make_transparent(stamp)
    sw_orig, sh_orig = stamp.size
    if fit_to_region:
        # 領域にぴったり合わせる
        sw, sh = int(rw * 1.1), int(rh * 1.1)
    else:
        # 短辺基準でアスペクト比維持リサイズ
        ratio = min(rw, rh) / max(sw_orig, sh_orig) * 1.1
        sw, sh = int(sw_orig * ratio), int(sh_orig * ratio)
    stamp_resized = stamp.resize((sw, sh), Image.LANCZOS)
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    px = cx - sw // 2
    py = cy - sh // 2
    result = base_img.copy().convert("RGBA")
    result.paste(stamp_resized, (px, py), stamp_resized)
    return result.convert("RGB")


def detect_pink_heart_regions(pil_img):
    """
    ピンクのハートスタンプの領域をHSV色検出で見つけて、個別のバウンディングボックスのリストを返す。
    """
    cv_img = cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2HSV)
    # ピンク〜マゼンタ系のHSV範囲
    lower1 = np.array([140, 50, 100])
    upper1 = np.array([180, 255, 255])
    lower2 = np.array([0, 50, 150])
    upper2 = np.array([10, 255, 255])
    mask = cv2.bitwise_or(
        cv2.inRange(cv_img, lower1, upper1),
        cv2.inRange(cv_img, lower2, upper2)
    )
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    regions = []
    for c in contours:
        if cv2.contourArea(c) < 1000:
            continue
        x, y, w, h = cv2.boundingRect(c)
        regions.append((x, y, x + w, y + h))
    return regions


def make_image(chara_name):
    chara_folder = find_chara_folder(chara_name)
    if not chara_folder:
        print(f"フォルダが見つかりません: {chara_name}")
        sys.exit(1)
    print(f"フォルダ: {chara_folder}")

    original_path = os.path.join(chara_folder, "original.jpg")
    if not os.path.exists(original_path):
        # .jpeg も試す
        original_path = os.path.join(chara_folder, "original.jpeg")
    if not os.path.exists(original_path):
        print(f"original画像が見つかりません: {chara_folder}")
        sys.exit(1)
    print(f"元画像: {original_path}")

    img = Image.open(original_path).convert("RGB")

    # 微妙な色調・傾き変化
    img = apply_subtle_changes(img)
    print("  色調・傾き調整完了")

    # iori: ピンクハートをstampsのランダムスタンプに置き換え
    if chara_name.lower() == "iori":
        stamps = load_stamps(STAMPS_PATH)
        if stamps:
            regions = detect_pink_heart_regions(img)
            if regions:
                print(f"  ピンクハート検出: {len(regions)}個")
                for region in regions:
                    img = paste_stamp(img, random.choice(stamps), region, fit_to_region=True)
                print("  ピンクハートをスタンプに置き換え完了")
            else:
                print("  ピンクハート未検出 → スキップ")
        else:
            print("  スタンプ画像なし → ピンクハート置き換えスキップ")

    # スタンプ処理（NO_STAMP_CHARASはスキップ）
    use_stamp = chara_name.lower() not in NO_STAMP_CHARAS and chara_name.lower() != "iori"
    if use_stamp:
        stamps = load_stamps(STAMPS_PATH)
        if not stamps:
            print("  スタンプなし → スキップ")
            use_stamp = False

    if use_stamp:
        nose_box, mouth_box = get_nose_mouth_regions(img)
        if nose_box is None:
            print("  顔検出失敗 → スタンプスキップ")
        else:
            print(f"  鼻領域: {nose_box}")
            print(f"  口領域: {mouth_box}")
            stamp = random.choice(stamps)

            # パターン: 0=口のみ 1=鼻のみ 2=両方
            pattern = random.randint(0, 2)
            pattern_name = ["口のみ", "鼻のみ", "口と鼻"][pattern]
            print(f"  スタンプパターン: {pattern_name}")

            if pattern == 0 and mouth_box:
                img = paste_stamp(img, stamp, mouth_box)
            elif pattern == 1 and nose_box:
                img = paste_stamp(img, stamp, nose_box)
            else:
                if nose_box:
                    img = paste_stamp(img, stamp, nose_box)
                if mouth_box:
                    img = paste_stamp(img, random.choice(stamps), mouth_box)
    elif chara_name.lower() == "iori":
        pass  # iori は上で処理済み
    else:
        print(f"  スタンプ: スキップ（{chara_name}）")

    # 保存（令和年号: 令和元年=2019）
    now = datetime.now()
    reiwa_year = now.year - 2018
    reiwa_date = f"{reiwa_year}{now.month:02d}{now.day:02d}"
    out_filename = f"{reiwa_date}.jpg"
    out_path = os.path.join(chara_folder, out_filename)
    img.save(out_path, "JPEG", quality=95)
    print(f"  保存完了: {out_path}")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python make_chara_image.py <キャラ名>")
        sys.exit(1)
    make_image(sys.argv[1])

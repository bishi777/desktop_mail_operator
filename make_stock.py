from PIL import Image, ImageEnhance

src = '/Users/yamamotokenta/Library/CloudStorage/GoogleDrive-kenta.bishi777@gmail.com/マイドライブ/キャラ画像/yukko_yuki/yukko/p80127.jpg'
dst = '/Users/yamamotokenta/Library/CloudStorage/GoogleDrive-kenta.bishi777@gmail.com/マイドライブ/キャラ画像/yukko_yuki/yukko/stock.jpeg'

img = Image.open(src).convert('RGB')

# 色調：わずかに暖色系（赤チャンネルを強め、青を少し下げる）
r, g, b = img.split()
r = ImageEnhance.Brightness(r).enhance(1.05)
g = ImageEnhance.Brightness(g).enhance(1.02)
b = ImageEnhance.Brightness(b).enhance(0.92)
img = Image.merge('RGB', (r, g, b))

# 彩度を少し上げる
img = ImageEnhance.Color(img).enhance(1.1)

# コントラストをわずかに調整
img = ImageEnhance.Contrast(img).enhance(1.05)

# 3度だけ傾ける（expand=Trueで余白付き）
img_rotated = img.rotate(-3, expand=True, fillcolor=(245, 245, 245))

# 元のサイズにクロップ（中心から）
orig_w, orig_h = img.size
new_w, new_h = img_rotated.size
left = (new_w - orig_w) // 2
top = (new_h - orig_h) // 2
img_cropped = img_rotated.crop((left, top, left + orig_w, top + orig_h))

img_cropped.save(dst, 'JPEG', quality=95)
print('保存完了:', dst)

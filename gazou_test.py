from deepface import DeepFace

# 画像パスを指定
img1_path = '/Users/yamamotokenta/Documents/書類 - MacBook Air/Pictures/キャラ画像/yukko/ yucco_p70422.jpeg'
img2_path = '/Users/yamamotokenta/Documents/書類 - MacBook Air/Pictures/キャラ画像/yukko/j61218_p70129.jpeg'

# 顔のembeddingを取得
embedding1 = DeepFace.represent(img1_path, model_name="Facenet")[0]["embedding"]
embedding2 = DeepFace.represent(img2_path, model_name="Facenet")[0]["embedding"]

# コサイン距離を計算
distance = DeepFace.dst.findCosineDistance(embedding1, embedding2)

print(f"コサイン距離: {distance:.4f}")
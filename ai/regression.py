import numpy as np
import json
import os
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from datetime import datetime

# ---------- 1️⃣ 사용자 지정 임베딩 파일 ----------
# ✅ 직접 임베딩 파일 경로 지정
EMBEDDING_PATH = "embeddings/embedding_20251024_162145.npy"
META_PATH = "embeddings/meta_20251025_162210.json"  # 선택사항 (있으면 읽기)

# 임베딩 로드
if not os.path.exists(EMBEDDING_PATH):
    raise FileNotFoundError(f"❌ 지정한 임베딩 파일을 찾을 수 없습니다: {EMBEDDING_PATH}")

embedding = np.load(EMBEDDING_PATH)
print(f"✅ 불러온 임베딩 벡터: {EMBEDDING_PATH} (shape={embedding.shape})")

# 메타파일 있으면 로드
meta_info = {}
if os.path.exists(META_PATH):
    with open(META_PATH, encoding="utf-8") as f:
        meta_info = json.load(f)
    print(f"📄 불러온 메타 파일: {META_PATH}")

# ---------- 2️⃣ Spotify 무드 피처 (17D) ----------
# 실제 Spotify의 오디오 피처 구조를 반영한 17차원 feature 벡터 예시
# 지금은 더미(임시) 값이지만, 나중에 실제 Spotify 곡 피처 DB랑 연결될 예정
spotify_features = {
    "acousticness": 0.62,
    "danceability": 0.74,
    "energy": 0.68,
    "instrumentalness": 0.05,
    "liveness": 0.11,
    "loudness": -5.3,
    "speechiness": 0.04,
    "valence": 0.72,
    "tempo": 118.4,
    "duration_ms": 210000,
    "mode": 1,
    "key": 5,
    "time_signature": 4,
    "id": "2takcwOaAZWiXQijPHIx7B",
    "uri": "spotify:track:2takcwOaAZWiXQijPHIx7B",
    "type": "audio_features",
    "track_href": "https://api.spotify.com/v1/tracks/2takcwOaAZWiXQijPHIx7B"
}

# 이 중에서 수치형 feature만 추출 (회귀 모델 target)
numeric_features = [
    "acousticness", "danceability", "energy", "instrumentalness",
    "liveness", "loudness", "speechiness", "valence", "tempo",
    "duration_ms", "mode", "key", "time_signature"
]
spotify_target = np.array([[spotify_features[k] for k in numeric_features]])

print(f"🎵 Spotify 무드 타깃 벡터 (shape={spotify_target.shape})")

# ---------- 3️⃣ Ridge 회귀 모델 ----------
model = Ridge(alpha=1.0)
model.fit(embedding, spotify_target)

# ---------- 4️⃣ 예측 ----------
pred = model.predict(embedding)
mse = mean_squared_error(spotify_target, pred)
print(f"\n🎯 Ridge 회귀 결과 — MSE: {mse:.6f}")

# ---------- 5️⃣ 결과 저장 ----------
os.makedirs("regression_results", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

result = {
    "timestamp": timestamp,
    "embedding_file": EMBEDDING_PATH,
    "meta_file": META_PATH if os.path.exists(META_PATH) else None,
    "spotify_target": spotify_target.tolist(),
    "predicted_vector": pred.tolist(),
    "feature_names": numeric_features,
    "mse": mse,
    "spotify_info": {k: v for k, v in spotify_features.items() if k not in numeric_features}
}

save_path = f"regression_results/result_{timestamp}.json"
with open(save_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n✅ 예측 결과 저장 완료 → {save_path}")
print(f"📈 예측된 Spotify 무드 피처 벡터 (13D):\n{pred}")

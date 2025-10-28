# 임베딩 생성 및 저장(일단 평균 앙상블)
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import os
from datetime import datetime

# ---------- 1. JSON 경로 직접 입력 ----------
json_path = "keyword/keywords_20251028_130303.json"

if not os.path.exists(json_path):
    raise FileNotFoundError(f"❌ 파일을 찾을 수 없습니다: {json_path}")

with open(json_path, encoding="utf-8") as f:
    data = json.load(f)

# ---------- 2. 키워드 읽기 ----------
korean_words = [kw["korean"] for kw in data.get("keywords", [])]
english_words = [kw["english"] for kw in data.get("keywords", [])]

if not korean_words or not english_words:
    raise ValueError("❌ JSON 파일에서 'keywords' 키를 찾을 수 없습니다.")

print(f"\n📝 불러온 키워드 파일: {json_path}")
print(f"한국어 키워드: {korean_words}")
print(f"영어 키워드: {english_words}")

# ---------- 3. 모델 로드 ----------
print("\n🚀 임베딩 모델 로드 중...")
model_en = SentenceTransformer("all-MiniLM-L6-v2")              # 영어용
model_ko = SentenceTransformer("jhgan/ko-sroberta-multitask")  # 한국어용

# ---------- 4. 임베딩 생성 ----------
# 한국어와 영어 키워드를 하나로 합칩니다.
all_keywords_text = " ".join(korean_words + english_words)
# 예: "행복한 신나는 happy exciting"

print(f"앙상블용 통합 텍스트: {all_keywords_text}")

# "하나의 텍스트"를 두 모델에 모두 입력합니다.
emb_en = model_en.encode([all_keywords_text]) # (1, 384)
emb_ko = model_ko.encode([all_keywords_text]) # (1, 768)

# 차원 맞추기 위해 zero padding (KoBERT:768 기준)
if emb_en.shape[1] != emb_ko.shape[1]:
    max_dim = max(emb_en.shape[1], emb_ko.shape[1]) # 768
    padded_en = np.pad(emb_en, ((0, 0), (0, max_dim - emb_en.shape[1])))
    padded_ko = np.pad(emb_ko, ((0, 0), (0, max_dim - emb_ko.shape[1])))
else:
    padded_en, padded_ko = emb_en, emb_ko

# 평균 앙상블
emb_concat = (padded_en + padded_ko) / 2

# ---------- 5. 저장 ----------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
os.makedirs("embeddings", exist_ok=True)
save_path = f"embeddings/embedding_{timestamp}.npy"
np.save(save_path, emb_concat)

# ---------- 6. 메타 정보 저장 ----------
meta = {
    "source_json": json_path,
    "timestamp": timestamp,
    "korean_keywords": korean_words,
    "english_keywords": english_words,
    "embedding_path": save_path
}

meta_path = f"embeddings/meta_{timestamp}.json"
with open(meta_path, "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

print(f"\n✅ 임베딩 저장 완료 → {save_path}")
print(f"🧾 메타 정보 저장 완료 → {meta_path}")


SAVE_DIR = "embeddings"
os.makedirs(SAVE_DIR, exist_ok=True)
# active_session.json 파일의 영어 키워드에 대한 임베딩 추가
# MiniLM-L6-v2 모델 사용 (영어 전용)

import json
from sentence_transformers import SentenceTransformer
import os
from datetime import datetime

# =========================================================
# 1. 설정
# =========================================================
SESSION_JSON_PATH = "agents/keywords/active_session.json"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" # 👈 영어 전용 모델만 사용

# =========================================================
# 2. 세션 파일 로드
# =========================================================
if not os.path.exists(SESSION_JSON_PATH):
    print(f"❌ 세션 파일({SESSION_JSON_PATH})이 없습니다. agent3_keywordExtractor.py 먼저 실행하세요.")
    exit()

print(f"🔄 Loading session file: {SESSION_JSON_PATH}")
with open(SESSION_JSON_PATH, "r", encoding="utf-8") as f:
    session_data = json.load(f)

# =========================================================
# 3. 임베딩 모델 로드
# =========================================================
print(f"🚀 Loading embedding model ({EMBEDDING_MODEL_NAME})...")
try:
    model_en = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("✅ Model loaded.")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    exit()

# =========================================================
# 4. 각 턴(Turn)별 키워드 임베딩 생성
# =========================================================
print("💬 Processing English keywords for embedding...")

# 기존 임베딩이 있으면 가져오고, 없으면 빈 리스트로 시작
all_embeddings = session_data.get("english_keyword_embeddings", [])
processed_count = 0

# english_keywords 리스트를 순회 (각 요소가 한 턴의 키워드 리스트)
for i, keywords_list in enumerate(session_data.get("english_keywords", [])):
    
    # [핵심] 👈 이미 해당 턴(i)의 임베딩이 존재하면 건너뛰기
    if i < len(all_embeddings) and all_embeddings[i]:
        continue 
        
    if not keywords_list: # 키워드가 없는 턴은 빈 리스트 추가
        if i >= len(all_embeddings):
             all_embeddings.append([])
        continue

    # 1. 키워드 리스트를 하나의 문자열로 합침 (예: "cozy winter peaceful")
    keywords_text = " ".join(keywords_list)
    print(f"   -> Turn {i+1}: Embedding '{keywords_text}'")
    
    # 2. 영어 모델로 임베딩 생성 (NumPy 배열)
    embedding_vector_np = model_en.encode([keywords_text])[0]
    
    # 3. JSON 저장을 위해 NumPy 배열을 Python 리스트로 변환
    embedding_vector_list = embedding_vector_np.tolist()
    
    # 4. 결과 리스트에 추가 (또는 기존 빈 리스트 업데이트)
    if i >= len(all_embeddings):
        all_embeddings.append(embedding_vector_list)
    else:
        all_embeddings[i] = embedding_vector_list # (이전 턴 처리 실패 시 덮어쓰기)
        
    processed_count += 1

# =========================================================
# 5. 세션 파일 업데이트 (임베딩 추가/덮어쓰기)
# =========================================================
if processed_count > 0:
    session_data["english_keyword_embeddings"] = all_embeddings
    
    print(f"\n💾 Updating session file with {processed_count} new embedding(s)...")
    with open(SESSION_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Session file updated: {SESSION_JSON_PATH}")
else:
    print("\n✅ No new keywords to embed. Session file is up-to-date.")
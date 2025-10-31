# 크로마 디비 로드 및 RAG 검색 기능
"""
rag_retriever.py
- build_chroma_db.py로 구축된 ChromaDB를 로드합니다.
- LangChain을 사용하여 RAG 검색(Similarity Search) 기능을 제공합니다.
"""

import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import json

# =========================================================
# 1. 설정 (DB 구축 스크립트와 동일해야 함)
# =========================================================
SCRIPT_DIR = os.path.dirname(__file__) # -> .../ai/rag
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # -> .../ai

# 👈 .../ai/rag/chroma_db
DB_PERSIST_DIR = os.path.join(PROJECT_ROOT, "rag/chroma_db") 

COLLECTION_NAME = "jamendo_songs"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

# =========================================================
# 2. 전역 변수 (DB 및 모델 캐시)
# =========================================================
_vector_db = None
_embedding_function = None

def _load_retriever_resources():
    """
    ChromaDB와 임베딩 모델을 로드하여 캐시합니다.
    (프로그램 실행 시 한 번만 호출되도록)
    """
    global _vector_db, _embedding_function
    
    if _vector_db is not None and _embedding_function is not None:
        return _vector_db, _embedding_function

    print(f"🚀 [RAG] Loading Embedding Model ({EMBED_MODEL_NAME})...")
    _embedding_function = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL_NAME,
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print(f"🚀 [RAG] Loading ChromaDB from: {DB_PERSIST_DIR}")
    if not os.path.exists(DB_PERSIST_DIR):
        print(f"❌ [RAG] DB directory not found: {DB_PERSIST_DIR}")
        print("   -> Please run 'build_chroma_db.py' first.")
        raise FileNotFoundError(DB_PERSIST_DIR)

    _vector_db = Chroma(
        persist_directory=DB_PERSIST_DIR,
        embedding_function=_embedding_function,
        collection_name=COLLECTION_NAME
    )
    
    print(f"✅ [RAG] Retriever ready. DB Collection '{COLLECTION_NAME}' loaded.")
    return _vector_db, _embedding_function

# =========================================================
# 3. RAG 검색 함수 (Agent 3에서 이 함수를 호출)
# =========================================================
def get_song_recommendations(english_keywords: list[str], top_k: int = 5) -> list[dict]:
    """
    영어 키워드 리스트를 기반으로 ChromaDB에서 유사한 노래를 검색합니다.
    
    Args:
        english_keywords (list[str]): Agent 3가 추출한 키워드 (예: ["angry", "rock"])
        top_k (int): 추천할 노래 개수

    Returns:
        list[dict]: 노래 메타데이터 딕셔너리의 리스트
    """
    try:
        # 1. DB 및 모델 로드 (캐시 활용)
        vector_db, _ = _load_retriever_resources()
        
        if not english_keywords:
            print("⚠️ [RAG] No keywords provided, skipping recommendation.")
            return []
            
        # 2. 쿼리 생성 (키워드를 하나의 텍스트로 합침)
        query_text = " ".join(english_keywords)
        print(f"🔍 [RAG] Searching for: '{query_text}' (Top {top_k})")
        
        # 3. LangChain RAG 검색 (유사도 검색)
        #    (LangChain이 내부적으로 query_text를 임베딩하여 DB와 비교)
        results = vector_db.similarity_search(query_text, k=top_k)
        
        # 4. 결과에서 메타데이터만 추출
        recommendations = [doc.metadata for doc in results]
        
        print(f"   -> Found {len(recommendations)} recommendations.")
        return recommendations

    except Exception as e:
        print(f"🔥 [RAG] Error during similarity search: {e}")
        return []

# =========================================================
# 4. 테스트 실행
# =========================================================
if __name__ == "__main__":
    """이 파일을 직접 실행하면 검색 테스트를 수행합니다."""
    
    print("--- RAG Retriever (Module) Test ---")
    
    # 테스트 키워드 1
    test_keywords_1 = ["angry", "rock", "metal"]
    recs = get_song_recommendations(test_keywords_1, top_k=3)
    print("\n--- [Test 1 Results] ---")
    print(json.dumps(recs, indent=2, ensure_ascii=False))
    
    # 테스트 키워드 2
    test_keywords_2 = ["gentle", "soft", "melodic"]
    recs = get_song_recommendations(test_keywords_2, top_k=3)
    print("\n--- [Test 2 Results] ---")
    print(json.dumps(recs, indent=2, ensure_ascii=False))
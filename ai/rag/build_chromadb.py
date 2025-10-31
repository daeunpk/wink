# -*- coding: utf-8 -*-
"""
build_chroma_db.py
- cleaned_merged_tags.csv 파일을 로드합니다.
- 'genre_tags'와 'mood_tags'를 결합하여 임베딩할 텍스트(page_content)를 만듭니다.
- 'TRACK_ID', 'PATH' 등은 메타데이터(metadata)로 저장합니다.
- LangChain과 ChromaDB를 사용하여 벡터 DB를 구축하고 디스크에 저장합니다.
"""

import os
import pandas as pd
from tqdm import tqdm
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

# =========================================================
# 1. 설정
# =========================================================
# 입력 클린 데이터
INPUT_CSV = "jamendo/data/cleaned_merged_tags.csv"
# ChromaDB를 저장할 폴더
DB_PERSIST_DIR = "rag/chroma_db"
# ChromaDB 컬렉션 이름 (테이블 이름과 유사)
COLLECTION_NAME = "jamendo_songs"
# Agent 3의 키워드와 동일한 임베딩 모델 사용 (매우 중요)
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

# =========================================================
# 2. 데이터 로드 및 LangChain Document로 변환
# =========================================================
def load_and_prepare_documents(csv_path: str) -> list[Document]:
    """CSV를 로드하여 LangChain Document 리스트로 변환합니다."""
    
    print(f"🔄 Loading cleaned data from: {csv_path}")
    if not os.path.exists(csv_path):
        print(f"❌ Input file not found: {csv_path}")
        return []
        
    df = pd.read_csv(csv_path)
    # 결측값(NaN)이 있을 경우를 대비해 빈 문자열로 대체
    df = df.fillna('')
    print(f"   -> Loaded {len(df)} songs.")

    documents = []
    print("📄 Converting DataFrame rows to LangChain Documents...")
    
    for _, row in tqdm(df.iterrows(), total=df.shape[0]):
        # 1. 임베딩될 텍스트 (page_content)
        #    RAG가 검색할 대상이 되는 텍스트 (장르 + 무드)
        content_text = f"Genre: {row['genre_tags']}. Mood: {row['mood_tags']}".strip()
        
        # 2. 검색 후 반환될 정보 (metadata)
        #    RAG가 검색한 후, 우리가 실제로 사용할 노래 정보
        metadata = {
            "track_id": row['TRACK_ID'],
            "path": row['PATH'],
            "genre_tags": row['genre_tags'],
            "mood_tags": row['mood_tags']
        }
        
        # LangChain Document 객체 생성
        doc = Document(page_content=content_text, metadata=metadata)
        documents.append(doc)
        
    print(f"   -> Created {len(documents)} documents.")
    return documents

# =========================================================
# 3. 임베딩 모델 로드
# =========================================================
from langchain_huggingface import HuggingFaceEmbeddings

def load_embedding_model(model_name: str):
    """HuggingFace 임베딩 모델을 LangChain 형식으로 로드합니다."""
    print(f"🚀 Loading embedding model ({model_name})...")
    # device='auto'로 설정하여 GPU가 있으면 자동으로 사용
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        encode_kwargs={'normalize_embeddings': True} # 코사인 유사도를 위해 정규화
    )
    print("   -> Model loaded.")
    return embeddings

# =========================================================
# 4. ChromaDB 생성 및 저장
# =========================================================
def build_and_persist_db(documents: list[Document], embeddings, db_path: str, collection_name: str):
    """
    LangChain Document 리스트를 ChromaDB에 임베딩하고 저장합니다.
    """
    if not documents:
        print("❌ No documents to process. Exiting.")
        return

    print(f"🛠️  Building ChromaDB (this may take a while)...")
    print(f"   -> DB will be saved to: {db_path}")

    # Chroma.from_documents:
    # 1. documents 리스트의 'page_content'를 'embeddings' 모델로 벡터 변환
    # 2. 벡터와 'metadata'를 'collection_name'에 저장
    # 3. 'persist_directory' 경로에 DB 파일 저장
    vector_db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=db_path
    )
    
    # (이미 from_documents에서 persist가 호출되지만, 명시적으로 한 번 더 호출)
    vector_db.persist()
    print(f"\n✅ ChromaDB built and saved successfully!")
    print(f"   -> Total vectors in collection '{collection_name}': {vector_db._collection.count()}")

# =========================================================
# 5. 메인 실행
# =========================================================
if __name__ == "__main__":
    # 1. 데이터 준비
    docs = load_and_prepare_documents(INPUT_CSV)
    
    if docs:
        # 2. 임베딩 모델 로드
        embedding_function = load_embedding_model(EMBED_MODEL_NAME)
        
        # 3. DB 구축 및 저장
        build_and_persist_db(
            documents=docs,
            embeddings=embedding_function,
            db_path=DB_PERSIST_DIR,
            collection_name=COLLECTION_NAME
        )
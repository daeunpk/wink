# spotify/build_chroma_db_spotify.py

import os
import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from tqdm import tqdm

INPUT_CSV = "spotify/data/spotify_tracks.csv"
DB_PERSIST_DIR = "spotify/chroma_db"
COLLECTION_NAME = "spotify_songs"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

def load_documents(csv_path):
    if not os.path.exists(csv_path):
        print(f"❌ CSV not found: {csv_path}")
        return []
    
    df = pd.read_csv(csv_path).fillna('')
    documents = []

    for _, row in tqdm(df.iterrows(), total=df.shape[0]):
        # 임베딩할 텍스트: 곡 이름 + 장르 + 분위기
        content = f"{row['track_name']} by {row['artist']}. Genre: {row['genre']}. Mood: {row['mood_tags']}"
        metadata = {
            "track_id": row["track_id"],
            "track_name": row["track_name"],
            "artist": row["artist"],
            "genre": row["genre"],
            "mood_tags": row["mood_tags"]
        }
        documents.append(Document(page_content=content, metadata=metadata))
    
    return documents

def build_chroma_db():
    docs = load_documents(INPUT_CSV)
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
    db = Chroma.from_documents(docs, embeddings, collection_name=COLLECTION_NAME, persist_directory=DB_PERSIST_DIR)
    db.persist()
    print(f"✅ Spotify ChromaDB built and saved to {DB_PERSIST_DIR}")

if __name__ == "__main__":
    build_chroma_db()

# -*- coding: utf-8 -*-
"""
build_spotify_db.py (v2 - Audio Features)
- Spotify API를 크롤링하여 '노래-태그' DB를 구축합니다.
1. 시드 키워드로 플레이리스트를 검색합니다.
2. 각 플레이리스트의 트랙을 수집합니다.
3. [신규] 수집된 트랙의 '오디오 피처'를 일괄 조회합니다.
4. (트랙 ID, 이름, URL 등)은 메타데이터로,
   (키워드 태그 + 오디오 피처 태그)는 page_content로 하여 ChromaDB에 저장합니다.
"""

import os
import re
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import time # (API 속도 제한을 위해 추가)

# =========================================================
# 1. 설정 (이전과 동일)
# =========================================================
CLIENT_ID = "9f601ae991474c5f9acbbca99f0d9c7c"
CLIENT_SECRET = "302529b448714aaabc311bdb65772a96"
DB_PERSIST_DIR = "spotify/spotify_chroma_db"
COLLECTION_NAME = "spotify_songs"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

SEED_KEYWORDS = [
    "happy", "sad", "chill", "relaxing", "energetic", "workout",
    "focus", "study", "sleep", "calm", "peaceful", "romantic", "love", 
    "breakup", "party", "driving", "morning", "rainy day", 
    "summer", "winter", "cozy", "pop", "rock", "metal", "hip hop", 
    "r&b", "jazz", "classical", "electronic", "dance", "folk", 
    "acoustic", "indie", "ambient", "soul", "funk", "reggae"
]
PLAYLISTS_PER_KEYWORD = 10

# =========================================================
# 2. Spotify API 인증 (이전과 동일)
# =========================================================
def get_spotify_client():
    """Spotify API 클라이언트를 인증하고 반환합니다."""
    print("🚀 [Spotify] Authenticating...")
    try:
        auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        sp.search(q='test', limit=1) # 인증 테스트
        print("✅ [Spotify] Authentication successful!")
        return sp
    except Exception as e:
        print(f"❌ [Spotify] Authentication failed: {e}")
        return None

# =========================================================
# 3. 플레이리스트 크롤링 (트랙 ID 수집)
# =========================================================
def crawl_track_data(sp: spotipy.Spotify):
    """Spotify API를 크롤링하여 트랙별 '태그'와 '메타데이터'를 수집합니다."""
    print(f"🔄 [Crawl] Starting crawl for {len(SEED_KEYWORDS)} keywords...")
    track_database = {}
    
    for keyword in tqdm(SEED_KEYWORDS, desc="Crawling Keywords"):
        try:
            results = sp.search(q=keyword, type='playlist', limit=PLAYLISTS_PER_KEYWORD)
            playlists = results['playlists']['items']
            
            for pl in playlists:
                if not pl or not pl['id']: continue
                
                pl_name = re.sub(r'[^a-z0-9\s]', '', pl['name'].lower())
                associated_tags = set(pl_name.split() + [keyword])

                try:
                    tracks = sp.playlist_tracks(pl['id'])
                except Exception:
                    continue 

                for item in tracks['items']:
                    track = item.get('track')
                    if not track or not track['id']: continue
                    track_id = track['id']
                    
                    if track_id not in track_database:
                        track_database[track_id] = {
                            "metadata": {
                                "track_id": track_id,
                                "track_name": track['name'],
                                "artist_name": ", ".join([a['name'] for a in track['artists']]),
                                "spotify_url": track['external_urls'].get('spotify', ''),
                                "preview_url": track.get('preview_url', ''),
                                "album_cover": track['album']['images'][0]['url'] if track['album']['images'] else ''
                            },
                            "tags": set()
                        }
                    track_database[track_id]["tags"].update(associated_tags)
        except Exception as e:
            print(f"⚠️ Error crawling keyword '{keyword}': {e}")
            time.sleep(5) # API 오류 시 잠시 대기
            
    print(f"✅ [Crawl] Crawl complete. Found {len(track_database)} unique tracks.")
    return track_database

# =========================================================
# 4. [신규] 오디오 피처를 태그로 변환하는 헬퍼 함수
# =========================================================
def get_feature_tags(features: dict) -> list[str]:
    """오디오 피처(숫자)를 'energy_high', 'valence_low' 같은 태그(문자)로 변환"""
    tags = []
    if not features:
        return tags

    # 긍정/부정 (Valence)
    valence = features.get('valence', 0.5)
    if valence < 0.3: tags.append("valence_low") # (우울, 분노, 슬픔)
    elif valence > 0.7: tags.append("valence_high") # (행복, 기쁨, 환희)

    # 에너지 (Energy)
    energy = features.get('energy', 0.5)
    if energy < 0.3: tags.append("energy_low") # (차분, 어쿠스틱, 수면)
    elif energy > 0.7: tags.append("energy_high") # (활기, 파티, 운동)

    # 템포 (Tempo)
    tempo = features.get('tempo', 110)
    if tempo < 80: tags.append("tempo_slow")
    elif tempo > 140: tags.append("tempo_fast")

    # 춤추기 좋은 (Danceability)
    if features.get('danceability', 0.5) > 0.7: 
        tags.append("danceable")
        
    # 연주곡 (Instrumentalness)
    if features.get('instrumentalness', 0) > 0.6:
        tags.append("instrumental")
        
    return tags

# =========================================================
# 5. [수정] LangChain Document로 변환 (오디오 피처 포함)
# =========================================================
def convert_to_documents(sp: spotipy.Spotify, track_database: dict) -> list[Document]:
    """
    크롤링한 데이터에 '오디오 피처'를 추가하고 LangChain Document로 변환합니다.
    (API 오류 처리 로직 강화)
    """
    print("🔄 [Features] Fetching audio features for all tracks...")
    
    all_track_ids = list(track_database.keys())
    audio_features_map = {}
    
    # --- 2. 오디오 피처 일괄 조회 (100개씩) ---
    for i in tqdm(range(0, len(all_track_ids), 100), desc="Fetching Audio Features"):
        batch_ids = all_track_ids[i:i+100]
        
        try:
            features_list = sp.audio_features(batch_ids)
            
            if features_list: # API가 None을 반환하지 않았는지 확인
                for features in features_list:
                    if features: # 개별 트랙 피처가 None이 아닌지 확인
                        audio_features_map[features['id']] = features
            
            # [수정] 👈 성공적인 API 호출 후에도, 0.5초간 휴식
            time.sleep(0.5) 

        except spotipy.exceptions.SpotifyException as e: # [수정] 👈 Spotify 전용 오류 잡기
            print(f"\n⚠️ Spotify API error fetching features batch {i}: {e.msg}")
            
            if e.http_status == 429: # Too Many Requests (속도 제한)
                print("   -> Rate limit (429) hit. Sleeping for 30 seconds...")
                time.sleep(30)
            elif e.http_status == 403: # Forbidden (금지됨)
                print("   -> Forbidden (403). Possible token/block. Sleeping for 60s...")
                time.sleep(60)
            else:
                print(f"   -> Other Spotify error ({e.http_status}). Sleeping for 5s.")
                time.sleep(5)
        
        except Exception as e:
            # [수정] 👈 기타 네트워크 오류 등
            print(f"\n⚠️ General error fetching features batch {i}: {e}")
            print("   -> Sleeping for 10s.")
            time.sleep(10)

    print(f"✅ [Features] Fetched features for {len(audio_features_map)} tracks.")
    
    # --- 3. Document 생성 (이하 동일) ---
    documents = []
    print("📄 [Convert] Converting tracks to LangChain Documents...")
    for track_id, data in tqdm(track_database.items(), desc="Creating Documents"):
        
        keyword_tags = list(data["tags"])
        features = audio_features_map.get(track_id)
        feature_tags = get_feature_tags(features)
        
        page_content = " ".join(keyword_tags + feature_tags)
        metadata = data["metadata"]
        
        if features:
            metadata['valence'] = features.get('valence', 0)
            metadata['energy'] = features.get('energy', 0)
            metadata['tempo'] = features.get('tempo', 0)
            metadata['danceability'] = features.get('danceability', 0)
        
        doc = Document(page_content=page_content, metadata=metadata)
        documents.append(doc)
        
    print(f"   -> Created {len(documents)} documents with combined tags.")
    return documents

# =========================================================
# 6. ChromaDB 생성 (이전과 동일)
# =========================================================
def build_spotify_chromadb(documents):
    if not documents:
        print("❌ No documents to build DB. Exiting.")
        return

    print(f"🚀 [Chroma] Loading embedding model ({EMBED_MODEL_NAME})...")
    embedding_function = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL_NAME,
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print(f"🛠️  [Chroma] Building ChromaDB...")
    if os.path.exists(DB_PERSIST_DIR):
        print(f"   -> Found old DB, removing: {DB_PERSIST_DIR}")
        import shutil
        shutil.rmtree(DB_PERSIST_DIR)

    vector_db = Chroma.from_documents(
        documents=documents,
        embedding=embedding_function,
        collection_name=COLLECTION_NAME,
        persist_directory=DB_PERSIST_DIR
    )
    
    vector_db.persist()
    print(f"\n✅ [Chroma] Spotify DB built and saved successfully!")
    print(f"   -> Total vectors in collection '{COLLECTION_NAME}': {vector_db._collection.count()}")

# =========================================================
# 7. 메인 실행 (수정)
# =========================================================
if __name__ == "__main__":
    # 1. Spotify 인증
    sp_client = get_spotify_client()
    if not sp_client:
        exit()
        
    # 2. Spotify 크롤링 (sp 클라이언트 전달)
    crawled_data = crawl_track_data(sp_client)
    
    # 3. Document 변환 (sp 클라이언트 전달)
    docs = convert_to_documents(sp_client, crawled_data)
    
    # 4. ChromaDB 구축
    if docs:
        build_spotify_chromadb(docs)
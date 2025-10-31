# 장르까지 저장
"""
spotify/collect_tracks.py
- Spotify Web API를 이용해 장르 기반으로 음악 데이터를 수집하고 CSV로 저장
- 장르 목록은 spotify/data/available_genres.csv에서 불러옴
- Access Token은 spotify_token.json에서 불러옴
"""

import os
import json
import time
import pandas as pd
import requests
from tqdm import tqdm

# --------------------------------------------------------
# 1️⃣ 설정
# --------------------------------------------------------
DATA_DIR = "spotify/data"
os.makedirs(DATA_DIR, exist_ok=True)
GENRE_FILE = os.path.join(DATA_DIR, "available_genres.csv")
OUTPUT_CSV = os.path.join(DATA_DIR, "spotify_tracks.csv")

TOKEN_FILE = "spotify/spotify_token.json"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

# --------------------------------------------------------
# 2️⃣ 토큰 불러오기
# --------------------------------------------------------
def get_access_token():
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(f"❌ {TOKEN_FILE}이 없습니다. auth_server.py 실행 후 재시도하세요.")
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["access_token"]

# --------------------------------------------------------
# 3️⃣ Spotify 검색 API
# --------------------------------------------------------
def search_tracks(query, limit=10):
    """특정 키워드(장르)로 Spotify 트랙 검색"""
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": limit, "market": "US"}
    res = requests.get(f"{SPOTIFY_API_BASE}/search", headers=headers, params=params)
    if res.status_code != 200:
        print(f"⚠️ Search failed ({res.status_code}): {res.text}")
        return []
    items = res.json().get("tracks", {}).get("items", [])
    return items

# --------------------------------------------------------
# 4️⃣ 오디오 피처 API
# --------------------------------------------------------
def get_audio_features(track_ids):
    """Spotify 트랙 ID 목록에 대한 오디오 피처 조회"""
    if not track_ids:
        return []
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"ids": ",".join(track_ids)}
    res = requests.get(f"{SPOTIFY_API_BASE}/audio-features", headers=headers, params=params)
    if res.status_code != 200:
        print(f"⚠️ Audio features fetch failed: {res.text}")
        return []
    return res.json().get("audio_features", [])

# --------------------------------------------------------
# 5️⃣ 데이터 수집 파이프라인
# --------------------------------------------------------
def collect_spotify_data(genres, tracks_per_genre=20):
    """장르 목록을 기반으로 Spotify 트랙 데이터를 수집"""
    all_data = []

    for genre in tqdm(genres, desc="🎧 Collecting Spotify Tracks"):
        results = search_tracks(genre, limit=tracks_per_genre)
        if not results:
            continue

        track_ids = [r["id"] for r in results]
        audio_features = get_audio_features(track_ids)
        feature_map = {f["id"]: f for f in audio_features if f}

        for r in results:
            t_id = r["id"]
            t_name = r["name"]
            artist = r["artists"][0]["name"] if r["artists"] else ""
            artist_id = r["artists"][0]["id"] if r["artists"] else ""
            album = r["album"]["name"] if r.get("album") else ""

            all_data.append({
                "track_id": t_id,
                "track_name": t_name,
                "artist": artist,
                "artist_id": artist_id,
                "album": album,
                "genre": genre,
            })

        time.sleep(0.3)  # API rate limit 방지

    # DataFrame 생성 및 저장
    df = pd.DataFrame(all_data)
    df.drop_duplicates(subset=["track_id"], inplace=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"\n✅ Saved {len(df)} tracks to {OUTPUT_CSV}")
    print(f"🎵 Unique genres collected: {df['genre'].nunique()}")

# --------------------------------------------------------
# 6️⃣ 실행
# --------------------------------------------------------
if __name__ == "__main__":
    if not os.path.exists(GENRE_FILE):
        raise FileNotFoundError(f"❌ 장르 파일이 없습니다. 먼저 extract_genres.py를 실행하세요.\n({GENRE_FILE})")

    genres_df = pd.read_csv(GENRE_FILE)
    genres = list(genres_df["genre"].dropna().unique())

    # 너무 많은 장르를 한 번에 수집하지 않도록 상한 제한
    genres = genres[:20]  # 예: 상위 20개 장르만 수집

    print(f"🎨 Total genres to collect: {len(genres)}")
    collect_spotify_data(genres, tracks_per_genre=25)

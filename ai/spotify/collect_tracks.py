# -*- coding: utf-8 -*-
"""
spotify/collect_tracks.py
- Spotify Web API를 이용해 음악 데이터를 수집하고 CSV로 저장
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
OUTPUT_CSV = os.path.join(DATA_DIR, "spotify_tracks.csv")

TOKEN_FILE = "spotify/spotify_token.json"  # auth_server.py로 발급된 토큰
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
    """특정 키워드로 Spotify 트랙을 검색"""
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
# 4️⃣ 오디오 피처 API (mood feature)
# --------------------------------------------------------
def get_audio_features(track_ids):
    """Spotify 트랙 ID 목록에 대한 오디오 피처 (valence, energy 등) 조회"""
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
def collect_spotify_data(keywords, tracks_per_keyword=10):
    """여러 키워드로 검색하여 Spotify 트랙 데이터 수집"""
    all_data = []

    for kw in tqdm(keywords, desc="🎧 Collecting Spotify Tracks"):
        results = search_tracks(kw, limit=tracks_per_keyword)
        if not results:
            continue

        track_ids = [r["id"] for r in results]
        audio_features = get_audio_features(track_ids)

        # audio_features 리스트를 dict로 변환 (track_id → feature)
        feature_map = {f["id"]: f for f in audio_features if f}

        for r in results:
            t_id = r["id"]
            t_name = r["name"]
            artist = r["artists"][0]["name"]
            album = r["album"]["name"]

            # 오디오 피처
            feature = feature_map.get(t_id, {})
            energy = feature.get("energy")
            valence = feature.get("valence")
            danceability = feature.get("danceability")

            # 분위기 태그 자동 생성
            mood_tags = []
            if energy is not None and valence is not None:
                if energy > 0.7 and valence > 0.6:
                    mood_tags.append("happy energetic")
                elif valence < 0.4:
                    mood_tags.append("sad calm")
                elif energy < 0.4:
                    mood_tags.append("soft gentle")
                else:
                    mood_tags.append("neutral")

            all_data.append({
                "track_id": t_id,
                "track_name": t_name,
                "artist": artist,
                "album": album,
                "genre": kw,  # 검색 키워드로 대체
            })

        time.sleep(0.5)  # API rate limit 방지

    # pandas DataFrame으로 저장
    df = pd.DataFrame(all_data)
    df.drop_duplicates(subset=["track_id"], inplace=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n✅ Saved {len(df)} tracks to {OUTPUT_CSV}")

# --------------------------------------------------------
# 6️⃣ 실행
# --------------------------------------------------------
if __name__ == "__main__":
    # 수집할 음악 장르/키워드 목록
    keywords = [
        "pop", "rock", "jazz", "piano", "acoustic",
        "chill", "rainy day", "study", "sleep", "dance"
    ]
    collect_spotify_data(keywords, tracks_per_keyword=30)
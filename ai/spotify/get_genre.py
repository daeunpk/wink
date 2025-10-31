# -*- coding: utf-8 -*-
"""
extract_genres.py
- Spotify Search API를 사용해 장르 기반으로 트랙을 검색하고
  그 결과에서 genre 관련 메타데이터를 추출합니다.
- API가 명시적으로 제공하지 않기 때문에, 실제 트랙/아티스트 데이터를 탐색하며
  현재 Spotify에서 사용 중인 장르명을 수집합니다.
"""

import os
import json
import time
import requests
import pandas as pd
from tqdm import tqdm

# =========================================================
# 1. 경로 설정
# =========================================================
BASE_DIR = os.path.dirname(__file__)  # /spotify
DATA_DIR = os.path.join(BASE_DIR, "data")
TOKEN_FILE = os.path.join(BASE_DIR, "spotify_token.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "available_genres.csv")

# =========================================================
# 2. 토큰 불러오기
# =========================================================
def get_access_token():
    """spotify_token.json에서 access_token 읽기"""
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError("❌ spotify_token.json이 없습니다. auth_server.py 실행 후 재시도하세요.")
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("access_token")

# =========================================================
# 3. Spotify Search API를 사용한 장르 추출
# =========================================================
def search_genres(token, seeds=None, max_pages=3):
    """
    Spotify Search API를 사용하여 genre를 기반으로 트랙을 검색하고,
    각 트랙의 아티스트 정보를 통해 장르 필드를 추출합니다.
    """
    headers = {"Authorization": f"Bearer {token}"}

    # 기본적으로 시도할 seed 단어 (검색 기반 장르 후보)
    if seeds is None:
        seeds = [
            "pop", "rock", "jazz", "hip hop", "lofi", "indie",
            "r&b", "acoustic", "electronic", "k-pop", "dance", "classical",
            "soul", "chill", "metal", "country", "funk", "house"
        ]

    all_genres = set()

    for seed in tqdm(seeds, desc="🎧 Searching genres"):
        for page in range(max_pages):
            url = f"https://api.spotify.com/v1/search?q=genre:{seed}&type=track&limit=20&offset={page*20}"
            res = requests.get(url, headers=headers)
            if res.status_code == 401:
                raise RuntimeError("⚠️ Access Token이 만료되었습니다. auth_server.py를 다시 실행하세요.")
            if res.status_code != 200:
                print(f"⚠️ 검색 실패 ({res.status_code}) for seed='{seed}'")
                break

            data = res.json()
            tracks = data.get("tracks", {}).get("items", [])
            artist_ids = [artist["id"] for track in tracks for artist in track["artists"] if artist.get("id")]

            if not artist_ids:
                break

            # 아티스트 정보에서 실제 장르 추출
            for i in range(0, len(artist_ids), 50):
                batch = artist_ids[i:i+50]
                artist_url = f"https://api.spotify.com/v1/artists?ids={','.join(batch)}"
                a_res = requests.get(artist_url, headers=headers)
                if a_res.status_code != 200:
                    continue
                a_data = a_res.json()
                for artist in a_data.get("artists", []):
                    all_genres.update(artist.get("genres", []))

            time.sleep(0.3)  # API rate limit 완화

    return sorted(list(all_genres))

# =========================================================
# 4. 메인 실행 로직
# =========================================================
def extract_genres():
    """Spotify에서 장르를 자동 수집하여 CSV로 저장"""
    print("🎧 Fetching Spotify Genre Seeds via Search API...")
    token = get_access_token()

    genres = search_genres(token)
    print(f"\n✅ 총 {len(genres)}개의 장르를 수집했습니다.")

    os.makedirs(DATA_DIR, exist_ok=True)
    pd.DataFrame({"genre": genres}).to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"💾 Saved available genres to: {OUTPUT_FILE}")

# =========================================================
# 5. 실행
# =========================================================
if __name__ == "__main__":
    try:
        extract_genres()
    except Exception as e:
        print(f"🔥 Error: {e}")

# -*- coding: utf-8 -*-
"""
spotify/fetch_audio_features.py
- 이미 수집된 spotify_tracks.csv를 불러와
  Spotify Audio Features를 별도 CSV로 저장합니다.
"""

import os
import json
import time
import pandas as pd
import requests
from tqdm import tqdm

# --------------------------------------------------------
# 설정
# --------------------------------------------------------
DATA_DIR = "spotify/data"
TRACKS_CSV = os.path.join(DATA_DIR, "spotify_tracks.csv")
OUTPUT_CSV = os.path.join(DATA_DIR, "spotify_audio_features.csv")
TOKEN_FILE = "spotify/spotify_token.json"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

# --------------------------------------------------------
# 토큰 불러오기
# --------------------------------------------------------
def get_access_token():
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError("❌ spotify_token.json이 없습니다. auth_server.py 실행 후 재시도하세요.")
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["access_token"]

# --------------------------------------------------------
# 오디오 피처 조회
# --------------------------------------------------------
def get_audio_features(track_ids):
    """Spotify 트랙 ID 리스트에 대한 오디오 피처 조회 (수정 버전)"""
    if not track_ids:
        return []
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    # ⚠️ URL 직접 구성 (requests의 자동 인코딩 방지)
    ids_str = ",".join(track_ids)
    url = f"{SPOTIFY_API_BASE}/audio-features?ids={ids_str}"
    
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"⚠️ Audio features fetch failed: {res.status_code} {res.text}")
        return []
    return res.json().get("audio_features", [])

# --------------------------------------------------------
# 메인 수집 함수
# --------------------------------------------------------
def fetch_all_audio_features():
    if not os.path.exists(TRACKS_CSV):
        raise FileNotFoundError(f"❌ {TRACKS_CSV} 파일이 없습니다. collect_tracks.py 실행 후 재시도하세요.")

    df = pd.read_csv(TRACKS_CSV)
    track_ids = list(df["track_id"].dropna().unique())

    all_features = []
    for i in tqdm(range(0, len(track_ids), 100), desc="🎧 Fetching Audio Features"):
        batch_ids = track_ids[i:i+100]
        features = get_audio_features(batch_ids)
        all_features.extend([f for f in features if f])
        time.sleep(0.3)

    features_df = pd.DataFrame(all_features)
    features_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n✅ Saved {len(features_df)} audio features to {OUTPUT_CSV}")

# --------------------------------------------------------
# 실행
# --------------------------------------------------------
if __name__ == "__main__":
    fetch_all_audio_features()

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
import time
import os
import json
from datetime import datetime
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import MinMaxScaler
from spotipy.oauth2 import SpotifyOAuth

# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
# 1. 모델 로드
# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
print("🚀 학습 데이터 생성을 위한 임베딩 모델 로드 중...")
try:
    model_ko = SentenceTransformer("jhgan/ko-sroberta-multitask") 
    model_en = SentenceTransformer("all-MiniLM-L6-v2")
    
    ko_dim = model_ko.get_sentence_embedding_dimension()
    en_dim = model_en.get_sentence_embedding_dimension()
    MAX_DIM = max(ko_dim, en_dim)
    
    print(f"✅ 모델 로드 완료 (Ko: {ko_dim}D, En: {en_dim}D) -> 최종 {MAX_DIM}D")
except Exception as e:
    print(f"❌ 모델 로드 실패: {e}")
    exit()

# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
# 2. Spotify API 인증
# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=

CLIENT_ID = "9f601ae991474c5f9acbbca99f0d9c7c"
CLIENT_SECRET = "302529b448714aaabc311bdb65772a96"
REDIRECT_URI = "https://nonexactingly-transbay-eboni.ngrok-free.dev/callback"

auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-library-read playlist-read-private",
    open_browser=True
)

# Spotipy가 localhost:8888에서 Flask-like 서버를 열어서 기다림
token_info = auth_manager.get_access_token(as_dict=False)
access_token = token_info

sp = spotipy.Spotify(auth=access_token)
print("✅ Spotify 인증 성공!")

# 테스트 쿼리
results = sp.search(q="happy", type="track", limit=1)
print("🎵 예시 검색 결과:", results["tracks"]["items"][0]["name"])

# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
# 3. 헬퍼 함수 및 설정
# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=

def get_ensemble_embedding(text_str):
    """
    [핵심] 사용자의 '추론(Script 1)' 방식과 100% 동일한 앙상블 임베딩을 생성합니다.
    (키워드 텍스트를 두 모델에 모두 입력 후 평균)
    """
    if not text_str: # 빈 텍스트 예외 처리
        return np.zeros((1, MAX_DIM))
        
    # "하나의 텍스트"를 두 모델에 모두 입력
    emb_ko = model_ko.encode([text_str]) # (1, 768)
    emb_en = model_en.encode([text_str]) # (1, 384)

    # 차원 맞추기 (MiniLM을 768로 패딩)
    padded_en = np.pad(emb_en, ((0, 0), (0, MAX_DIM - emb_en.shape[1])))
    
    # --- ✅ [버그 수정] ---
    # ko_dim (숫자) 대신 emb_ko (벡터)를 더합니다.
    emb_ensemble = (padded_en + emb_ko) / 2
    return emb_ensemble # (1, 768)

# 숫자(Number)로만 구성된 13D 피처
FEATURE_KEYS = [
    'danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 
    'liveness', 'speechiness', 'mode', 'loudness', 'tempo', 
    'key', 'time_signature', 'duration_ms',
]
print(f"✅ {len(FEATURE_KEYS)}차원 무드 벡터(Y)를 수집합니다.")

# 정규화기
scaler_loudness = MinMaxScaler(feature_range=(0, 1)); scaler_loudness.fit(np.array([[-60], [0]]))
scaler_tempo = MinMaxScaler(feature_range=(0, 1)); scaler_tempo.fit(np.array([[40], [220]]))
scaler_key = MinMaxScaler(feature_range=(0, 1)); scaler_key.fit(np.array([[0], [11]]))
scaler_time_sig = MinMaxScaler(feature_range=(0, 1)); scaler_time_sig.fit(np.array([[3], [7]]))
scaler_duration = MinMaxScaler(feature_range=(0, 1)); scaler_duration.fit(np.array([[30000], [600000]]))

def process_features(feature_dict):
    f = feature_dict
    vector = []
    try:
        for key in FEATURE_KEYS:
            if key == 'loudness': vector.append(scaler_loudness.transform([[f[key]]])[0, 0])
            elif key == 'tempo': vector.append(scaler_tempo.transform([[f[key]]])[0, 0])
            elif key == 'key': vector.append(scaler_key.transform([[f[key]]])[0, 0])
            elif key == 'time_signature': vector.append(scaler_time_sig.transform([[f[key]]])[0, 0])
            elif key == 'duration_ms': vector.append(scaler_duration.transform([[f[key]]])[0, 0])
            elif key in f: vector.append(f[key])
        
        if len(vector) == len(FEATURE_KEYS):
            return vector
        else:
            return None
    except Exception as e:
        return None

# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
# 4. 데이터 수집 메인 로직
# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=

# [수정] 한/영 키워드 혼합 사용
SEARCH_KEYWORDS = [
    'happy', 'sad', 'angry', 'chill', 'study', 'workout', 'party', 'focus', 'sleep', 
    'morning', 'driving', 'romance', 'jazz', 'classical', 'K-Pop',
    '행복한', '슬픈', '우울한', '신나는', '공부', '운동', '파티', '집중', 
    '새벽', '드라이브', '로맨틱', '재즈', '클래식', '감성'
]
PLAYLISTS_PER_KEYWORD = 5

training_data_X = []
training_data_Y = []
metadata_list = []

print(f"\n🚀 {len(SEARCH_KEYWORDS)}개 키워드로 플레이리스트 검색 및 피처 수집 시작...")

for keyword in tqdm(SEARCH_KEYWORDS, desc="전체 키워드 진행도"):
    try:
        results = sp.search(q=keyword, type='playlist', limit=PLAYLISTS_PER_KEYWORD)
        playlists = results['playlists']['items']
    except Exception as e:
        print(f"⚠️ '{keyword}' 검색 중 오류 (Rate Limit?): {e}")
        print("   -> 10초 대기 후 다음 키워드로 넘어갑니다.")
        time.sleep(10)
        continue

    for pl in tqdm(playlists, desc=f"'{keyword}' 플레이리스트", leave=False):
        try:
            if not pl:
                continue 

            playlist_id = pl['id']
            playlist_name = pl['name']
            playlist_desc = pl.get('description', '')
            
            x_text_input = playlist_name + " " + playlist_desc
            if not x_text_input.strip(): continue

            # --- 1. X (입력 벡터) 생성 ---
            x_input = get_ensemble_embedding(x_text_input) 
            x_input_squeezed = x_input.squeeze()

            # --- 2. Y (정답 벡터) 생성 ---
            
            # --- 👇 [핵심 수정] API 호출 1 ---
            tracks = sp.playlist_tracks(playlist_id, limit=30)['items']
            
            # --- 👇 [핵심 수정] API 호출 1과 2 사이에 휴식 ---
            time.sleep(0.5) 
            
            track_ids_names = []
            for item in tracks:
                if item and item['track'] and item['track']['id']:
                     track_ids_names.append((item['track']['id'], item['track']['name']))

            if not track_ids_names: continue

            track_ids = [t[0] for t in track_ids_names]
            
            # --- 👇 [핵심 수정] API 호출 2 ---
            features_list = sp.audio_features(tracks=track_ids)
            features_list = [f for f in features_list if f is not None]

            if not features_list: continue

            # --- 3. 개별 곡 단위로 X, Y 저장 ---
            valid_song_count = 0
            for f in features_list:
                y_vector = process_features(f) 
                if y_vector is not None:
                    training_data_X.append(x_input_squeezed)
                    training_data_Y.append(y_vector)
                    valid_song_count += 1
            
            if valid_song_count > 0:
                metadata_list.append({
                    "keyword": keyword, "playlist_id": playlist_id,
                    "playlist_name": playlist_name, "added_songs": valid_song_count 
                })            
            time.sleep(0.5) 

        except spotipy.exceptions.SpotifyException as se:
            if se.http_status == 429: 
                print("🔥 Rate Limit (429)! 30초 대기...")
                time.sleep(30)
            elif se.http_status == 403: pass 
            elif se.http_status == 404: pass
            else: 
                print(f"🔥 Spotify 오류: {se}")
        except Exception as e:
            print(f"🔥 Python 내부 오류: {e}") 
            
    # --- 👇 [핵심 수정] 다음 '키워드' 검색 전 '충분한' 휴식 ---
    time.sleep(3.0)
        
# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
# 5. 수집된 데이터 저장
# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
if not training_data_X:
    print("\n❌ 수집된 데이터가 없습니다. 키워드나 API 설정을 확인하세요.")
    print("   (ID/Secret은 정상이나, 검색 결과가 없거나 모든 플리 처리에 실패했을 수 있습니다.)")
else:
    X_train_data = np.array(training_data_X)
    Y_train_data = np.array(training_data_Y)

    SAVE_DIR = "training_dataset"
    os.makedirs(SAVE_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    save_path_x = f"{SAVE_DIR}/X_train_{timestamp}.npy"
    save_path_y = f"{SAVE_DIR}/Y_train_{timestamp}.npy"
    meta_path = f"{SAVE_DIR}/meta_{timestamp}.json"

    np.save(save_path_x, X_train_data)
    np.save(save_path_y, Y_train_data)
    
    meta = {
        "timestamp": timestamp,
        "total_samples": len(training_data_X),
        "total_playlists_processed": len(metadata_list),
        "search_keywords": SEARCH_KEYWORDS,
        "feature_keys_used": FEATURE_KEYS,
        "x_shape": X_train_data.shape,
        "y_shape": Y_train_data.shape,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\n\n✅ 총 {len(training_data_X)}개의 학습 데이터 수집 완료!")
    print(f"  (총 {len(metadata_list)}개의 플레이리스트에서 추출됨)")
    print(f"  ➡️ X (입력) 저장: {save_path_x}")
    print(f"  ➡️ Y (정답) 저장: {save_path_y}")
    print(f"  ➡️ 메타 정보 저장: {meta_path}")
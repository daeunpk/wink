import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
# ID와 Secret에는 문제가 없음
# Secret은 새로고침하는 게 좋음

# ID와 Secret
CLIENT_ID = "9f601ae991474c5f9acbbca99f0d9c7c"
CLIENT_SECRET = "302529b448714aaabc311bdb65772a96"
print("🚀 인증 시도 중...")

try:
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    print("✅ 인증 성공!")
    
    print("\n🚀 'happy' 키워드로 검색 테스트...")
    results = sp.search(q='happy', type='playlist', limit=10)
    
    print("✅ 검색 성공!")
    
    count = 0
    for i, pl in enumerate(results['playlists']['items']):
        # --- 👇 [수정] 'pl'이 None이 아닐 때만 처리 ---
        if pl: 
            print(f"  {i+1}. {pl['name']}")
            count += 1
        else:
            print(f"  {i+1}. (빈 아이템 발견 - 스킵)")
    
    print(f"\n✅ {count}개의 유효한 플레이리스트 출력 완료.")

except spotipy.exceptions.SpotifyException as e:
    print(f"\n❌❌❌ API 오류: {e}")
except Exception as e:
    print(f"\n❌ 알 수 없는 오류: {e}")
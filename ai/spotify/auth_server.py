# spotify/auth_server.py
# Spotify OAuth 토큰 발급 및 저장용 Flask 서버
# 사용자 인증 방식

import os
import requests
from flask import Flask, request, redirect
from urllib.parse import urlencode

CLIENT_ID = "9f601ae991474c5f9acbbca99f0d9c7c"
CLIENT_SECRET = "302529b448714aaabc311bdb65772a96"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-read-private user-read-email user-read-playback-state user-modify-playback-state"

app = Flask(__name__)

@app.route('/')
def login():
    """사용자를 Spotify 로그인 페이지로 리디렉션"""
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    })
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Spotify 인증 후 access_token 교환"""
    code = request.args.get("code")
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    res = requests.post(token_url, data=payload)
    data = res.json()
    print("\n✅ Access Token:", data.get("access_token"))
    print("🔁 Refresh Token:", data.get("refresh_token"))

    # 토큰을 파일로 저장해두기
    with open("spotify/spotify_token.json", "w", encoding="utf-8") as f:
        f.write(res.text)

    return "✅ Spotify 인증 완료! 터미널을 확인하세요."

if __name__ == "__main__":
    print(f"🎧 Running Spotify Auth Server on {REDIRECT_URI}")
    app.run(host="127.0.0.1", port=8888, debug=True)

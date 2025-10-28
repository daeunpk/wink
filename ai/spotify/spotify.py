import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint # 데이터를 보기 좋게 출력(pretty print)
import json

cid = '9f601ae991474c5f9acbbca99f0d9c7c'
secret = 'b1c4c21c122c443a8d692397b4b8b58a'
redirect_uri = 'https://example.com/callback'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cid, client_secret=secret, redirect_uri=redirect_uri))


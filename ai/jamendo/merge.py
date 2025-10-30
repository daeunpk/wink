# -*- coding: utf-8 -*-
"""
merge.py
- processed_genre_tags.csv 와 processed_mood_tags.csv 병합
- 기준 컬럼: TRACK_ID
"""

import os
import pandas as pd

# 현재 스크립트 기준 경로 계산
BASE_DIR = os.path.dirname(__file__) # This should be jamendo directory
DATA_DIR = os.path.join(BASE_DIR, "data") # 👈 Look inside the 'data' subfolder
OUTPUT_DIR = DATA_DIR # 👈 Save the output in the same 'data' folder

genre_file = os.path.join(DATA_DIR, "processed_genre_tags.csv")
mood_file = os.path.join(DATA_DIR, "processed_mood_tags.csv") 
output_file = os.path.join(OUTPUT_DIR, "merged_tags.csv") 

# CSV 파일 로드
print(f"🔄 Loading Genre file: {genre_file}")
genre_df = pd.read_csv(genre_file)

print(f"🔄 Loading Mood file: {mood_file}")
mood_df = pd.read_csv(mood_file)
mood_df = mood_df.rename(columns={"X_text": "mood_tags"})

# 병합 (TRACK_ID 기준, outer join)
# [수정] PATH 컬럼 처리: genre_df의 PATH를 사용하고, mood_df의 PATH는 버림
merged_df = pd.merge(genre_df, mood_df[['TRACK_ID', 'mood_tags']], on="TRACK_ID", how="outer")

# 필요한 컬럼만 선택하고 순서 지정
final_df = merged_df[["TRACK_ID", "PATH", "genre_tags", "mood_tags"]]

# 결측값 개수 출력
missing_counts = final_df.isna().sum()

print("✅ 병합 완료!")
print(f"📊 총 행 개수: {len(final_df)}")
print("\n🧩 결측값 개수:")
print(missing_counts)


complete_rows = final_df.dropna(subset=["TRACK_ID", "PATH", "genre_tags", "mood_tags"])
num_complete_rows = len(complete_rows)

print(f"\n📊 4개 열 (TRACK_ID, PATH, genre_tags, mood_tags) 모두 값이 있는 행 개수: {num_complete_rows}")

# CSV로 저장
final_df.to_csv(output_file, index=False, encoding="utf-8-sig") # utf-8-sig for Excel compatibility
print(f"\n💾 결과 저장: {output_file}")

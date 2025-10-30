# -*- coding: utf-8 -*-
"""
clean_merged_data.py
- merged_tags.csv 파일을 로드합니다.
- TRACK_ID, PATH, genre_tags, mood_tags 4개 열 모두에
  값이 있는 행만 필터링합니다.
- 결과를 cleaned_merged_tags.csv로 저장합니다.
"""

import os
import pandas as pd

# --- 1. 파일 경로 설정 ---
# 현재 스크립트 기준 경로 계산
BASE_DIR = os.path.dirname(__file__) # This should be the jamendo directory
DATA_DIR = os.path.join(BASE_DIR, "data")

input_file = os.path.join(DATA_DIR, "merged_tags.csv")
output_file = os.path.join(DATA_DIR, "cleaned_merged_tags.csv")

# --- 2. 입력 파일 로드 ---
print(f"🔄 Loading merged data: {input_file}")
if not os.path.exists(input_file):
    print(f"❌ Input file not found: {input_file}")
    exit()

try:
    merged_df = pd.read_csv(input_file)
    print(f"   -> Loaded {len(merged_df)} rows.")
except Exception as e:
    print(f"🔥 Failed to load CSV: {e}")
    exit()

# --- 3. 결측값 있는 행 제거 ---
print("🧹 Removing rows with missing values in key columns...")
# 'subset'에 명시된 컬럼 중 하나라도 NaN이면 해당 행 제거
cleaned_df = merged_df.dropna(subset=["TRACK_ID", "PATH", "genre_tags", "mood_tags"])
num_cleaned_rows = len(cleaned_df)
num_removed_rows = len(merged_df) - num_cleaned_rows

print(f"   -> Removed {num_removed_rows} rows.")
print(f"   -> Kept {num_cleaned_rows} complete rows.")

# --- 4. 클린 데이터 저장 ---
print(f"💾 Saving cleaned data to: {output_file}")
cleaned_df.to_csv(output_file, index=False, encoding="utf-8-sig") # utf-8-sig for Excel compatibility

print("\n✅ Cleaning complete!")
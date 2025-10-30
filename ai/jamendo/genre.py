# autotagging_genre.tsv 파일에서 TRACK_ID, PATH, genre 태그 추출

import pandas as pd
from tqdm import tqdm
import csv
import os
import re # 정규식 모듈 추가

# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
# 1. 원본 autotagging_genre.tsv 파일 로드
# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
print("1. 원본 autotagging_genre.tsv 파일 로드 중...")

# [수정] 👈 입력 파일 경로 변경
tsv_path = "/Users/eunjung/Desktop/wink/ai/mtg-jamendo-dataset/data/autotagging_genre.tsv" 

if not os.path.exists(tsv_path):
    print(f"❌ 파일을 찾을 수 없습니다: {tsv_path}")
    exit()

# --- CSV 모듈로 파싱 (오류 방지) ---
data_list = []
try:
    with open(tsv_path, 'r', encoding='utf-8') as f:
        header_line = f.readline().strip()
        header = header_line.split('\t')

        if 'TRACK_ID' not in header or 'TAGS' not in header or 'PATH' not in header:
            print("❌ TSV 헤더에서 'TRACK_ID', 'TAGS', 'PATH' 컬럼 중 하나를 찾을 수 없습니다.")
            exit()

        track_id_idx = header.index('TRACK_ID')
        path_idx = header.index('PATH')
        tags_idx = header.index('TAGS')

        reader = csv.reader(f, delimiter='\t')
        for line_parts in reader:
            if len(line_parts) <= tags_idx:
                continue

            track_id = line_parts[track_id_idx]
            path = line_parts[path_idx]
            tags_str = "\t".join(line_parts[tags_idx:]) # TAGS 이후 모든 컬럼을 다시 합침

            # [수정] 👈 genre 태그만 추출 및 정제
            all_tags_list = tags_str.split('\t\t\t') # 탭 3개로 구분
            genre_tags_only = []
            for tag in all_tags_list:
                if tag.startswith('genre---'):
                    # 'genre---' 접두사 제거하고 소문자로 변환
                    clean_tag = tag.replace('genre---', '').lower()
                    # (선택) 하이픈(-)을 공백으로 바꾸거나 제거할 수 있음
                    # clean_tag = clean_tag.replace('-', ' ') 
                    genre_tags_only.append(clean_tag)

            # genre 태그가 있는 경우에만 리스트에 추가
            if genre_tags_only:
                data_list.append({
                    "TRACK_ID": track_id,
                    "PATH": path,
                    # [수정] 👈 리스트를 공백으로 구분된 문자열로 저장
                    "genre_tags": " ".join(genre_tags_only) 
                })

except FileNotFoundError:
    print(f"❌ 파일을 찾을 수 없습니다: {tsv_path}")
    exit()
except Exception as e:
    print(f"🔥 파일 읽기 중 알 수 없는 오류 발생: {e}")
    exit()

# 리스트를 DataFrame으로 변환
processed_df = pd.DataFrame(data_list)
# --- 로드 및 정제 완료 ---

print(f"   -> 총 {len(processed_df)}개의 트랙에서 유효한 genre 태그 추출 완료.")

# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
# 2. 정제된 데이터를 DataFrame으로 변환 및 저장
# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
print("\n2. 정제된 genre 데이터 저장 시작...")

# (결과 예시 출력)
print("\n--- [처리 결과 예시 (상위 5개)] ---")
print(processed_df.head())

# --- [수정] 👈 저장 경로 및 파일명 변경 ---
save_dir = "jamendo/data"
# [수정] 👈 파일명을 genre 용도로 변경
save_path = os.path.join(save_dir, "processed_genre_tags.csv") 

# 폴더가 없으면 생성
os.makedirs(save_dir, exist_ok=True)

processed_df.to_csv(save_path, index=False, encoding='utf-8')
print(f"\n✅ 정제된 genre 데이터를 '{save_path}'에 저장 완료.")
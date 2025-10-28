# autotagging_moodtheme.tsv 파일에서 mood/theme 태그 추출

import pandas as pd
from tqdm import tqdm
import csv 
import os   

# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
# 1. 원본 TSV 파일 로드 (오류 수정)
# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
print("1. 원본 autotagging_moodtheme.tsv 파일 로드 중...")

tsv_path = "mtg-jamendo-dataset/data/autotagging_moodtheme.tsv"

if not os.path.exists(tsv_path):
    print(f"❌ 파일을 찾을 수 없습니다: {tsv_path}")
    exit()

# --- [수정] pd.read_csv 대신 csv 모듈로 파싱 오류 해결 ---
data_list = []
try:
    with open(tsv_path, 'r', encoding='utf-8') as f:
        # 1. 헤더 읽기
        header_line = f.readline().strip()
        header = header_line.split('\t')
        
        if 'TRACK_ID' not in header or 'TAGS' not in header or 'PATH' not in header:
            print("TSV 헤더에서 'TRACK_ID', 'TAGS', 'PATH' 컬럼 중 하나를 찾을 수 없습니다.")
            exit()
            
        track_id_idx = header.index('TRACK_ID')
        path_idx = header.index('PATH')
        tags_idx = header.index('TAGS')
        
        # 3. csv.reader로 나머지 데이터 읽기
        reader = csv.reader(f, delimiter='\t')
        for line_parts in reader:
            if len(line_parts) <= tags_idx:
                continue 
            
            track_id = line_parts[track_id_idx]
            path = line_parts[path_idx]
            tags_str = "\t".join(line_parts[tags_idx:])
            
            data_list.append({
                "TRACK_ID": track_id,
                "PATH": path,
                "TAGS": tags_str
            })

except FileNotFoundError:
    print(f"❌ 파일을 찾을 수 없습니다: {tsv_path}")
    exit()
except Exception as e:
    print(f"🔥 파일 읽기 중 알 수 없는 오류 발생: {e}")
    exit()

# 리스트를 DataFrame으로 변환 (이후 로직은 동일)
data = pd.DataFrame(data_list)
# --- [수정 완료] ---


print(f"   -> 총 {len(data)}개의 트랙 로드 완료.")

# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
# 2. X (입력) 데이터 추출 및 정제 (이 로직은 완벽하므로 수정 X)
# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
print("2. 'mood/theme' 태그 추출 및 정제 시작...")

processed_X_data = []

# tqdm을 사용하여 진행 상황 표시
for index, row in tqdm(data.iterrows(), total=len(data)):
    track_id = row['TRACK_ID']
    path = row['PATH']
    all_tags_str = row['TAGS']
    
    # 태그 문자열을 개별 태그 리스트로 분리 (탭 3개 기준)
    all_tags_list = all_tags_str.split('\t\t\t')
    
    # 'mood/theme---'로 시작하는 태그만 추출
    mood_tags_only = []
    for tag in all_tags_list:
        if tag.startswith('mood/theme---'):
            clean_tag = tag.replace('mood/theme---', '')
            mood_tags_only.append(clean_tag)
            
    # 3. 정제된 텍스트 생성
    if mood_tags_only: # 무드 태그가 하나라도 있는 경우
        final_x_text = " ".join(mood_tags_only)
        
        # (TRACK_ID, 정제된 텍스트) 쌍으로 저장
        processed_X_data.append({
            "TRACK_ID": track_id,
            "PATH": path,
            "X_text": final_x_text 
        })
    # (무드 태그가 없는 트랙은 무시하고 넘어감)

# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
# 4. 정제된 데이터를 DataFrame으로 변환 및 저장 (수정)
# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
processed_df = pd.DataFrame(processed_X_data)

print("\n3. X (입력) 데이터 정제 완료!")
print(f"   -> 원본 {len(data)}여 곡 중 {len(processed_df)}개의 곡이 유효한 무드 태그 보유.")

# (결과 예시 출력)
print("\n--- [처리 결과 예시 (상위 5개)] ---")
print(processed_df.head())

# --- [수정] 요청하신 경로에 파일 저장 ---
save_dir = "jamendo/data"
save_path = os.path.join(save_dir, "processed_X_text.csv")

# 폴더가 없으면 생성
os.makedirs(save_dir, exist_ok=True)

# index=False: CSV 저장 시 불필요한 인덱스(0,1,2...) 제외
# encoding='utf-8': 한글 태그(있을 경우) 깨짐 방지
processed_df.to_csv(save_path, index=False, encoding='utf-8')
print(f"\n✅ 정제된 X 데이터를 '{save_path}'에 저장 완료.")
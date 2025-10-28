# autotagging_moodtheme.tsv를 읽어 각 TRACK_ID 별로 임베딩에 사용할 키워드 텍스트 생성

import pandas as pd
from tqdm import tqdm

# 1. 원본 TSV 파일 로드 (수정 X)
print("1. 원본 autotagging_moodtheme.tsv 파일 로드 중...")
try:
    # TSV 파일은 '탭(\t)'으로 구분되어 있습니다.
    data = pd.read_csv("mtg-jamendo-dataset/data/autotagging_moodtheme.tsv", sep='\t')
except FileNotFoundError:
    print("❌ 파일을 찾을 수 없습니다. 경로를 확인하세요.")
    exit()

print(f"   -> 총 {len(data)}개의 트랙 로드 완료.")

# 2. X (입력) 데이터 추출 및 정제
print("2. 'mood/theme' 태그 추출 및 정제 시작...")

# 정제된 데이터를 저장할 리스트
# (나중에 DataFrame으로 변환하기 쉬움)
processed_X_data = []

# tqdm을 사용하여 진행 상황 표시
for index, row in tqdm(data.iterrows(), total=len(data)):
    track_id = row['TRACK_ID']
    all_tags_str = row['TAGS'] # 'mood/theme---happy\t\t\tgenre---pop'
    
    # 태그 문자열을 개별 태그 리스트로 분리 (탭 3개 기준)
    all_tags_list = all_tags_str.split('\t\t\t')
    
    # 'mood/theme---'로 시작하는 태그만 추출
    mood_tags_only = []
    for tag in all_tags_list:
        if tag.startswith('mood/theme---'):
            # 'mood/theme---' 접두사 제거
            clean_tag = tag.replace('mood/theme---', '')
            mood_tags_only.append(clean_tag)
            
    # 3. 정제된 텍스트 생성
    if mood_tags_only: # 무드 태그가 하나라도 있는 경우
        # ["happy", "relaxing"] -> "happy relaxing"
        final_x_text = " ".join(mood_tags_only)
        
        # (TRACK_ID, 정제된 텍스트) 쌍으로 저장
        processed_X_data.append({
            "TRACK_ID": track_id,
            "X_text": final_x_text 
        })
    # (무드 태그가 없는 트랙은 무시하고 넘어감)

# 4. 정제된 데이터를 DataFrame으로 변환 및 저장 (선택 사항)
processed_df = pd.DataFrame(processed_X_data)

print("\n3. X (입력) 데이터 정제 완료!")
print(f"   -> 원본 18,000여 곡 중 {len(processed_df)}개의 곡이 유효한 무드 태그 보유.")

# (결과 예시 출력)
print("\n--- [처리 결과 예시 (상위 5개)] ---")
print(processed_df.head())

# (선택 사항) 이 중간 결과를 파일로 저장해두면 나중에 편합니다.
processed_df.to_csv("processed_X_text.csv", index=False)
print("\n   -> 'processed_X_text.csv'로 중간 저장 완료.")
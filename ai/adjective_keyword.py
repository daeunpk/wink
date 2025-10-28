import requests
import base64
import json
import os
from datetime import datetime
import re

# ngrok 주소
OLLAMA_URL = "http://localhost:11434"

# 1️⃣ 프롬프트 정의 - 이미지 텍스트 동시 혹은 단일 처리 모두 가능하게
prompt = (
    "입력된 데이터(텍스트 또는 이미지)를 분석해서 분위기를 표현하는 형용사를 한국어-영어 다섯 쌍을 추출해. "
    "출력은 JSON 형식으로만 반환하고, key 이름은 반드시 'keywords'로 해. "
    "형식 예시는 다음과 같아:\n"
    "{'keywords': [{'korean': '따뜻한', 'english': 'warm'}, {'korean': '평화로운', 'english': 'peaceful'}, ...]}"
)

# 텍스트 입력
user_text = input("텍스트 설명을 입력하세요 (없으면 엔터): ").strip()
# 이미지 입력
image_path = input("이미지 파일 경로를 입력하세요 (없으면 엔터): ").strip()

# 3️⃣ 요청 payload 구성
payload = {
    "model": "gemma3:27b",            # 모델 이름 (Gemma3)
    "prompt": prompt,             # 질문 / 지시문
    "stream": False               # 실시간 스트림 X (JSON 전체 응답)
}

# 텍스트가 있다면 프롬프트에 포함
if user_text:
    payload["prompt"] += f"\n\n사용자 입력 텍스트: {user_text}"

# 이미지가 있다면 base64 인코딩해서 추가
if image_path and os.path.exists(image_path):
    with open(image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode("utf-8")
    payload["images"] = [img_base64]

# 4️⃣ Ollama 서버에 POST 요청
response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload)

# 5️⃣ 결과 출력
if response.status_code == 200:
    data = response.json()
    raw_output = data.get("response", "").strip()
    
    cleaned_output = re.sub(r"```json|```", "", raw_output).strip()
    
    try:
        # 모델 응답을 JSON으로 변환
        result = json.loads(cleaned_output.replace("'", "\""))
    except json.JSONDecodeError:
        print("모델이 JSON 형식으로 응답하지 않았습니다. 원문:")
        print(raw_output)
        result = {"keywords": []}

    # 입력 정보 추가
    result["input"] = {
        "type": "text+image" if (user_text and image_path) else ("text" if user_text else "image"),
        "text": user_text or None,
        "file": image_path or None
    }

    # 저장 폴더 및 파일명
    os.makedirs("keyword", exist_ok=True)
    filename = f"keyword/keywords_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ JSON 저장 완료 → {filename}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
else:
    print("오류 발생:", response.status_code, response.text)
# import os
# import base64
# import requests
# import re

# # =========================================================
# # 1. 설정
# # =========================================================
# OLLAMA_URL = "http://localhost:11434"
# MODEL_NAME = "gemma3:27b"

# # =========================================================
# # 2. 이미지 캡션 생성 함수
# # =========================================================
# def image_to_english_caption(image_path: str) -> str:
#     """
#     Gemma3 멀티모달 모델을 이용해 이미지 캡션(영문 한 문장)을 생성합니다.

#     Args:
#         image_path (str): 로컬 이미지 경로
#     Returns:
#         str: 영어 문장 (예: "A calm sunset over the river with a warm glow.")
#     """
#     if not os.path.exists(image_path):
#         raise FileNotFoundError(f"❌ Image not found: {image_path}")

#     # 이미지 파일을 base64로 인코딩
#     with open(image_path, "rb") as f:
#         image_b64 = base64.b64encode(f.read()).decode("utf-8")

#     # 프롬프트 구성
#     prompt = (
#         "Describe this image in ONE natural English sentence. "
#         "Focus on the atmosphere, mood, and main objects. "
#         "Do not list elements; write a single complete sentence."
#     )

#     payload = {
#         "model": MODEL_NAME,
#         "prompt": prompt,
#         "images": [image_b64],
#         "stream": False
#     }

#     # Ollama API 요청
#     try:
#         res = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
#         res.raise_for_status()
#     except requests.exceptions.ConnectionError:
#         raise RuntimeError("🚨 Ollama 서버가 꺼져 있습니다. 터미널에서 `ollama serve` 를 실행하세요.")
#     except requests.exceptions.SSLError:
#         raise RuntimeError("❌ HTTPS를 쓰면 안 됩니다. `http://localhost:11434`로 유지하세요.")
#     except Exception as e:
#         raise RuntimeError(f"🔥 Ollama 요청 실패: {e}")

#     data = res.json()
#     caption = (data.get("response") or "").strip()

#     return caption

# # =========================================================
# # 3. 테스트 실행 (독립 실행용)
# # =========================================================
# if __name__ == "__main__":
#     print("\n🖼️  Gemma3 (Ollama) 이미지 캡션 생성 테스트")
#     image_path = input("이미지 파일 경로를 입력하세요: ").strip()

#     if not image_path:
#         print("❌ 이미지 경로가 비어 있습니다.")
#     else:
#         try:
#             caption = image_to_english_caption(image_path)
#             print("\n🌍 생성된 영어 문장:")
#             print(caption)
#         except Exception as e:
#             print(f"\n⚠️ 오류 발생: {e}")

# -*- coding: utf-8 -*-
"""
Agent 2 (Module)
- Ollama (Gemma3)를 이용한 이미지 캡션 생성을 전담합니다.
"""

import os
import base64
import requests
import re  # 👈 후처리를 위한 re 임포트

# =========================================================
# 1. 설정
# =========================================================
OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "gemma3:27b" # (Agent 3와 동일한 모델 사용)

# =========================================================
# 2. 이미지 캡션 생성 함수 (메인 파이프라인에서 이 함수를 import)
# =========================================================
def image_to_english_caption(image_path: str) -> str:
    """
    Gemma3 멀티모달 모델을 이용해 이미지 캡션(영문 한 문장)을 생성합니다.
    """
    if not image_path or not os.path.exists(image_path):
        return ""
    
    print("🖼️  [Agent 2] Describing image → English caption (Ollama)...")

    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return ""

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    prompt = (
        "Describe this image in ONE natural English sentence. "
        "Focus on the atmosphere, mood, and main objects. "
        "Do not list elements; write a single complete sentence."
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False
    }

    try:
        res = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
        res.raise_for_status()
    except requests.exceptions.ConnectionError:
        print("🚨 Ollama 서버가 꺼져 있습니다. 터미널에서 `ollama serve` 를 실행하세요.")
        return ""
    except Exception as e:
        print(f"🔥 Ollama 요청 실패: {e}")
        return ""

    # [수정] 👈 Agent 3와 동일한 후처리 로직 적용
    raw_response = (res.json().get("response") or "").strip()
    match = re.search(r'["\'](.*?_*)["\']', raw_response) # 따옴표 안 내용 추출
    if match:
        return match.group(1).strip()
    return raw_response.split('\n')[-1].strip() # 따옴표 없으면 마지막 줄 반환

# =========================================================
# 3. 테스트 실행 (독립 실행용)
# =========================================================
if __name__ == "__main__":
    print("\n🖼️  Agent 2 (Module) 테스트")
    image_path = input("이미지 파일 경로를 입력하세요: ").strip()

    if not image_path:
        print("❌ 이미지 경로가 비어 있습니다.")
    else:
        try:
            caption = image_to_english_caption(image_path)
            print("\n🌍 생성된 영어 문장:")
            print(caption)
        except Exception as e:
            print(f"\n⚠️ 오류 발생: {e}")
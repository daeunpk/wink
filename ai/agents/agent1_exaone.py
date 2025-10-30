# -*- coding: utf-8 -*-
# agent 1:한국어 입력 → 영어 출력
# agent 3-3:영어 키워드 입력 → 한국어 키워드

"""
EXAONE Agent (Module)
- EXAONE 모델의 캐시 로드를 관리합니다.
- (Agent 1) 한국어 -> 영어 번역 기능을 제공합니다.
- (Agent 3-3) 영어 -> 한국어 번역 기능을 제공합니다.
"""

import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# =========================================================
# 1. 모델 설정
# =========================================================
MODEL_NAME = "LGAI-EXAONE/EXAONE-4.0-1.2B"

# =========================================================
# 2. EXAONE 모델 캐시 로드 (Agent 3의 방식을 가져옴)
# =========================================================
_exa_tok, _exa_model = None, None
def _load_exaone():
    """
    EXAONE 모델을 한 번만 로드하여 VRAM을 절약하는 캐시 함수.
    """
    global _exa_tok, _exa_model
    if _exa_tok is None or _exa_model is None:
        print(f"🔄 Loading EXAONE model ({MODEL_NAME})...")
        _exa_tok = AutoTokenizer.from_pretrained(MODEL_NAME)
        _exa_model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME, torch_dtype=torch.bfloat16, device_map="auto"
        )
    return _exa_tok, _exa_model

# =========================================================
# 3. [Agent 1 기능] 한국어 → 영어
# =========================================================
def korean_to_english(korean_text: str) -> str:
    """
    한국어 텍스트를 자연스러운 영어 문장으로 변환합니다.
    """
    if not korean_text.strip():
        return ""
    print("🧠 [Agent 1] Translating Korean → English (EXAONE)...")
    tok, mdl = _load_exaone() # 캐시된 모델 사용

    messages = [
        {"role": "user", "content": f"Translate the following Korean text into one natural English sentence. Respond *only* with the translated sentence itself, without any explanations or conversational text.\n\nKorean: {korean_text}"}
    ]
    inputs = tok.apply_chat_template(
        messages, return_tensors="pt", add_generation_prompt=True
    ).to(mdl.device)

    input_length = inputs.shape[1]
    with torch.no_grad():
        outputs = mdl.generate(inputs, max_new_tokens=256, do_sample=False)
    
    new_tokens = outputs[0][input_length:]
    result_text = tok.decode(new_tokens, skip_special_tokens=True).strip()

    match = re.search(r'["\'](.*?_*)["\']', result_text)
    if match:
        return match.group(1).strip()
    return result_text.split('\n')[-1].strip()

# =========================================================
# 5. 테스트 실행 (Agent 1의 원본 테스트 코드)
# =========================================================
if __name__ == "__main__":
    """
    이 파일을 직접 실행할 경우, Agent 1 기능만 테스트합니다.
    """
    try:
        print("--- EXAONE Agent (Module) Test ---")
        text_ko = input("\n한국어 문장을 입력하세요: ").strip()
        if not text_ko:
            print("❌ 입력이 비어 있습니다.")
        else:
            result = korean_to_english(text_ko)
            print("\n🌍 변환된 영어 문장:")
            print(result)
    except KeyboardInterrupt:
        print("\n🛑 프로그램 종료됨.")
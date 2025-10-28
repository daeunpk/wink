# -*- coding: utf-8 -*-
"""
Agent 3 (Merge + Save)
- Agent1, 2에서 생성된 영어 문장을 입력받음
- 두 문장을 Gemma3로 자연스럽게 하나의 문장으로 재작성
- 감성 키워드 5개 추출
- 모든 결과를 agents/keywords 폴더에 JSON으로 저장
"""

import os
import re
import json
import requests
from datetime import datetime

# =========================================================
# 1. 전역 설정
# =========================================================
OLLAMA_URL = "http://localhost:11434"  # Gemma3 서버
GEMMA3_MODEL = "gemma3:27b"
SAVE_DIR = "agents/keywords"
os.makedirs(SAVE_DIR, exist_ok=True)

# =========================================================
# 2. 영어 문장 재생성 (Gemma3)
# =========================================================
def rewrite_combined_sentence(text1: str, text2: str) -> str:
    """
    두 영어 문장을 자연스럽게 하나로 합친다.
    """
    if not text1 and not text2:
        return ""

    combined_prompt = f"""
Combine the following two English sentences into ONE smooth, natural descriptive sentence. 
Preserve their emotional and atmospheric tone.

Sentence 1: {text1}
Sentence 2: {text2}
"""
    payload = {
        "model": GEMMA3_MODEL,
        "prompt": combined_prompt.strip(),
        "stream": False
    }

    try:
        res = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
        res.raise_for_status()
        merged_text = (res.json().get("response") or "").strip()
        return merged_text
    except Exception as e:
        print(f"⚠️ Failed to merge sentences: {e}")
        return f"{text1} {text2}".strip()

# =========================================================
# 3. 감성 키워드 추출 (Gemma3)
# =========================================================
def extract_keywords(merged_text: str, k: int = 5) -> list[str]:
    """
    영어 문장에서 감성/분위기 중심 키워드 k개 추출
    """
    if not merged_text.strip():
        return []

    prompt = f"""
From the following English description, extract exactly {k} concise single-word adjectives 
that best represent its overall mood, lighting, or emotional style.
Output only a comma-separated list (no explanations).

Example: calm, dreamy, warm, nostalgic, peaceful

Text:
{merged_text}
"""

    payload = {"model": GEMMA3_MODEL, "prompt": prompt.strip(), "stream": False}
    try:
        res = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
        res.raise_for_status()
        raw = (res.json().get("response") or "").strip()
        keywords = [re.sub(r"[^a-z\-]", "", w.strip().lower()) for w in raw.split(",")]
        return [w for w in keywords if w][:k]
    except Exception as e:
        print(f"🔥 Keyword extraction failed: {e}")
        return []

# =========================================================
# 4. 전체 실행 + 저장
# =========================================================
def run_agent3(english_text_from_agent1: str, english_caption_from_agent2: str):
    """
    Agent1, 2의 영어 결과를 받아 합치고 키워드를 추출 후 JSON 저장.
    """
    print("🧩 Merging English sentences via Gemma3...")
    merged_sentence = rewrite_combined_sentence(english_text_from_agent1, english_caption_from_agent2)

    print("💬 Extracting emotional keywords...")
    keywords = extract_keywords(merged_sentence)

    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "english_text_from_agent1": english_text_from_agent1,
        "english_caption_from_agent2": english_caption_from_agent2,
        "merged_sentence": merged_sentence,
        "extracted_keywords": keywords
    }

    # 저장
    filename = f"keyword_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 결과 저장 완료 → {filepath}")
    return result

# =========================================================
# 5. 테스트 실행
# =========================================================
if __name__ == "__main__":
    print("\n🤖 Agent3 실행 테스트 (Agent1, 2 결과 직접 입력)")
    text1 = input("Agent1의 영어 문장 입력: ").strip()
    text2 = input("Agent2의 영어 캡션 입력: ").strip()

    output = run_agent3(text1, text2)

    print("\n🎯 최종 결과:")
    print(json.dumps(output, ensure_ascii=False, indent=2))

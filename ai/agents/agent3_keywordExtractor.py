# -*- coding: utf-8 -*-
"""
Agent3 (Session-based Pipeline)
- 사용자 입력(한국어 텍스트, 이미지 경로)을 직접 받음
- 내부적으로 Agent1(한국어→영어), Agent2(이미지→영어 캡션)
- Gemma3: 두 결과를 자연스럽게 하나의 문장으로 재작성
- Gemma3: 영어 키워드 5개 추출
- EXAONE: 영어 키워드를 한국어로 번역
- 모든 실행 결과를 세션 단위 JSON에 누적 저장
"""

import os
import re
import json
import base64
from datetime import datetime
import requests
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# =========================================================
# 1. 전역 설정
# =========================================================
OLLAMA_URL = "http://localhost:11434"
GEMMA3_MODEL = "gemma3:27b"
EXAONE_MODEL = "LGAI-EXAONE/EXAONE-4.0-1.2B"
SAVE_DIR = "agents/keywords"
os.makedirs(SAVE_DIR, exist_ok=True)

# =========================================================
# 2. EXAONE 모델 캐시 로드
# =========================================================
_exa_tok, _exa_model = None, None
def _load_exaone():
    global _exa_tok, _exa_model
    if _exa_tok is None or _exa_model is None:
        print("🔄 Loading EXAONE model...")
        _exa_tok = AutoTokenizer.from_pretrained(EXAONE_MODEL)
        _exa_model = AutoModelForCausalLM.from_pretrained(
            EXAONE_MODEL, torch_dtype="bfloat16", device_map="auto"
        )
    return _exa_tok, _exa_model

# =========================================================
# 3. 한국어 → 영어 (EXAONE) - (버그 수정)
# =========================================================
def korean_to_english(korean_text: str) -> str:
    if not korean_text.strip():
        return ""
    print("🧠 Translating Korean → English ...")
    tok, mdl = _load_exaone()

    # [수정] Chat 템플릿 적용
    messages = [
        {"role": "user", "content": f"Translate this Korean sentence into natural English:\n{korean_text}"}
    ]
    inputs = tok.apply_chat_template(
        messages,
        return_tensors="pt",
        add_generation_prompt=True # <|assistant|> 프롬프트 추가
    ).to(mdl.device)

    # [수정] 프롬프트 길이를 제외하고 '새로 생성된 토큰'만 디코딩
    input_length = inputs.shape[1]
    with torch.no_grad():
        outputs = mdl.generate(inputs, max_new_tokens=256, do_sample=False)
    
    new_tokens = outputs[0][input_length:]
    result_text = tok.decode(new_tokens, skip_special_tokens=True).strip()
    
    return result_text

# =========================================================
# 4. 이미지 → 영어 캡션 (Gemma3 via Ollama)
# =========================================================
def image_to_english_caption(image_path: str) -> str:
    if not image_path or not os.path.exists(image_path):
        return ""
    print("🖼️ Describing image → English caption ...")

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    prompt = "Describe this image in ONE English sentence focusing on mood and atmosphere."
    payload = {"model": GEMMA3_MODEL, "prompt": prompt, "images": [image_b64], "stream": False}
    try:
        res = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
        res.raise_for_status()
        return (res.json().get("response") or "").strip()
    except Exception as e:
        print(f"⚠️ Image caption generation failed: {e}")
        return ""

# =========================================================
# 5. 두 영어 문장 합치기 (Gemma3)
# =========================================================
def rewrite_combined_sentence(text1: str, text2: str) -> str:
    if not (text1 or text2):
        return ""
    print("🧩 Merging English sentences ...")

    prompt = f"""
Combine the following two English sentences into ONE smooth, natural descriptive sentence. 
Preserve their emotional and atmospheric tone.

Sentence 1: {text1}
Sentence 2: {text2}
"""
    payload = {"model": GEMMA3_MODEL, "prompt": prompt.strip(), "stream": False}
    try:
        res = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
        res.raise_for_status()
        return (res.json().get("response") or "").strip()
    except Exception as e:
        print(f"⚠️ Merge failed: {e}")
        return f"{text1} {text2}".strip()

# =========================================================
# 6. 감성 키워드 추출 (Gemma3)
# =========================================================
def extract_keywords(merged_text: str, k: int = 5) -> list[str]:
    if not merged_text.strip():
        return []
    print("💬 Extracting mood keywords ...")

    prompt = f"""
From the text below, extract exactly {k} concise single-word adjectives that describe the mood or tone.
Output only a comma-separated list.

Text:
{merged_text}
"""
    payload = {"model": GEMMA3_MODEL, "prompt": prompt.strip(), "stream": False}
    try:
        res = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
        res.raise_for_status()
        raw = (res.json().get("response") or "").strip()
        words = [re.sub(r"[^a-z\-]", "", w.strip().lower()) for w in raw.split(",")]
        return [w for w in words if w][:k]
    except Exception as e:
        print(f"🔥 Keyword extraction failed: {e}")
        return []

# =========================================================
# 7. 영어 키워드 → 한국어 (EXAONE) - (버그 수정)
# =========================================================
def translate_keywords_to_korean(english_keywords: list[str]) -> list[str]:
    """
    영어 감성 키워드를 한국어로 번역 (EXAONE, 완전 개선 버전)
    """
    if not english_keywords:
        return []

    print("🌐 Translating English keywords → Korean (EXAONE)...")
    tok, mdl = _load_exaone()

    # [수정] Chat 템플릿 적용
    prompt_content = (
        "다음 영어 형용사들을 자연스러운 한국어 단어로 번역하시오.\n"
        "출력은 쉼표(,)로 구분된 한글 단어만 포함하시오.\n\n"
        f"{', '.join(english_keywords)}"
    )
    messages = [
        {"role": "user", "content": prompt_content}
    ]
    inputs = tok.apply_chat_template(
        messages,
        return_tensors="pt",
        add_generation_prompt=True
    ).to(mdl.device)

    # [수정] 프롬프트 길이를 제외하고 '새로 생성된 토큰'만 디코딩
    input_length = inputs.shape[1]
    with torch.no_grad():
        outputs = mdl.generate(inputs, max_new_tokens=128, do_sample=False)
    
    new_tokens = outputs[0][input_length:]
    translated = tok.decode(new_tokens, skip_special_tokens=True).strip()

    # [수정] 모델이 프롬프트를 반복하지 않도록, 응답에서 한글/쉼표만 추출
    ko_words = re.findall(r"[\u3131-\ucb4f]+", translated) # 정규식으로 한글 단어만 추출

    # 만약 모델이 "으스스한, 외로운, ..." 처럼 쉼표로 잘 반환했을 경우
    if not ko_words or len(ko_words) < len(english_keywords):
        ko_words = [w.strip() for w in re.split(r"[,，\s\n]+", translated) if w.strip()]
        
    final_list = [w for w in ko_words if not w.isascii() and w not in ["다음", "영어", "형용사들을"]] # 프롬프트 단어 필터링
    
    if len(final_list) >= len(english_keywords):
        return final_list[:len(english_keywords)]
    else:
        # 번역 실패 시
        print(f"⚠️ KO translation parsing failed. Raw output: {translated}")
        return (final_list + ["번역실패"] * len(english_keywords))[:len(english_keywords)]
    
# =========================================================
# 8. 세션 저장 (안전한 버전)
# =========================================================
def save_to_session_simple(data: dict, session_file: str):
    """
    지정된 세션 JSON 파일을 안전하게 열고, 데이터를 append합니다.
    파일이 없으면 새로 생성합니다.
    """
    
    # 1. 새 세션의 기본 구조 정의
    default_structure = {
        "session_name": os.path.basename(session_file).replace(".json", ""),
        "session_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_korean": [],
        "input_image": [],
        "english_text_from_agent1": [],
        "english_caption_from_agent2": [],
        "merged_sentence": [],
        "english_keywords": [],
        "korean_keywords": []
    }
    
    if os.path.exists(session_file):
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)
            
            # [안전장치] 👈 기존 파일에 키가 누락되었는지 확인하고 추가
            for key, default_value in default_structure.items():
                if key not in session_data:
                    print(f"⚠️ 기존 세션 파일에 '{key}' 키가 없어 추가합니다.")
                    session_data[key] = default_value
                    
        except json.JSONDecodeError:
            print(f"⚠️ 세션 파일이 손상되어 새로 만듭니다: {session_file}")
            session_data = default_structure # 손상 시 기본 구조로 덮어쓰기
    else:
        # 파일이 없으면 기본 구조 사용
        session_data = default_structure

    # 2. 이제 모든 키가 존재하므로 안전하게 append
    try:
        session_data["input_korean"].append(data["input"]["korean_text"])
        session_data["input_image"].append(data["input"]["image_path"])
        session_data["english_text_from_agent1"].append(data["english_text_from_agent1"])
        session_data["english_caption_from_agent2"].append(data["english_caption_from_agent2"])
        session_data["merged_sentence"].append(data["merged_sentence"])
        session_data["english_keywords"].append(data["english_keywords"])
        session_data["korean_keywords"].append(data["korean_keywords"])
    except KeyError as e:
        print(f"🔥 데이터 저장 중 치명적인 Key Error 발생: {e}")
        return

    # 3. 파일 쓰기
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
                
# =========================================================
# 9. 전체 실행 파이프라인
# =========================================================
def run_agent3_session(korean_text="", image_path="", session_name="current_session"):
    english_text = korean_to_english(korean_text) if korean_text else ""
    english_caption = image_to_english_caption(image_path) if image_path else ""
    merged = rewrite_combined_sentence(english_text, english_caption)
    eng_keywords = extract_keywords(merged)
    kor_keywords = translate_keywords_to_korean(eng_keywords)

    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input": {"korean_text": korean_text, "image_path": image_path},
        "english_text_from_agent1": english_text,
        "english_caption_from_agent2": english_caption,
        "merged_sentence": merged,
        "english_keywords": eng_keywords,
        "korean_keywords": kor_keywords
    }

    session_file = os.path.join(SAVE_DIR, f"{session_name}.json")
    save_to_session_simple(data, session_file)
    print(f"\n✅ Saved to session → {session_file}")
    return data

# =========================================================
# 10. CLI (세션 관리자)
# =========================================================
if __name__ == "__main__":
    print("\n🤖 Agent3 세션형 실행 (한국어 텍스트/이미지 입력)")
    
    # --- 1. 기존 세션 파일 목록 불러오기 ---
    session_files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.json')]
    session_files.sort(reverse=True) # 최근 세션이 위로 오도록 정렬
    
    session_name = ""

    if not session_files:
        print("   -> 기존 세션이 없습니다. 'new'를 선택하세요.")
    else:
        print("\n--- 🗂️  기존 세션 목록 ---")
        for i, f_name in enumerate(session_files):
            print(f"   [{i+1}] {f_name}")
        print("--------------------------")

    # --- 2. 세션 선택 ---
    choice = input("\n새 대화는 'new', 이어하기는 '번호' 입력: ").strip().lower()

    if choice == "new":
        session_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"   -> 🆕 새 세션을 시작합니다: {session_name}.json")
    elif choice.isdigit() and 1 <= int(choice) <= len(session_files):
        # 사용자가 1을 입력하면 리스트의 0번째 파일 선택
        selected_file = session_files[int(choice) - 1]
        session_name = selected_file.replace(".json", "") # '.json' 확장자 제거
        print(f"   -> ➡️ 기존 세션에 이어합니다: {session_name}.json")
    else:
        print("   -> ⚠️ 잘못된 입력입니다. 새 세션을 시작합니다.")
        session_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"   -> 🆕 새 세션을 시작합니다: {session_name}.json")

    # --- 3. 사용자 입력 받기 ---
    print("\n--- 💬 입력을 시작하세요 ---")
    text = input("한국어 텍스트 입력 (없으면 Enter): ").strip()
    img = input("이미지 파일 경로 입력 (없으면 Enter): ").strip()

    if not text and not img:
        print("\n🛑 입력이 없어 종료합니다.")
        exit()

    # --- 4. 파이프라인 실행 ---
    print("\n--- 🚀 에이전트 파이프라인 실행 ---")
    try:
        result = run_agent3_session(text, img, session_name=session_name)
        
        print("\n--- 🎯 실행 결과 ---")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"\n🔥🔥🔥 파이프라인 실행 중 심각한 오류 발생: {e}")
        # (예: EXAONE 로드 실패, Ollama 연결 실패 등)
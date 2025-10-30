# main pipeline
# -*- coding: utf-8 -*-
"""
Agent3 (통합 파이프라인)
- Agent 1 로직: 한국어 텍스트 입력 → 영어 번역 (EXAONE)
- Agent 2 로직: 이미지 경로 입력 → 영어 캡션 (Ollama Gemma3)
- Agent 3 로직 (1): 두 영어 문장 → 하나의 문장으로 재작성 (Ollama Gemma3)
- Agent 3 로직 (2): 재작성된 문장 → 영어 키워드 5개 추출 (Ollama Gemma3)
- 세션 관리: 모든 결과를 'active_session.json'에 누적 저장
"""

import os
import re
import json
import base64
from datetime import datetime
import requests
# import torch
# from transformers import AutoModelForCausalLM, AutoTokenizer
# from rag_recommender import recommend_song_based_on_context

# agent1 import
try:
    from agent1_exaone import korean_to_english
except ImportError:
    print("❌ 'agents/exaone_agent.py' 파일을 찾을 수 없습니다.")
    exit()

# agent2 import
try:
    from agent2_imageToEng import image_to_english_caption
except ImportError:
    print("❌ 'agents/agent2_imageToEng.py' 파일을 찾을 수 없습니다.")
    exit()
    
# rag import
try:
    from context_manager import get_full_conversation_history
except ImportError:
    print("❌ 'agents/context_manager.py' 파일을 찾을 수 없습니다.")
    exit()
    
# =========================================================
# 1. 전역 설정
# =========================================================
OLLAMA_URL = "http://localhost:11434"
GEMMA3_MODEL = "gemma3:27b" # (Ollama가 멀티모달을 지원하는 모델 ID)
SAVE_DIR = "agents/keywords"
os.makedirs(SAVE_DIR, exist_ok=True)

# =========================================================
# 5. [Agent 3-1] 두 영어 문장 합치기 (Ollama Gemma3)
# =========================================================
def rewrite_combined_sentence(text1: str, text2: str, full_history: str) -> str:
    """
    (Agent 3, 1단계)
    (수정) '전체 대화 이력'과 '새 입력'을 Ollama로 결합(재작성)합니다.
    """
    
    # --- 1. 새 입력 조합 ---
    new_input_sentence = f"{text1} {text2}".strip()
    if not new_input_sentence:
        # (예: "비 오는 날" -> "더 차분하게")
        # 새 입력(text1, text2)이 없더라도, 이전 이력(full_history)만으로
        # Gemma3가 키워드를 다시 생성하도록 유도할 수 있습니다.
        # 하지만 여기서는 새 입력이 없으면 에러로 간주하고 빈 문자열 반환
        print("⚠️ [Agent 3] No new input text or image provided.")
        return ""

    print("🧩 [Agent 3] Merging (Context + New Input) sentences (Ollama)...")

    # [핵심] 👈 Gemma3에게 '이전 대화'와 '새 요청'을 함께 전달
    prompt = f"""
You are a context-aware chat assistant. Your job is to understand the user's full request by combining their past conversation history with their newest input.

[Past Conversation History]
{full_history}

[User's Newest Input]
"{new_input_sentence}"

Combine *all* this context (History + New Input) into ONE single, updated descriptive sentence that reflects the user's *final* intent.
For example, if History is "Rainy day" and New Input is "make it calmer", the output should be "A calm and rainy day".

Respond *only* with the final combined English sentence.
"""
    
    messages = [{"role": "user", "content": prompt.strip()}]
    payload = {"model": GEMMA3_MODEL, "messages": messages, "stream": False, "format": "text"}
    try:
        res = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=60)
        res.raise_for_status()
        
        raw_response = (res.json().get("message", {}).get("content", "") or "").strip()
        match = re.search(r'["\'](.*?_*)["\']', raw_response)
        if match:
            return match.group(1).strip()
        return raw_response.split('\n')[-1].strip()
        
    except Exception as e:
        print(f"⚠️ Merge failed: {e}")
        return new_input_sentence # 실패 시 새 입력만 반환
    
# =========================================================
# 6. [Agent 3-2] 감성 키워드 추출 (Gemma3) - (수정: JSON 모드)
# =========================================================
def extract_keywords(merged_text: str, k: int = 3) -> list[str]:
    if not merged_text.strip():
        return []
    print("💬 [Agent 3] Extracting mood keywords (Ollama w/ JSON)...")

    prompt_content = f"""
From the text below, extract exactly {k} keywords that **best describe and are most relevant to** the core mood, atmosphere, or genre.
Text:
"{merged_text}"
"""
    system_prompt = """
You are an expert keyword extractor.
Respond *only* with a valid JSON object in this format:
{"keywords": ["keyword1", "keyword2", "keyword3"]}
"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt_content}
    ]
    payload = {"model": GEMMA3_MODEL, "messages": messages, "stream": False, "format": "json"}
    try:
        res = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=60)
        res.raise_for_status()

        # ✅ Ollama 응답 구조 대응
        raw_output = (
            res.json().get("message", {}).get("content")
            or res.json().get("response")
            or ""
        ).strip()

        try:
            parsed_data = json.loads(raw_output)
            keywords = parsed_data.get("keywords", [])
        except json.JSONDecodeError:
            print(f"⚠️ JSON parsing failed. Raw: {raw_output}")
            raw = re.sub(r"[^a-zA-Z,\n ]", "", raw_output)
            keywords = [w.strip().lower() for w in re.split(r"[, \n]+", raw) if w.strip()]

        # ✅ 필터링 및 상한 제한
        keywords = [w for w in keywords if 2 <= len(w) <= 15][:k]
        print(f"🪶 Extracted keywords → {keywords}")
        return keywords

    except Exception as e:
        print(f"🔥 Keyword extraction failed: {e}")
        return []
    
# =========================================================
# 8. 세션 저장
# =========================================================
def save_to_session_simple(data: dict, session_file: str):
    """
    지정된 세션 JSON 파일을 안전하게 열고, 데이터를 append합니다.
    파일이 없으면 새로 생성합니다.
    """
    default_structure = {
        "session_name": os.path.basename(session_file).replace(".json", ""),
        "session_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_korean": [], "input_image": [],
        "english_text_from_agent1": [], "english_caption_from_agent2": [],
        "merged_sentence": [], "english_keywords": []
    }
    
    if os.path.exists(session_file):
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)
            for key, default_value in default_structure.items():
                if key not in session_data:
                    session_data[key] = default_value
        except json.JSONDecodeError:
            print(f"⚠️ 세션 파일이 손상되어 새로 만듭니다: {session_file}")
            session_data = default_structure
    else:
        session_data = default_structure

    try:
        session_data["input_korean"].append(data["input"]["korean_text"])
        session_data["input_image"].append(data["input"]["image_path"])
        session_data["english_text_from_agent1"].append(data["english_text_from_agent1"])
        session_data["english_caption_from_agent2"].append(data["english_caption_from_agent2"])
        session_data["merged_sentence"].append(data["merged_sentence"])
        session_data["english_keywords"].append(data["english_keywords"])
        # session_data["korean_keywords"].append(data["korean_keywords"])
    except KeyError as e:
        print(f"🔥 데이터 저장 중 치명적인 Key Error 발생: {e}")
        return

    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

# =========================================================
# 9. 전체 실행 파이프라인
# =========================================================
def run_agent_pipeline(korean_text="", image_path="") -> dict:
    """
(수정) 'active_session.json'에서 '전체 이력'을 로드한 후 파이프라인을 실행합니다.
    """
    
    # --- [수정] 1. RAG: 전체 대화 이력 로드 ---
    session_file_path = os.path.join(SAVE_DIR, "active_session.json")
    full_history = get_full_conversation_history(session_file_path)
    
    # [Agent 1]
    english_text = korean_to_english(korean_text) if korean_text else ""
    # [Agent 2]
    english_caption = image_to_english_caption(image_path) if image_path else ""
    # [Agent 3-1]
    merged = rewrite_combined_sentence(english_text, english_caption, full_history)    # [Agent 3-2]
    # [Agent 3-2]: 영어 키워드 추출
    eng_keywords = extract_keywords(merged, k=3)
    
    session_file_path = os.path.join(SAVE_DIR, "active_session.json")

    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input": {"korean_text": korean_text, "image_path": image_path},
        "english_text_from_agent1": english_text,
        "english_caption_from_agent2": english_caption,
        "merged_sentence": merged,
        "english_keywords": eng_keywords,
    }

    session_file_path = os.path.join(SAVE_DIR, "active_session.json")
    save_to_session_simple(data, session_file_path)
    
    print(f"\n✅ Saved to active session → {session_file_path}")
    return data

# =========================================================
# 10. CLI (세션 관리자)
# =========================================================
if __name__ == "__main__":
    print("\n🤖 Agent Pipeline (세션형 실행)")
    
    active_session_path = os.path.join(SAVE_DIR, "active_session.json")
    choice = input("\n새 대화를 시작하려면 'new' 입력 (기존 대화 이어하기는 Enter): ").strip().lower()

    if choice == "new":
        if os.path.exists(active_session_path):
            try:
                with open(active_session_path, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                start_time_str = old_data.get("session_start", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                ts = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S").strftime('%Y%m%d_%H%M%S')
                archive_name = f"session_{ts}.json"
            except Exception as e:
                archive_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_corrupted.json"
            
            archive_path = os.path.join(SAVE_DIR, archive_name)
            os.rename(active_session_path, archive_path)
            print(f"   -> 🗂️  기존 대화({active_session_path.split('/')[-1]})를 '{archive_name}'(으)로 보관합니다.")
            
        print(f"   -> 🆕 새 대화({active_session_path.split('/')[-1]})를 시작합니다.")
        
    else:
        print(f"   -> ➡️  기존 대화({active_session_path.split('/')[-1]})에 이어합니다.")
        if not os.path.exists(active_session_path):
            print("      (기존 파일이 없어 새로 시작합니다)")

    print("\n--- 💬 입력을 시작하세요 ---")
    text = input("한국어 텍스트 입력 (없으면 Enter): ").strip()
    img = input("이미지 파일 경로 입력 (없으면 Enter): ").strip()

    if not text and not img:
        print("\n🛑 입력이 없어 종료합니다.")
        exit()

    print("\n--- 🚀 에이전트 파이프라인 실행 ---")
    try:
        result = run_agent_pipeline(text, img) 
        print("\n--- 🎯 실행 결과 ---")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"\n🔥🔥🔥 파이프라인 실행 중 심각한 오류 발생: {e}")
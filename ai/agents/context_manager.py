# active_session.json 현재 대화 이력 기억
# -*- coding: utf-8 -*-
"""
context_manager.py
- 'active_session.json' 파일을 읽어옵니다.
- Agent 3가 키워드를 추출할 때 참고할 수 있도록,
  '전체 대화 이력'을 하나의 문자열로 생성하여 제공합니다.
"""

import os
import json

def get_full_conversation_history(session_file: str) -> str:
    """
    세션 JSON을 불러와, 'merged_sentence'와 'english_keywords'를 조합하여
    지금까지의 전체 대화 이력 문자열을 생성합니다.
    
    Returns:
        "No past conversation history." 또는
        "- Turn 1: ... (Keywords: ...)
         - Turn 2: ... (Keywords: ...)"
    """
    if not os.path.exists(session_file):
        return "No past conversation history."

    try:
        with open(session_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        merged_sentences = data.get("merged_sentence", [])
        eng_keywords_list = data.get("english_keywords", [])
        
        if not merged_sentences:
            return "No past conversation history."
        
        full_history = []
        # JSON에 저장된 모든 대화 턴을 순회
        for i, sentence in enumerate(merged_sentences):
            turn_context = f"- Turn {i+1}: {sentence}"
            
            # 해당 턴에 키워드가 정상적으로 저장되었다면
            if i < len(eng_keywords_list) and eng_keywords_list[i]:
                kws = ", ".join(eng_keywords_list[i])
                turn_context += f" (Extracted Keywords: {kws})"
                
            full_history.append(turn_context)
            
        print(f"🔄 [Context] Loaded {len(full_history)} past turn(s).")
        return "\n".join(full_history)
        
    except Exception as e:
        print(f"⚠️ Failed to load conversation history: {e}")
        return "Error loading history."

# (RAG 검색, 노래 추천 등 나머지 함수는 모두 삭제)
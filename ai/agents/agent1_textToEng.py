from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# =========================================================
# 1. 모델 로드 (EXAONE)
# =========================================================
MODEL_NAME = "LGAI-EXAONE/EXAONE-4.0-1.2B"

print("🚀 Loading EXAONE model for Korean→English translation...")

# EXAONE 모델 및 토크나이저 로드
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

print("✅ Model loaded successfully!")

# =========================================================
# 2. 변환 함수 정의
# =========================================================
def korean_to_english(text_ko: str, max_new_tokens: int = 256) -> str:
    """
    한국어 텍스트를 자연스러운 영어 문장으로 변환하는 함수.
    """
    if not text_ko.strip():
        return ""

    # EXAONE에 전달할 명령어 (prompt)
    prompt = (
        "Convert the following Korean sentence into one natural English sentence. "
        "Do not include explanations or translations in parentheses. "
        "Output only the final English sentence.\n\n"
        f"Korean: {text_ko}"
    )

    # 대화 메시지 형식으로 구성
    messages = [{"role": "user", "content": prompt}]

    # Chat 템플릿 적용 (EXAONE 전용)
    input_ids = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
        enable_thinking=False,  # 추론 모드 끔
    ).to(model.device)

    # 모델로 생성 실행
    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=False
        )

    # 토큰 디코딩
    full_text = tokenizer.decode(output[0], skip_special_tokens=True)
    # 마지막 줄만 남기기 (Assistant 응답)
    english_sentence = full_text.split("\n")[-1].strip()

    return english_sentence

# =========================================================
# 3. 테스트 실행
# =========================================================
if __name__ == "__main__":
    try:
        text_ko = input("\n한국어 문장을 입력하세요: ").strip()
        if not text_ko:
            print("❌ 입력이 비어 있습니다.")
        else:
            result = korean_to_english(text_ko)
            print("\n🌍 변환된 영어 문장:")
            print(result)
    except KeyboardInterrupt:
        print("\n🛑 프로그램 종료됨.")
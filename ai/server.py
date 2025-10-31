from flask import Flask, request, jsonify
from ollama_client import query_ollama
from agent2_imageToEng import extract_image_features
from agent3_keywordExtractor import extract_keywords
from agent1_exaone import generate_music_recommendation

app = Flask(__name__)

@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    text = data.get("inputText", "")
    image_urls = data.get("imageUrls", [])
    topic = data.get("topic", "")

    # 1️⃣ 이미지 분석 → 감정 feature 추출
    image_features = extract_image_features(image_urls)

    # 2️⃣ Ollama로 키워드 생성 (agent3 내부에서도 호출 가능)
    prompt = f"문장과 이미지 묘사를 바탕으로 음악 추천용 감성 키워드 3개를 영어로 생성해줘.\n\n문장: {text}\n이미지: {image_features}"
    keywords_text = query_ollama(prompt)
    keywords = [k.strip() for k in keywords_text.split(",") if k.strip()]

    # 3️⃣ 음악 추천
    recs = generate_music_recommendation(keywords)

    return jsonify({
        "sessionId": data.get("sessionId"),
        "topic": topic,
        "aiMessage": f"'{topic}' 감성에 어울리는 음악을 추천합니다.",
        "keywords": keywords,
        "recommendations": recs
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

package com.wink.backend.service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;
import java.net.http.*;
import java.net.URI;
import java.time.Duration;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class GeminiService {

    private static final String GEMINI_MODEL = "gemini-2.0-flash-exp";
    private static final String GEMINI_URL =
        "https://generativelanguage.googleapis.com/v1beta/models/" + GEMINI_MODEL + ":generateContent";

    @Value("${GEMINI_API_KEY:#{null}}") // 환경변수나 application.properties에서 가져옴
    private String apiKey;

    private static final ObjectMapper mapper = new ObjectMapper();

    /**
     * API 키와 URL 상태를 로그로 출력하는 테스트 메서드
     * Spring Boot 실행 시 호출해도 무방
     */
    public void checkApiConnection() {
        System.out.println("--------------------------------------------------");
        System.out.println("🔍 Gemini API 연결 상태 확인");
        System.out.println("📡 엔드포인트 URL: " + GEMINI_URL);
        if (apiKey == null || apiKey.isBlank()) {
            System.out.println("❌ GEMINI_API_KEY 인식 안 됨 (환경변수 또는 properties 확인 필요)");
        } else {
            System.out.println("✅ GEMINI_API_KEY 인식됨 (길이: " + apiKey.length() + "자)");
        }
        System.out.println("--------------------------------------------------");
    }

    /**
     * 입력 텍스트로부터 핵심 주제(topic) 도출
     */
    public String extractTopic(String inputText) {
        try {
            // API 키 확인
            if (apiKey == null || apiKey.isBlank()) {
                System.err.println("❌ GEMINI_API_KEY is not set. Using fallback.");
                return fallbackTopic(inputText);
            }

            // 프롬프트 구성
            String prompt = "다음 문장의 핵심 주제를 한 문장으로 요약해줘. " + "꼭 필요한 문장 기호가 아닌 이상 넣지 마." +
                    "음악 분위기나 상황 중심으로 간결하게 표현해줘. 문장: \"" + inputText + "\"";

            // JSON 요청 본문
            String requestBody = String.format("""
                {
                  "contents": [{
                    "parts": [{"text": "%s"}]
                  }]
                }
            """, prompt.replace("\"", "'")); // 큰따옴표 escape

            // HTTP 클라이언트 생성
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(GEMINI_URL + "?key=" + apiKey))
                    .timeout(Duration.ofSeconds(10))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                    .build();

            // API 호출
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

            System.out.println("📨 Gemini 요청: " + prompt);
            System.out.println("✅ Gemini 응답 코드: " + response.statusCode());
            System.out.println("✅ Gemini 응답 본문: " + response.body());

            if (response.statusCode() != 200) {
                System.err.println("⚠️ Gemini API 호출 실패 (" + response.statusCode() + ")");
                return fallbackTopic(inputText);
            }

            // JSON 파싱
            JsonNode root = mapper.readTree(response.body());
            JsonNode textNode = root.path("candidates").get(0)
                    .path("content").path("parts").get(0).path("text");

            if (textNode.isMissingNode() || textNode.asText().isBlank()) {
                System.err.println("⚠️ Gemini 응답에 주제 텍스트 없음");
                return fallbackTopic(inputText);
            }

            return textNode.asText().trim();

        } catch (Exception e) {
            e.printStackTrace();
            return fallbackTopic(inputText);
        }
    }

    /**
     * Gemini API 실패 시 간단한 규칙 기반 주제 추출
     */
    private String fallbackTopic(String text) {
        text = text == null ? "" : text;

        if (text.contains("비")) return "비 오는 날 감성";
        if (text.contains("집중")) return "집중용 재즈";
        if (text.contains("산책")) return "산책할 때 듣는 음악";
        if (text.contains("퇴근")) return "퇴근길 플레이리스트";
        if (text.contains("밤")) return "밤 감성 음악";
        if (text.contains("사랑")) return "로맨틱한 분위기 음악";

        return "오늘의 감성 음악";
    }
}

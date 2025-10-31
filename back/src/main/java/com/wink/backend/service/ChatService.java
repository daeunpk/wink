package com.wink.backend.service;

import com.wink.backend.dto.*;
import com.wink.backend.entity.ChatMessage;
import com.wink.backend.entity.ChatSession;
import com.wink.backend.repository.ChatMessageRepository;
import com.wink.backend.repository.ChatSessionRepository;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.time.LocalDateTime;
import java.util.stream.Collectors;
import java.util.*;

@Service
public class ChatService {

    private final ChatSessionRepository sessionRepo;
    private final GeminiService geminiService;
    private final ChatMessageRepository messageRepo;

    public ChatService(ChatSessionRepository sessionRepo,
                    GeminiService geminiService,
                    ChatMessageRepository messageRepo) {
        this.sessionRepo = sessionRepo;
        this.geminiService = geminiService;
        this.messageRepo = messageRepo;
    }

    // 나의 순간
    public ChatStartResponse startMy(ChatStartMyRequest req) {
        ChatSession session = new ChatSession();
        session.setType("MY");
        session.setStartTime(LocalDateTime.now());

        // 프롬프트 구성: 텍스트 + 이미지 URL을 함께 전달
        StringBuilder prompt = new StringBuilder(req.getInputText());
        if (req.getImageUrls() != null && !req.getImageUrls().isEmpty()) {
            prompt.append(" (참고 이미지: ");
            prompt.append(String.join(", ", req.getImageUrls()));
            prompt.append(")");
        }


        // Gemini API로 주제 추출
        String topic = geminiService.extractTopic(prompt.toString());
        session.setTopic(topic);
        sessionRepo.save(session);

        return new ChatStartResponse(
                session.getId(),
                session.getType(),
                session.getTopic(),
                "Gemini API 기반 주제 추출 완료",
                session.getStartTime()
        );
    }

    // 공간의 순간
    public ChatStartResponse startSpace(ChatStartSpaceRequest req) {
        ChatSession session = new ChatSession();
        session.setType("SPACE");
        session.setStartTime(LocalDateTime.now());

        // 주변 음악 요약
        String nearbySummary = "";
        if (req.getNearbyMusic() != null && !req.getNearbyMusic().isEmpty()) {
            nearbySummary = req.getNearbyMusic().stream()
                    .map(m -> m.getTitle() + " - " + m.getArtist())
                    .collect(Collectors.joining(", "));
        }

        // AI 프롬프트 구성
        String prompt = String.format(
                "📍장소명: %s (%s, %.4f, %.4f)\n" +
                "🎧 주변 음악: %s\n" +
                "이 장소의 분위기와 어울리는 음악적 주제를 한 문장으로 요약해줘.",
                req.getLocation().getPlaceName(),
                req.getLocation().getAddress(),
                req.getLocation().getLat(),
                req.getLocation().getLng(),
                nearbySummary.isBlank() ? "정보 없음" : nearbySummary
        );

        // Gemini 호출
        String topic = geminiService.extractTopic(prompt);
        session.setTopic(topic);
        sessionRepo.save(session);

        return new ChatStartResponse(
                session.getId(),
                session.getType(),
                session.getTopic(),
                "Gemini API 기반 공간 주제 생성 완료",
                session.getStartTime()
        );
    }

    // !!!!!나중에 은정이랑 연결할 부분!!!!!
    public AiResponseResponse generateAiResponse(AiResponseRequest req) {
        try {
            Long sessionId = req.getSessionId();
            ChatSession session = sessionRepo.findById(sessionId)
                    .orElseThrow(() -> new RuntimeException("Session not found: " + sessionId));

            // topic 재추출 금지 (이미 세션 생성 시 추출됨)
            String topic = session.getTopic();

            // AI 추천 서버에 전달할 요청 구성
            String aiServerUrl = "http://localhost:5001/api/recommend"; // ← 실제 AI 서버 주소로 변경 가능
            ObjectMapper mapper = new ObjectMapper();
            RestTemplate restTemplate = new RestTemplate();

            Map<String, Object> payload = new HashMap<>();
            payload.put("sessionId", sessionId);
            payload.put("topic", topic);
            payload.put("inputText", req.getInputText());
            payload.put("imageUrls", req.getImageUrls());

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(payload, headers);
            ResponseEntity<String> response = restTemplate.exchange(
                    aiServerUrl,
                    HttpMethod.POST,
                    entity,
                    String.class
            );

            try {
                ChatMessage userMsg = new ChatMessage();
                userMsg.setSession(session);
                userMsg.setSender("user");
                userMsg.setText(req.getInputText());

                // 이미지가 여러 개인 경우 JSON 문자열로 병합
                if (req.getImageUrls() != null && !req.getImageUrls().isEmpty()) {
                    userMsg.setImageUrl(String.join(",", req.getImageUrls()));
                }

                messageRepo.save(userMsg);
                System.out.println("💾 사용자 메시지 저장 완료 (messageId=" + userMsg.getId() + ")");
            } catch (Exception ex) {
                ex.printStackTrace();
                System.err.println("⚠️ 사용자 메시지 저장 중 오류 발생: " + ex.getMessage());
            }

            // AI 서버 응답 파싱
            if (response.getStatusCode() == HttpStatus.OK) {
                JsonNode root = mapper.readTree(response.getBody());

                List<String> keywords = mapper.convertValue(
                        root.path("keywords"),
                        mapper.getTypeFactory().constructCollectionType(List.class, String.class)
                );

                List<AiResponseResponse.Recommendation> recs = new ArrayList<>();
                for (JsonNode songNode : root.path("recommendations")) {
                    recs.add(AiResponseResponse.Recommendation.builder()
                            .songId(songNode.path("songId").asLong())
                            .title(songNode.path("title").asText())
                            .artist(songNode.path("artist").asText())
                            .albumCover(songNode.path("albumCover").asText())
                            .previewUrl(songNode.path("previewUrl").asText())
                            .build());
                }

                 String aiMessage = root.path("aiMessage").asText("AI 추천 결과입니다.");

                try {
                    ChatMessage aiMsg = new ChatMessage();
                    aiMsg.setSession(session);
                    aiMsg.setSender("ai");
                    aiMsg.setText(aiMessage);

                    aiMsg.setKeywordsJson(mapper.writeValueAsString(keywords));
                    aiMsg.setRecommendationsJson(mapper.writeValueAsString(recs));

                    messageRepo.save(aiMsg);

                    System.out.println("💾 AI 메시지 저장 완료 (messageId=" + aiMsg.getId() + ")");
                } catch (Exception ex) {
                    ex.printStackTrace();
                    System.err.println("⚠️ AI 메시지 저장 중 오류 발생: " + ex.getMessage());
                }

                return AiResponseResponse.builder()
                        .sessionId(sessionId)
                        .topic(topic)
                        .keywords(keywords)
                        .aiMessage(root.path("aiMessage").asText("AI 추천 결과입니다."))
                        .recommendations(recs)
                        .timestamp(LocalDateTime.now())
                        .build();
            }

            throw new RuntimeException("AI server returned " + response.getStatusCode());

        } catch (Exception e) {
            e.printStackTrace();
            return AiResponseResponse.builder()
                    .sessionId(req.getSessionId())
                    .topic("추천 생성 실패")
                    .keywords(List.of("error"))
                    .aiMessage("AI 추천 서버와 통신 중 오류가 발생했습니다.")
                    .recommendations(List.of())
                    .timestamp(LocalDateTime.now())
                    .build();
        }
    }

    public ChatHistoryResponse getMyChatHistory(Long sessionId) {
        ChatSession session = sessionRepo.findById(sessionId)
                .orElseThrow(() -> new RuntimeException("Session not found: " + sessionId));

        List<ChatMessage> messages = messageRepo.findBySessionIdOrderByCreatedAtAsc(sessionId);

        List<ChatMessageResponse> messageResponses = messages.stream().map(msg -> {
            List<String> keywords = new ArrayList<>();
            List<AiResponseResponse.Recommendation> recs = new ArrayList<>();

            try {
                ObjectMapper mapper = new ObjectMapper();
                if (msg.getKeywordsJson() != null)
                    keywords = mapper.readValue(msg.getKeywordsJson(), List.class);
                if (msg.getRecommendationsJson() != null)
                    recs = Arrays.asList(mapper.readValue(msg.getRecommendationsJson(),
                            AiResponseResponse.Recommendation[].class));
            } catch (Exception ignored) {}

            return ChatMessageResponse.builder()
                    .messageId(msg.getId())
                    .sender(msg.getSender())
                    .text(msg.getText())
                    .keywords(keywords)
                    .recommendations(recs)
                    .timestamp(msg.getCreatedAt())
                    .build();
        }).toList();

        return ChatHistoryResponse.builder()
                .sessionId(session.getId())
                .type(session.getType())
                .topic(session.getTopic())
                .messages(messageResponses)
                .build();
    }
}

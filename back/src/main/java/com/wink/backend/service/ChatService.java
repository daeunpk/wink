package com.wink.backend.service;

import com.wink.backend.dto.ChatStartMyRequest;
import com.wink.backend.dto.ChatStartResponse;
import com.wink.backend.entity.ChatSession;
import com.wink.backend.repository.ChatSessionRepository;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;

@Service
public class ChatService {

    private final ChatSessionRepository sessionRepo;
    private final GeminiService geminiService;

    public ChatService(ChatSessionRepository sessionRepo, GeminiService geminiService) {
        this.sessionRepo = sessionRepo;
        this.geminiService = geminiService;
    }

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
}

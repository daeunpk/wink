package com.wink.backend.service;

import com.wink.backend.entity.ChatSession;
import com.wink.backend.repository.ChatSessionRepository;
import org.springframework.stereotype.Service;

@Service
public class ChatService {

    private final ChatSessionRepository chatRepo;

    public ChatService(ChatSessionRepository chatRepo) {
        this.chatRepo = chatRepo;
    }

    public ChatSession createMySession(String text) {
        String topic = generateTopic(text);

        ChatSession session = new ChatSession();
        session.setType("MY");
        session.setTopic(topic);
        session.setMessage("Session created with AI-generated topic.");

        return chatRepo.save(session);
    }

    private String generateTopic(String text) {
        if (text.contains("비")) return "비 오는 밤 집중용 재즈";
        return "새로운 감성 추천";
    }
}

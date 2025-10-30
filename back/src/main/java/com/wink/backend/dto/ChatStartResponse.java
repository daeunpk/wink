package com.wink.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ChatStartResponse {
    private Long sessionId;
    private String type;
    private String topic;
    private String message;
    private LocalDateTime timestamp;

    // 👇 추가: 3개 인자만 받는 보조 생성자 (ChatController용)
    public ChatStartResponse(Long sessionId, String type, String topic) {
        this.sessionId = sessionId;
        this.type = type;
        this.topic = topic;
        this.message = "Session created successfully";
        this.timestamp = LocalDateTime.now();
    }
}

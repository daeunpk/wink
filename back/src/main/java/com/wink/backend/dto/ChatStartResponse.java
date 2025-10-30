// src/main/java/com/wink/backend/dto/ChatStartResponse.java
package com.wink.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
@AllArgsConstructor
public class ChatStartResponse {
    private Long sessionId;
    private String type;
    private String topic;
    private String message;
    private LocalDateTime timestamp;
}

package com.wink.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@AllArgsConstructor
public class ChatStartResponse {
    private Long sessionId;
    private String type;
    private String topic;
    private String message;
    private LocalDateTime startTime;
}

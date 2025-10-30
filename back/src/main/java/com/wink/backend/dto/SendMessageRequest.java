package com.wink.backend.dto;

import lombok.Data;

@Data
public class SendMessageRequest {
    private Long sessionId;
    private String sender;
    private String text;
    private String imageUrl;
}

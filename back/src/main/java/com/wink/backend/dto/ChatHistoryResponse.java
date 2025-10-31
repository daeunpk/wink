package com.wink.backend.dto;

import lombok.*;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatHistoryResponse {
    private Long sessionId;
    private String type;
    private String topic;
    private List<ChatMessageResponse> messages;
}

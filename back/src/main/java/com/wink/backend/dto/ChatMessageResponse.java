package com.wink.backend.dto;

import lombok.*;
import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatMessageResponse {
    private Long messageId;
    private String sender;
    private String text;
    private List<String> keywords;
    private List<AiResponseResponse.Recommendation> recommendations;
    private LocalDateTime timestamp;
}

package com.wink.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import java.time.LocalDateTime;
import java.util.List;

@Data
@AllArgsConstructor
@Builder
public class AiResponseResponse {
    private Long sessionId;
    private String topic;
    private List<String> keywords;
    private String aiMessage;
    private List<Recommendation> recommendations;
    private LocalDateTime timestamp;

    @Data
    @AllArgsConstructor
    @Builder
    public static class Recommendation {
        private Long songId;
        private String title;
        private String artist;
        private String albumCover;
        private String previewUrl;
    }
}

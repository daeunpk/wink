package com.wink.backend.dto;

import lombok.Getter;
import lombok.Setter;
import java.util.List;

@Getter
@Setter
public class AiResponsePayload {

    private Long sessionId;          // 세션 ID
    private String summary;          // 요약된 주제
    private List<String> keywords;   // 키워드 리스트
    private List<Song> recommendations; // 추천된 노래 리스트

    @Getter
    @Setter
    public static class Song {
        private String title;       // 노래 제목
        private String artist;      // 가수 이름
        private String albumCover;  // 앨범 커버 이미지 URL
        private String previewUrl;  // 미리듣기 URL
        private Integer rank;       // 순위 (옵션)
    }
}

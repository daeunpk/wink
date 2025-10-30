package com.wink.backend.dto;

import lombok.Getter;
import lombok.Setter;
import java.util.List;

@Getter
@Setter
public class ChatStartSpaceRequest {

    private String spaceImageUrl;           // 지도나 배경 이미지 URL
    private Location location;              // 위치 정보
    private List<MusicInfo> nearbyMusic;    // 주변 음악 리스트

    @Getter
    @Setter
    public static class Location {
        private double latitude;     // 위도
        private double longitude;    // 경도
        private String address;      // 주소
        private String placeName;    // 장소명
    }

    @Getter
    @Setter
    public static class MusicInfo {
        private Long songId;         // 음악 ID
        private String title;        // 제목
        private String artist;       // 아티스트
    }
}

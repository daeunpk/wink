package com.wink.backend.dto;

import lombok.Data;
import java.util.List;

@Data
public class ChatStartSpaceRequest {
    private String imageUrl;

    private Location location;
    private List<NearbyMusic> nearbyMusic;

    @Data
    public static class Location {
        private double lat;
        private double lng;
        private String address;
        private String placeName;
    }

    @Data
    public static class NearbyMusic {
        private Long songId;
        private String title;
        private String artist;
    }
}

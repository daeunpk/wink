package com.wink.backend.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter @Setter
public class AiRecommendationSong {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 어떤 AI 추천 묶음에 속한 곡인지
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "recommendation_id")
    private AiRecommendation recommendation;

    private Long songId;       // 시스템 곡 ID(있으면)
    private String title;
    private String artist;
    private String albumCover;
    private String previewUrl;

    private Integer rankNo;    // 추천 순위
}

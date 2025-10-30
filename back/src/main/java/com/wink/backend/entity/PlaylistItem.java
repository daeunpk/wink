package com.wink.backend.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter @Setter
public class PlaylistItem {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 소속 플레이리스트
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "playlist_id")
    private Playlist playlist;

    // 노래 기본 정보
    private Long songId;          // 외부/내부 곡 ID (옵션)
    private String title;
    private String artist;
    private String albumCover;
    private String previewUrl;

    private Integer orderNo;      // 재생 순서
}

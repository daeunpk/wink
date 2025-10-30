// entity/AiRecommendationSong.java
package com.wink.backend.entity;

import jakarta.persistence.*;

@Entity @Table(name="ai_recommendation_song")
public class AiRecommendationSong {
  @Id @GeneratedValue(strategy=GenerationType.IDENTITY)
  private Long id;

  @ManyToOne(fetch=FetchType.LAZY) @JoinColumn(name="rec_id", nullable=false)
  private AiRecommendation recommendation;

  private Long songId; // nullable
  @Column(nullable=false) private String title;
  @Column(nullable=false) private String artist;
  private String albumCover; private String previewUrl;
  @Column(name="rank_no", nullable=false) private Integer rankNo;

  public AiRecommendationSong(){}
  // getters/setters ...
}

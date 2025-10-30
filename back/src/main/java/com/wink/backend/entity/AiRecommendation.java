// entity/AiRecommendation.java
package com.wink.backend.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity @Table(name="ai_recommendation")
public class AiRecommendation {
  @Id @GeneratedValue(strategy=GenerationType.IDENTITY)
  private Long id;

  @OneToOne @JoinColumn(name="session_id", nullable=false, unique=true)
  private ChatSession session;

  @Column(columnDefinition="TEXT") private String summary;
  @Column(name="keywords_json", columnDefinition="JSON") private String keywordsJson;
  @Column(nullable=false) private LocalDateTime createdAt = LocalDateTime.now();

  public AiRecommendation(){}
  // getters/setters ...
}

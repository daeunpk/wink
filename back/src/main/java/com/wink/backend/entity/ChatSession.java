// entity/ChatSession.java
package com.wink.backend.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity @Table(name="chat_session")
public class ChatSession {
  @Id @GeneratedValue(strategy=GenerationType.IDENTITY)
  private Long id;
  @Column(nullable=false, length=20) private String type;
  @Column(nullable=false, length=255) private String topic;
  @Column(name="created_at", nullable=false) private LocalDateTime createdAt = LocalDateTime.now();

  public ChatSession() {}
  public Long getId(){return id;} public void setId(Long id){this.id=id;}
  public String getType(){return type;} public void setType(String type){this.type=type;}
  public String getTopic(){return topic;} public void setTopic(String topic){this.topic=topic;}
  public LocalDateTime getCreatedAt(){return createdAt;} public void setCreatedAt(LocalDateTime t){this.createdAt=t;}
}

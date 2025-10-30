// entity/ChatMessage.java
package com.wink.backend.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity @Table(name="chat_message")
public class ChatMessage {
  @Id @GeneratedValue(strategy=GenerationType.IDENTITY)
  private Long id;

  @ManyToOne(fetch=FetchType.LAZY) @JoinColumn(name="session_id", nullable=false)
  private ChatSession session;

  @Column(nullable=false, length=10) private String sender; // user/ai
  @Column(columnDefinition="TEXT") private String text;
  private String imageUrl;
  @Column(nullable=false) private LocalDateTime createdAt = LocalDateTime.now();

  public ChatMessage() {}
  // getters/setters ...
  public Long getId(){return id;} public void setId(Long id){this.id=id;}
  public ChatSession getSession(){return session;} public void setSession(ChatSession s){this.session=s;}
  public String getSender(){return sender;} public void setSender(String s){this.sender=s;}
  public String getText(){return text;} public void setText(String t){this.text=t;}
  public String getImageUrl(){return imageUrl;} public void setImageUrl(String i){this.imageUrl=i;}
  public LocalDateTime getCreatedAt(){return createdAt;} public void setCreatedAt(LocalDateTime t){this.createdAt=t;}
}

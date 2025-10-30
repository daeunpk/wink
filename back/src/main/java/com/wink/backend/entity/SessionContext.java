// entity/SessionContext.java
package com.wink.backend.entity;

import jakarta.persistence.*;

@Entity @Table(name="session_context")
public class SessionContext {
  @Id @GeneratedValue(strategy=GenerationType.IDENTITY)
  private Long id;

  @OneToOne @JoinColumn(name="session_id", nullable=false, unique=true)
  private ChatSession session;

  private String imageUrl;
  private Double lat; private Double lng;
  private String address; private String placeName;

  public SessionContext(){}
  // getters/setters ...
}

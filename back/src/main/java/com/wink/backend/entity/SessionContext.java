package com.wink.backend.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import java.time.LocalDateTime;

@Entity
@Getter
@Setter
public class SessionContext {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne
    private ChatSession session;

    private Double lat;
    private Double lng;
    private String address;
    private String placeName;
    private String imageUrl;

    private LocalDateTime createdAt = LocalDateTime.now();
}

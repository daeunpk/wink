package com.wink.backend.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ChatSession {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String type; // "MY" or "SPACE"
    private String topic;

    private LocalDateTime startTime;  // ✅ 추가
    private LocalDateTime endTime;

    // optional: 세션이 생성될 때 기본값 지정
    @PrePersist
    public void onCreate() {
        this.startTime = LocalDateTime.now();
    }
}

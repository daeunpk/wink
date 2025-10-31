package com.wink.backend.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "chat_message")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ChatMessage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id", nullable = false)
    private ChatSession session;

    @Column(nullable = false, length = 10)
    private String sender; // user / ai

    @Column(columnDefinition = "TEXT")
    private String text;

    private String imageUrl;

    // ✅ AI 추천 관련 확장 필드 (옵션)
    @Lob
    private String keywordsJson;  // ["calm", "sentimental", "earthytone"]

    @Lob
    private String recommendationsJson; // 추천곡 JSON 배열 전체 문자열

    @Column(nullable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    @PrePersist
    public void onCreate() {
        if (createdAt == null)
            createdAt = LocalDateTime.now();
    }
}

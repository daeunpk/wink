package com.wink.backend.repository;

import com.wink.backend.entity.AiRecommendation;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AiRecommendationRepository extends JpaRepository<AiRecommendation, Long> {
    AiRecommendation findBySession_Id(Long sessionId);
}

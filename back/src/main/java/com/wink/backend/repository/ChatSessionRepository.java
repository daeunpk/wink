package com.wink.backend.repository;

import com.wink.backend.entity.*;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ChatSessionRepository extends JpaRepository<ChatSession, Long> {}
public interface ChatMessageRepository extends JpaRepository<ChatMessage, Long> {}
public interface SessionContextRepository extends JpaRepository<SessionContext, Long> {}
public interface AiRecommendationRepository extends JpaRepository<AiRecommendation, Long> {
  AiRecommendation findBySession_Id(Long sessionId);
}
public interface AiRecommendationSongRepository extends JpaRepository<AiRecommendationSong, Long> {}
public interface PlaylistRepository extends JpaRepository<Playlist, Long> {}
public interface PlaylistItemRepository extends JpaRepository<PlaylistItem, Long> {}

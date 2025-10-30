package com.wink.backend.service;

import com.wink.backend.dto.AiResponsePayload;
import com.wink.backend.dto.ChatStartMyRequest;
import com.wink.backend.dto.ChatStartSpaceRequest;
import com.wink.backend.entity.*;
import com.wink.backend.repository.*;
import com.wink.backend.util.JsonUtil;
import org.springframework.stereotype.Service;
import lombok.RequiredArgsConstructor;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class ChatService {

    private final ChatSessionRepository sessionRepo;
    private final ChatMessageRepository messageRepo;
    private final SessionContextRepository contextRepo;
    private final AiRecommendationRepository recRepo;
    private final AiRecommendationSongRepository recSongRepo;

    private final TopicGenerator topicGen = new TopicGenerator();

    /**
     * 나의 순간 새 채팅 시작
     */
    public ChatSession startMy(ChatStartMyRequest req) {
        String topic = topicGen.fromText(req.getText());
        ChatSession session = new ChatSession();
        session.setType("MY");
        session.setTopic(topic);
        session.setCreatedAt(LocalDateTime.now());
        sessionRepo.save(session);

        ChatMessage msg = new ChatMessage();
        msg.setSession(session);
        msg.setSender("user");
        msg.setText(req.getText());
        msg.setCreatedAt(LocalDateTime.now());
        messageRepo.save(msg);

        return session;
    }

    /**
     * 공간의 순간 새 채팅 시작
     */
    public ChatSession startSpace(ChatStartSpaceRequest req) {
        String topic = topicGen.fromText("space:" +
                (req.getLocation() != null ? req.getLocation().getPlaceName() : ""));

        ChatSession session = new ChatSession();
        session.setType("SPACE");
        session.setTopic(topic);
        session.setCreatedAt(LocalDateTime.now());
        sessionRepo.save(session);

        SessionContext ctx = new SessionContext();
        ctx.setSession(session);
        if (req.getLocation() != null) {
            ctx.setLat(req.getLocation().getLatitude());
            ctx.setLng(req.getLocation().getLongitude());
            ctx.setAddress(req.getLocation().getAddress());
            ctx.setPlaceName(req.getLocation().getPlaceName());
        }
        ctx.setImageUrl(req.getSpaceImageUrl());
        contextRepo.save(ctx);

        return session;
    }

    /**
     * AI 응답 저장
     */
    public void saveAiResponse(AiResponsePayload payload) {
        ChatSession session = sessionRepo.findById(payload.getSessionId())
                .orElseThrow(() -> new RuntimeException("Session not found"));

        AiRecommendation rec = new AiRecommendation();
        rec.setSession(session);
        rec.setSummary(payload.getSummary());
        rec.setKeywordsJson(JsonUtil.toJson(payload.getKeywords()));
        rec.setCreatedAt(LocalDateTime.now());
        recRepo.save(rec);

        int rank = 1;
        if (payload.getRecommendations() != null) {
            for (AiResponsePayload.Song s : payload.getRecommendations()) {
                AiRecommendationSong rs = new AiRecommendationSong();
                rs.setRecommendation(rec);
                rs.setTitle(s.getTitle());
                rs.setArtist(s.getArtist());
                rs.setAlbumCover(s.getAlbumCover());
                rs.setPreviewUrl(s.getPreviewUrl());
                rs.setRankNo(s.getRank() != null ? s.getRank() : rank++);
                recSongRepo.save(rs);
            }
        }
    }
}

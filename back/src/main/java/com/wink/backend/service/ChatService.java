// service/ChatService.java
package com.wink.backend.service;

import com.wink.backend.dto.*;
import com.wink.backend.entity.*;
import com.wink.backend.repository.*;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;

@Service
public class ChatService {

  private final ChatSessionRepository sessionRepo;
  private final SessionContextRepository ctxRepo;
  private final ChatMessageRepository msgRepo;
  private final AiRecommendationRepository recRepo;
  private final AiRecommendationSongRepository recSongRepo;
  private final TopicGenerator topicGen;

  public ChatService(ChatSessionRepository s, SessionContextRepository c, ChatMessageRepository m,
                     AiRecommendationRepository r, AiRecommendationSongRepository rs, TopicGenerator t) {
    this.sessionRepo = s; this.ctxRepo = c; this.msgRepo = m; this.recRepo = r; this.recSongRepo = rs; this.topicGen = t;
  }

  public ChatStartResponse startMy(ChatStartMyRequest req){
    String topic = topicGen.fromText(req.getText());
    ChatSession sess = new ChatSession();
    sess.setType("MY"); sess.setTopic(topic); sess.setCreatedAt(LocalDateTime.now());
    sessionRepo.save(sess);

    if (req.getText()!=null) {
      ChatMessage m = new ChatMessage();
      m.setSession(sess); m.setSender("user"); m.setText(req.getText()); m.setImageUrl(req.getImageUrl());
      msgRepo.save(m);
    }
    return new ChatStartResponse(sess.getId(), "MY", topic, "Session created with AI-generated topic.", LocalDateTime.now());
  }

  public ChatStartResponse startSpace(ChatStartSpaceRequest req){
    String topic = topicGen.fromText("space:" + (req.getLocation()!=null?req.getLocation().placeName:""));
    ChatSession sess = new ChatSession();
    sess.setType("SPACE"); sess.setTopic(topic); sess.setCreatedAt(LocalDateTime.now());
    sessionRepo.save(sess);

    SessionContext ctx = new SessionContext();
    ctx.setSession(sess);
    if (req.getLocation()!=null){ ctx.setLat(req.getLocation().latitude); ctx.setLng(req.getLocation().longitude);
      ctx.setAddress(req.getLocation().address); ctx.setPlaceName(req.getLocation().placeName);}
    ctx.setImageUrl(req.getSpaceImageUrl());
    ctxRepo.save(ctx);

    return new ChatStartResponse(sess.getId(), "SPACE", topic, "Space session created.", LocalDateTime.now());
  }

  /** AI 응답 저장 (요약/키워드/추천곡) */
  public AiResponsePayload saveAiResponse(AiResponsePayload payload){
    ChatSession sess = sessionRepo.findById(payload.getSessionId()).orElseThrow();
    // upsert recommendation
    AiRecommendation rec = recRepo.findBySession_Id(sess.getId());
    if (rec==null) rec = new AiRecommendation();
    rec.setSession(sess);
    rec.setSummary(payload.getSummary());
    rec.setKeywordsJson(JsonUtil.toJson(payload.getKeywords())); // 아래 유틸 사용
    rec.setCreatedAt(LocalDateTime.now());
    recRepo.save(rec);

    // 기존 곡 제거 후 재삽입(단순화)
    recSongRepo.findAll().stream().filter(x -> x.getRecommendation().getId().equals(rec.getId()))
      .forEach(x -> recSongRepo.deleteById(x.getId()));
    if (payload.getRecommendations()!=null){
      int rank=1;
      for (AiResponsePayload.Song s : payload.getRecommendations()){
        AiRecommendationSong rs = new AiRecommendationSong();
        rs.setRecommendation(rec); rs.setSongId(null);
        rs.setTitle(s.title); rs.setArtist(s.artist);
        rs.setAlbumCover(s.albumCover); rs.setPreviewUrl(s.previewUrl);
        rs.setRankNo(s.rank!=null?s.rank:rank++);
        recSongRepo.save(rs);
      }
    }
    return payload;
  }
}

package com.wink.backend.controller;

import com.wink.backend.dto.AiResponseRequest;
import com.wink.backend.dto.AiResponseResponse;
import com.wink.backend.dto.ChatHistoryResponse;
import com.wink.backend.dto.ChatStartMyRequest;
import com.wink.backend.dto.ChatStartResponse;
import com.wink.backend.dto.ChatStartSpaceRequest;
import com.wink.backend.service.ChatService;
import io.swagger.v3.oas.annotations.Operation;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    @Operation(summary = "새 채팅 시작 (나의 순간)", description = "입력된 문장에서 핵심 키워드로 topic 추출")
    @PostMapping("/start/my")
    public ChatStartResponse startMy(@RequestBody ChatStartMyRequest req) {
        return chatService.startMy(req);
    }

    @Operation(summary = "새 채팅 시작 (공간의 순간)", description = "장소/사진/주변 음악 정보를 기반으로 공간 분위기 topic 설정")
    @PostMapping("/start/space")
    public ChatStartResponse startSpace(@RequestBody ChatStartSpaceRequest req) {
        return chatService.startSpace(req);
    }

    @Operation(summary = "AI 추천 응답 생성", description = "AI 추천 서버와 연동하여 추천곡/키워드/분위기 분석 결과 반환")
    @PostMapping("/ai-response")
    public AiResponseResponse generateAiResponse(@RequestBody AiResponseRequest req) {
        return chatService.generateAiResponse(req);
    }

    @Operation(summary = "나의 순간 채팅 기록 조회", description = "특정 세션의 메시지 목록을 반환")
    @GetMapping("/history/my/{sessionId}")
    public ChatHistoryResponse getMyChatHistory(@PathVariable Long sessionId) {
        return chatService.getMyChatHistory(sessionId);
    }
}

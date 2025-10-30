package com.wink.backend.controller;

import com.wink.backend.dto.ChatStartMyRequest;
import com.wink.backend.dto.ChatStartResponse;
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

    @Operation(summary = "새 채팅 시작 (나의 순간)", description = "입력된 문장에서 Gemini AI를 사용해 topic 추출")
    @PostMapping("/start/my")
    public ChatStartResponse startMy(@RequestBody ChatStartMyRequest req) {
        return chatService.startMy(req);
    }
}

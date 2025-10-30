package com.wink.backend.controller;

import com.wink.backend.dto.*;
import com.wink.backend.entity.ChatSession;
import com.wink.backend.service.ChatService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
public class ChatController {

    private final ChatService chatService;

    @PostMapping("/start/my")
    public ChatStartResponse startMy(@RequestBody ChatStartMyRequest req) {
        ChatSession session = chatService.startMy(req);
        return new ChatStartResponse(session.getId(), session.getType(), session.getTopic());
    }

    @PostMapping("/start/space")
    public ChatStartResponse startSpace(@RequestBody ChatStartSpaceRequest req) {
        ChatSession session = chatService.startSpace(req);
        return new ChatStartResponse(session.getId(), session.getType(), session.getTopic());
    }

    @PostMapping("/ai/response")
    public void aiResponse(@RequestBody AiResponsePayload payload) {
        chatService.saveAiResponse(payload);
    }
}

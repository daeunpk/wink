package com.wink.backend.controller;

import com.wink.backend.entity.ChatSession;
import com.wink.backend.service.ChatService;
import org.springframework.web.bind.annotation.*;
import java.time.ZonedDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    @PostMapping("/start/my")
    public Map<String, Object> startMyChat(@RequestBody Map<String, Object> request) {
        String text = (String) request.get("text");

        ChatSession session = chatService.createMySession(text);

        Map<String, Object> response = new HashMap<>();
        response.put("sessionId", session.getId());
        response.put("type", session.getType());
        response.put("topic", session.getTopic());
        response.put("message", session.getMessage());
        response.put("timestamp", ZonedDateTime.now().toString());
        return response;
    }
}

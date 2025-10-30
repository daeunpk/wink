// controller/ChatController.java
package com.wink.backend.controller;

import com.wink.backend.dto.*;
import com.wink.backend.service.ChatService;
import io.swagger.v3.oas.annotations.Operation;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
public class ChatController {

  private final ChatService chatService;
  public ChatController(ChatService chatService){ this.chatService = chatService; }

  @Operation(summary="새 채팅 시작(나의 순간)", description="사용자 입력을 요약/가공해 topic을 자동 생성하고 세션을 만듭니다.")
  @PostMapping("/start/my")
  public ChatStartResponse startMy(@RequestBody ChatStartMyRequest req){ return chatService.startMy(req); }

  @Operation(summary="새 채팅 시작(공간의 순간)", description="사진/위치/주변음악과 함께 세션을 생성합니다.")
  @PostMapping("/start/space")
  public ChatStartResponse startSpace(@RequestBody ChatStartSpaceRequest req){ return chatService.startSpace(req); }

  @Operation(summary="AI 응답 저장(추천/키워드)", description="AI 서버 결과를 받아 요약/키워드/추천곡을 저장합니다.")
  @PostMapping("/ai-response")
  public AiResponsePayload aiResponse(@RequestBody AiResponsePayload payload){ return chatService.saveAiResponse(payload); }
}

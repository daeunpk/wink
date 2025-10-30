// dto/ChatStartResponse.java
package com.wink.backend.dto;
import java.time.LocalDateTime;
public class ChatStartResponse {
  private Long sessionId; private String type; private String topic; private String message; private LocalDateTime timestamp;
  public ChatStartResponse(){}
  public ChatStartResponse(Long id,String type,String topic,String msg,LocalDateTime ts){
    this.sessionId=id; this.type=type; this.topic=topic; this.message=msg; this.timestamp=ts;
  }
  // getters/setters...
}

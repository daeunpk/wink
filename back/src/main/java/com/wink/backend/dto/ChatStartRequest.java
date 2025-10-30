// src/main/java/com/wink/backend/dto/ChatStartRequest.java
package com.wink.backend.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class ChatStartRequest {
    private String text;
    private String imageUrl;
}

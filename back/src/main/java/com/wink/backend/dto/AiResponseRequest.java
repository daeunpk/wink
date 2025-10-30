package com.wink.backend.dto;

import lombok.Data;
import java.util.List;

@Data
public class AiResponseRequest {
    private Long sessionId;
    private String inputText;
    private List<String> imageUrls;
}

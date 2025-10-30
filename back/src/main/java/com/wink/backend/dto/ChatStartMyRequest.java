package com.wink.backend.dto;

import lombok.Data;
import java.util.List;

@Data
public class ChatStartMyRequest {
    private String inputText;
    private List<String> imageUrls;
}

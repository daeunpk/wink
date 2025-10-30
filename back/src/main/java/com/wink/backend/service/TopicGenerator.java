package com.wink.backend.service;

public class TopicGenerator {
    public String fromText(String input) {
        // 실제로는 AI 호출, 지금은 단순 문자열 처리
        if (input == null || input.isBlank()) return "Untitled";
        return input.length() > 20 ? input.substring(0, 20) + "..." : input;
    }
}

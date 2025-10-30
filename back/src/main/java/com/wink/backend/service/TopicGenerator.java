// service/TopicGenerator.java
package com.wink.backend.service;
import org.springframework.stereotype.Component;

@Component
public class TopicGenerator {
  public String fromText(String text) {
    if (text == null || text.isBlank()) return "Untitled Chat";
    if (text.contains("비")) return "Rainy Night Jazz";
    if (text.contains("산책")) return "Chill Walk Mood";
    return "Mood-based Chat";
  }
}

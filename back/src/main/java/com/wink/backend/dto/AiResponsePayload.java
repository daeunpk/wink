// dto/AiResponsePayload.java
package com.wink.backend.dto;
import java.util.List;
public class AiResponsePayload {
  public static class Song { public String title; public String artist; public String albumCover; public String previewUrl; public Integer rank; }
  private Long sessionId; private String topic; private String summary; private List<String> keywords; private List<Song> recommendations;
  public AiResponsePayload(){}
  // getters/setters...
}

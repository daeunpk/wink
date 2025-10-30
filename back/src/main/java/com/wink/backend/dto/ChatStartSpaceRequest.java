// dto/ChatStartSpaceRequest.java
package com.wink.backend.dto;
import java.util.List;
public class ChatStartSpaceRequest {
  public static class Location { public Double latitude; public Double longitude; public String address; public String placeName; }
  public static class Nearby { public Long songId; public String title; public String artist; }
  private String spaceImageUrl; private Location location; private List<Nearby> nearbyMusic;
  public ChatStartSpaceRequest(){}
  // getters/setters...
}

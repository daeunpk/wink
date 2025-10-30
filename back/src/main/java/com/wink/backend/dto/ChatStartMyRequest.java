// dto/ChatStartMyRequest.java
package com.wink.backend.dto;
public class ChatStartMyRequest {
  private String text;
  private String imageUrl;
  public ChatStartMyRequest(){}
  public String getText(){return text;} public void setText(String t){this.text=t;}
  public String getImageUrl(){return imageUrl;} public void setImageUrl(String i){this.imageUrl=i;}
}

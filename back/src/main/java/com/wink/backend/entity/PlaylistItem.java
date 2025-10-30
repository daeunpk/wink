// entity/PlaylistItem.java
package com.wink.backend.entity;

import jakarta.persistence.*;

@Entity @Table(name="playlist_item")
public class PlaylistItem {
  @Id @GeneratedValue(strategy=GenerationType.IDENTITY)
  private Long id;

  @ManyToOne(fetch=FetchType.LAZY) @JoinColumn(name="playlist_id", nullable=false)
  private Playlist playlist;

  @Column(nullable=false) private String songTitle;
  @Column(nullable=false) private String artist;
  private String albumCover;
  @Column(nullable=false) private Integer trackNo;

  public PlaylistItem(){}
  // getters/setters ...
}

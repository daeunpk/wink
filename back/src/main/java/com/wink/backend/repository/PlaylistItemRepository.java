package com.wink.backend.repository;

import com.wink.backend.entity.PlaylistItem;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PlaylistItemRepository extends JpaRepository<PlaylistItem, Long> {}

package com.wink.backend.repository;

import com.wink.backend.entity.SessionContext;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SessionContextRepository extends JpaRepository<SessionContext, Long> {
}

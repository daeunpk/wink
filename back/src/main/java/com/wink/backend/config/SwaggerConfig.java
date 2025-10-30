package com.wink.backend.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SwaggerConfig {
    @Bean
    public OpenAPI winkOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Wink Backend API")
                        .description("AI topic extraction, chat, recommendation, playlist APIs")
                        .version("v1.0"));
    }
}

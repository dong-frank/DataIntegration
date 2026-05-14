package com.example.dataintegration.common;

import java.time.Instant;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class HealthController {

    @GetMapping("/health")
    public ApiResponse<HealthStatus> health() {
        return ApiResponse.ok(new HealthStatus("UP", Instant.now().toString()));
    }
}

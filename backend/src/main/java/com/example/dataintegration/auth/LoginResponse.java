package com.example.dataintegration.auth;

import com.example.dataintegration.college.CollegeCode;

public record LoginResponse(
    String token,
    String displayName,
    Role role,
    CollegeCode college
) {
}

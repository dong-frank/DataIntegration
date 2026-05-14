package com.example.dataintegration.auth;

import java.util.Map;

import com.example.dataintegration.college.CollegeCode;
import com.example.dataintegration.common.ApiResponse;

import jakarta.validation.Valid;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private static final Map<String, LoginResponse> MOCK_USERS = Map.of(
        "college-a", new LoginResponse("token-college-a", "学院A教务员", Role.COLLEGE, CollegeCode.A),
        "college-b", new LoginResponse("token-college-b", "学院B教务员", Role.COLLEGE, CollegeCode.B),
        "college-c", new LoginResponse("token-college-c", "学院C教务员", Role.COLLEGE, CollegeCode.C),
        "integration-admin", new LoginResponse("token-integration", "集成服务器管理员", Role.INTEGRATION_ADMIN, null)
    );

    @PostMapping("/login")
    @ResponseStatus(HttpStatus.OK)
    public ApiResponse<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        LoginResponse response = MOCK_USERS.get(request.username());
        if (response == null || !"password".equals(request.password())) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "用户名或密码错误");
        }
        return ApiResponse.ok(response);
    }
}

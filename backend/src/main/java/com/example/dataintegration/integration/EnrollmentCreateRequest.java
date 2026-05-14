package com.example.dataintegration.integration;

import com.example.dataintegration.college.CollegeCode;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record EnrollmentCreateRequest(
    @NotNull CollegeCode studentCollege,
    @NotBlank String studentId,
    @NotNull CollegeCode courseCollege,
    @NotBlank String courseId
) {
}

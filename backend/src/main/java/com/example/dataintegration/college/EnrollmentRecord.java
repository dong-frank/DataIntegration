package com.example.dataintegration.college;

import java.time.LocalDate;

public record EnrollmentRecord(
    String id,
    CollegeCode studentCollege,
    String studentId,
    CollegeCode courseCollege,
    String courseId,
    LocalDate enrolledAt,
    String status,
    String score
) {
}

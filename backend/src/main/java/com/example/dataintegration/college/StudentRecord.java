package com.example.dataintegration.college;

public record StudentRecord(
    String id,
    CollegeCode college,
    String name,
    String gender,
    String major,
    int grade
) {
}

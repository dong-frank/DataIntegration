package com.example.dataintegration.college;

public record CourseRecord(
    String id,
    CollegeCode college,
    String name,
    double credits,
    String teacher,
    boolean shared
) {
}

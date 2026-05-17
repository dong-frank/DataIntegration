package com.example.dataintegration.college;

public record CourseRecord(
    String id,
    CollegeCode college,
    String name,
    int hours,
    double credits,
    String teacher,
    String location,
    boolean shared
) {
}

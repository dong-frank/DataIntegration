package com.example.dataintegration.integration;

import java.util.List;

import com.example.dataintegration.college.CollegeCode;

public record StatsSummary(
    int totalStudents,
    int totalCourses,
    int totalEnrollments,
    List<CollegeStat> colleges,
    List<CourseOverlap> overlappingCourses
) {
    public record CollegeStat(
        CollegeCode college,
        String displayName,
        int studentCount,
        int courseCount,
        int enrollmentCount,
        String dbms
    ) {
    }
}

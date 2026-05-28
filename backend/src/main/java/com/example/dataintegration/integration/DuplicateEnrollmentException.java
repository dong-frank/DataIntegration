package com.example.dataintegration.integration;

import com.example.dataintegration.college.CollegeCode;

public class DuplicateEnrollmentException extends RuntimeException {

    public DuplicateEnrollmentException(
        CollegeCode studentCollege,
        String studentId,
        CollegeCode courseCollege,
        String courseId
    ) {
        super("该学生已选择课程 %s，请勿重复创建选课".formatted(courseId));
    }
}

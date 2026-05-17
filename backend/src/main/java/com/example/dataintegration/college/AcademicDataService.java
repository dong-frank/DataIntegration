package com.example.dataintegration.college;

import java.util.List;
import java.util.Optional;

import com.example.dataintegration.integration.EnrollmentCreateRequest;
import com.example.dataintegration.integration.StatsSummary;
import com.example.dataintegration.integration.WithdrawalResult;

public interface AcademicDataService {

    List<StudentRecord> students(CollegeCode college);

    List<CourseRecord> courses(CollegeCode college);

    List<EnrollmentRecord> enrollments(CollegeCode college);

    List<CourseRecord> sharedCourses(Optional<CollegeCode> source);

    EnrollmentRecord createEnrollment(EnrollmentCreateRequest request);

    WithdrawalResult withdraw(String enrollmentId);

    StatsSummary stats();
}

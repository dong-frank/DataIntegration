package com.example.dataintegration.college;

import java.util.List;

import com.example.dataintegration.common.ApiResponse;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/college/{college}")
public class CollegeController {

    private final MockAcademicDataService dataService;

    public CollegeController(MockAcademicDataService dataService) {
        this.dataService = dataService;
    }

    @GetMapping("/students")
    public ApiResponse<List<StudentRecord>> students(@PathVariable CollegeCode college) {
        return ApiResponse.ok(dataService.students(college));
    }

    @GetMapping("/courses")
    public ApiResponse<List<CourseRecord>> courses(@PathVariable CollegeCode college) {
        return ApiResponse.ok(dataService.courses(college));
    }

    @GetMapping("/enrollments")
    public ApiResponse<List<EnrollmentRecord>> enrollments(@PathVariable CollegeCode college) {
        return ApiResponse.ok(dataService.enrollments(college));
    }
}

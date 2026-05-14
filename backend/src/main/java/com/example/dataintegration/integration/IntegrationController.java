package com.example.dataintegration.integration;

import java.util.List;
import java.util.Optional;

import com.example.dataintegration.college.CollegeCode;
import com.example.dataintegration.college.CourseRecord;
import com.example.dataintegration.college.EnrollmentRecord;
import com.example.dataintegration.college.MockAcademicDataService;
import com.example.dataintegration.common.ApiResponse;

import jakarta.validation.Valid;

import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/integration")
public class IntegrationController {

    private final MockAcademicDataService dataService;

    public IntegrationController(MockAcademicDataService dataService) {
        this.dataService = dataService;
    }

    @GetMapping("/shared-courses")
    public ApiResponse<List<CourseRecord>> sharedCourses(@RequestParam Optional<CollegeCode> source) {
        return ApiResponse.ok(dataService.sharedCourses(source));
    }

    @PostMapping("/enrollments")
    public ApiResponse<EnrollmentRecord> enroll(@Valid @RequestBody EnrollmentCreateRequest request) {
        return ApiResponse.ok(dataService.createEnrollment(request));
    }

    @DeleteMapping("/enrollments/{id}")
    public ApiResponse<WithdrawalResult> withdraw(@PathVariable String id) {
        return ApiResponse.ok(dataService.withdraw(id));
    }

    @GetMapping("/stats")
    public ApiResponse<StatsSummary> stats() {
        return ApiResponse.ok(dataService.stats());
    }
}

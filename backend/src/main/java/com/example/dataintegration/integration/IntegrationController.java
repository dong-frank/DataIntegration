package com.example.dataintegration.integration;

import java.util.List;
import java.util.Optional;

import com.example.dataintegration.college.CollegeCode;
import com.example.dataintegration.college.CourseRecord;
import com.example.dataintegration.college.EnrollmentRecord;
import com.example.dataintegration.college.AcademicDataService;
import com.example.dataintegration.common.ApiResponse;
import com.example.dataintegration.xml.XmlImportService;

import jakarta.validation.Valid;

import org.springframework.http.MediaType;
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

    private final AcademicDataService dataService;
    private final XmlImportService xmlImportService;

    public IntegrationController(AcademicDataService dataService, XmlImportService xmlImportService) {
        this.dataService = dataService;
        this.xmlImportService = xmlImportService;
    }

    @GetMapping("/shared-courses")
    public ApiResponse<List<CourseRecord>> sharedCourses(@RequestParam Optional<CollegeCode> source) {
        return ApiResponse.ok(dataService.sharedCourses(source));
    }

    @PostMapping(value = "/enrollments", consumes = MediaType.APPLICATION_JSON_VALUE)
    public ApiResponse<EnrollmentRecord> enroll(@Valid @RequestBody EnrollmentCreateRequest request) {
        return ApiResponse.ok(dataService.createEnrollment(request));
    }

    @PostMapping(value = "/enrollments", consumes = MediaType.APPLICATION_XML_VALUE)
    public ApiResponse<List<EnrollmentRecord>> enrollFromXml(
        @RequestBody String xml,
        @RequestParam Optional<CollegeCode> college
    ) {
        return ApiResponse.ok(xmlImportService.importEnrollments(xml, college));
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

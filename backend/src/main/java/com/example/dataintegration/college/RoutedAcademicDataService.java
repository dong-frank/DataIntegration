package com.example.dataintegration.college;

import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import com.example.dataintegration.integration.CourseOverlap;
import com.example.dataintegration.integration.EnrollmentCreateRequest;
import com.example.dataintegration.integration.StatsSummary;
import com.example.dataintegration.integration.WithdrawalResult;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Service;

@Service
@Primary
@ConditionalOnProperty(name = "app.data-mode", havingValue = "database")
public class RoutedAcademicDataService implements AcademicDataService {

    private final SqlServerCollegeADataService collegeAService;
    private final OracleCollegeBDataService collegeBService;
    private final MySqlCollegeCDataService collegeCService;

    public RoutedAcademicDataService(
        SqlServerCollegeADataService collegeAService,
        OracleCollegeBDataService collegeBService,
        MySqlCollegeCDataService collegeCService
    ) {
        this.collegeAService = collegeAService;
        this.collegeBService = collegeBService;
        this.collegeCService = collegeCService;
    }

    @Override
    public List<StudentRecord> students(CollegeCode college) {
        return switch (college) {
            case A -> collegeAService.students();
            case B -> collegeBService.students();
            case C -> collegeCService.students();
        };
    }

    @Override
    public List<CourseRecord> courses(CollegeCode college) {
        return switch (college) {
            case A -> collegeAService.courses();
            case B -> collegeBService.courses();
            case C -> collegeCService.courses();
        };
    }

    @Override
    public List<EnrollmentRecord> enrollments(CollegeCode college) {
        return switch (college) {
            case A -> collegeAService.enrollments();
            case B -> collegeBService.enrollments();
            case C -> collegeCService.enrollments();
        };
    }

    @Override
    public List<CourseRecord> sharedCourses(Optional<CollegeCode> source) {
        return source
            .map(this::courses)
            .orElseGet(() -> Stream.of(CollegeCode.values()).flatMap(college -> courses(college).stream()).toList())
            .stream()
            .filter(CourseRecord::shared)
            .sorted(Comparator.comparing(CourseRecord::college).thenComparing(CourseRecord::id))
            .toList();
    }

    @Override
    public EnrollmentRecord createEnrollment(EnrollmentCreateRequest request) {
        if (request.courseCollege() == CollegeCode.A) {
            if (request.studentCollege() != CollegeCode.A) {
                StudentRecord sourceStudent = students(request.studentCollege()).stream()
                    .filter(student -> student.id().equals(request.studentId()))
                    .findFirst()
                    .orElseThrow(() -> new IllegalArgumentException("未找到源学院学生: " + request.studentId()));
                return collegeAService.createImportedEnrollment(request, sourceStudent);
            }
            return collegeAService.createEnrollment(request);
        }
        if (request.courseCollege() == CollegeCode.B) {
            if (request.studentCollege() != CollegeCode.B) {
                StudentRecord sourceStudent = students(request.studentCollege()).stream()
                    .filter(student -> student.id().equals(request.studentId()))
                    .findFirst()
                    .orElseThrow(() -> new IllegalArgumentException("未找到源学院学生: " + request.studentId()));
                return collegeBService.createImportedEnrollment(request, sourceStudent);
            }
            return collegeBService.createEnrollment(request);
        }
        if (request.courseCollege() == CollegeCode.C) {
            if (request.studentCollege() != CollegeCode.C) {
                StudentRecord sourceStudent = students(request.studentCollege()).stream()
                    .filter(student -> student.id().equals(request.studentId()))
                    .findFirst()
                    .orElseThrow(() -> new IllegalArgumentException("未找到源学院学生: " + request.studentId()));
                return collegeCService.createImportedEnrollment(request, sourceStudent);
            }
            return collegeCService.createEnrollment(request);
        }
        throw new IllegalArgumentException("不支持的目标学院: " + request.courseCollege());
    }

    @Override
    public WithdrawalResult withdraw(String enrollmentId) {
        WithdrawalResult collegeAResult = collegeAService.withdraw(enrollmentId);
        if (collegeAResult.withdrawn()) {
            return collegeAResult;
        }
        WithdrawalResult collegeBResult = collegeBService.withdraw(enrollmentId);
        if (collegeBResult.withdrawn()) {
            return collegeBResult;
        }
        WithdrawalResult collegeCResult = collegeCService.withdraw(enrollmentId);
        if (collegeCResult.withdrawn()) {
            return collegeCResult;
        }
        return new WithdrawalResult(enrollmentId, false, null);
    }

    @Override
    public StatsSummary stats() {
        List<StatsSummary.CollegeStat> collegeStats = Stream.of(CollegeCode.values())
            .map(college -> new StatsSummary.CollegeStat(
                college,
                college.getDisplayName(),
                students(college).size(),
                courses(college).size(),
                enrollments(college).size(),
                college.getDbms()
            ))
            .toList();

        Map<String, Long> courseNameCounts = Stream.of(CollegeCode.values())
            .flatMap(college -> courses(college).stream())
            .collect(Collectors.groupingBy(CourseRecord::name, LinkedHashMap::new, Collectors.counting()));

        List<CourseOverlap> overlaps = courseNameCounts.entrySet().stream()
            .filter(entry -> entry.getValue() > 1)
            .map(entry -> new CourseOverlap(entry.getKey(), entry.getValue().intValue()))
            .toList();

        return new StatsSummary(
            collegeStats.stream().mapToInt(StatsSummary.CollegeStat::studentCount).sum(),
            collegeStats.stream().mapToInt(StatsSummary.CollegeStat::courseCount).sum(),
            collegeStats.stream().mapToInt(StatsSummary.CollegeStat::enrollmentCount).sum(),
            collegeStats,
            overlaps
        );
    }
}

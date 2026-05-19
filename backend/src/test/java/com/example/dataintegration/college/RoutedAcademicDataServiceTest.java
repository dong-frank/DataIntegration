package com.example.dataintegration.college;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import java.time.LocalDate;
import java.util.List;

import org.junit.jupiter.api.Test;

import com.example.dataintegration.integration.EnrollmentCreateRequest;

class RoutedAcademicDataServiceTest {

    private final SqlServerCollegeADataService collegeAService = mock(SqlServerCollegeADataService.class);
    private final MySqlCollegeCDataService collegeCService = mock(MySqlCollegeCDataService.class);
    private final MockAcademicDataService fallbackService = mock(MockAcademicDataService.class);
    private final RoutedAcademicDataService service = new RoutedAcademicDataService(
        collegeAService,
        collegeCService,
        fallbackService
    );

    @Test
    void routesCollegeCReadsToMySqlService() {
        List<CourseRecord> courses = List.of(
            new CourseRecord("C001", CollegeCode.C, "数据库系统", 48, 3.0, "C教师01", "实验楼101", true)
        );
        when(collegeCService.courses()).thenReturn(courses);

        assertThat(service.courses(CollegeCode.C)).isSameAs(courses);
        verify(collegeCService).courses();
        verifyNoInteractions(fallbackService);
    }

    @Test
    void createsImportedCollegeCEnrollmentForExternalStudent() {
        EnrollmentCreateRequest request = new EnrollmentCreateRequest(CollegeCode.B, "B-S001", CollegeCode.C, "C002");
        StudentRecord sourceStudent = new StudentRecord("B-S001", CollegeCode.B, "学院B学生001", "女", "学院B教学管理", 2023);
        EnrollmentRecord expected = new EnrollmentRecord(
            "C002-B-S001",
            CollegeCode.B,
            "B-S001",
            CollegeCode.C,
            "C002",
            LocalDate.now(),
            "ACTIVE",
            "0"
        );

        when(fallbackService.students(CollegeCode.B)).thenReturn(List.of(sourceStudent));
        when(collegeCService.createImportedEnrollment(request, sourceStudent)).thenReturn(expected);

        assertThat(service.createEnrollment(request)).isEqualTo(expected);
        verify(collegeCService).createImportedEnrollment(request, sourceStudent);
    }
}

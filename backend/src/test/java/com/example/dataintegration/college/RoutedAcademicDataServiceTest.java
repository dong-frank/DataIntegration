package com.example.dataintegration.college;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import java.time.LocalDate;
import java.util.List;

import org.junit.jupiter.api.Test;

import com.example.dataintegration.integration.EnrollmentCreateRequest;
import com.example.dataintegration.integration.WithdrawalResult;

class RoutedAcademicDataServiceTest {

    private final SqlServerCollegeADataService collegeAService = mock(SqlServerCollegeADataService.class);
    private final OracleCollegeBDataService collegeBService = mock(OracleCollegeBDataService.class);
    private final MySqlCollegeCDataService collegeCService = mock(MySqlCollegeCDataService.class);
    private final MockAcademicDataService fallbackService = mock(MockAcademicDataService.class);
    private final RoutedAcademicDataService service = new RoutedAcademicDataService(
        collegeAService,
        collegeBService,
        collegeCService
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
    void routesCollegeBReadsToOracleService() {
        List<CourseRecord> courses = List.of(
            new CourseRecord("B0001", CollegeCode.B, "数据库系统", 48, 3.0, "B教师01", "实验楼101", true)
        );
        when(collegeBService.courses()).thenReturn(courses);

        assertThat(service.courses(CollegeCode.B)).isSameAs(courses);
        verify(collegeBService).courses();
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

        when(collegeBService.students()).thenReturn(List.of(sourceStudent));
        when(collegeCService.createImportedEnrollment(request, sourceStudent)).thenReturn(expected);

        assertThat(service.createEnrollment(request)).isEqualTo(expected);
        verify(collegeCService).createImportedEnrollment(request, sourceStudent);
    }

    @Test
    void createsImportedCollegeBEnrollmentForExternalStudent() {
        EnrollmentCreateRequest request = new EnrollmentCreateRequest(CollegeCode.C, "C-S001", CollegeCode.B, "B0002");
        StudentRecord sourceStudent = new StudentRecord("C-S001", CollegeCode.C, "学院C学生001", "女", "学院C教学管理", 2023);
        EnrollmentRecord expected = new EnrollmentRecord(
            "B0002-C-S001",
            CollegeCode.C,
            "C-S001",
            CollegeCode.B,
            "B0002",
            LocalDate.now(),
            "ACTIVE",
            "0"
        );

        when(collegeCService.students()).thenReturn(List.of(sourceStudent));
        when(collegeBService.createImportedEnrollment(request, sourceStudent)).thenReturn(expected);

        assertThat(service.createEnrollment(request)).isEqualTo(expected);
        verify(collegeBService).createImportedEnrollment(request, sourceStudent);
    }

    @Test
    void returnsNotWithdrawnWhenDatabaseServicesCannotFindEnrollment() {
        when(collegeAService.withdraw("missing")).thenReturn(new WithdrawalResult("missing", false, CollegeCode.A));
        when(collegeBService.withdraw("missing")).thenReturn(new WithdrawalResult("missing", false, CollegeCode.B));
        when(collegeCService.withdraw("missing")).thenReturn(new WithdrawalResult("missing", false, CollegeCode.C));
        when(fallbackService.withdraw("missing")).thenReturn(new WithdrawalResult("missing", true, CollegeCode.A));

        assertThat(service.withdraw("missing")).isEqualTo(new WithdrawalResult("missing", false, null));
        verify(fallbackService, never()).withdraw("missing");
    }
}

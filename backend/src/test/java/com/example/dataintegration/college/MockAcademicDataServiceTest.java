package com.example.dataintegration.college;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Optional;
import java.util.stream.Stream;

import org.junit.jupiter.api.Test;

class MockAcademicDataServiceTest {

    @Test
    void courseNamesAreCollegeSpecificIncludingSharedCourses() {
        MockAcademicDataService service = new MockAcademicDataService();

        assertThat(Stream.of(CollegeCode.values())
            .flatMap(college -> service.courses(college).stream())
            .map(CourseRecord::name)
            .toList())
            .doesNotHaveDuplicates()
            .contains("算法设计", "商业数据分析", "新媒体传播");

        assertThat(service.sharedCourses(Optional.empty()).stream()
            .map(CourseRecord::name)
            .toList())
            .doesNotHaveDuplicates()
            .contains("软件工程实践", "数字经济导论", "数字内容设计");
    }

    @Test
    void studentsUseMeaningfulChineseNamesInsteadOfPlaceholderLabels() {
        MockAcademicDataService service = new MockAcademicDataService();

        assertThat(service.students(CollegeCode.A).stream()
            .map(StudentRecord::name)
            .toList())
            .contains("林安然", "陈安然")
            .doesNotContain("学院A学生001");

        assertThat(service.students(CollegeCode.B).stream()
            .map(StudentRecord::name)
            .toList())
            .contains("周景文")
            .doesNotContain("学院B学生001");

        assertThat(service.students(CollegeCode.C).stream()
            .map(StudentRecord::name)
            .toList())
            .contains("苏知夏")
            .doesNotContain("学院C学生001");
    }
}

package com.example.dataintegration.college;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.LocalDate;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.embedded.EmbeddedDatabase;
import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseBuilder;
import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseType;

import com.example.dataintegration.integration.EnrollmentCreateRequest;

class OracleCollegeBDataServiceTest {

    private OracleCollegeBDataService service;

    @BeforeEach
    void setUp() {
        EmbeddedDatabase database = new EmbeddedDatabaseBuilder()
            .generateUniqueName(true)
            .setType(EmbeddedDatabaseType.H2)
            .build();
        JdbcTemplate jdbcTemplate = new JdbcTemplate(database);

        jdbcTemplate.execute("""
            CREATE TABLE B_STUDENT (
                student_no VARCHAR(20) PRIMARY KEY,
                student_name VARCHAR(50),
                gender VARCHAR(2),
                major VARCHAR(50),
                student_passwd VARCHAR(6)
            )
            """);
        jdbcTemplate.execute("""
            CREATE TABLE B_COURSE (
                course_no VARCHAR(20) PRIMARY KEY,
                course_name VARCHAR(50),
                class_hours VARCHAR(2),
                credit_pts VARCHAR(1),
                teacher VARCHAR(50),
                location VARCHAR(50),
                shared CHAR(1)
            )
            """);
        jdbcTemplate.execute("""
            CREATE TABLE B_SELECTION (
                course_no VARCHAR(20),
                student_no VARCHAR(20),
                score_text VARCHAR(3)
            )
            """);
        jdbcTemplate.execute("""
            CREATE TABLE B_IMPORTED_STUDENT (
                source_college VARCHAR(1),
                student_no VARCHAR(20),
                student_name VARCHAR(50),
                gender VARCHAR(2),
                major VARCHAR(50),
                imported_on DATE
            )
            """);
        jdbcTemplate.execute("""
            CREATE TABLE B_IMPORTED_SELECTION (
                course_no VARCHAR(20),
                source_college VARCHAR(1),
                student_no VARCHAR(20),
                score_text VARCHAR(3),
                enrolled_on DATE,
                status_code VARCHAR(20)
            )
            """);
        jdbcTemplate.execute("""
            CREATE VIEW vw_adapter_students AS
            SELECT
                student_no AS id,
                'B' AS college,
                student_name AS name,
                gender AS gender,
                major AS major,
                CAST(SUBSTRING(student_no, 1, 4) AS INT) AS grade
            FROM B_STUDENT
            """);
        jdbcTemplate.execute("""
            CREATE VIEW vw_adapter_courses AS
            SELECT
                course_no AS id,
                'B' AS college,
                course_name AS name,
                CAST(class_hours AS INT) AS hours,
                CAST(credit_pts AS DECIMAL(3, 1)) AS credits,
                teacher AS teacher,
                location AS location,
                CASE WHEN shared = 'Y' THEN 1 ELSE 0 END AS shared
            FROM B_COURSE
            """);
        jdbcTemplate.execute("""
            CREATE VIEW vw_adapter_enrollments AS
            SELECT
                CONCAT(course_no, '-', student_no) AS id,
                'B' AS studentCollege,
                student_no AS studentId,
                'B' AS courseCollege,
                course_no AS courseId,
                DATE '2026-03-01' AS enrolledAt,
                'ACTIVE' AS status,
                score_text AS score
            FROM B_SELECTION
            UNION ALL
            SELECT
                CONCAT(course_no, '-', student_no) AS id,
                source_college AS studentCollege,
                student_no AS studentId,
                'B' AS courseCollege,
                course_no AS courseId,
                enrolled_on AS enrolledAt,
                status_code AS status,
                score_text AS score
            FROM B_IMPORTED_SELECTION
            """);

        jdbcTemplate.update("""
            INSERT INTO B_STUDENT (student_no, student_name, gender, major, student_passwd)
            VALUES ('202200001', 'B学生001', '男', '学院B', '123456')
            """);
        jdbcTemplate.update("""
            INSERT INTO B_COURSE (course_no, course_name, class_hours, credit_pts, teacher, location, shared)
            VALUES ('B0001', '数据库系统', '48', '3', 'B教师01', '实验楼101', 'Y')
            """);
        jdbcTemplate.update("""
            INSERT INTO B_COURSE (course_no, course_name, class_hours, credit_pts, teacher, location, shared)
            VALUES ('B0002', '数据集成', '64', '4', 'B教师02', '实验楼102', 'Y')
            """);
        jdbcTemplate.update("""
            INSERT INTO B_SELECTION (course_no, student_no, score_text)
            VALUES ('B0001', '202200001', '88')
            """);

        service = new OracleCollegeBDataService(jdbcTemplate);
    }

    @Test
    void readsStudentsFromAdapterView() {
        assertThat(service.students()).containsExactly(
            new StudentRecord("202200001", CollegeCode.B, "B学生001", "男", "学院B", 2022)
        );
    }

    @Test
    void readsCoursesFromAdapterView() {
        assertThat(service.courses()).containsExactly(
            new CourseRecord("B0001", CollegeCode.B, "数据库系统", 48, 3.0, "B教师01", "实验楼101", true),
            new CourseRecord("B0002", CollegeCode.B, "数据集成", 64, 4.0, "B教师02", "实验楼102", true)
        );
    }

    @Test
    void readsEnrollmentsFromAdapterView() {
        assertThat(service.enrollments()).containsExactly(
            new EnrollmentRecord(
                "B0001-202200001",
                CollegeCode.B,
                "202200001",
                CollegeCode.B,
                "B0001",
                LocalDate.of(2026, 3, 1),
                "ACTIVE",
                "88"
            )
        );
    }

    @Test
    void createEnrollmentWritesLocalSelection() {
        EnrollmentRecord record = service.createEnrollment(
            new EnrollmentCreateRequest(CollegeCode.B, "202200001", CollegeCode.B, "B0002")
        );

        assertThat(record).isEqualTo(new EnrollmentRecord(
            "B0002-202200001",
            CollegeCode.B,
            "202200001",
            CollegeCode.B,
            "B0002",
            LocalDate.now(),
            "ACTIVE",
            "0"
        ));
        assertThat(service.enrollments()).extracting(EnrollmentRecord::id).contains("B0002-202200001");
    }

    @Test
    void createImportedEnrollmentWritesImportedStudentAndSelection() {
        EnrollmentRecord record = service.createImportedEnrollment(
            new EnrollmentCreateRequest(CollegeCode.C, "C-S001", CollegeCode.B, "B0002"),
            new StudentRecord("C-S001", CollegeCode.C, "学院C学生001", "女", "学院C教学管理", 2023)
        );

        assertThat(record).isEqualTo(new EnrollmentRecord(
            "B0002-C-S001",
            CollegeCode.C,
            "C-S001",
            CollegeCode.B,
            "B0002",
            LocalDate.now(),
            "ACTIVE",
            "0"
        ));
        assertThat(service.enrollments()).extracting(EnrollmentRecord::id).contains("B0002-C-S001");
    }
}

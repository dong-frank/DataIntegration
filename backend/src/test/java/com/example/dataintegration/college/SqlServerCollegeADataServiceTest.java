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

class SqlServerCollegeADataServiceTest {

    private EmbeddedDatabase database;
    private SqlServerCollegeADataService service;

    @BeforeEach
    void setUp() {
        database = new EmbeddedDatabaseBuilder()
            .generateUniqueName(true)
            .setType(EmbeddedDatabaseType.H2)
            .build();
        JdbcTemplate jdbcTemplate = new JdbcTemplate(database);

        jdbcTemplate.execute("CREATE SCHEMA dbo");
        jdbcTemplate.execute("""
            CREATE TABLE dbo.A_STUDENT (
                student_no VARCHAR(20) PRIMARY KEY,
                student_name VARCHAR(50),
                gender_name VARCHAR(2),
                department_name VARCHAR(50)
            )
            """);
        jdbcTemplate.execute("""
            CREATE TABLE dbo.A_COURSE (
                course_no VARCHAR(20) PRIMARY KEY,
                course_name VARCHAR(50),
                credit_text VARCHAR(2),
                teacher_name VARCHAR(50),
                teaching_place VARCHAR(50),
                shared_flag CHAR(1)
            )
            """);
        jdbcTemplate.execute("""
            CREATE TABLE dbo.A_SELECTION (
                course_no VARCHAR(20),
                student_no VARCHAR(20),
                score_text VARCHAR(3)
            )
            """);
        jdbcTemplate.execute("""
            CREATE TABLE dbo.A_IMPORTED_STUDENT (
                source_college VARCHAR(1),
                student_no VARCHAR(20),
                student_name VARCHAR(50),
                gender_name VARCHAR(2),
                major_name VARCHAR(50),
                imported_on DATE
            )
            """);
        jdbcTemplate.execute("""
            CREATE TABLE dbo.A_IMPORTED_SELECTION (
                course_no VARCHAR(20),
                source_college VARCHAR(1),
                student_no VARCHAR(20),
                score_text VARCHAR(3),
                enrolled_on DATE,
                status_code VARCHAR(20)
            )
            """);
        jdbcTemplate.execute("""
            CREATE VIEW dbo.vw_adapter_students AS
            SELECT
                student_no AS id,
                'A' AS college,
                student_name AS name,
                gender_name AS gender,
                department_name AS major,
                CAST(SUBSTRING(student_no, 1, 4) AS INT) AS grade
            FROM dbo.A_STUDENT
            """);
        jdbcTemplate.execute("""
            CREATE VIEW dbo.vw_adapter_courses AS
            SELECT
                course_no AS id,
                'A' AS college,
                course_name AS name,
                CAST(CAST(credit_text AS INT) * 16 AS INT) AS hours,
                CAST(credit_text AS DECIMAL(3, 1)) AS credits,
                teacher_name AS teacher,
                teaching_place AS location,
                CASE WHEN shared_flag = 'Y' THEN TRUE ELSE FALSE END AS shared
            FROM dbo.A_COURSE
            """);
        jdbcTemplate.execute("""
            CREATE VIEW dbo.vw_adapter_enrollments AS
            SELECT
                CONCAT(course_no, '-', student_no) AS id,
                'A' AS studentCollege,
                student_no AS studentId,
                'A' AS courseCollege,
                course_no AS courseId,
                DATE '2026-03-01' AS enrolledAt,
                'ACTIVE' AS status,
                score_text AS score
            FROM dbo.A_SELECTION
            UNION ALL
            SELECT
                CONCAT(course_no, '-', student_no) AS id,
                source_college AS studentCollege,
                student_no AS studentId,
                'A' AS courseCollege,
                course_no AS courseId,
                enrolled_on AS enrolledAt,
                status_code AS status,
                score_text AS score
            FROM dbo.A_IMPORTED_SELECTION
            """);

        jdbcTemplate.update("""
            INSERT INTO dbo.A_STUDENT (student_no, student_name, gender_name, department_name)
            VALUES ('202200000001', 'A000000001', '男', '学院A')
            """);
        jdbcTemplate.update("""
            INSERT INTO dbo.A_COURSE (course_no, course_name, credit_text, teacher_name, teaching_place, shared_flag)
            VALUES ('A0000001', '数据库系统', '3', 'A教师01', '实验楼101', 'Y')
            """);
        jdbcTemplate.update("""
            INSERT INTO dbo.A_COURSE (course_no, course_name, credit_text, teacher_name, teaching_place, shared_flag)
            VALUES ('A0000002', '数据集成', '4', 'A教师02', '实验楼102', 'Y')
            """);
        jdbcTemplate.update("""
            INSERT INTO dbo.A_SELECTION (course_no, student_no, score_text)
            VALUES ('A0000001', '202200000001', '88')
            """);

        service = new SqlServerCollegeADataService(jdbcTemplate);
    }

    @Test
    void readsStudentsFromAdapterView() {
        assertThat(service.students()).containsExactly(
            new StudentRecord("202200000001", CollegeCode.A, "A000000001", "男", "学院A", 2022)
        );
    }

    @Test
    void readsCoursesFromAdapterView() {
        assertThat(service.courses()).containsExactly(
            new CourseRecord("A0000001", CollegeCode.A, "数据库系统", 48, 3.0, "A教师01", "实验楼101", true),
            new CourseRecord("A0000002", CollegeCode.A, "数据集成", 64, 4.0, "A教师02", "实验楼102", true)
        );
    }

    @Test
    void readsEnrollmentsFromAdapterView() {
        assertThat(service.enrollments()).containsExactly(
            new EnrollmentRecord(
                "A0000001-202200000001",
                CollegeCode.A,
                "202200000001",
                CollegeCode.A,
                "A0000001",
                LocalDate.of(2026, 3, 1),
                "ACTIVE",
                "88"
            )
        );
    }

    @Test
    void createEnrollmentWritesLocalSelection() {
        EnrollmentRecord record = service.createEnrollment(
            new EnrollmentCreateRequest(CollegeCode.A, "202200000001", CollegeCode.A, "A0000002")
        );

        assertThat(record).isEqualTo(new EnrollmentRecord(
            "A0000002-202200000001",
            CollegeCode.A,
            "202200000001",
            CollegeCode.A,
            "A0000002",
            LocalDate.now(),
            "ACTIVE",
            "0"
        ));
        assertThat(service.enrollments()).extracting(EnrollmentRecord::id).contains("A0000002-202200000001");
    }

    @Test
    void createImportedEnrollmentWritesImportedStudentAndSelection() {
        EnrollmentRecord record = service.createImportedEnrollment(
            new EnrollmentCreateRequest(CollegeCode.B, "B-S001", CollegeCode.A, "A0000002"),
            new StudentRecord("B-S001", CollegeCode.B, "学院B学生001", "女", "学院B教学管理", 2023)
        );

        assertThat(record).isEqualTo(new EnrollmentRecord(
            "A0000002-B-S001",
            CollegeCode.B,
            "B-S001",
            CollegeCode.A,
            "A0000002",
            LocalDate.now(),
            "ACTIVE",
            "0"
        ));
        assertThat(service.enrollments()).extracting(EnrollmentRecord::id).contains("A0000002-B-S001");
    }
}

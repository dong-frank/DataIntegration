package com.example.dataintegration.college;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.embedded.EmbeddedDatabase;
import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseBuilder;
import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseType;

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
            CREATE TABLE dbo.vw_adapter_students (
                id VARCHAR(20),
                college VARCHAR(1),
                name VARCHAR(50),
                gender VARCHAR(2),
                major VARCHAR(50),
                grade INT
            )
            """);
        jdbcTemplate.execute("""
            CREATE TABLE dbo.vw_adapter_courses (
                id VARCHAR(20),
                college VARCHAR(1),
                name VARCHAR(50),
                credits DECIMAL(3, 1),
                teacher VARCHAR(50),
                shared BOOLEAN
            )
            """);
        jdbcTemplate.execute("""
            CREATE TABLE dbo.vw_adapter_enrollments (
                id VARCHAR(50),
                studentCollege VARCHAR(1),
                studentId VARCHAR(20),
                courseCollege VARCHAR(1),
                courseId VARCHAR(20),
                enrolledAt DATE,
                status VARCHAR(20)
            )
            """);

        jdbcTemplate.update("""
            INSERT INTO dbo.vw_adapter_students (id, college, name, gender, major, grade)
            VALUES ('202200000001', 'A', 'A000000001', '男', '学院A', 2022)
            """);
        jdbcTemplate.update("""
            INSERT INTO dbo.vw_adapter_courses (id, college, name, credits, teacher, shared)
            VALUES ('A0000001', 'A', '数据库系统', 3.0, 'A教师01', TRUE)
            """);
        jdbcTemplate.update("""
            INSERT INTO dbo.vw_adapter_enrollments
                (id, studentCollege, studentId, courseCollege, courseId, enrolledAt, status)
            VALUES ('A0000001-202200000001', 'A', '202200000001', 'A', 'A0000001', DATE '2026-03-01', 'ACTIVE')
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
            new CourseRecord("A0000001", CollegeCode.A, "数据库系统", 3.0, "A教师01", true)
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
                java.time.LocalDate.of(2026, 3, 1),
                "ACTIVE"
            )
        );
    }
}

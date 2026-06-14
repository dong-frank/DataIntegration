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

class MySqlCollegeCDataServiceTest {

    private MySqlCollegeCDataService service;

    @BeforeEach
    void setUp() {
        EmbeddedDatabase database = new EmbeddedDatabaseBuilder()
            .generateUniqueName(true)
            .setType(EmbeddedDatabaseType.H2)
            .build();
        JdbcTemplate jdbcTemplate = new JdbcTemplate(database);

        jdbcTemplate.execute("""
            CREATE TABLE C_STUDENT (
                Sno VARCHAR(20) PRIMARY KEY,
                Snm VARCHAR(50),
                Sex VARCHAR(2),
                Sde VARCHAR(50),
                Pwd CHAR(6)
            )
            """);
        jdbcTemplate.execute("""
            CREATE TABLE C_COURSE (
                Cno VARCHAR(20) PRIMARY KEY,
                Cnm VARCHAR(50),
                Ctm INTEGER,
                Cpt INTEGER,
                Tec VARCHAR(50),
                Pla VARCHAR(50),
                Share CHAR(1)
            )
            """);
        jdbcTemplate.execute("""
            CREATE TABLE C_SELECTION (
                Cno VARCHAR(20),
                Sno VARCHAR(20),
                Grd INTEGER
            )
            """);
        jdbcTemplate.execute("""
            CREATE TABLE C_IMPORTED_STUDENT (
                source_college VARCHAR(1),
                student_no VARCHAR(20),
                student_name VARCHAR(50),
                gender_name VARCHAR(2),
                major_name VARCHAR(50),
                imported_on DATE
            )
            """);
        jdbcTemplate.execute("""
            CREATE TABLE C_IMPORTED_SELECTION (
                Cno VARCHAR(20),
                source_college VARCHAR(1),
                student_no VARCHAR(20),
                Grd INTEGER,
                enrolled_on DATE,
                status_code VARCHAR(20)
            )
            """);
        jdbcTemplate.execute("""
            CREATE VIEW vw_adapter_students AS
            SELECT
                Sno AS id,
                'C' AS college,
                Snm AS name,
                Sex AS gender,
                Sde AS major,
                CAST(SUBSTRING(Sno, 1, 4) AS INT) AS grade
            FROM C_STUDENT
            """);
        jdbcTemplate.execute("""
            CREATE VIEW vw_adapter_courses AS
            SELECT
                Cno AS id,
                'C' AS college,
                Cnm AS name,
                Ctm AS hours,
                CAST(Cpt AS DECIMAL(3, 1)) AS credits,
                Tec AS teacher,
                Pla AS location,
                CASE WHEN Share = 'Y' THEN TRUE ELSE FALSE END AS shared
            FROM C_COURSE
            """);
        jdbcTemplate.execute("""
            CREATE VIEW vw_adapter_enrollments AS
            SELECT
                CONCAT(Cno, '-', Sno) AS id,
                'C' AS studentCollege,
                Sno AS studentId,
                'C' AS courseCollege,
                Cno AS courseId,
                DATE '2026-03-01' AS enrolledAt,
                'ACTIVE' AS status,
                CAST(Grd AS VARCHAR(3)) AS score
            FROM C_SELECTION
            UNION ALL
            SELECT
                CONCAT(Cno, '-', student_no) AS id,
                source_college AS studentCollege,
                student_no AS studentId,
                'C' AS courseCollege,
                Cno AS courseId,
                enrolled_on AS enrolledAt,
                status_code AS status,
                CAST(Grd AS VARCHAR(3)) AS score
            FROM C_IMPORTED_SELECTION
            """);

        jdbcTemplate.update("""
            INSERT INTO C_STUDENT (Sno, Snm, Sex, Sde, Pwd)
            VALUES ('202300001', '学生001', '男', '学院C', '123456')
            """);
        jdbcTemplate.update("""
            INSERT INTO C_COURSE (Cno, Cnm, Ctm, Cpt, Tec, Pla, Share)
            VALUES ('C001', '数据库系统', 48, 3, 'C教师01', '实验楼101', 'Y')
            """);
        jdbcTemplate.update("""
            INSERT INTO C_COURSE (Cno, Cnm, Ctm, Cpt, Tec, Pla, Share)
            VALUES ('C002', '数据集成', 64, 4, 'C教师02', '实验楼102', 'Y')
            """);
        jdbcTemplate.update("""
            INSERT INTO C_SELECTION (Cno, Sno, Grd)
            VALUES ('C001', '202300001', 88)
            """);

        service = new MySqlCollegeCDataService(jdbcTemplate);
    }

    @Test
    void readsStudentsFromAdapterView() {
        assertThat(service.students()).containsExactly(
            new StudentRecord("202300001", CollegeCode.C, "学生001", "男", "学院C", 2023)
        );
    }

    @Test
    void readsCoursesFromAdapterView() {
        assertThat(service.courses()).containsExactly(
            new CourseRecord("C001", CollegeCode.C, "数据库系统", 48, 3.0, "C教师01", "实验楼101", true),
            new CourseRecord("C002", CollegeCode.C, "数据集成", 64, 4.0, "C教师02", "实验楼102", true)
        );
    }

    @Test
    void readsEnrollmentsFromAdapterView() {
        assertThat(service.enrollments()).containsExactly(
            new EnrollmentRecord(
                "C001-202300001",
                CollegeCode.C,
                "202300001",
                CollegeCode.C,
                "C001",
                LocalDate.of(2026, 3, 1),
                "ACTIVE",
                "88"
            )
        );
    }

    @Test
    void createEnrollmentWritesLocalSelection() {
        EnrollmentRecord record = service.createEnrollment(
            new EnrollmentCreateRequest(CollegeCode.C, "202300001", CollegeCode.C, "C002")
        );

        assertThat(record).isEqualTo(new EnrollmentRecord(
            "C002-202300001",
            CollegeCode.C,
            "202300001",
            CollegeCode.C,
            "C002",
            LocalDate.now(),
            "ACTIVE",
            "0"
        ));
        assertThat(service.enrollments()).extracting(EnrollmentRecord::id).contains("C002-202300001");
    }

    @Test
    void createImportedEnrollmentWritesImportedStudentAndSelection() {
        EnrollmentRecord record = service.createImportedEnrollment(
            new EnrollmentCreateRequest(CollegeCode.A, "A-S001", CollegeCode.C, "C002"),
            new StudentRecord("A-S001", CollegeCode.A, "学院A学生001", "女", "学院A教学管理", 2023)
        );

        assertThat(record).isEqualTo(new EnrollmentRecord(
            "C002-A-S001",
            CollegeCode.A,
            "A-S001",
            CollegeCode.C,
            "C002",
            LocalDate.now(),
            "ACTIVE",
            "0"
        ));
        assertThat(service.enrollments()).extracting(EnrollmentRecord::id).contains("C002-A-S001");
    }
}

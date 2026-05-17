package com.example.dataintegration.college;

import java.sql.Date;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDate;
import java.util.List;

import com.example.dataintegration.integration.EnrollmentCreateRequest;
import com.example.dataintegration.integration.WithdrawalResult;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.jdbc.core.JdbcOperations;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(name = "app.data-mode", havingValue = "database")
public class SqlServerCollegeADataService {

    private final JdbcOperations jdbc;

    public SqlServerCollegeADataService(JdbcOperations collegeAJdbcTemplate) {
        this.jdbc = collegeAJdbcTemplate;
    }

    public List<StudentRecord> students() {
        return jdbc.query("""
            SELECT id, college, name, gender, major, grade
            FROM dbo.vw_adapter_students
            ORDER BY id
            """, studentMapper());
    }

    public List<CourseRecord> courses() {
        return jdbc.query("""
            SELECT id, college, name, hours, credits, teacher, location, shared
            FROM dbo.vw_adapter_courses
            ORDER BY id
            """, courseMapper());
    }

    public List<EnrollmentRecord> enrollments() {
        return jdbc.query("""
            SELECT id, studentCollege, studentId, courseCollege, courseId, enrolledAt, status, score
            FROM dbo.vw_adapter_enrollments
            ORDER BY id
            """, enrollmentMapper());
    }

    public EnrollmentRecord createEnrollment(EnrollmentCreateRequest request) {
        assertCourseExists(request.courseId());
        assertLocalStudentExists(request.studentId());
        jdbc.update(
            "INSERT INTO dbo.A_SELECTION (course_no, student_no, score_text) VALUES (?, ?, '0')",
            request.courseId(),
            request.studentId()
        );
        return new EnrollmentRecord(
            "%s-%s".formatted(request.courseId(), request.studentId()),
            request.studentCollege(),
            request.studentId(),
            CollegeCode.A,
            request.courseId(),
            LocalDate.now(),
            "ACTIVE",
            "0"
        );
    }

    public EnrollmentRecord createImportedEnrollment(EnrollmentCreateRequest request, StudentRecord sourceStudent) {
        if (sourceStudent == null) {
            throw new IllegalArgumentException("外院学生信息不能为空");
        }
        if (request.courseCollege() != CollegeCode.A) {
            throw new IllegalArgumentException("当前服务仅处理学院 A 的落库");
        }
        if (!sourceStudent.id().equals(request.studentId())) {
            throw new IllegalArgumentException("外院学生信息与选课请求不一致");
        }

        assertCourseExists(request.courseId());
        upsertImportedStudent(sourceStudent);

        jdbc.update(
            """
            INSERT INTO dbo.A_IMPORTED_SELECTION
                (course_no, source_college, student_no, score_text, enrolled_on, status_code)
            VALUES (?, ?, ?, '0', ?, 'ACTIVE')
            """,
            request.courseId(),
            request.studentCollege().name(),
            request.studentId(),
            Date.valueOf(LocalDate.now())
        );

        return new EnrollmentRecord(
            "%s-%s".formatted(request.courseId(), request.studentId()),
            request.studentCollege(),
            request.studentId(),
            CollegeCode.A,
            request.courseId(),
            LocalDate.now(),
            "ACTIVE",
            "0"
        );
    }

    public WithdrawalResult withdraw(String enrollmentId) {
        String[] parts = enrollmentId.split("-", 2);
        if (parts.length != 2) {
            return new WithdrawalResult(enrollmentId, false, CollegeCode.A);
        }
        int affectedRows = jdbc.update(
            "DELETE FROM dbo.A_SELECTION WHERE course_no = ? AND student_no = ?",
            parts[0],
            parts[1]
        );
        affectedRows += jdbc.update(
            "DELETE FROM dbo.A_IMPORTED_SELECTION WHERE course_no = ? AND student_no = ?",
            parts[0],
            parts[1]
        );
        return new WithdrawalResult(enrollmentId, affectedRows > 0, CollegeCode.A);
    }

    private RowMapper<StudentRecord> studentMapper() {
        return (rs, rowNum) -> new StudentRecord(
            rs.getString("id"),
            CollegeCode.valueOf(rs.getString("college")),
            rs.getString("name"),
            rs.getString("gender"),
            rs.getString("major"),
            rs.getInt("grade")
        );
    }

    private RowMapper<CourseRecord> courseMapper() {
        return (rs, rowNum) -> new CourseRecord(
            rs.getString("id"),
            CollegeCode.valueOf(rs.getString("college")),
            rs.getString("name"),
            rs.getInt("hours"),
            rs.getDouble("credits"),
            rs.getString("teacher"),
            rs.getString("location"),
            rs.getBoolean("shared")
        );
    }

    private RowMapper<EnrollmentRecord> enrollmentMapper() {
        return (rs, rowNum) -> new EnrollmentRecord(
            rs.getString("id"),
            CollegeCode.valueOf(rs.getString("studentCollege")),
            rs.getString("studentId"),
            CollegeCode.valueOf(rs.getString("courseCollege")),
            rs.getString("courseId"),
            localDate(rs, "enrolledAt"),
            rs.getString("status"),
            rs.getString("score")
        );
    }

    private void assertCourseExists(String courseId) {
        Integer count = jdbc.queryForObject(
            "SELECT COUNT(*) FROM dbo.A_COURSE WHERE course_no = ?",
            Integer.class,
            courseId
        );
        if (count == null || count == 0) {
            throw new IllegalArgumentException("学院 A 不存在课程: " + courseId);
        }
    }

    private void assertLocalStudentExists(String studentId) {
        Integer count = jdbc.queryForObject(
            "SELECT COUNT(*) FROM dbo.A_STUDENT WHERE student_no = ?",
            Integer.class,
            studentId
        );
        if (count == null || count == 0) {
            throw new IllegalArgumentException("学院 A 不存在学生: " + studentId);
        }
    }

    private void upsertImportedStudent(StudentRecord sourceStudent) {
        Integer count = jdbc.queryForObject(
            "SELECT COUNT(*) FROM dbo.A_IMPORTED_STUDENT WHERE source_college = ? AND student_no = ?",
            Integer.class,
            sourceStudent.college().name(),
            sourceStudent.id()
        );
        if (count != null && count > 0) {
            jdbc.update(
                """
                UPDATE dbo.A_IMPORTED_STUDENT
                SET student_name = ?, gender_name = ?, major_name = ?
                WHERE source_college = ? AND student_no = ?
                """,
                sourceStudent.name(),
                sourceStudent.gender(),
                sourceStudent.major(),
                sourceStudent.college().name(),
                sourceStudent.id()
            );
            return;
        }

        jdbc.update(
            """
            INSERT INTO dbo.A_IMPORTED_STUDENT
                (source_college, student_no, student_name, gender_name, major_name, imported_on)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            sourceStudent.college().name(),
            sourceStudent.id(),
            sourceStudent.name(),
            sourceStudent.gender(),
            sourceStudent.major(),
            Date.valueOf(LocalDate.now())
        );
    }

    private LocalDate localDate(ResultSet rs, String columnName) throws SQLException {
        Date date = rs.getDate(columnName);
        return date == null ? null : date.toLocalDate();
    }
}

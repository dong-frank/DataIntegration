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
            SELECT id, college, name, credits, teacher, shared
            FROM dbo.vw_adapter_courses
            ORDER BY id
            """, courseMapper());
    }

    public List<EnrollmentRecord> enrollments() {
        return jdbc.query("""
            SELECT id, studentCollege, studentId, courseCollege, courseId, enrolledAt, status
            FROM dbo.vw_adapter_enrollments
            ORDER BY id
            """, enrollmentMapper());
    }

    public EnrollmentRecord createEnrollment(EnrollmentCreateRequest request) {
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
            "ACTIVE"
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
            rs.getDouble("credits"),
            rs.getString("teacher"),
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
            rs.getString("status")
        );
    }

    private LocalDate localDate(ResultSet rs, String columnName) throws SQLException {
        Date date = rs.getDate(columnName);
        return date == null ? null : date.toLocalDate();
    }
}

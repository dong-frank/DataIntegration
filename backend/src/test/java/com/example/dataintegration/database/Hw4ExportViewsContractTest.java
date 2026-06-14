package com.example.dataintegration.database;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

import org.junit.jupiter.api.Test;

class Hw4ExportViewsContractTest {

    @Test
    void sqlServerInitExposesHw4ExportViewsForCollegeA() throws IOException {
        assertHw4ExportViews(sqlServerInitSql(), "dbo.vw_hw4_", "A");
    }

    @Test
    void oracleInitExposesHw4ExportViewsForCollegeB() throws IOException {
        String sql = oracleInitSql();

        assertHw4ExportViews(sql, "vw_hw4_", "B");
        assertThat(sql).contains("'bacc' || LPAD(TO_CHAR(LEVEL), 6, '0')");
        assertThat(sql).doesNotContain("'bacc' || LPAD(TO_CHAR(LEVEL), 8, '0')");
        assertThat("bacc000001".length()).isLessThanOrEqualTo(10);
    }

    @Test
    void mysqlInitExposesHw4ExportViewsForCollegeC() throws IOException {
        String sql = mysqlInitSql();

        assertHw4ExportViews(sql, "vw_hw4_", "C");
        assertThat(sql).contains("Sno                                  AS account");
        assertThat(sql).contains("Pwd                                  AS password");
    }

    private void assertHw4ExportViews(String sql, String viewPrefix, String deptNo) {
        assertThat(sql)
            .contains(viewPrefix + "students")
            .contains(viewPrefix + "courses")
            .contains(viewPrefix + "sc")
            .contains("student_id")
            .contains("student_name")
            .contains("account")
            .contains("password")
            .contains("course_id")
            .contains("course_name")
            .contains("practice_hours")
            .contains("group_no")
            .contains("dept_no")
            .contains("'18'")
            .contains("'" + deptNo + "'");
    }

    private String sqlServerInitSql() throws IOException {
        return readSql("../database/sqlserver/init.sql", "database/sqlserver/init.sql");
    }

    private String oracleInitSql() throws IOException {
        return readSql("../database/oracle/init.sql", "database/oracle/init.sql");
    }

    private String mysqlInitSql() throws IOException {
        return readSql("../database/mysql/init.sql", "database/mysql/init.sql");
    }

    private String readSql(String backendRelativePath, String repoRelativePath) throws IOException {
        Path fromBackend = Path.of(backendRelativePath);
        Path path = Files.exists(fromBackend) ? fromBackend : Path.of(repoRelativePath);
        return Files.readString(path, StandardCharsets.UTF_8);
    }
}

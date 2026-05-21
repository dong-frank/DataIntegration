package com.example.dataintegration.database;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

import org.junit.jupiter.api.Test;

class SqlServerInitSqlContractTest {

    private static final Path INIT_SQL = Path.of("../database/sqlserver/init.sql");

    @Test
    void usesUnicodeColumnsAndLiteralsForChineseTeachingData() throws IOException {
        String sql = Files.readString(INIT_SQL, StandardCharsets.UTF_8);

        assertThat(sql).contains("student_name NVARCHAR(10)");
        assertThat(sql).contains("gender_name NVARCHAR(2)");
        assertThat(sql).contains("department_name NVARCHAR(10)");
        assertThat(sql).contains("course_name NVARCHAR(10)");
        assertThat(sql).contains("teacher_name NVARCHAR(10)");
        assertThat(sql).contains("teaching_place NVARCHAR(20)");
        assertThat(sql).contains("N'数据库系统'");
        assertThat(sql).contains("N'实验楼101'");
    }

    @Test
    void avoidsReservedOffsetCteNameWhenGeneratingSelections() throws IOException {
        String sql = Files.readString(INIT_SQL, StandardCharsets.UTF_8);

        assertThat(sql).contains("course_offsets AS");
        assertThat(sql).doesNotContain("\noffsets AS");
        assertThat(sql).contains("CROSS JOIN course_offsets");
    }
}

package com.example.dataintegration.database;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import org.junit.jupiter.api.Test;

class OracleInitSqlContractTest {

    @Test
    void genderColumnsUseCharacterLengthSemanticsForChineseValues() throws IOException {
        String sql = Files.readString(oracleInitSqlPath());

        assertThat(occurrencesOf(sql, "gender         VARCHAR2(2 CHAR)  NOT NULL"))
            .isEqualTo(2);
    }

    @Test
    void courseTextColumnsUseCharacterLengthSemanticsForChineseValues() throws IOException {
        String sql = Files.readString(oracleInitSqlPath());

        assertThat(sql).contains("course_name VARCHAR2(16 CHAR) NOT NULL");
        assertThat(sql).contains("location    VARCHAR2(20 CHAR) NOT NULL");
        assertThat(sql).contains("'商业数据分析'");
    }

    @Test
    void seedsMeaningfulChineseStudentNames() throws IOException {
        String sql = Files.readString(oracleInitSqlPath());

        assertThat(sql).contains("student_names AS");
        assertThat(sql).contains("'周'", "'景文'");
        assertThat(sql).doesNotContain("'B学生' ||");
    }

    private Path oracleInitSqlPath() {
        Path fromBackend = Path.of("../database/oracle/init.sql");
        if (Files.exists(fromBackend)) {
            return fromBackend;
        }
        return Path.of("database/oracle/init.sql");
    }

    private int occurrencesOf(String text, String needle) {
        return text.split(java.util.regex.Pattern.quote(needle), -1).length - 1;
    }
}

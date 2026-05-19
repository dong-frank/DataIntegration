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

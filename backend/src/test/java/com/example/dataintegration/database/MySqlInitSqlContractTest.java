package com.example.dataintegration.database;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

import org.junit.jupiter.api.Test;

class MySqlInitSqlContractTest {

    @Test
    void seedsMeaningfulChineseStudentNames() throws IOException {
        String sql = Files.readString(mysqlInitSqlPath(), StandardCharsets.UTF_8);

        assertThat(sql).contains("'苏知夏'", "'林知夏'");
        assertThat(sql).doesNotContain("'学生001'");
    }

    private Path mysqlInitSqlPath() {
        Path fromBackend = Path.of("../database/mysql/init.sql");
        if (Files.exists(fromBackend)) {
            return fromBackend;
        }
        return Path.of("database/mysql/init.sql");
    }
}

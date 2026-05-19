package com.example.dataintegration.config;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest(properties = "app.data-mode=mock")
class DatabaseConnectionPropertiesTest {

    @Autowired
    private DatabaseConnectionProperties properties;

    @Test
    void mysqlJdbcUrlAllowsPublicKeyRetrievalForLocalDocker() {
        assertThat(properties.getDatabases().get("C").getUrl())
            .contains("allowPublicKeyRetrieval=true");
    }
}

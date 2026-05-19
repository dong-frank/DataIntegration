package com.example.dataintegration.config;

import com.example.dataintegration.college.CollegeCode;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.JdbcOperations;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

@Configuration
@ConditionalOnProperty(name = "app.data-mode", havingValue = "database")
public class CollegeAJdbcConfig {

    @Bean
    public JdbcOperations collegeAJdbcTemplate(DatabaseConnectionProperties properties) {
        return jdbcTemplate(properties, CollegeCode.A);
    }

    @Bean
    public JdbcOperations collegeBJdbcTemplate(DatabaseConnectionProperties properties) {
        return jdbcTemplate(properties, CollegeCode.B);
    }

    @Bean
    public JdbcOperations collegeCJdbcTemplate(DatabaseConnectionProperties properties) {
        return jdbcTemplate(properties, CollegeCode.C);
    }

    private JdbcOperations jdbcTemplate(DatabaseConnectionProperties properties, CollegeCode college) {
        DatabaseConnectionProperties.JdbcEndpoint endpoint = properties.getDatabases().get(college.name());
        if (endpoint == null) {
            throw new IllegalStateException("Missing JDBC config for college " + college.name());
        }

        DriverManagerDataSource dataSource = new DriverManagerDataSource();
        dataSource.setDriverClassName(endpoint.getDriverClassName());
        dataSource.setUrl(endpoint.getUrl());
        dataSource.setUsername(endpoint.getUsername());
        dataSource.setPassword(endpoint.getPassword());
        return new JdbcTemplate(dataSource);
    }
}

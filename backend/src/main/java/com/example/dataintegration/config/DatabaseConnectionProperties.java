package com.example.dataintegration.config;

import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "app")
public class DatabaseConnectionProperties {

    private Map<String, JdbcEndpoint> databases = new LinkedHashMap<>();

    public Map<String, JdbcEndpoint> getDatabases() {
        return databases;
    }

    public void setDatabases(Map<String, JdbcEndpoint> databases) {
        this.databases = databases;
    }

    public static class JdbcEndpoint {
        private String dbms;
        private String driverClassName;
        private String url;
        private String username;
        private String password;

        public String getDbms() {
            return dbms;
        }

        public void setDbms(String dbms) {
            this.dbms = dbms;
        }

        public String getDriverClassName() {
            return driverClassName;
        }

        public void setDriverClassName(String driverClassName) {
            this.driverClassName = driverClassName;
        }

        public String getUrl() {
            return url;
        }

        public void setUrl(String url) {
            this.url = url;
        }

        public String getUsername() {
            return username;
        }

        public void setUsername(String username) {
            this.username = username;
        }

        public String getPassword() {
            return password;
        }

        public void setPassword(String password) {
            this.password = password;
        }
    }
}

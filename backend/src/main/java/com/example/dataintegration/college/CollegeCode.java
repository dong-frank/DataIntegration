package com.example.dataintegration.college;

public enum CollegeCode {
    A("学院A", "SQL Server"),
    B("学院B", "Oracle"),
    C("学院C", "MySQL");

    private final String displayName;
    private final String dbms;

    CollegeCode(String displayName, String dbms) {
        this.displayName = displayName;
        this.dbms = dbms;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getDbms() {
        return dbms;
    }
}

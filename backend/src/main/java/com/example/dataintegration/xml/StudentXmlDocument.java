package com.example.dataintegration.xml;

import java.util.List;
import java.util.stream.Collectors;

import com.example.dataintegration.college.StudentRecord;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "students")
public record StudentXmlDocument(
    @JacksonXmlProperty(localName = "student")
    @JacksonXmlElementWrapper(useWrapping = false)
    List<StudentXmlEntry> students
) {
    public static StudentXmlDocument from(List<StudentRecord> students) {
        return new StudentXmlDocument(students.stream()
            .map(student -> new StudentXmlEntry(
                student.id(),
                student.name(),
                student.gender(),
                student.major()
            ))
            .collect(Collectors.toList()));
    }

    @JsonPropertyOrder({ "id", "name", "gender", "major" })
    public record StudentXmlEntry(
        String id,
        String name,
        @JacksonXmlProperty(localName = "sex")
        String gender,
        String major
    ) {
    }
}

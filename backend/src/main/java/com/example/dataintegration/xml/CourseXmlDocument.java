package com.example.dataintegration.xml;

import java.util.List;
import java.util.stream.Collectors;

import com.example.dataintegration.college.CourseRecord;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "classes")
public record CourseXmlDocument(
    @JacksonXmlProperty(localName = "class")
    @JacksonXmlElementWrapper(useWrapping = false)
    List<CourseXmlEntry> courses
) {
    public static CourseXmlDocument from(List<CourseRecord> courses) {
        return new CourseXmlDocument(courses.stream()
            .map(course -> new CourseXmlEntry(
                course.id(),
                course.name(),
                course.hours(),
                (int) Math.round(course.credits()),
                course.teacher(),
                course.location()
            ))
            .collect(Collectors.toList()));
    }

    @JsonPropertyOrder({ "id", "name", "time", "score", "teacher", "location" })
    public record CourseXmlEntry(
        String id,
        String name,
        @JacksonXmlProperty(localName = "time")
        int time,
        @JacksonXmlProperty(localName = "score")
        int score,
        String teacher,
        String location
    ) {
    }
}

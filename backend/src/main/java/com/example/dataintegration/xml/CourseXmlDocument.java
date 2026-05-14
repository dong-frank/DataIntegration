package com.example.dataintegration.xml;

import java.util.List;

import com.example.dataintegration.college.CourseRecord;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "courses")
public record CourseXmlDocument(
    @JacksonXmlProperty(localName = "course")
    @JacksonXmlElementWrapper(useWrapping = false)
    List<CourseRecord> courses
) {
}

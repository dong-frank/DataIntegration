package com.example.dataintegration.xml;

import java.util.List;

import com.example.dataintegration.college.StudentRecord;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "students")
public record StudentXmlDocument(
    @JacksonXmlProperty(localName = "student")
    @JacksonXmlElementWrapper(useWrapping = false)
    List<StudentRecord> students
) {
}

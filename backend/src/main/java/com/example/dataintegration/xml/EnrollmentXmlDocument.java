package com.example.dataintegration.xml;

import java.util.List;

import com.example.dataintegration.college.EnrollmentRecord;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "enrollments")
public record EnrollmentXmlDocument(
    @JacksonXmlProperty(localName = "enrollment")
    @JacksonXmlElementWrapper(useWrapping = false)
    List<EnrollmentRecord> enrollments
) {
}

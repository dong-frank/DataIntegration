package com.example.dataintegration.xml;

import java.util.List;

import com.example.dataintegration.college.CollegeCode;
import com.example.dataintegration.integration.EnrollmentCreateRequest;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "enrollmentRequests")
public record EnrollmentRequestsXmlDocument(
    @JacksonXmlProperty(localName = "enrollmentRequest")
    @JacksonXmlElementWrapper(useWrapping = false)
    List<EnrollmentRequestXmlEntry> requests
) {
    public List<EnrollmentCreateRequest> toCreateRequests() {
        if (requests == null) {
            return List.of();
        }
        return requests.stream().map(EnrollmentRequestXmlEntry::toCreateRequest).toList();
    }

    @JsonPropertyOrder({ "studentCollege", "studentId", "courseCollege", "courseId" })
    public record EnrollmentRequestXmlEntry(
        String studentCollege,
        String studentId,
        String courseCollege,
        String courseId
    ) {
        public EnrollmentCreateRequest toCreateRequest() {
            return new EnrollmentCreateRequest(
                CollegeCode.valueOf(studentCollege),
                studentId,
                CollegeCode.valueOf(courseCollege),
                courseId
            );
        }
    }
}

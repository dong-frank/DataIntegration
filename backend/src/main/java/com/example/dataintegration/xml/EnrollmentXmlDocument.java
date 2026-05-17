package com.example.dataintegration.xml;

import java.util.List;
import java.util.stream.Collectors;

import com.example.dataintegration.college.EnrollmentRecord;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "choices")
public record EnrollmentXmlDocument(
    @JacksonXmlProperty(localName = "choice")
    @JacksonXmlElementWrapper(useWrapping = false)
    List<EnrollmentXmlEntry> enrollments
) {
    public static EnrollmentXmlDocument from(List<EnrollmentRecord> enrollments) {
        return new EnrollmentXmlDocument(enrollments.stream()
            .map(enrollment -> new EnrollmentXmlEntry(
                enrollment.studentId(),
                enrollment.courseId(),
                parseScore(enrollment.score())
            ))
            .collect(Collectors.toList()));
    }

    private static int parseScore(String score) {
        if (score == null || score.isBlank()) {
            return 0;
        }
        try {
            return Integer.parseInt(score);
        } catch (NumberFormatException error) {
            return 0;
        }
    }

    @JsonPropertyOrder({ "sid", "cid", "score" })
    public record EnrollmentXmlEntry(
        String sid,
        String cid,
        int score
    ) {
    }
}

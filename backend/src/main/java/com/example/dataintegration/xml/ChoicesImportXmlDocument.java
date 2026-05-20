package com.example.dataintegration.xml;

import java.util.List;
import java.util.Optional;

import com.example.dataintegration.college.CollegeCode;
import com.example.dataintegration.integration.EnrollmentCreateRequest;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "choices")
public record ChoicesImportXmlDocument(
    @JacksonXmlProperty(localName = "choice")
    @JacksonXmlElementWrapper(useWrapping = false)
    List<ChoiceImportEntry> choices
) {
    public List<EnrollmentCreateRequest> toCreateRequests(CollegeCode defaultCollege) {
        if (choices == null) {
            return List.of();
        }
        return choices.stream()
            .map(choice -> choice.toCreateRequest(defaultCollege))
            .toList();
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    @JsonPropertyOrder({
        "studentCollege", "studentId", "courseCollege", "courseId", "score",
        "sid", "cid"
    })
    public record ChoiceImportEntry(
        String studentCollege,
        String studentId,
        String courseCollege,
        String courseId,
        Integer score,
        String sid,
        String cid
    ) {
        public EnrollmentCreateRequest toCreateRequest(CollegeCode defaultCollege) {
            if (studentCollege != null && studentId != null && courseCollege != null && courseId != null) {
                return new EnrollmentCreateRequest(
                    CollegeCode.valueOf(studentCollege),
                    studentId,
                    CollegeCode.valueOf(courseCollege),
                    courseId
                );
            }
            if (sid == null || cid == null) {
                throw new IllegalArgumentException("choice 须为导出格式(sid/cid/score)或导入格式(studentCollege/.../courseId)");
            }
            CollegeCode college = Optional.ofNullable(defaultCollege)
                .orElseThrow(() -> new IllegalArgumentException("本院 sid/cid 格式导入须指定 college 查询参数"));
            return new EnrollmentCreateRequest(college, sid, college, cid);
        }
    }
}

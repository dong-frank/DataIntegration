package com.example.dataintegration.xml;

import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import org.junit.jupiter.api.Test;
import org.springframework.web.server.ResponseStatusException;

class XmlSchemaValidationServiceTest {

    private final XmlSchemaValidationService validationService = new XmlSchemaValidationService();

    @Test
    void acceptsEnrollmentRequestDocument() {
        String xml = """
            <enrollmentRequests>
              <enrollmentRequest>
                <studentCollege>A</studentCollege>
                <studentId>A-S001</studentId>
                <courseCollege>B</courseCollege>
                <courseId>B-C001</courseId>
              </enrollmentRequest>
            </enrollmentRequests>
            """;

        assertThatCode(() -> validationService.validate(xml)).doesNotThrowAnyException();
    }

    @Test
    void acceptsCrossCollegeChoiceImportDocument() {
        String xml = """
            <choices>
              <choice>
                <studentCollege>B</studentCollege>
                <studentId>B-S001</studentId>
                <courseCollege>C</courseCollege>
                <courseId>C-C001</courseId>
              </choice>
            </choices>
            """;

        assertThatCode(() -> validationService.validate(xml)).doesNotThrowAnyException();
    }

    @Test
    void rejectsInvalidRootElement() {
        assertThatThrownBy(() -> validationService.validate("<invalid/>"))
            .isInstanceOf(ResponseStatusException.class)
            .hasMessageContaining("academic-integration.xsd");
    }
}

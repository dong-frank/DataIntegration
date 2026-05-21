package com.example.dataintegration.xml;

import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.assertj.core.api.Assertions.assertThat;

import javax.xml.validation.Validator;

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
    void acceptsWithdrawRequestDocument() {
        String xml = """
            <withdrawRequests>
              <withdrawRequest>
                <enrollmentId>B0001-202300001</enrollmentId>
              </withdrawRequest>
            </withdrawRequests>
            """;

        assertThatCode(() -> validationService.validate(xml)).doesNotThrowAnyException();
    }

    @Test
    void validatesCollegeSpecificXmlAgainstLocalSchema() {
        String xml = """
            <Choices>
              <choice>
                <学生编号>202300001</学生编号>
                <课程编号>B0001</课程编号>
                <得分>0</得分>
              </choice>
            </Choices>
            """;

        assertThatCode(() -> validationService.validate(xml, "schemas/local/choiceB.xsd"))
            .doesNotThrowAnyException();
    }

    @Test
    void rejectsInvalidRootElement() {
        assertThatThrownBy(() -> validationService.validate("<invalid/>"))
            .isInstanceOf(ResponseStatusException.class)
            .hasMessageContaining("academic-integration.xsd");
    }

    @Test
    void doesNotReuseValidatorInstancesAcrossRequests() {
        assertThat(XmlSchemaValidationService.class.getDeclaredFields())
            .noneMatch(field -> field.getType().equals(Validator.class));
    }
}

package com.example.dataintegration.xml;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import com.example.dataintegration.college.AcademicDataService;
import com.example.dataintegration.college.CollegeCode;
import com.example.dataintegration.college.EnrollmentRecord;
import com.example.dataintegration.integration.EnrollmentCreateRequest;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.dataformat.xml.XmlMapper;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class XmlImportService {

    private final XmlSchemaValidationService validationService;
    private final AcademicDataService dataService;
    private final XmlMapper xmlMapper;

    public XmlImportService(XmlSchemaValidationService validationService, AcademicDataService dataService) {
        this.validationService = validationService;
        this.dataService = dataService;
        this.xmlMapper = new XmlMapper();
        this.xmlMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        this.xmlMapper.findAndRegisterModules();
    }

    public List<EnrollmentRecord> importEnrollments(String xml, Optional<CollegeCode> defaultCollege) {
        validationService.validate(xml);
        List<EnrollmentCreateRequest> requests = parseRequests(xml, defaultCollege);
        if (requests.isEmpty()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "XML 中未包含可导入的选课记录");
        }
        List<EnrollmentRecord> created = new ArrayList<>();
        for (EnrollmentCreateRequest request : requests) {
            created.add(dataService.createEnrollment(request));
        }
        return created;
    }

    private List<EnrollmentCreateRequest> parseRequests(String xml, Optional<CollegeCode> defaultCollege) {
        String trimmed = xml.strip();
        try {
            if (trimmed.contains("<enrollmentRequests")) {
                EnrollmentRequestsXmlDocument document = xmlMapper.readValue(trimmed, EnrollmentRequestsXmlDocument.class);
                return document.toCreateRequests();
            }
            if (trimmed.contains("<choices")) {
                ChoicesImportXmlDocument document = xmlMapper.readValue(trimmed, ChoicesImportXmlDocument.class);
                return document.toCreateRequests(defaultCollege.orElse(null));
            }
        } catch (JsonProcessingException error) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "XML 解析失败: " + error.getOriginalMessage(), error);
        } catch (IllegalArgumentException error) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, error.getMessage(), error);
        }
        throw new ResponseStatusException(
            HttpStatus.BAD_REQUEST,
            "不支持的 XML 根元素，请使用 <choices> 或 <enrollmentRequests>"
        );
    }
}

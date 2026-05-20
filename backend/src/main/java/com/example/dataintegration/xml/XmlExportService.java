package com.example.dataintegration.xml;

import com.example.dataintegration.college.AcademicDataService;
import com.example.dataintegration.college.CollegeCode;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.dataformat.xml.XmlMapper;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class XmlExportService {

    private final AcademicDataService dataService;
    private final XmlSchemaValidationService validationService;
    private final XmlMapper xmlMapper = new XmlMapper();

    public XmlExportService(AcademicDataService dataService, XmlSchemaValidationService validationService) {
        this.dataService = dataService;
        this.validationService = validationService;
        this.xmlMapper.findAndRegisterModules();
    }

    public String export(CollegeCode college, String type) {
        Object document = switch (type) {
            case "students" -> StudentXmlDocument.from(dataService.students(college));
            case "courses" -> CourseXmlDocument.from(dataService.courses(college));
            case "enrollments" -> EnrollmentXmlDocument.from(dataService.enrollments(college));
            default -> throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "不支持的 XML 类型: " + type);
        };

        try {
            String xml = xmlMapper.writeValueAsString(document);
            validationService.validate(xml);
            return xml;
        } catch (JsonProcessingException error) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "XML 导出失败", error);
        }
    }
}

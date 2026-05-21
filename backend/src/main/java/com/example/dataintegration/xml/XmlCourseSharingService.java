package com.example.dataintegration.xml;

import java.util.List;
import java.util.Optional;

import com.example.dataintegration.college.AcademicDataService;
import com.example.dataintegration.college.CollegeCode;
import com.example.dataintegration.college.CourseRecord;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.dataformat.xml.XmlMapper;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class XmlCourseSharingService {

    private final AcademicDataService dataService;
    private final XmlSchemaValidationService validationService;
    private final XmlTransformService transformService;
    private final XmlMapper xmlMapper = new XmlMapper();

    public XmlCourseSharingService(
        AcademicDataService dataService,
        XmlSchemaValidationService validationService,
        XmlTransformService transformService
    ) {
        this.dataService = dataService;
        this.validationService = validationService;
        this.transformService = transformService;
        this.xmlMapper.findAndRegisterModules();
    }

    public String sharedCoursesForTarget(Optional<CollegeCode> source, CollegeCode target) {
        List<CourseRecord> courses = dataService.sharedCourses(source);
        try {
            String unifiedXml = xmlMapper.writeValueAsString(CourseXmlDocument.from(courses));
            validationService.validate(unifiedXml);

            String targetXml = transformService.transformCoursesToCollege(unifiedXml, target);
            validationService.validate(targetXml, transformService.localSchemaPath("class", target));
            return targetXml;
        } catch (JsonProcessingException error) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "共享课程 XML 生成失败", error);
        }
    }
}

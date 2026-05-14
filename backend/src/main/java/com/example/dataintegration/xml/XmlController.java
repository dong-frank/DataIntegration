package com.example.dataintegration.xml;

import com.example.dataintegration.college.CollegeCode;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/xml/{college}")
public class XmlController {

    private final XmlExportService xmlExportService;

    public XmlController(XmlExportService xmlExportService) {
        this.xmlExportService = xmlExportService;
    }

    @GetMapping(value = "/{type}", produces = MediaType.APPLICATION_XML_VALUE)
    public String export(@PathVariable CollegeCode college, @PathVariable String type) {
        return xmlExportService.export(college, type);
    }
}

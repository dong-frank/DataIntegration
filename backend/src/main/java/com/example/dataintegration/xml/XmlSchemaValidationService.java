package com.example.dataintegration.xml;

import java.io.IOException;
import java.io.StringReader;

import javax.xml.XMLConstants;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;

import org.springframework.core.io.ClassPathResource;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import org.xml.sax.SAXException;

@Service
public class XmlSchemaValidationService {

    private static final String XSD_PATH = "academic-integration.xsd";

    private final Schema schema;

    public XmlSchemaValidationService() {
        this.schema = loadSchema(XSD_PATH);
    }

    public void validate(String xml) {
        validate(xml, schema, XSD_PATH);
    }

    public void validate(String xml, String schemaPath) {
        validate(xml, loadSchema(schemaPath), schemaPath);
    }

    private static void validate(String xml, Schema schema, String schemaPath) {
        try {
            Validator validator = schema.newValidator();
            validator.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "");
            validator.setProperty(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "");
            validator.validate(new StreamSource(new StringReader(xml)));
        } catch (SAXException error) {
            throw new ResponseStatusException(
                HttpStatus.BAD_REQUEST,
                "XML 未通过 " + schemaPath + " 校验: " + error.getMessage(),
                error
            );
        } catch (IOException error) {
            throw new ResponseStatusException(
                HttpStatus.BAD_REQUEST,
                "XML 校验失败: " + error.getMessage(),
                error
            );
        }
    }

    private static Schema loadSchema(String schemaPath) {
        try (var inputStream = new ClassPathResource(schemaPath).getInputStream()) {
            var schemaSource = new StreamSource(inputStream);
            schemaSource.setSystemId("classpath:" + schemaPath);
            SchemaFactory factory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
            factory.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "");
            factory.setProperty(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "");
            return factory.newSchema(schemaSource);
        } catch (IOException | SAXException error) {
            throw new IllegalStateException("无法加载 XSD: " + schemaPath, error);
        }
    }
}

package com.example.dataintegration.xml;

import java.io.StringReader;
import java.io.StringWriter;

import javax.xml.XMLConstants;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;

import com.example.dataintegration.college.CollegeCode;

import org.springframework.core.io.ClassPathResource;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class XmlTransformService {

    public String transform(String xml, String stylesheetPath) {
        try (var stylesheet = new ClassPathResource(stylesheetPath).getInputStream()) {
            TransformerFactory factory = TransformerFactory.newInstance();
            disableExternalAccess(factory);

            StreamSource stylesheetSource = new StreamSource(stylesheet);
            stylesheetSource.setSystemId("classpath:" + stylesheetPath);
            var transformer = factory.newTransformer(stylesheetSource);

            StringWriter output = new StringWriter();
            transformer.transform(
                new StreamSource(new StringReader(xml)),
                new StreamResult(output)
            );
            return output.toString();
        } catch (Exception error) {
            throw new ResponseStatusException(
                HttpStatus.BAD_REQUEST,
                "XML XSLT 转换失败: " + stylesheetPath,
                error
            );
        }
    }

    public String transformCoursesToCollege(String unifiedXml, CollegeCode target) {
        return transform(unifiedXml, "xslt/classTo%s.xsl".formatted(target.name()));
    }

    public String transformChoicesToCollege(String unifiedXml, CollegeCode target) {
        return transform(unifiedXml, "xslt/choiceTo%s.xsl".formatted(target.name()));
    }

    public String localSchemaPath(String type, CollegeCode target) {
        return "schemas/local/%s%s.xsd".formatted(type, target.name());
    }

    private static void disableExternalAccess(TransformerFactory factory) throws TransformerException {
        factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
        setAttributeIfSupported(factory, XMLConstants.ACCESS_EXTERNAL_DTD, "");
        setAttributeIfSupported(factory, XMLConstants.ACCESS_EXTERNAL_STYLESHEET, "");
    }

    private static void setAttributeIfSupported(TransformerFactory factory, String name, String value) {
        try {
            factory.setAttribute(name, value);
        } catch (IllegalArgumentException ignored) {
            // Some JAXP implementations do not expose these attributes.
        }
    }
}

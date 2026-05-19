package com.example.dataintegration;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.hasSize;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import com.example.dataintegration.college.CollegeCode;
import com.example.dataintegration.xml.XmlSchemaValidationService;

@SpringBootTest(properties = "app.data-mode=mock")
@AutoConfigureMockMvc
class ApiContractTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private XmlSchemaValidationService xmlSchemaValidationService;

    @Test
    void healthEndpointReturnsOkStatus() throws Exception {
        mockMvc.perform(get("/api/health"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data.status").value("UP"));
    }

    @Test
    void loginReturnsRoleAndCollegeForCollegeUser() throws Exception {
        mockMvc.perform(post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"username":"college-a","password":"password"}
                    """))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.role").value("COLLEGE"))
            .andExpect(jsonPath("$.data.college").value("A"));
    }

    @Test
    void collegeEndpointsExposeSeededTeachingData() throws Exception {
        mockMvc.perform(get("/api/college/A/students"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data", hasSize(50)));

        mockMvc.perform(get("/api/college/A/courses"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data", hasSize(10)))
            .andExpect(jsonPath("$.data[0].hours").exists())
            .andExpect(jsonPath("$.data[0].location").exists());

        mockMvc.perform(get("/api/college/A/enrollments"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data", hasSize(250)))
            .andExpect(jsonPath("$.data[0].score").exists());
    }

    @Test
    void integrationStatsSummarizeAllColleges() throws Exception {
        mockMvc.perform(get("/api/integration/stats"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.totalStudents").value(150))
            .andExpect(jsonPath("$.data.totalCourses").value(30))
            .andExpect(jsonPath("$.data.totalEnrollments").value(750));
    }

    @ParameterizedTest
    @EnumSource(CollegeCode.class)
    void xmlExportForAllCollegesPassesXsd(CollegeCode college) throws Exception {
        String studentXml = mockMvc.perform(get("/api/xml/{college}/students", college))
            .andExpect(status().isOk())
            .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_XML))
            .andExpect(content().string(containsString("<students>")))
            .andReturn()
            .getResponse()
            .getContentAsString();
        assertTrue(studentXml.contains("<sex>"));
        xmlSchemaValidationService.validate(studentXml);

        String courseXml = mockMvc.perform(get("/api/xml/{college}/courses", college))
            .andExpect(status().isOk())
            .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_XML))
            .andExpect(content().string(containsString("<classes>")))
            .andReturn()
            .getResponse()
            .getContentAsString();
        assertTrue(courseXml.contains("<time>"));
        assertTrue(courseXml.contains("<location>"));
        xmlSchemaValidationService.validate(courseXml);

        String enrollmentXml = mockMvc.perform(get("/api/xml/{college}/enrollments", college))
            .andExpect(status().isOk())
            .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_XML))
            .andExpect(content().string(containsString("<choices>")))
            .andReturn()
            .getResponse()
            .getContentAsString();
        assertTrue(enrollmentXml.contains("<sid>"));
        assertTrue(enrollmentXml.contains("<cid>"));
        assertTrue(enrollmentXml.contains("<score>"));
        xmlSchemaValidationService.validate(enrollmentXml);
    }

    @Test
    void enrollmentImportFromXmlValidatesBeforeProcessing() throws Exception {
        mockMvc.perform(post("/api/integration/enrollments")
                .contentType(MediaType.APPLICATION_XML)
                .content("""
                    <enrollmentRequests>
                      <enrollmentRequest>
                        <studentCollege>A</studentCollege>
                        <studentId>A-S001</studentId>
                        <courseCollege>B</courseCollege>
                        <courseId>B-C001</courseId>
                      </enrollmentRequest>
                    </enrollmentRequests>
                    """))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data", hasSize(1)))
            .andExpect(jsonPath("$.data[0].studentCollege").value("A"))
            .andExpect(jsonPath("$.data[0].courseCollege").value("B"));
    }

    @Test
    void enrollmentImportRejectsInvalidXml() throws Exception {
        mockMvc.perform(post("/api/integration/enrollments")
                .contentType(MediaType.APPLICATION_XML)
                .content("<not-a-contract/>"))
            .andExpect(status().isBadRequest());
    }

    @Test
    void withdrawalEndpointAcceptsExistingEnrollmentId() throws Exception {
        mockMvc.perform(delete("/api/integration/enrollments/A-E0001"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.withdrawn").value(true));
    }

}

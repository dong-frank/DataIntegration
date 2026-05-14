package com.example.dataintegration;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class ApiContractTest {

    @Autowired
    private MockMvc mockMvc;

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
            .andExpect(jsonPath("$.data", hasSize(10)));

        mockMvc.perform(get("/api/college/A/enrollments"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data", hasSize(250)));
    }

    @Test
    void integrationStatsSummarizeAllColleges() throws Exception {
        mockMvc.perform(get("/api/integration/stats"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.totalStudents").value(150))
            .andExpect(jsonPath("$.data.totalCourses").value(30))
            .andExpect(jsonPath("$.data.totalEnrollments").value(750));
    }

    @Test
    void xmlExportEndpointReturnsXmlForStudentsCoursesAndEnrollments() throws Exception {
        mockMvc.perform(get("/api/xml/A/students"))
            .andExpect(status().isOk())
            .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_XML))
            .andExpect(content().string(containsString("<students>")));

        mockMvc.perform(get("/api/xml/A/courses"))
            .andExpect(status().isOk())
            .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_XML))
            .andExpect(content().string(containsString("<courses>")));

        mockMvc.perform(get("/api/xml/A/enrollments"))
            .andExpect(status().isOk())
            .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_XML))
            .andExpect(content().string(containsString("<enrollments>")));
    }

    @Test
    void withdrawalEndpointAcceptsExistingEnrollmentId() throws Exception {
        mockMvc.perform(delete("/api/integration/enrollments/A-E0001"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.withdrawn").value(true));
    }
}

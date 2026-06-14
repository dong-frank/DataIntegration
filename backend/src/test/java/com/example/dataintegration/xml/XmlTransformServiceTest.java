package com.example.dataintegration.xml;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class XmlTransformServiceTest {

    private final XmlTransformService transformService = new XmlTransformService();

    @Test
    void transformsUnifiedCourseXmlToCollegeAFormatWithXslt() {
        String transformed = transformService.transform("""
            <classes>
              <class>
                <id>B0001</id>
                <name>数据库系统</name>
                <time>48</time>
                <score>3</score>
                <teacher>B教师01</teacher>
                <location>实验楼101</location>
              </class>
            </classes>
            """, "xslt/classToA.xsl");

        assertThat(transformed)
            .contains("<Classes>")
            .contains("<课程编号>B0001</课程编号>")
            .contains("<课程名称>数据库系统</课程名称>")
            .contains("<课时>48</课时>")
            .contains("<学分>3</学分>")
            .contains("<授课老师>B教师01</授课老师>")
            .contains("<授课地点>实验楼101</授课地点>");
    }

    @Test
    void transformsCollegeCChoiceXmlToUnifiedChoiceFormatWithXslt() {
        String transformed = transformService.transform("""
            <Choices>
              <choice>
                <Sno>202300001</Sno>
                <Cno>C001</Cno>
                <Grd>88</Grd>
              </choice>
            </Choices>
            """, "xslt/formatClassChoice.xsl");

        assertThat(transformed)
            .contains("<choices>")
            .contains("<sid>202300001</sid>")
            .contains("<cid>C001</cid>")
            .contains("<score>88</score>");
    }
}

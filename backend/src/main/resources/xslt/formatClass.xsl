<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="UTF-8" omit-xml-declaration="yes"/>
  <xsl:template match="/">
    <classes>
      <xsl:for-each select="//*[local-name()='class']">
        <class>
          <id><xsl:value-of select="*[local-name()='课程编号' or local-name()='编号' or local-name()='Cno' or local-name()='id'][1]"/></id>
          <name><xsl:value-of select="*[local-name()='课程名称' or local-name()='名称' or local-name()='Cnm' or local-name()='name'][1]"/></name>
          <time>
            <xsl:choose>
              <xsl:when test="*[local-name()='课时' or local-name()='学时' or local-name()='Ctm' or local-name()='time']">
                <xsl:value-of select="*[local-name()='课时' or local-name()='学时' or local-name()='Ctm' or local-name()='time'][1]"/>
              </xsl:when>
              <xsl:otherwise>1</xsl:otherwise>
            </xsl:choose>
          </time>
          <score><xsl:value-of select="*[local-name()='学分' or local-name()='Cpt' or local-name()='score'][1]"/></score>
          <teacher><xsl:value-of select="*[local-name()='授课老师' or local-name()='老师' or local-name()='Tec' or local-name()='teacher'][1]"/></teacher>
          <location><xsl:value-of select="*[local-name()='授课地点' or local-name()='地点' or local-name()='Pla' or local-name()='location'][1]"/></location>
        </class>
      </xsl:for-each>
    </classes>
  </xsl:template>
</xsl:stylesheet>

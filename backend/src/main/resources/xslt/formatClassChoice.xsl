<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="UTF-8" omit-xml-declaration="yes"/>
  <xsl:template match="/">
    <choices>
      <xsl:for-each select="//*[local-name()='choice']">
        <choice>
          <sid><xsl:value-of select="*[local-name()='学号' or local-name()='学生编号' or local-name()='Sno' or local-name()='sid'][1]"/></sid>
          <cid><xsl:value-of select="*[local-name()='课程编号' or local-name()='Cno' or local-name()='cid'][1]"/></cid>
          <score><xsl:value-of select="*[local-name()='成绩' or local-name()='得分' or local-name()='Grd' or local-name()='score'][1]"/></score>
        </choice>
      </xsl:for-each>
    </choices>
  </xsl:template>
</xsl:stylesheet>

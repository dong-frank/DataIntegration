<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="UTF-8" omit-xml-declaration="yes"/>
  <xsl:template match="/">
    <students>
      <xsl:for-each select="//*[local-name()='student']">
        <student>
          <id><xsl:value-of select="*[local-name()='学号' or local-name()='Sno' or local-name()='id'][1]"/></id>
          <name><xsl:value-of select="*[local-name()='姓名' or local-name()='名臣' or local-name()='Snm' or local-name()='name'][1]"/></name>
          <sex><xsl:value-of select="*[local-name()='性别' or local-name()='Sex' or local-name()='sex'][1]"/></sex>
          <major><xsl:value-of select="*[local-name()='院系' or local-name()='专业' or local-name()='Sde' or local-name()='major'][1]"/></major>
        </student>
      </xsl:for-each>
    </students>
  </xsl:template>
</xsl:stylesheet>

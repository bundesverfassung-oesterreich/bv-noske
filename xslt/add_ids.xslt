<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns="http://www.tei-c.org/ns/1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0"
                xmlns:xs="http://www.w3.org/2001/XMLSchema" version="2.0" exclude-result-prefixes="#all">
    <xsl:output encoding="UTF-8" media-type="text/xml" method="xml" version="1.0" indent="yes"
                omit-xml-declaration="yes"/>
    <xsl:template match="text() | @* | //text()[not(ancestor::tei:body)]">
        <xsl:copy>
            <xsl:apply-templates select="node() | @*"/>
        </xsl:copy>
    </xsl:template>
    <xsl:variable name="docbased_prefix" as="xs:string" select="substring-before(tokenize(base-uri(), '/')[last()], '.xml')"/>
    <xsl:template match="*">
        <xsl:copy>
            <xsl:if test="local-name()=('p', 'div', 'w', 'label', 'pc', 'item') and ancestor::tei:body and not(@xml:id)">
                <xsl:attribute name="xml:id">
                    <xsl:value-of select="concat($docbased_prefix, '_', generate-id())"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:apply-templates select="node() | @*"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>

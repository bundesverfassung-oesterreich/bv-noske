<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns="http://www.w3.org/1999/xhtml"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" version="2.0" exclude-result-prefixes="#all">
    <xsl:output encoding="UTF-8" media-type="text/xml" method="xml" version="1.0" indent="yes"
        omit-xml-declaration="yes"/>
    <xsl:template match="* | @* | //text()[not(ancestor::tei:body)]">
        <xsl:copy>
            <xsl:apply-templates select="node() | @*"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="//tei:body//text()">
        <xsl:for-each select="tokenize(., '\s+')">
            <xsl:choose>
                <xsl:when test="matches(., '[0-9]+\.|Art\.|\.{2}')">
                    <w>
                        <xsl:value-of select="."/>
                    </w>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:analyze-string select="." regex="[,;?!()\[\]§/.:]+|^-$">
                        <xsl:matching-substring>
                            <pc>
                                <xsl:value-of select="."/>
                            </pc>
                        </xsl:matching-substring>
                        <xsl:non-matching-substring>
                            <w>
                                <xsl:value-of select="."/>
                            </w>
                        </xsl:non-matching-substring>
                    </xsl:analyze-string>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:for-each>
    </xsl:template>
    <xsl:template match="tei:fw"/>
    <xsl:template match="tei:del"/>
    <xsl:template match="tei:sic"/>
</xsl:stylesheet>

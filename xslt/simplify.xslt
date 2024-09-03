<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns="http://www.tei-c.org/ns/1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0"
                xmlns:xs="http://www.w3.org/2001/XMLSchema" version="2.0" exclude-result-prefixes="#all">
    <xsl:output encoding="UTF-8" media-type="text/xml" method="xml" version="1.0" indent="yes"
                omit-xml-declaration="yes"/>
    <xsl:template match="* | @* | //text()[not(ancestor::tei:body or ancestor::tei:p or ancestor::tei:item)]">
        <xsl:copy>
            <xsl:apply-templates select="node() | @*"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="tei:body//tei:p|tei:body//tei:item|tei:body//tei:div">
        <xsl:variable name="head_id">
            <xsl:value-of select="./tei:head/@xml:id"/>
        </xsl:variable>
        <xsl:copy>
            <xsl:if test="$head_id!=''">
                <xsl:attribute name="xml:id" select="$head_id"/> 
            </xsl:if>
            <xsl:choose>
                <xsl:when test="local-name()='div'">
                    <xsl:apply-templates/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="normalize-space()"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="tei:head/@xml:id"/>
    <xsl:template match="tei:fw"/>
    <xsl:template match="tei:del"/>
    <xsl:template match="tei:sic"/>
    <xsl:template match="tei:pb"/>
    <xsl:template match="tei:lb"/>
    <xsl:template match="tei:facsimile"/>
    <xsl:template match="tei:funder"/>
    <xsl:template match="tei:respStmt"/>
</xsl:stylesheet>

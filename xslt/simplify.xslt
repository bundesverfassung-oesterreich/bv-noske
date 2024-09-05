<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns="http://www.tei-c.org/ns/1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0"
                xmlns:xs="http://www.w3.org/2001/XMLSchema" version="2.0" exclude-result-prefixes="#all">
    <xsl:output encoding="UTF-8" media-type="text/xml" method="xml" version="1.0" indent="yes"
                omit-xml-declaration="yes"/>
    <!-- top elements -->
    <!-- copy the root -->
    <xsl:template match="tei:TEI">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>
    <!-- keep the header -->
    <xsl:template match="tei:teiHeader">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates mode="header"/>
        </xsl:copy>
    </xsl:template>
    <!-- and its child elements -->
    <xsl:template match="node() | @*" mode="header">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates mode="header"/>
        </xsl:copy>
    </xsl:template>
    <!-- kill the facs -->
    <xsl:template match="tei:facsimile"/>
    <!-- process the body -->
    <xsl:template match="tei:text">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates mode="body"/>
        </xsl:copy>
    </xsl:template>
    <!-- text handling -->
    <xsl:template match="text()" mode="body">
        <xsl:value-of select="normalize-space()"/>
    </xsl:template>
    <!-- structure templates -->
    <xsl:template match="tei:body" mode="body">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates mode="body"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="tei:list" mode="body">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates mode="body"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="tei:item" mode="body">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates mode="body"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="tei:label" mode="body">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates mode="body"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="tei:head" mode="body">
        <xsl:copy>
            <xsl:apply-templates mode="body"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="tei:note" mode="body">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates mode="body"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="tei:div" mode="body">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:call-template name="get_id"/>
            <xsl:apply-templates mode="body"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="tei:p" mode="body">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:call-template name="get_id"/>
            <xsl:apply-templates mode="body"/>
        </xsl:copy>
    </xsl:template>
    <!-- keep contents but ignore tag (no copy) -->
    <xsl:template match="tei:choice" mode="body">
        <xsl:apply-templates mode="body"/>
    </xsl:template>
    <xsl:template match="tei:corr" mode="body">
        <xsl:apply-templates mode="body"/>
    </xsl:template>
    <xsl:template match="tei:emph" mode="body">
        <xsl:apply-templates mode="body"/>
    </xsl:template>
    <xsl:template match="tei:add" mode="body">
        <xsl:apply-templates mode="body"/>
    </xsl:template>
    <!-- killer templates -->
    <xsl:template match="tei:gap" mode="body"/>
    <xsl:template match="tei:fw" mode="body"/>
    <xsl:template match="tei:del" mode="body"/>
    <xsl:template match="tei:sic" mode="body"/>
    <xsl:template match="tei:pb" mode="body"/>
    <xsl:template match="tei:lb" mode="body"/>
    <xsl:template match="tei:funder" mode="header"/>
    <xsl:template match="tei:respStmt" mode="header"/>
    
    <!-- head ids handling -->
    <xsl:template name="get_id">
        <xsl:variable name="head_id">
            <xsl:value-of select="./tei:head/@xml:id"/>
        </xsl:variable>
        <xsl:if test="$head_id!=''">
            <xsl:attribute name="xml:id" select="$head_id"/> 
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>

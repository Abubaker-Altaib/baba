<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fo="http://www.w3.org/1999/XSL/Format">

    <xsl:import href="budget_custom_rml.xsl"/>

    <xsl:template match="//report/page">
		<xsl:if test="attribute::size='A3_landscape'">
			<xsl:call-template name="A3_landscape" />
		</xsl:if>	
		<xsl:if test="attribute::size='A3_portrait'">
			<xsl:call-template name="A3_portrait" />
		</xsl:if>		
		<xsl:if test="attribute::size='A4_landscape'">
			<xsl:call-template name="A4_landscape" />
		</xsl:if>
		<xsl:if test="attribute::size='A4_portrait'">
			<xsl:call-template name="A4_portrait" />
		</xsl:if>
	</xsl:template>
					
    <!-- xsl:template match="/">
        <xsl:call-template name="rml" />
    </xsl:template-->

    <xsl:template name="stylesheet">
		<paraStyle name="Tilte" fontName="Helvetica-Bold" fontSize="14.0" alignment="CENTER" spaceBefore="12.0" spaceAfter="6.0"/>
		<paraStyle name="Header_Table_Header_Centre" fontName="Helvetica-Bold" fontSize="9.0" alignment="CENTER"/>
		<paraStyle name="Header_Table_Detail_Centre" fontName="Helvetica" fontSize="9.0" alignment="CENTER"/>
		<paraStyle name="Content_Table_Detail_Bold" fontName="Helvetica-Bold" fontSize="8.0" alignment="CENTER"/>
		<paraStyle name="Content_Table_Detail" fontName="Helvetica" fontSize="8.0" alignment="RIGHT" rightIndent="0"/>
		<paraStyle name="Content_Table_Header" fontName="Helvetica-Bold" fontSize="8.0" alignment="CENTER"/>
		<blockTableStyle id="Content_Table">
		    <blockValign value="CENTER"/>
		    <blockAlignment value="CENTER"/>
		    <blockBackground colorName="#D3D3D3" start="0,0" stop="-1,0"/>
		    <lineStyle kind="GRID" colorName="#e6e6e6"/>
		    <blockTopPadding length="8"/>
		    <blockBottomPadding length="4"/>
		</blockTableStyle>
    </xsl:template>

    <xsl:template name="story">
    	<xsl:for-each select="//report/page">			
    		<para style="Tilte" t="1"> <xsl:value-of select="header/title"/></para>
			<para style="Tilte" t="1"> المبالغ بـ <xsl:value-of select="header/accuracy"/></para>
			<spacer length="1cm"/>
			<blockTable>
			    <xsl:attribute name="style">Content_Table</xsl:attribute>
			    <xsl:attribute name="colWidths"><xsl:value-of select="cols" /></xsl:attribute>
		        <tr>
				    <td> <para style="Content_Table_Header" t="1"> الإجمـالي </para></td>
				    <xsl:for-each select="datas/header">
				    <td>
					<para style="Content_Table_Header" t="1"><xsl:value-of select="attribute::name" /></para>
				    </td>
				    </xsl:for-each>
				    <td> <para style="Content_Table_Header" t="1"> البيـــان </para></td>
				    <td> <para style="Content_Table_Header" t="1"> بند الخصم </para></td>
		        </tr>
				<xsl:for-each select="row">
		        <tr>
				    <xsl:for-each select="cols">
				    <td>
				    	<xsl:if test="attribute::type='total'">
				    	    <para style="Content_Table_Detail_Bold"><xsl:value-of select="val"/></para>
						</xsl:if>
						<xsl:if test="attribute::type='detail'">
				    	    <para style="Content_Table_Detail"><xsl:value-of select="val"/></para>
						</xsl:if>
				    </td>
				    </xsl:for-each>
				</tr>
				</xsl:for-each>
			</blockTable>
		</xsl:for-each>
    </xsl:template>
</xsl:stylesheet>

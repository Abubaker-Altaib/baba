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


    <xsl:template name="stylesheet">
		<paraStyle name="Tilte" fontName="Helvetica-Bold" fontSize="14.0" alignment="CENTER" spaceBefore="6.0" spaceAfter="4.0"/>
		<paraStyle name="Reasons" fontName="Helvetica-Bold" fontSize="12.0" alignment="RIGHT" spaceBefore="6.0" spaceAfter="4.0"/>
		<paraStyle name="Reasons_Detail" fontName="Helvetica-Bold" fontSize="12.0" alignment="RIGHT"/>
		<paraStyle name="Content_Table_Detail_Bold" fontName="Helvetica-Bold" fontSize="11.0" alignment="RIGHT"/>
		<paraStyle name="Content_Table_Header" fontName="Helvetica-Bold" fontSize="14.0" alignment="CENTER"/>
		<paraStyle name="Content_Table_Detail" fontName="Helvetica" fontSize="12" alignment="RIGHT" rightIndent="0"/>
		
		<blockTableStyle id="Content_Table">
		    <blockAlignment value="RIGHT"/>
		    <blockBackground colorName="#D3D3D3" start="0,0" stop="-1,0"/>
		    <lineStyle kind="GRID" colorName="#e6e6e6"/>
		    <blockTopPadding length="4"/>
		    <blockBottomPadding length="4"/>
		</blockTableStyle>
		<blockTableStyle id="Content_Table2">
		    <blockAlignment value="RIGHT"/>
		    <blockBackground colorName="#ffffff" start="0,0" stop="-1,0"/>
		    <lineStyle kind="GRID" colorName="#e6e6e6"/>
		    <blockTopPadding length="4"/>
		    <blockBottomPadding length="4"/>
		</blockTableStyle>
    </xsl:template>




    <xsl:template name="story">
    	<xsl:for-each select="//report/page">		
    		<para style="Tilte" t="1"> <xsl:value-of select="header/title"/></para>
			<spacer length="1cm"/>

			<blockTable>
			    <xsl:attribute name="style">Content_Table</xsl:attribute>
			    <xsl:attribute name="colWidths"><xsl:value-of select="cols" /></xsl:attribute>
		        <tr>
				    <xsl:for-each select="datas/header">
						<td>
							<para style="Content_Table_Header" t="1"><xsl:value-of select="attribute::name" /></para>
						</td>							

				    </xsl:for-each>
		        </tr>
			</blockTable>


			<blockTable>
			    <xsl:attribute name="style">Content_Table2</xsl:attribute>
			    <xsl:attribute name="colWidths"><xsl:value-of select="cols" /></xsl:attribute>
				<xsl:for-each select="row">
		        <tr>
				    <xsl:for-each select="cols">
				    <td >
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

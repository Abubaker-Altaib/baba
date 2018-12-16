<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fo="http://www.w3.org/1999/XSL/Format">



    <xsl:template match="//report/page">
		<document filename="Report.pdf">
  <template pageSize="792.0,612.0" title="Check" author="NCTR" allowSplitting="20">
				<pageTemplate id="first">
					<xsl:if test="attribute::type='flow'">
					</xsl:if>
					<frame id="first" x1="0" y1="0" width="770" height="570"/>
				</pageTemplate>
			</template>

			<stylesheet>
			    <xsl:call-template name="stylesheet"/>
		    </stylesheet>

			<story>
				<xsl:call-template name="story"/>
			</story>

		</document>
	</xsl:template>

    <xsl:template name="stylesheet">
                <paraStyle name="normal" fontName="Helvetica-Bold"    textColor="black" alignment="right" >
			<xsl:attribute name="fontSize">
		<xsl:for-each select="//report/page"><xsl:value-of select="font_size"/>
		</xsl:for-each>
			</xsl:attribute>
		</paraStyle>
    </xsl:template>

	<xsl:template name="story">
		<xsl:for-each select="//report/page">
			<spacer><xsl:attribute name="length">
				<xsl:value-of select="date_spacer"/></xsl:attribute>
			</spacer>
			<para>
				<xsl:attribute name="style">normal</xsl:attribute>
				<xsl:value-of select="date"/><font color="white" ><xsl:value-of select="date_dot"/></font>
			</para>



			<spacer><xsl:attribute name="length">
				<xsl:value-of select="name_spacer"/></xsl:attribute>
			</spacer>
			<para>
				<xsl:attribute name="style">normal</xsl:attribute>
				<xsl:value-of select="name"/><font color="white" ><xsl:value-of select="name_dot"/></font>
			</para>


			<spacer><xsl:attribute name="length">
				<xsl:value-of select="amount_spacer"/></xsl:attribute>
			</spacer>
			<para>
				<xsl:attribute name="style">normal</xsl:attribute>
				<xsl:value-of select="amount"/><font color="white" ><xsl:value-of select="amount_dot"/></font>
			</para>


			<spacer><xsl:attribute name="length">
				<xsl:value-of select="number_spacer"/></xsl:attribute>
			</spacer>
			<para>
				<xsl:attribute name="style">normal</xsl:attribute>
				#<xsl:value-of select="number"/>#<font color="white" ><xsl:value-of select="number_dot"/></font>
			</para>
		</xsl:for-each>
	</xsl:template>
</xsl:stylesheet>

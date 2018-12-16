<?xml version = '1.0' encoding="utf-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">

	<xsl:template name="A3_landscape">
		<document filename="Report.pdf">
			<template pageSize="1684.0,1200.0" title="Account Budget" author="NCTR" allowSplitting="20">
				<pageTemplate id="first">
					<xsl:if test="attribute::type='flow'">
						<pageGraphics>
							<setFont name="DejaVu Sans Bold" size="7"/>
							<fill color="black"/>
							<stroke color="black"/>
							<lines>20.2cm 2.15cm 38.9cm 2.15cm</lines>
							<rect x="23.5 cm" y="0.7 cm" width="4.3 cm" height="0.7 cm"
							fill="no" stroke="yes" />
							<rect x="27.8 cm" y="0.7 cm" width="4 cm" height="0.7 cm"
							fill="no" stroke="yes" />
							<rect x="31.8 cm" y="0.7 cm" width="4 cm" height="0.7 cm"
							fill="no" stroke="yes" />
							<drawString x="23.7cm" y="0.9cm">2012/6/6</drawString>
							<drawString x="25.2cm" y="0.9cm">:</drawString>
							<drawString x="25.6cm" y="0.9cm">تاريخ الاصدار</drawString>
							<drawString x="28.2cm" y="0.9cm">00/1</drawString>
							<drawString x="29.4cm" y="0.9cm">:</drawString>
							<drawString x="30.0cm" y="0.9cm">رقم الاصدار</drawString>
							<drawString x="32.3cm" y="0.9cm">BPP-04</drawString>
							<drawString x="33.6cm" y="0.9cm">:</drawString>
							<drawString x="34.3cm" y="0.9cm">نموذج رقم</drawString>
						</pageGraphics>
					</xsl:if>
					<frame id="first" x1="60" y1="70" width="1572" height="1070"/>
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
    
    <xsl:template name="A3_portrait">
		<document filename="Report.pdf">
			<template pageSize="1200.0,1684.0" title="Account Budget" author="NCTR" allowSplitting="20">
				<pageTemplate id="first">
					<xsl:if test="attribute::type='flow'">
						<pageGraphics>
							<setFont name="DejaVu Sans Bold" size="7"/>
							 <fill color="black"/>
							 <stroke color="black"/>
							 <lines>13.2cm 2.15cm 31.9cm 2.15cm</lines>
							<rect x="16.5 cm" y="0.7 cm" width="4.3 cm" height="0.7 cm"
							fill="no" stroke="yes" />
							<rect x="20.8 cm" y="0.7 cm" width="4 cm" height="0.7 cm"
							fill="no" stroke="yes" />
							<rect x="24.8 cm" y="0.7 cm" width="4 cm" height="0.7 cm"
							fill="no" stroke="yes" />
							<drawString x="16.7cm" y="0.9cm">2012/6/6</drawString>
							<drawString x="18.2cm" y="0.9cm">:</drawString>
							<drawString x="18.6cm" y="0.9cm">تاريخ الاصدار</drawString>
							<drawString x="21.2cm" y="0.9cm">00/1</drawString>
							<drawString x="22.4cm" y="0.9cm">:</drawString>
							<drawString x="23.0cm" y="0.9cm">رقم الاصدار</drawString>
							<drawString x="25.3cm" y="0.9cm">BPP-04</drawString>
							<drawString x="26.6cm" y="0.9cm">:</drawString>
							<drawString x="27.3cm" y="0.9cm">نموذج رقم</drawString>
						</pageGraphics>
					</xsl:if>
					<frame id="first" x1="60" y1="60" width="1090" height="1572"/>
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
    
    
    <xsl:template name="A4_landscape">
		<document filename="Report.pdf">
			<template pageSize="842.0,595.0" title="Account Budget" author="NCTR" allowSplitting="20">
				<pageTemplate id="first">

				<frame id="first"  x1="1.2cm" y1="1.7cm" width="27.5cm" height="16.5cm" showBoundary="0"/>
				<!--header-->
					<pageGraphics>
						<setFont name="DejaVu Sans" size="11"/>
						<drawString x="13.5cm" y="19.7cm"  fontSize="14.0">الهيئة القومية للاتصالات</drawString>
						<drawString x="13.7cm" y="18.9cm"  fontSize="14.0">نظام إدارة المؤسسة</drawString>
						<setFont name="DejaVu Sans" size="8"/>
						<fill color="black"/>
						<stroke color="black"/>

						<!-- page header -->
						<lines>2cm 18.5cm 27.5cm 18.5cm</lines>
						<lines>2cm 18.4cm 27.5cm 18.4cm</lines>
						<lines>1.2cm 1.65cm 27.5cm 1.65cm</lines>
					</pageGraphics>
					<place x="3.3cm" y="0cm" height="1.55cm" width="27.7cm">
					<blockTable colWidths="10cm,10cm,7cm" >
						<tr>
							<td>
							<para leading="11" alignment="CENTER"> Page <pageNumber/> of <getName x="6cm" y="0cm" id="lastPage"/></para>
							</td>
							<td>
								<para leading="11" alignment="CENTER">المستخدم</para>
							</td>
							<td>
								<para></para>
							</td>
						</tr>
					</blockTable>
            		</place>
				<!--/header-->
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
    
        <xsl:template name="A4_portrait">
		<document filename="Report.pdf">
			<template pageSize="595.0,842.0" title="Account Budget" author="NCTR" allowSplitting="20">
				<pageTemplate id="first">
					<xsl:if test="attribute::type='flow'">
						<pageGraphics>
							<setFont name="DejaVu Sans Bold" size="7"/>
							 <fill color="black"/>
							 <stroke color="black"/>
							 <lines>1.1cm 2.15cm 19.9cm 2.15cm</lines>
							<rect x="4.5 cm" y="0.7 cm" width="4.3 cm" height="0.7 cm"
							fill="no" stroke="yes" />
							<rect x="8.8 cm" y="0.7 cm" width="4 cm" height="0.7 cm"
							fill="no" stroke="yes" />
							<rect x="12.8 cm" y="0.7 cm" width="4 cm" height="0.7 cm"
							fill="no" stroke="yes" />
							<drawString x="4.8cm" y="0.9cm">2012/6/6</drawString>
							<drawString x="6.3cm" y="0.9cm">:</drawString>
							<drawString x="6.7cm" y="0.9cm">تاريخ الاصدار</drawString>
							<drawString x="9.0cm" y="0.9cm">00/1</drawString>
							<drawString x="10.3cm" y="0.9cm">:</drawString>
							<drawString x="11.0cm" y="0.9cm">رقم الاصدار</drawString>
							<drawString x="13.0cm" y="0.9cm">BPP-04</drawString>
							<drawString x="14.3cm" y="0.9cm">:</drawString>
							<drawString x="15.0cm" y="0.9cm">نموذج رقم</drawString>
						</pageGraphics>
					</xsl:if>
					<frame id="first" x1="28" y1="50" width="535" height="750"/>
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
    
</xsl:stylesheet>


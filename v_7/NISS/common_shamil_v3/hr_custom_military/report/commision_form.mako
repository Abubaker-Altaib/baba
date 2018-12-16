<html dir="rtl" lang="ar">
	<head>
		<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
		<style type="text/css">

			.tb-data{
				border-collapse: collapse;
				width: 100%;
				outline:  3px solid black;
			}
			.tb-data td , .tb-data th{
				
	    		text-align: center;
	    		border: 1px solid black;
	    		padding: 1px;
	    	}
			.manager-block{
	    		text-align: right;
	    		float: left;
	    		margin-top: 3px;
	    		padding: 30px;
	    		font-size: 18px;
	    	}
	    	


	    	.right-block{
	    		float: right;
	    		margin-top: 80px;
	    	}

	    	.com{
	    		border-collapse: collapse;
				width: 100%;
				outline:  1px solid black;
				text-align: center;
	    		
	    	}

	    	#con2{
	    		margin-top: 30px;
	    	}
	    	#con3{
	    		margin-top: 30px;
	    	}

		</style>
	</head>
	<body>
		<div id="con1" class="container">
			<center>
				<p>
					بسم الله الرحمن الرحيم
				</p>
				<h2>
					<u>أورنيك مقابلة القمسيون الطبي</u>
				</h2>

				<!-- ___________________ header___________________________ -->

				<table class="trh">
					<tr>
						<td width="200">
							<u>معنون إلي السيد</u>/مقرر القميسيون الطبي
						</td>
						<td width="200">

						</td>

						<td width="80">
							التاريخ
						</td>
						<td>
							${date}
						</td>
					</tr>

					<tr>
						<td width="200">
						</td>
						<td width="200">
						</td>

						<td width="80">
							نمرة القيد
						</td>
						<td>
							${name}
						</td>
					</tr>

				</table>

				<br/>
			</center>
				</div>
				<!-- ___________________ basic data ___________________________ -->
				<table>
				<tr>
					<td>
						1-<b><u>البيانات الأساسية</u></b>
					</td>
					<td width="600">
					</td>
				</tr>
				</table>

				<table>
					<tr>
						<td width="30">
						</td>
						<td  width="100">
							رقم البطاقة
						</td>
						<td width="200" style="text-align: right;">
							<b>${otherid}</b>
						</td>
						<td width="30">
						</td>
						<td width="100">
							تاريخ الميلاد
						</td>
						<td width="150">
							${birthday}
						</td>
						<td  width="200">
						</td>
						<td  width="30">
						</td>
						<td  width="30">
						</td>
						<td  width="30">
						</td>
						<td  width="30">
						</td>
						<td  width="30">
						</td>
						<td  width="30">
						</td>
					</tr>

					<tr>
						<td width="30">
						</td>
						<td  width="100">
						</td>
						<td width="200">
						</td>
						<td width="30">
						</td>
						<td width="100">
						</td>
						<td width="150">
						</td>
						<td  width="200">
							العمر حتى تاريخ اليوم
						</td>
						<td  width="30">
							${birthday_duration['days']}
						</td>
						<td  width="30">
							يوم
						</td>
						<td  width="30">
							${birthday_duration['months']}
						</td>
						<td  width="30">
							شهر
						</td>
						<td  width="30">
							${birthday_duration['years']}
						</td>
						<td  width="30">
							سنة
						</td>
					</tr>


					<tr>
						<td width="30">
						</td>
						<td  width="100">
							الرتبة
						</td>
						<td width="200" style="text-align: right;">
							<b>${degree}</b>
						</td>
						<td width="30">
						</td>
						<td width="100">
							تاريخ التعين
						</td>
						<td width="150">
							${employment_date}
						</td>
						<td  width="200">
						</td>
						<td  colspan="6">
							<hr/>
						</td>
					</tr>

					<tr>
						<td width="30">
						</td>
						<td  width="100">
						</td>
						<td width="200">
						</td>
						<td width="30">
						</td>
						<td width="100">
						</td>
						<td width="150">
						</td>
						<td  width="200">
							مدة الخدمة حتى اليوم
						</td>
						<td  width="30">
							${work_duration['total_days']}
						</td>
						<td  width="30">
							يوم
						</td>
						<td  width="30">
							${work_duration['total_months']}
						</td>
						<td  width="30">
							شهر
						</td>
						<td  width="30">
							${work_duration['total_years']}
						</td>
						<td  width="30">
							سنة
						</td>
					</tr>
				</table>
				<table>
					<tr>
						<td width="30">
						</td>
						<td  width="100">
							الإسم
						</td>
						<td width="500" style="text-align: right;">
							${employee}
						</td>
						<td width="50">
						</td>
						<td width="200">
						</td>
						<td width="200">
						</td>
					</tr>

					<tr>
						<td width="30">
						</td>
						<td  width="100">
							الإدارة
						</td>
						<td width="500" style="text-align: right;">
							${department}
						</td>
						<td width="50">
						</td>
						<td  width="200">
							يتبع إلى
						</td>
						<td  width="200">
							${hospital}
						</td>
					</tr>
				</table>
				<hr/>
				<!-- ___________________ status info ___________________________ -->
				<table>
				<tr>
					<td width="300">
						2-<b><u>بيانات الحالة</u></b>
					</td>
					<td width="400">
					</td>
					<td width="100">
						تاريخ التبليغ
					</td>
					<td width="150">
						${report_date}
					</td>
					</tr>

				</table>

				<table>
					<tr>
						<td width="30">
						</td>
						<td  width="200">
							العنوان و التلفون
						</td>
						<td width="200">
						</td>
						<td width="200">
						</td>
						<td width="100">
							المرجع
						</td>
						<td width="300">
						</td>
					</tr>
					<tr>
						<td>
						</td>
					</tr>
					<tr>
						<td width="30">
						</td>
						<td  width="200">
							الغرض من المقابلة
						</td>
						<td width="200">
						</td>
						<td width="200">
						</td>
						<td width="100">
						</td>
						<td width="300">
						</td>
					</tr>
					<tr>
						<td>
						</td>
					</tr>
					<tr>
						<td width="30">
						</td>
						<td  width="200">
							المستندات المرفقة
						</td>
						<td width="200">
						</td>
						<td width="200">
						</td>
						<td width="100">
						</td>
						<td width="300">
						</td>
					</tr>
					<tr>
						<td>
						</td>
					</tr>
					<tr>
						<td width="30">
						</td>
						<td  width="200">
							ملخص عام للإصابة
						</td>
						<td width="200">
						</td>
						<td width="200">
						</td>
						<td width="100">
						</td>
						<td width="300">
						</td>
					</tr>
					<tr>
						<td>
						</td>
					</tr>
					<tr>
						<td width="30">
						</td>
						<td  width="200">
						</td>
						<td width="200">
						</td>
						<td width="200">
						</td>
						<td width="100">
						</td>
						<td width="300">
							${company.hq and u'مدير إدارة الرتب الأخرى' or u'مدير إدارة الشئون اﻹدارية'}
						</td>
					</tr>
				</table>
				<hr/>

				<!-- ___________________ commision data ___________________________ -->
				<table>
					<tr>
						<td width="300">
							3-<b><u>قرار القميسيون الطبي</u></b>
						</td>
						<td width="400">
						</td>
					</tr>

				</table>
				<table>
					<tr>
						<td width="200" style="text-align: center;">
						</td>
						<td width="150">
							1- نسبة العجز 
						</td>
						<td width="500" style="vertical-align:bottom;">
---------------------------------------------------------------------------------</td>
					</tr>
					<tr>
					</tr>

					<tr>
						<td width="200" style="text-align: center;">
							<b>أ- قرار اللجنة</b>
						</td>
						<td width="150">
							2- النسبة بالأحرف 
						</td>
						<td width="500" style="vertical-align:bottom;">
---------------------------------------------------------------------------------</td>
					</tr>
					<tr>
						<td width="200">
						</td>
						<td width="150">
						</td>
						<td width="500" style="vertical-align:bottom;">
---------------------------------------------------------------------------------</td>
					</tr>
					<tr>
					</tr>

					<tr>
						<td width="200" style="text-align: center;">
						</td>
						<td width="150">
							3- درجة الصلاحية للعمل 
						</td>
						<td width="500" style="vertical-align:bottom;">
---------------------------------------------------------------------------------</td>
					</tr>
					<tr>
					</tr>
				</table>
				<hr/>

				<table>
					<tr>
						<td width="60">
						</td>
						<td width="200" style="text-align: center;">
							<b>ب- <u>أعضاء لجنة القميسيون الطبي</u></b>
						</td>
					</tr>
				</table>
				<br/>

				<table border="1" class="com">
					<tr>
						<td width="30" style="text-align: center;">
							م
						</td>
						<td width="100">
							الوظيفة
						</td>
						<td width="300">
							الإسم
						</td>
						<td width="200">
							اللجنة
						</td>
						<td width="200">
							التوقيع
						</td>

					<tr>
						<td width="30" style="text-align: center;">
							1-
						</td>
						<td width="100">
						</td>
						<td width="300">
						</td>
						<td width="200">
							رئيساً
						</td>
						<td width="200">
						</td>
					</tr>

					<tr>
						<td width="30" style="text-align: center;">
							2-
						</td>
						<td width="100">
						</td>
						<td width="300">
						</td>
						<td width="200">
						عضواً
						</td>
						<td width="200">
						</td>
					</tr>

					<tr>
						<td width="30" style="text-align: center;">
							3-
						</td>
						<td width="100">
						</td>
						<td width="300">
						</td>
						<td width="200">
						عضواً
						</td>
						<td width="200">
						</td>
					</tr>
				</table>
				<br/>
				<table>
					<tr>
						<td width="60">
						</td>
						<td colspan="2" style="text-align: center;">
							<b>ج- <u>إعتماد مقرر لجنة القميسيون الطبي</u></b>
						</td>
						
						<td width="150" style="text-align: center;">
							التوقيع
						</td>
						<td width="200">
						</td>
					</tr>
					<tr>
						<td width="60">
						</td>
						<td width="200">
						</td>
						<td width="300">
						</td>
						<td width="150" style="text-align: center;">
							-----------------
						</td>
						<td width="200">
							<pre>     التاريخ	 ____/____/____20 م<pre>
						</td>
					</tr>
					<tr>
						<td width="60">
						</td>
						<td width="200">
							الوظيفة ----------------
						</td>
						<td width="300">
							الإسم ------------------------------
						</td>
						<td width="150" style="text-align: center;">
							والختم
						</td>
						<td width="200">
						</td>
					</tr>
				</table>
				<table>
					<tr>
						<td width="60">
						</td>
						<td>
							نمرة قيد الصادر
						</td>
						<td width="200">
							--------------/----------------
						</td>
						<td>
						</td>
						<td width="200">
							<pre>     التاريخ	 ____/____/____20 م<pre>
						</td>
					</tr>
				</table>
				<!--<p style="page-break-after: always;">&nbsp;</p>-->
				<!--  ________________________________legal data________________________ -->
			<table>
				<tr>
					<td>
						4-<b><u>الرأي القانوني</u></b>
					</td>
				</tr>
			</table>
			<p>------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------</p>

			<table>
					<tr>
						<td width="60">
						</td>
						<td colspan="2">
						</td>
						
						<td width="150" style="text-align: center;">
							التوقيع
						</td>
						<td width="200">
						</td>
					</tr>
					<tr>
						<td width="60">
						</td>
						<td width="200">
						</td>
						<td width="300">
						</td>
						<td width="150" style="text-align: center;">
							-----------------
						</td>
						<td width="200">
							<pre>     التاريخ	 ____/____/____20 م<pre>
						</td>
					</tr>
					<tr>
						<td width="60">
						</td>
						<td width="200">
							الرتبة ----------------
						</td>
						<td width="300">
							الإسم ------------------------------
						</td>
						<td width="150" style="text-align: center;">
							والختم
						</td>
						<td width="200">
						</td>
					</tr>
				</table>
				<table>
					<tr>
						<td width="60">
						</td>
						<td>
							نمرة قيد الصادر
						</td>
						<td width="200">
							--------------/----------------
						</td>
						<td>
						</td>
						<td width="200">
							<pre>     التاريخ	 ____/____/____20 م<pre>
						</td>
					</tr>
				</table>
				<hr/>

			<!--  ________________________________ other degree manger data ________________________ -->
			<table>
				<tr>
					<td>
						5- <b><u>رأي السيد ${company.hq and u'مدير إدارة شئون الرتب الأخرى' or u'مدير إدارة الشئون اﻹدارية'}</u></b>
					</td>
				</tr>
			</table>
			<p>------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------</p>

			<table>
					<tr>
						<td width="60">
						</td>
						<td width="300">
						</td>
						<td width="200">
						</td>
						<td width="150" style="text-align: center;">
							التوقيع
						</td>
					</tr>
					<tr>
						<td width="60">
						</td>
						<td width="300">
						</td>
						<td width="200">
						</td>
						<td width="150" style="text-align: center;">
							--------------------
						</td>
						<td width="200">
							<pre>     التاريخ	 ____/____/____20 م<pre>
						</td>
					</tr>
				</table>

				<table>
					<tr>
						<td width="60">
						</td>
						<td>
							نمرة قيد الصادر
						</td>
						<td width="200">
							--------------/----------------
						</td>
						<td>
						</td>
						<td width="200">
							<pre>     التاريخ	 ____/____/____20 م<pre>
						</td>
					</tr>
				</table>
				<hr/>

		<!--  ________________________________ department manger data ________________________ -->
			<table>
				<tr>
					<td>
						6- <b><u>رأي السيد رئيس ${company.hq and u'الدائرة اﻹدارية' or u'دائرة اﻹسناد و التوجيه'}</u></b>
					</td>
				</tr>
			</table>
			<p>------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------</p>

			<table>
					<tr>
						<td width="60">
						</td>
						<td width="300">
						</td>
						<td width="200">
						</td>
						<td width="150" style="text-align: center;">
							التوقيع
						</td>
					</tr>
					<tr>
						<td width="60">
						</td>
						<td width="300">
						</td>
						<td width="200">
						</td>
						<td width="150" style="text-align: center;">
							--------------------
						</td>
						<td width="200">
							<pre>     التاريخ	 ____/____/____20 م<pre>
						</td>
					</tr>
				</table>

				<table>
					<tr>
						<td width="60">
						</td>
						<td>
							نمرة قيد الصادر
						</td>
						<td width="200">
							--------------/----------------
						</td>
						<td>
						</td>
						<td width="200">
							<pre>     التاريخ	 ____/____/____20 م<pre>
						</td>
					</tr>
				</table>
				<!--hr/-->
				<!--<p style="page-break-after: always;">&nbsp;</p>-->
		<!--  ________________________________ otheraty manger data ________________________ -->
			%if company.hq == False:
			<table>
				<tr>
					<td>
						7- <b><u>رأي السيد مدير هيئة العمليات</u></b>
					</td>
				</tr>
			</table>
			<p>------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------</p>

			<table>
					<tr>
						<td width="60">
						</td>
						<td width="300">
						</td>
						<td width="200">
						</td>
						<td width="150" style="text-align: center;">
							التوقيع
						</td>
					</tr>
					<tr>
						<td width="60">
						</td>
						<td width="300">
						</td>
						<td width="200">
						</td>
						<td width="150" style="text-align: center;">
							--------------------
						</td>
						<td width="200">
							<pre>     التاريخ	 ____/____/____20 م<pre>
						</td>
					</tr>
				</table>

				<table>
					<tr>
						<td width="60">
						</td>
						<td>
							نمرة قيد الصادر
						</td>
						<td width="200">
							--------------/----------------
						</td>
						<td>
						</td>
						<td width="200">
							<pre>     التاريخ	 ____/____/____20 م<pre>
						</td>
					</tr>
				</table>
				<hr/>
				%endif


			<table>
				<tr>
					<td>
						7- <b><u>رأي السيد مدير هيئة الإدارة</u></b>
					</td>
				</tr>
			</table>
			<p>------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------</p>

			<table>
					<tr>
						<td width="60">
						</td>
						<td width="300">
						</td>
						<td width="200">
						</td>
						<td width="150" style="text-align: center;">
							التوقيع
						</td>
					</tr>
					<tr>
						<td width="60">
						</td>
						<td width="300">
						</td>
						<td width="200">
						</td>
						<td width="150" style="text-align: center;">
							--------------------
						</td>
						<td width="200">
							<pre>     التاريخ	 ____/____/____20 م<pre>
						</td>
					</tr>
				</table>

				<table>
					<tr>
						<td width="60">
						</td>
						<td>
							نمرة قيد الصادر
						</td>
						<td width="200">
							--------------/----------------
						</td>
						<td>
						</td>
						<td width="200">
							<pre>     التاريخ	 ____/____/____20 م<pre>
						</td>
					</tr>
				</table>
				<hr/>

		<!--  ________________________________ General manger data ________________________ -->
			<table>
				<tr>
					<td>
						8- <b><u>قرار ${company.hq and u'المدير العام' or u'نائب المدير العام'}</u></b>
					</td>
				</tr>
			</table>
			<p>------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------</p>
			<br/>
			

			<table>
				<tr>
					<td width="60">
					</td>
					<td width="300">
						<u>صورة إلى</u>
					</td>
					<td width="100">
					</td>
					<td width="150">
					</td>
				</tr>
				<tr>
					<td width="60">
					</td>
					<td width="300">
					</td>
					<td width="100">
					</td>
					<td width="150" style="text-align: center;">
						<pre>/ ملفات الخدمة  /   فرع الخدمة العامة<pre>
					</td>
				</tr>
			</table>

			</center>
				
		</div>

	</body>

<footer>


</footer>

</html>

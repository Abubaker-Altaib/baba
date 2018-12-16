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

	    	.trh{
	    		border-bottom: solid 3px black;
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
		%if type == 'department_duration': 
		<div id="con1" class="container">
			<center>
				<p>
					بسم الله الرحمن الرحيم
				</p>
				<p>
					 تقرير عام يوضح فترة العمل بالافرع بين فترتين
				</p>
				
			</center>
			<table>
					<tr>
					<td width="300">
					</td>
					<td width="70">
						الفرع
					</td>
					<td>
					${department}
					</td>
					</tr>

					<tr>
					<td width="300">
					</td>

					<td width="150">
						الإجمالي الكلي
					</td>
					<td>
					${total}
					</td>
					</tr>

				</table>
				<table>
					<tr>
					<td width="300">
					</td>

					<td width="75">
						أكثر من
					</td>
					<td width="40">
					${more}
					</td>
					<td width="60">
					سنة
					</td>

					<td width="75">
						أقل من
					</td>
					<td width="40">
					${less}
					</td>
					<td width="120">
					سنة
					</td>
					<td width="70">
					التاريخ
					</td>
					<td>
					${date}
					</td>


					</tr>
				</table>
				<center>
					<table border="1" class="tb-data">
					<tr class="trh">
		
					<th>
						<u>م</u>
					</th>
					<th>
						<u>ر.البطاقة</u>
					</th>
					<th>
						<u>الرتبة</u>
					</th>
					<th>
						<u>الإسم</u>
					</th>
					<th>
						<u>تاريخ التعين</u>
					</th>
					<th>
						<u>المهام</u>
					</th>
					<th>
						<u>الوظيفة</u>
					</th>
					<th colspan="3">
						<u>مدة الخدمة حتى اليوم</u><br/>

						<u>يوم</u>   |    <u>شهر</u>   |    <u>سنة</u> 
					
					</th>
					<th>
						<u>تاريخ العمل بالإدارة</u>
					</th>
					<th colspan="3">
						<u>مدة العمل بالإدارة حتى اليوم</u><br/>

						<u>يوم</u>   |    <u>شهر</u>   |    <u>سنة</u> 
					
					</th>
					</tr>

					%for i , obj in enumerate(employees):
					<tr>
						<td>
						${i + 1} 
					</td>
					<td>
						${obj['emp'].otherid} 
					</td>
					<td>
						${obj['emp'].degree_id.name}
					</td>
					<td>
						${obj['emp'].name}
					</td>
					<td>
						${obj['emp'].employment_date}
					</td>
					<td>
						${obj['emp'].department_id.name}
					</td>
					<td>
						${obj['emp'].job_id.name}
					</td>

					<td>${obj['emp'].actual_service_days}</td>  
					<td>${obj['emp'].actual_service_months}</td>  
					<td>${obj['emp'].actual_service_years}</td>
					<td>
						${obj['emp'].join_date}
					</td>
					<td>${obj['emp'].dept_service_days}</td>  
					<td>${obj['emp'].dept_service_months}</td>  
					<td>${obj['emp'].dept_service_years}</td>

					</tr>
					%endfor
				</table>
			</center>
				
		</div>
		%endif

		%if type == 'age': 
		<div id="con1" class="container">
			<center>
				<p>
					بسم الله الرحمن الرحيم
				</p>
				<p>
					تقرير حسب العمر
				</p>
				
			</center>
			<table>
					<tr>
					<td width="300">
					</td>

					<td width="75">
						العمر من
					</td>
					<td width="40">
						${age_from}
					</td>
					<td width="60">
						سنة
					</td>
					<td width="75">
						إلى
					</td>
					<td width="40">
					${age_to}
					</td>
					<td width="120">
					سنة
					</td>
					<td width="70">
					</td>
					<td>
					</td>


					</tr>
				</table>
			<table>
					<tr>
					<td width="300">
					</td>
					<td width="70">
						الرتبة
					</td>
					<td>
					${degree}
					</td>
					</tr>

					<tr>
					<td width="300">
					</td>

					<td width="150">
						الإجمالي الكلي
					</td>
					<td>
					${total}
					</td>
					<td width="70">
					التاريخ
					</td>
					<td>
					${date}
					</td>
					</tr>

				</table>
				
				<center>
					<table border="1" class="tb-data">
					<tr class="trh">
		
					<th>
						<u>م</u>
					</th>
					<th>
						<u>ر.البطاقة</u>
					</th>
					<th>
						<u>الرتبة</u>
					</th>
					<th>
						<u>الإسم</u>
					</th>
					<th>
						<u>الإدارة</u>
					</th>
					<th>
						<u>تاريخ الميلاد</u>
					</th>
					<th>
						<u>الدفعة</u>
					</th>
					<th>
						<u>تاريخ التعين</u>
					</th>
					<th colspan="3">
						<u>مدة الخدمة حتى اليوم</u><br/>

						<u>يوم</u>   |    <u>شهر</u>   |    <u>سنة</u> 
					
					</th>
					<th>
						<u>الوظيفة</u>
					</th>
					<th colspan="3">
						<u>العمر اليوم</u><br/>

						<u>يوم</u>   |    <u>شهر</u>   |    <u>سنة</u> 
					
					</th>
					<th>
						<u>عقد الخدمة</u>
					</th>
					</tr>

					%for i , obj in enumerate(employees):
					<tr>
						<td>
						${i + 1} 
					</td>
					<td>
						${obj['emp'].otherid} 
					</td>
					<td>
						${obj['emp'].degree_id.name}
					</td>
					<td>
						${obj['emp'].name}
					</td>
					<td>
						${obj['emp'].department_id.name}
					</td>
					<td>
						${obj['emp'].birthday}
					</td>
					<td>
						${obj['emp'].batch.name or ' '}
					</td>
					<td>
						${obj['emp'].employment_date}
					</td>

					<td>${obj['emp'].actual_service_days}</td>  
					<td>${obj['emp'].actual_service_months}</td>  
					<td>${obj['emp'].actual_service_years}</td>
					<td>
						${obj['emp'].job_id.name}
					</td>
					<td>${obj['age_days']}</td>  
					<td>${obj['age_months']}</td>  
					<td>${obj['age_years']}</td>
					<td>
					</td>
					</tr>
					%endfor
				</table>
			</center>
				
		</div>
		%endif


	</body>

<footer>


</footer>

</html>

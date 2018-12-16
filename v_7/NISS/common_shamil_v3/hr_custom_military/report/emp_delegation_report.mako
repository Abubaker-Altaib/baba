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
		<div id="con1" class="container">
			<center>
				<p>
					بسم الله الرحمن الرحيم
				</p>
				<p>
					 تقرير بوضع الخدمة ${delegation}
				</p>
				
			</center>
			<table>
				%if department:
					<tr>
					<td width="300">
					</td>
					<td width="70">
						الإدارة
					</td>
					<td>
					${department}
					</td>
					</tr>
				%endif
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
						<u>الدفعة</u>
					</th>
					<th>
						<u>الوظيفة</u>
					</th>
					<th colspan="3">
						<u>مدة ${delegation} حتى اليوم</u><br/>

						<u>يوم</u>   |    <u>شهر</u>   |    <u>سنة</u> 
					
					</th>
					<th>
						<u>تاريخ ${delegation}</u>
					</th>
					<th colspan="3">
						<u>مدة الخدمة حتى اليوم</u><br/>

						<u>يوم</u>   |    <u>شهر</u>   |    <u>سنة</u> 
					
					</th>
					</tr>
					</table>
				</center>

				<table>
				%if level2:
					<tr>
						<td width="200">
							<u>جهة ${delegation}</u>
						</td>
						<td>
						${level2}
						</td>
					</tr>
				%endif
					%if level3:
					<tr>
						<td width="200">
							<u>موقع العمل</u>
						</td>
						<td>
						${level3}
						</td>
					</tr>
				%endif
				</table>

				<center>
					<table border="1" class="tb-data">
					%for i , obj in enumerate(employees):
					<tr>
						<td>
						${i + 1} 
					</td>
					<td>
						${obj['emp'].employee_id.otherid} 
					</td>
					<td>
						${obj['emp'].employee_id.degree_id.name}
					</td>
					<td>
						${obj['emp'].employee_id.name}
					</td>
					<td>
						${obj['emp'].employee_id.employment_date}
					</td>
					<td>
						${obj['emp'].employee_id.batch.name or ' '}
					</td>
					<td>
						${obj['emp'].employee_id.job_id.name}
					</td>

					<td>${obj['delegation_days']}</td>  
					<td>${obj['delegation_months']}</td>  
					<td>${obj['delegation_years']}</td>
					<td>
						${obj['emp'].start_date}
					</td>
					<td>${obj['emp'].employee_id.actual_service_days}</td>  
					<td>${obj['emp'].employee_id.actual_service_months}</td>  
					<td>${obj['emp'].employee_id.actual_service_years}</td>

					</tr>
					%endfor
				</table>
			</center>
				
		</div>

	</body>

<footer>


</footer>

</html>

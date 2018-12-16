<html dir="rtl" lang="ar">

	<head>
	    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
	    <style type="text/css">
	    	body{
	    		font-size: 16px;
	    	}
	    	.order_data{
	    	}
	    	.order_data th{
	    		text-align: right;
	    		padding-left: 0;
	    		padding-top: 10px;
	    		padding-bottom: 0;
	    	}
	    	.order_data td{
	    		text-align: right;	
	    		padding-bottom: 0;
	    		border-bottom: 1px dotted black;
	    	}

	    	#tb1{
	    		width: 100%;
	    		right: 0;

	    	}

	    	#tb1{
	    		text-align: right;
	    	}

	    	#tb1 td{
	    		text-align: center;
	    	}
	    	.manager-block{
	    		text-align: right;
	    		float: left;
	    		margin-top: 30px;
	    		padding: 30px;
	    		font-size: 18px;
	    	}

	    	.copy-block {
	    		margin-top: 140px;
	    	}

	    	.copy-block p{
	    		padding: 9px;
	    		margin-right: 30px;
	    	}

	    	.pagebreak { page-break-before: always; }

	    	.employee-table{
	    		border-collapse: collapse;
	    	}

	    	.employee-table td , .employee-table th{
	    		text-align: center;
	    		border: 1px solid black;
	    	}

	    	.emp-tb-th{
	    		min-width: 160px;
	    	}





	    </style>
	</head>
	<body>

		<center>
			<p>بسم الله الرحمن الرحيم</p>
			<u>سري للغاية</u>
			<h1><b><u>(أورنيك القوات المسلحة رقم 1973 تحركات)</u></b></h1>
		</center>
		

		<table width="90%" height="55%" class="order_data">
			<tr>
				<th>
					اسم التشكيل : 
				</th>
				<td>
					${company_name}
				</td>
			</tr>
			<tr>
				<th>
					القوة المتحركة : 
				</th>
				<td>
					${power}
				</td>
			</tr>
			<tr>
				<th>
					السلاح :
				</th>
				<td>
					${weapon}
				</th>
			</tr>
			<tr>
				<th>
					الذخيرة :
				</th>
				<td>
					${ammu}
				</td>
			</tr>
			<tr>
				<th>
					المركبات ونوعها :
				</th>
				<td>
					${vehicle}
				</td>
			</tr>
			<tr>
				<th>
					أي معدات أخرى :
				</th>
				<td>
					${equipment}
				</td>
			</tr>
			<tr>
				<th>
					اسم قائد القوة
				</th>
				<td>
					${employees[0]['type']} ${employees[0]['code']} ${employees[0]['degree']}/${employees[0]['name']}
				</td>
			</tr>
			<tr>
				<th>
					عدد وأسماء الضباط/الأفراد تحت قيادته
				</th>
				<td>
					%if len(employees) > 1 :
						${employees[1]['type']} ${employees[1]['code']} ${employees[1]['degree']}/${employees[1]['name']}
						%if len(employees) == 3:
							<span>و
							${employees[2]['type']} ${employees[2]['code']} ${employees[2]['degree']}/${employees[2]['name']} 
							</span>
						%elif len(employees) > 2  :
							<span>وآخرون (${len(employees)}) بظاهره </span>

						%endif
					%endif
				</td>
			</tr>
			<tr>
				<th>
					الجهة المقصودة
				</th>
				<td>
					${destination}
				</td>
			</tr>
			<tr>
				<th>
					زمن وتاريخ التحرك :
				</th>
				<td>
					${move_date}
				</td>
			</tr>
			<tr>
				<th>
					اسم وتوقيع ركن العمليات :
				</th>
				<td>
				</td>
			</tr>
			<tr>
				<th>
					التعليمات الخاصة بالقوة :
				</th>
				<td>
				</td>
			</tr>
			<tr>
				<th>
					الطريق :
				</th>
				<td>
					${road}
				</td>
			</tr>
			<tr>
				<th>
					زمن وتاريخ التحرك :
				</th>
				<td>
					${move_date}
				</td>
			</tr>
			<tr>
				<th rowspan="3" style="vertical-align:top">
					توقيع قائد الوحدة :
				</th>
				<td>
				&nbsp;
				</td>
			</tr>
			<tr><td>&nbsp;</td></tr>
			<tr><td>&nbsp;</td></tr>
			<tr>
				<th rowspan="4" style="vertical-align:top">
					تصديق إدارة العمليات :
				</th>
				<th>&nbsp;
				</th>
			</tr>
			<tr><td style="border-bottom:none">.......................</td></tr>
			<tr><td style="border-bottom:none">.....................................</td></tr>
			<tr><td style="border-bottom:none">المنصب : مدير إدارة العمليات الحربية</td></tr>
			<tr>
				<th>النسخة الأولى : ﻹدارة العمليات الحربية</th>
			</tr>
			<tr>
				<td style="border-bottom:none"><b>النسخة الثانية :</b> ........................</td>
			</tr>
			<tr>
				<th>النسخة الثالثة : هيئة الأمن والاستخبارات.</th>
			</tr>
			<tr>
				<th>النسخة الرابعة : لقائد القوة المتحرة.</th>
			</tr>


		</table>
		
	


		%if len(employees) > 2 :
			<div class="pagebreak"> </div>

			<center>
				<h1>
				كشف أمر التحرك
				</h1>
			

			<table class="employee-table">
				<tr>
				<th>
				م
				</th>
				<th class="emp-tb-th">
				ر.البطاقة/النمرة
				</th>
				<th class="emp-tb-th">
				الرتبة
				</th>
				<th class="emp-tb-th">
				الاسم
				</th>
				<th class="emp-tb-th">
				ملحوظات
				</th>
				</tr>

				%for i , obj in enumerate(employees) :
					<tr>
					<td>
						${i + 1} 
					</td>
					<td>
						${obj['code']}
					</td>
					<td>
						${obj['degree']}  
					</td>
					<td>
						${obj['name']}
					</td>
					<td>
						
					</td>
					</tr>
				%endfor

			</table>

			</center>
		%endif
	</body>
</html>
<html dir="rtl" lang="ar">

	<head>
	    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
	    <style type="text/css">
	    	body{
	    		font-size: 16px;
	    	}
	    	.order_data th{
	    		width: 110px;
	    		text-align: right;
	    		padding-left: 0;
	    		padding-top: 10px;
	    	}
	    	.order_data td{
	    		text-align: right;
	    		
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
			<h1><b><u>أمر تحرك</u></b></h1>
		</center>
		<table id="tb1" width="100%">
			<tr>
			<th>
			الصادر بأمر السيد  /  
			</th>
			<td>
				${source_manger_text}
			</td>
			<th>
			بتاريخ : 
			</th>
			<td>
				${date}
			</td>
			</tr>
		</table>



		<table width="90%" height="55%" class="order_data">
			<tr>
				<th>
					الأشخاص هم:
				</th>
				<td>
					<b>
					%if len(employees) > 0 :
						${employees[0]['type']} ${employees[0]['code']} ${employees[0]['degree']}/${employees[0]['name']}
						%if len(employees) == 2:
							<span>و
							${employees[1]['type']} ${employees[1]['code']} ${employees[1]['degree']}/${employees[1]['name']} 
							</span>
						%elif len(employees) > 2  :
							<span>وآخرون (${len(employees)}) بظاهره </span>

						%endif
					%endif
					</b>
					
				</td>
			</tr>
			<tr>
				<th>
					من : 
				</th>
				<td>
					${source}
				</td>
			</tr>
			<tr>
				<th>
					إلى :
				</th>
				<td>
					${destination}
				</td>
			</tr>
			<tr>
				<th>
					الغرض :
				</th>
				<td>
					${type}
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
					اللبس :
				</th>
				<td>
					${clothes}
				</td>
			</tr>
			
			<tr>
				<th>
					تاريخ القيام :
				</th>
				<td>
					${move_date}
				</td>
			</tr>
			<tr>
				<th>
					وسيلة السفر :
				</th>
				<td>
					${method}
				</td>
			</tr>
			<tr>
				<th>
					التصديق :
				</th>
				<td>
					${source_manger}
				</td>
			</tr>
		</table>
		<center>
			<u>
			التعليمات
			</u>
		</center>
		بهذا قد تعين عليك/عليكم مغادرة ${source} والتوجه إلى ${destination} وعند وصولك / وصولكم مقابلة السيد  ${dest_manger} ﻷخذ التعليمات الأخيرة منه.
		<p>
		التوقيع : ..................................
		</p>

		<div class="manager-block">
		<p>${source_manger_degree}</p>
		<p>${source_manger_name}</p>
		</div>

		<div class="copy-block">
		نسخة إلى :
		<p>${dest_manger}</p>
		<p>بيد المسافر</p>
		<p>الملف</p>
		</div>


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
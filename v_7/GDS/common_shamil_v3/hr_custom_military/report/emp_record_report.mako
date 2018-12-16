<html dir="rtl" lang="ar">

	<head>
	    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
	    <style type="text/css">
	    	body{
	    		font-size: 20px;
	    	}

	    	table{
	    	}

	    	td , th , tr{
	    		border: 1px black solid;
	    	}
	    	
	    </style>
	</head>
	<body>

		<center>
			بسم الله الرحمن الرحيم
			<u>
			سري
			<h2>
			<p>قوات الدعم السريع</p>
			<p>الدائرة الإدارية</p>
			<p>إدارة شئون الرتب الأخرى</p>
			</h2>
			</u>
			<h2>
			المعلومات الأساسية لسجل الجندي
			</h2>
		</center>
		<table  width="100%">
			<tr>
			<th rowspan="2">م </th>
			<th rowspan="2"> النمرة العسكرية</th>
			<th rowspan="2">الرتبة </th>
			<th rowspan="2">الاسم </th>
			<th rowspan="2">تاريخ الميلاد </th>
			<th rowspan="2"> الديانة</th>
			<th rowspan="2">المستوى التعليمي </th>
			<th rowspan="1"  colspan="3"> الوطن</th>
			<th rowspan="2">القبيلة </th>
			<th rowspan="2">المهنة </th>
			<th rowspan="2">الحالة الاجتماعية </th>
			<th rowspan="2"> الرقم الوطني</th>
			<th rowspan="2"> فصيلة الدم</th>
			<th rowspan="2">أقرب الاقربين وعنوانه </th>
			<th rowspan="2"> اسم الوالدة</th>
			<th rowspan="2"> تاريخ التجنيد</th>
			<th rowspan="2"> تاريخ انتهاء عقد الخدمة</th>
			<th rowspan="2"> الخدمة السابقة ونوعها</th>
			</tr>
			<tr>
				<th>
				الولاية
				</th>
				<th>
				المحلية
				</th>
				<th>
				المدينة أو القرية
				</th>
			</tr>
			%for i , obj in enumerate(employees) :
			<tr>
				<td> ${i + 1}</td>
				<td> ${obj['emp_code']}</td>
				<td> ${obj['degree_name']}</td>
				<td> ${obj['name']}</td>
				<td> ${obj['birthday']}</td>
				<td> ${obj['religion']}</td>
				<td> ${obj['qualification']}</td>
				<td> ${obj['pl_state']}</td>
				<td> ${obj['local']}</td>
				<td> ${obj['managiral_unit']}</td>
				<td> ${obj['tribe']}</td>
				<td> ${obj['job']}</td>
				<td> ${obj['marital']}</td>
				<td> ${obj['no']}</td>
				<td> ${obj['blood_type']}</td>
				<td> ${obj['ne']}</td>
				<td> ${obj['mother']}</td>
				<td> ${obj['recruitment_date']}</td>
				<td> ${obj['end_date']}</td>
				<td> 'sss'</td>
			</tr>
			%endfor
		</table>
	</body>
</html>
<html dir="rtl" lang="ar">
	<head>
		<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
		<style type="text/css">
			table{
				width: 80%;

			}
			td{
				padding: 10px;
				padding-left: 0;
				padding-bottom: 20px;
				text-align: center;
			}

			.th{
				text-align: right;
				font-weight: bold;
			}
		</style>
	<body>
		<center>
		<table border="1">
			<tr>
				<td class="th">${type}</td>
				<td>${code}</td>
				<td class="th">الرتبة</td>
				<td>${degree}</td>
				<td class="th">الاسم</td>
				<td>${name}</td>
			</tr>
			<tr>
				<td class="th">الوحدة</td>
				<td>${company_name}</td>
			</tr>
			<tr>
				<td class="th">تاريخ الإصابة</td>
				<td>${date}</td>
				<td class="th">مكان الإصابة</td>
				<td>${place}</td>
			</tr>
			<tr>
				<td class="th">إشارة العمليات</td>
				<td>${ref}</td>
				<td class="th">تاريخ إشارة العمليات</td>
				<td>${ref_date}</td>
			</tr>
			<tr>
				<td class="th">نسبة العجز</td>
				<td>${inability_date}</td>
				<td class="th">تاريخ نسبة العجز</td>
				<td>${inability_per}</td>
			</tr>
			<tr>
				<td class="th">القرار</td>
				<td>${decision}</td>
			</tr>
			<tr>
				<td class="th">التصديق</td>
				<td>${approve}</td>
			</tr>
		</table>
		</center>
	</body>
</html>
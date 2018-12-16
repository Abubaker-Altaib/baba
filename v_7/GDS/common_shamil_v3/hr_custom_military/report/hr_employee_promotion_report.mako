<html dir="rtl" lang="ar">
	<head>
		<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
		<style type="text/css">
			.emp-tb{
				width: 90%;
				border-collapse: collapse;
				outline: black 3px solid;

			}
			.emp-tb tr , .emp-tb td , .emp-tb th {
				border: black 1px solid;
				text-align: center;
			}
		</style>
	</head>
	<body>
		<center>
		<p>بسم الله الرحمن الرحيم</p>
		<p><u>سري</u>
			<br />
			كشف الترقيات إلى رتبة ${ref}
		</p>
		
		<table class="emp-tb">
			<tr>
			<th style="width:5%;">
			م
			</th>
			<th style="width:20%;">
			${type}
			</th>
			<th style="width:20%;">
			الرتبة
			</th>
			<th style="width:40%;">
			الاسم
			</th>
			<th style="width:15%;">
				ملحوظات
			</th>
			</tr>
			<tr>
				<td>
				(أ)
				</td>
				<td>
				(ب)
				</td>
				<td>
				(ج)
				</td>
				<td>
				(د)
				</td>
				<td>
				(ه)
				</td>
				</tr>
			%for i , obj in enumerate(vals) :
				<tr>
				<td>
				${i + 1}
				</td>
				<td>
				${obj['code']}
				</td>
				<td>
				${obj['prev']}
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
	</body>
</html>
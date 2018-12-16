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
					<u>طلب تبليغ لإجراءات القمسيون الطبي</u>
				</h2>

				<table class="trh">
					<tr>
					<td>
						<u>البيانات الأساسية</u>
					</td>
					<td width="400">
					</td>

					<td width="100">
						التاريخ
					</td>
					<td>
					${date}
					</td>
					</tr>
				</table>
			</center>
				</div>

				<br/>

				<table>
					<tr>
						<td  width="100">
							<u>رقم البطاقة</u>
						</td>
						<td width="100">
							${otherid}
						</td>
						<td width="300">
						</td>
						<td width="100">
							<b>رقم القيد</b>
						</td>
						<td>
						<b>${name}</b>
						</td>
					</tr>

					<tr>
					</tr>

					<tr>
						<td  width="100">
							<u>الرتبة</u>
						</td>
						<td width="100">
							${degree}
						</td>
						<td width="300">
						</td>
						<td width="100">
						</td>
						<td>
						</td>
					</tr>

					<tr>
					</tr>

					<tr>
						<td  width="100">
							<u>الإسم</u>
						</td>
						<td colspan="4">
							${employee}
						</td>
						
					</tr>

					<tr>
					</tr>

					<tr>
						<td  width="100">
							<u>الإدارة</u>
						</td>
						<td width="100">
							${department}
						</td>
						<td width="300">
						</td>
						<td width="100">
						</td>
						<td>
						</td>
					</tr>

					<tr>
					</tr>

					<tr>
						<td  width="100">
							<u>يتبع إلى</u>
						</td>
						<td width="100">
							${hospital}
						</td>
						<td width="300">
						</td>
						<td width="100">
						</td>
						<td>
						</td>
					</tr>

					<tr>
					</tr>

					<tr>
						<td  width="100">
							<u>تاريخ الميلاد</u>
						</td>
						<td width="100">
							${birthday}
						</td>
						<td width="300">
						</td>
						<td width="100">
						</td>
						<td>
						</td>
					</tr>

					<tr>
					</tr>

					<tr>
						<td  width="100">
							<u>تاريخ التتعيين</u>
						</td>
						<td width="100">
							${employment_date}
						</td>
						<td width="300">
						</td>
						<td width="100">
						</td>
						<td>
						</td>
					</tr>

					<tr>
					</tr>

					<tr>
						<td>
							<u>الغرض من التبليغ</u>
						</td>
						<td width="100">
						</td>
						<td width="300">
						</td>
						<td width="100">
						</td>
						<td>
						</td>
					</tr>

					<tr>
					</tr>

					<tr>
						<td  width="100">
							<u>تاريخ التبليغ</u>
						</td>
						<td width="100">
							${report_date}
						</td>
						<td width="300">
						</td>
						<td width="100">
						</td>
						<td>
						</td>
					</tr>

					<tr>
					</tr>

					<tr>
						<td>
							<u>المرجع</u>
						</td>
						<td width="100">
						</td>
						<td width="300">
						</td>
						<td width="100">
						</td>
						<td>
						</td>
					</tr>

					<tr>
					</tr>

					<tr>
						<td>
							<u>المستندات المرفقة</u>
						</td>
						<td width="100">
						</td>
						<td width="300">
						</td>
						<td width="100">
						</td>
						<td>
						</td>
					</tr>

					<tr>
					</tr>

					<tr>
						<td>
							<u>معنون</u>
						</td>
						<td width="100">
						</td>
						<td width="300">
						</td>
						<td width="100">
						</td>
						<td>
						</td>
					</tr>

					<tr>
					</tr>

					<tr>
						<td width="100">
						</td>
						<td width="100">
						</td>
						<td width="300">
							<u>الرتبة</u>
						</td>
						<td width="100">
						</td>
						<td>
						</td>
					</tr>

					<tr>
					</tr>

					<tr>
						<td width="100">
						</td>
						<td width="100">
						</td>
						<td width="300">
							<u>الإسم</u>
						</td>
						<td width="100">
						</td>
						<td>
						</td>
					</tr>
				</table>
			</br>
				<table>

					<tr>
						<td width="100">
						</td>
						<td width="100">
						</td>
						<td width="100">
						</td>
						<td width="200">
							<b>${company.hq and u'المدير العام' or u'نائب المدير العام'}</b>
						</td>
						<td>
						</td>
					</tr>

					<tr>
					</tr>

					<tr>
						<td width="100">
						</td>
						<td width="100">
						</td>
						<td width="100">
							<b><u>التوقيع</u></b>
						</td>
						<td width="200">
						</td>
						<td>
						</td>
					</tr>
				</table>
				<br/>
				<br/>
				<br/>
				<table>
					<tr>
						<td width="100">
							<u>صورة إلى</u>
						</td>
						<td width="100">
						</td>
						<td width="100">
						</td>
						<td width="400">
						</td>
						<td>
						</td>
					</tr>

					<tr>
						<td width="100">
						</td>
						<td width="100">
							ملف الخدمة
						</td>
						<td width="100">
						</td>
						<td width="400">
						</td>
						<td>
						</td>
					</tr>

					<tr>
						<td width="100">
						</td>
						<td width="100">
							فرع الخدمة العامة
						</td>
						<td width="100">
						</td>
						<td width="400">
						</td>
						<td>
						</td>
					</tr>
				</table>
			</center>
				
		</div>

	</body>

<footer>


</footer>

</html>

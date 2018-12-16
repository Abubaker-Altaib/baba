<html dir="rtl" lang="ar">
	<head>
		<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
		<style type="text/css">

			.tb-data{
				border-collapse: collapse;
				width: 100%;
				outline:  3px solid black;
				max-height: 7px;
				height: 7px;
				font-size: 15px;
				padding-top: 0px;
	    		padding-bottom: 0px;
			}
			.tb-data td , .tb-data th ,.tb-data th{
				
	    		text-align: center;
	    		border: 1px solid black;
	    		padding: 0px;
	    		max-height: 7px;
	    		height: 7px;
	    		font-size: 15px;
	    		padding-bottom: 0px;
	    		padding-top: 0px;
	    		line-height: 8pt;
	    		/*height: 7px;*/
	    		/*white-space: nowrap;*/

	    	}

	    	.tb-data p {
				
	    		text-align: center;
	    		/*border: 1px solid black;*/
	    		padding: 0px;
	    		font-size: 15px;
	    		padding-bottom: 0px;
	    		padding-top: 0px;
	    		height: 7px;
	    		max-height: 7px;
	    		line-height: 8pt;
	    		/*height: 7px;*/
	    		/*white-space: nowrap;*/

	    	}


	    	.tb-data td p{
				
	    		text-align: center;
	    		height: 7px;
	    		max-height: 7px;
	    		padding-bottom: 0px;
	    		padding-top: 0px;
	    		/*white-space: nowrap;*/
	    		font-size: 15px;
	    		line-height: 8pt;

	    	}

	    	.right-block{
	    		float: right;
	    		margin-top: 80px;
	    	}

	    	.trh{
	    		border-bottom: solid 3px black;
	    		font-size: 15px;
	    	}

	    	.trh2{
	    		border-bottom: solid 3px black;
	    		border-top: solid 3px black;
	    		font-size: 15px;
	    		
	    	}


	    	.trh2 th p{
				
	    		text-align: center;
	    		height: 7px;
	    		padding-top: 0px;
	    		padding-bottom: 0px;
	    		line-height: 8pt;

	    	}

	    	.trh th p{
				
	    		text-align: center;
	    		height: 7px;
	    		padding-top: 0px;
	    		padding-bottom: 0px;
	    		line-height: 8pt;


	    	}

	    	.custom td{
	    		text-align: right;
	    	}

	    	td, th, p{
	    		height: 7px;
	    		padding-top: 0px;
	    		padding-bottom: 0px;
	    		line-height: 8pt;
	    	}
	    	th {
	    		font-weight: bold;
	    	}

	    	table {
	    		width: 100%;
	    		font-size: 15px;
	    		padding-top: 0px;
	    		padding-bottom: 0px;
	    		text-align: center;
	    		height: 7px;
	    		max-height: 7px;
	    	}

		</style>
	</head>
	<body>
		<div id="con1" class="container">
			<table>
				<tr class="trh">
					<th width="30%" >
						<p></p>
					</th>
					<th width="30%" >
						<p>بسم الله الرحمن الرحيم</p>
						<p>سري للغاية</p>
						<p></p>
						<p></p>
						<p></p>
						<p></p>
					</th>
					<th width="30%" >
						<p></p>
						<p></p>
						<p></p>
						<p></p>
						<p>جهاز اﻷمن و المخابرات الوطني</p>
						<p>هيئة اﻹدارة</p>
						<p>دائرة الخدمات الهندسية</p>
						<p>إدراة المركبات و الوقود</p>
						<p>فرع الوقود</p>
						<p>التاريخ:${time.strftime("%Y-%m-%d")}</p>
					</th>
					
					
				</tr>
			</table>
			<center>
				<h3 >
					<u>تقرير شرائح الوقود</u>
				</h3>
				<p>
					<!--<u>Insurance Form</u>-->
				</p>
			</center>

			<!-- <table>
				<tr>
				<td width="200" style="font-weight: bold" >
					<u>التاريخ:${time.strftime("%Y-%m-%d")}</u>
				</td>
				<td width="700">
				</td>
				</tr>
			</table> -->
			<br/>

			<center>
				<p style="text-align: right; font-size: 20px;"><u>خيارات التقرير:</u></p>
				<table border="1" class="tb-data">
					<tr  class="trh">
						<th><p>من تاريخ</p></th>
						<th><p>الى تاريخ</p></th>
						<th><p>نوع العملية</p></th>
						<th><p>تصنيف المركبة</p></th>
						<th><p>موديل المركبة</p></th>
						<th><p>الادارة</p></th>
					</tr>
					%for x in selection(data['form']):
						<tr>
							<td><p >${x['date_from']}</p></td>
							<td><p >${x['date_to']}</p></td>
							<td><p >${x['process_type']}</p></td>
							<td><p >${x['type']}</p></td>
							<td><p >${x['year']}</p></td>
							<td><p >${x['department_id']}</p></td>
						</tr>
					%endfor
				<table>
				<br />
				<table border="1" class="tb-data">
					<tr  class="trh">
						<th><p>م.</p></th>
						<th style="width: 90px; "><p>رقم اللوحة</p></th>
						<th style="width: 100px; "><p>رقم الشاسي</p></th>
						<th style="width: 110px; "><p>رقم الماكينة</p></th>
						<!--th><p>نوع المركبة</p></th-->
						<th ><p>ماركة المركبة</p></th>
						<th ><p>شريحة الوقود</p></th>
						<th ><p>الادارة</p></th>
						<th ><p>الرتبة</p></th>
						<th ><p>العضو</p></th>
						<!--th ><p>الاستخدام</p></th-->
					</tr>
					%if record_list(data['form']):
						%for i , l in enumerate(record_data(data['form'])):
							%if page_break(data['form'],i)['count'] == 13 :
								</table>
								<p style="page-break-after: always;">&nbsp;</p>
								<table border="1" class="tb-data">
									<tr  class="trh2">
										<th><p>م.</p></th>
										<th style="width: 90px; "><p>رقم اللوحة</p></th>
										<th style="width: 100px; "><p>رقم الشاسي</p></th>
										<th style="width: 110px; "><p>رقم الماكينة</p></th>
										<!--th><p>نوع المركبة</p></th-->
										<th ><p>ماركة المركبة</p></th>
										<th ><p>شريحة الوقود</p></th>
										<th ><p>الادارة</p></th>
										<th ><p>الرتبة</p></th>
										<th ><p>العضو</p></th>
										<!--th ><p>الاستخدام</p></th-->
									</tr>
									
							%endif
							
							<tr >
								<td><p >${i+1}</p></td>
								<td style="width: 90px;"><p >${l['license_plate']}</p></td>
								<td style="width: 100px;"><p >${l['vin_sn']}</p></td>
								<td style="width: 110px;"><p >${l['machine_no']}</p></td>
								<!--td><p style="height: 39px; max-height: 39px;">${l['type']}</p></td-->
								<td><p >${l['model_name']}</p></td>
								<td><p >${l['fuel_slice']}</p></td>
								<td><p >${l['department_name'] and l['department_name'].strip() or ''}</p></td>
								<td><p >${ l['employee_degree'] or '' }</p></td>
								<td><p >${ l['employee_name'] or '' }</p></td>
							</tr>
								
						%endfor
					%endif


		
		</div>
	</body>

<footer>


</footer>

</html>

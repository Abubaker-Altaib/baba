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
			<center>
				<p >
					<u>بسم الله الرحمن الرحيم</u>
				</p>
				<h3 >
					<u> تقرير المركبات خارج الجهاز</u>
				</h3>
				<p>
					<!--<u>Insurance Form</u>-->
				</p>
			</center>

			<table>
				<tr>
				<td width="200" style="font-weight: bold" >
					<u>التاريخ:${time.strftime("%Y-%m-%d")}</u>
				</td>
				<td width="700">
				</td>
				</tr>
			</table>
			<br/>
			<center>
				<table border="1" class="tb-data">
					%if not data['form']['place_id']:
						<tr  class="trh">
							<th><p>م.</p></th>
							<th style="width: 90px; "><p>رقم اللوحة</p></th>
							<th style="width: 100px; "><p>رقم الشاسي</p></th>
							<th style="width: 110px; "><p>رقم الماكينة</p></th>
							<!--th><p>نوع المركبة</p></th-->
							<th ><p>موديل المركبة</p></th>
							<th ><p>ماركة المركبة</p></th>
							<th ><p>الادارة</p></th>
							<th ><p>السائق الخارجي</p></th>
							<th ><p>الاستخدام</p></th>
						</tr>
					%endif
					%if data['form']['place_id']:
						<tr  class="trh">
							<th><p>م.</p></th>
							<th style="width: 90px; "><p>رقم اللوحة</p></th>
							<th style="width: 100px; "><p>رقم الشاسي</p></th>
							<th style="width: 110px; "><p>رقم الماكينة</p></th>
							<!--th><p>نوع المركبة</p></th-->
							<th ><p>موديل المركبة</p></th>
							<th ><p>ماركة المركبة</p></th>
							<th ><p>الادارة</p></th>
							<th ><p>موقع المركبة</p></th>
							<th ><p>نوع الوقود</p></th>
							<th ><p>الاستخدام</p></th>
						</tr>
					%endif
					%if vehicle_list(data['form']):
						%for i , l in enumerate(vehicle_data(data['form'])):
							%if page_break(data['form'],i)['count'] == 13 :
								</table>
								<p style="text-align:right">اجمالي السجلات:${len(total_data(data['form']))}</p>
								<p style="page-break-after: always;">&nbsp;</p>
								<table border="1" class="tb-data">
									%if not data['form']['place_id']:
										<tr  class="trh2">
											<th><p>م.</p></th>
											<th style="width: 90px; "><p>رقم اللوحة</p></th>
											<th style="width: 100px; "><p>رقم الشاسي</p></th>
											<th style="width: 110px; "><p>رقم الماكينة</p></th>
											<!--th><p>نوع المركبة</p></th-->
											<th ><p>موديل المركبة</p></th>
											<th ><p>ماركة المركبة</p></th>
											<th ><p>الادارة</p></th>
											<th ><p>السائق</p></th>
											<th ><p>الاستخدام</p></th>
										</tr>
									%endif
									%if data['form']['place_id']:
										<tr  class="trh2">
											<th><p>م.</p></th>
											<th style="width: 90px; "><p>رقم اللوحة</p></th>
											<th style="width: 100px; "><p>رقم الشاسي</p></th>
											<th style="width: 110px; "><p>رقم الماكينة</p></th>
											<!--th><p>نوع المركبة</p></th-->
											<th ><p>موديل المركبة</p></th>
											<th ><p>ماركة المركبة</p></th>
											<th ><p>الادارة</p></th>
											<th ><p>موقع المركبة</p></th>
											<th ><p>نوع الوقود</p></th>
											<th ><p>الاستخدام</p></th>
										</tr>
									%endif
							%endif
							%if data['form']['vehicle_type'] and data['form']['vehicle_type'] == 'state':
								%if not data['form']['place_id']:
									<tr >
										<td><p >${i+1}</p></td>
										<td style="width: 90px;"><p >${l['license_plate']}</p></td>
										<td style="width: 100px;"><p >${l['vin_sn']}</p></td>
										<td style="width: 110px;"><p >${l['machine_no']}</p></td>
										<!--td><p style="height: 39px; max-height: 39px;">${l['type']}</p></td-->
										<td><p >${l['year']}</p></td>
										<td><p >${l['model_name']}</p></td>
										<td><p >${l['department_name'] and l['department_name'].strip() or ''}</p></td>
										<td><p >${'-'}</p></td>
										<td><p >${(l['out_driver'] and l['out_driver']) or '' }</p></td>
										<td><p >${l['use_name']}</p></td>
									</tr>
								%endif
								%if data['form']['place_id']:
									<tr >
										<td><p >${i+1}</p></td>
										<td style="width: 90px;"><p >${l['license_plate']}</p></td>
										<td style="width: 100px;"><p >${l['vin_sn']}</p></td>
										<td style="width: 110px;"><p >${l['machine_no']}</p></td>
										<!--td><p style="height: 39px; max-height: 39px;">${l['type']}</p></td-->
										<td><p >${l['year']}</p></td>
										<td><p >${l['model_name']}</p></td>
										<td><p >${l['department_name'] and l['department_name'].strip() or ''}</p></td>
										<td><p >${l['place_name']}</p></td>
										<td><p >${ (l['fuel_type'] == 'gasoline' and u'جازولين') or (l['fuel_type'] == 'diesel' and u'بنزين') or (l['fuel_type'] == 'electric' and u'كهربائي') or (l['fuel_type'] == 'hybrid' and u'هجين') or '' }</p></td>
										<td><p >${l['use_name']}</p></td>
									</tr>
								%endif
							%endif
							%if not data['form']['vehicle_type'] or data['form']['vehicle_type'] == 'non-state':
								%if not data['form']['place_id']:
									<tr >
										<td><p >${i+1}</p></td>
										<td style="width: 90px;"><p >${l['license_plate']}</p></td>
										<td style="width: 100px;"><p >${l['vin_sn']}</p></td>
										<td style="width: 110px;"><p >${l['machine_no']}</p></td>
										<!--td><p style="height: 39px; max-height: 39px;">${l['type']}</p></td-->
										<td><p >${l['year']}</p></td>
										<td><p >${l['model_name']}</p></td>
										<td><p >${l['department_name'] and l['department_name'].strip() or ''}</p></td>
										<td><p >${ (l['out_driver'] and l['out_driver']) or '' }</p></td>
										<td><p >${l['use_name']}</p></td>
									</tr>
								%endif
								%if data['form']['place_id']:
									<tr >
										<td><p >${i+1}</p></td>
										<td style="width: 90px;"><p >${l['license_plate']}</p></td>
										<td style="width: 100px;"><p >${l['vin_sn']}</p></td>
										<td style="width: 110px;"><p >${l['machine_no']}</p></td>
										<!--td><p style="height: 39px; max-height: 39px;">${l['type']}</p></td-->
										<td><p >${l['year']}</p></td>
										<td><p >${l['model_name']}</p></td>
										<td><p >${l['department_name'] and l['department_name'].strip() or ''}</p></td>
										<td><p >${l['place_name']}</p></td>
										<td><p >${ (l['fuel_type'] == 'gasoline' and u'جازولين') or (l['fuel_type'] == 'diesel' and u'بنزين') or (l['fuel_type'] == 'electric' and u'كهربائي') or (l['fuel_type'] == 'hybrid' and u'هجين') or '' }</p></td>
										<td><p >${l['use_name']}</p></td>
									</tr>
								%endif
							%endif
						%endfor
					%endif


		
		</div>
	</body>

<footer>


</footer>

</html>

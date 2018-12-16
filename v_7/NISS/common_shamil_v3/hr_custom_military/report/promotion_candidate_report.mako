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
					<u>تقرير المرشحين للترقية من رتبة ${data['form']['degree_from'] and data['form']['degree_from'] or '-'} الى رتبة  ${data['form']['degree_to'] and data['form']['degree_to'] or '-'} </u>
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
					<tr  class="trh">
						<th><p>م.</p></th>
						<th ><p>رقم البطاقة</p></th>
						<th ><p>الرتبة</p></th>
						<th ><p>الاسم</p></th>
						<!--th><p>نوع المركبة</p></th-->
						<th ><p>الادارة</p></th>
						<th ><p>الوظيفة</p></th>
						<th ><p>تاريخ الدخول في الرتبة</p></th>
						<th ><p>وضع الخدمة</p></th>
						<!--th ><p>العضو</p></th>
						<th ><p>الاستخدام</p></th-->
					</tr>
					%if data['form']['emp_list']:
						%for i , l in enumerate(data['form']['emp_list']):
							%if page_break(data['form'],i)['count'] == 13 :
								</table>
								<!--p style="text-align:right">اجمالي السجلات:${len(total_data(data['form']))}</p-->
								<p style="page-break-after: always;">&nbsp;</p>
								<table border="1" class="tb-data">
									<tr  class="trh">
										<th><p>م.</p></th>
										<th ><p>رقم البطاقة</p></th>
										<th ><p>الرتبة</p></th>
										<th ><p>الاسم</p></th>
										<!--th><p>نوع المركبة</p></th-->
										<th ><p>الادارة</p></th>
										<th ><p>الوظيفة</p></th>
										<th ><p>تاريخ الدخول في الرتبة</p></th>
										<th ><p>وضع الخدمة</p></th>
										<!--th ><p>العضو</p></th>
										<th ><p>الاستخدام</p></th-->
									</tr>
							%endif
							<tr >
								<td><p >${ i+1 }</p></td>
								<td><p >${ l['otherid'] }</p></td>
								<td><p >${ l['degree'] }</p></td>
								<td><p >${ l['name'] }</p></td>
								<!--td><p style="height: 39px; max-height: 39px;">${l['type']}</p></td-->
								<td><p >${ l['department'] }</p></td>
								<td><p >${ l['job'] }</p></td>
								<td><p >${ l['promotion_date'] }</p></td>
								<td><p >${ l['service_state'] }</p></td>
								<!--td><p >${(l['employee_name'] and (l['employee_degree'] + u'/' + l['employee_name']) ) or (l['old_system_driver'] and l['old_system_driver']) or '' }</p></td>
								<td><p >${l['use_name']}</p></td-->
							</tr>
								
						%endfor
					%endif


		
		</div>
	</body>

<footer>


</footer>

</html>

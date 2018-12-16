<html dir="rtl" lang="ar">
	<head>
		<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
		<style type="text/css">

			.tb-data{
				border-collapse: collapse;
				width: 100%;
				font-weight: bold;
	    		/*transform: rotate(-90deg); 
	    		transform-origin: top left;
	    		-moz-transform: rotate(-90deg);
	    		-ms-transform: rotate(-90deg);
	    		-o-transform: rotate(-90deg);
	    		-webkit-transform: rotate(-90deg);*/
				outline:  3px solid black;
				margin-left: 0px;
				padding-left: 0px;
				margin-right: 0px;
				padding-right: 0px;

				font-size: 25px;
	    		padding-top: 0px;
	    		padding-bottom: 0px;
	    		text-align: center;
	    		height: 180px;
	    		max-height: 180px;
			}

			.tb-data td , .tb-data th {
				
	    		text-align: center;
	    		border: 1px solid black;
	    		padding: 0px;
	    		font-size: 20px;
	    		padding-top: 0px;
	    		padding-bottom: 0px;
	    		padding-left: 0px;
	    		padding-right: 0px;
	    		
	    		/*vertical-align: bottom;*/
	    		/*white-space: nowrap;*/

	    	}

	    	.tb-data td {
				
	    		/*width: 20px;*/
	    		height: 100px;
	    		max-height: 100px;
	    		max-width: 60px;

	    	}


	    	.tb-data th {
				
	    		text-align: center;
	    		border: 1px solid black;
	    		padding: 0px;
	    		font-size: 25px;
	    		padding-top: 0px;
	    		padding-bottom: 0px;
	    		height: 180px;
	    		max-height: 180px;
	    		/*width: 20px;*/
	    		/*white-space: nowrap;*/

	    	}

	    	.tb-data td p {
				
	    		/*border: 1px solid black;*/
	    		padding: 0px;
	    		font-size: 20px;
	    		padding-bottom: 0px;
	    		padding-top: 0px;
	    		padding-left: 0px;
	    		padding-right: 0px;
	    		height: 170px;
	    		max-height: 170px;
	    		line-height: 15pt;
	    		/*transform: translate(0, 100%) rotate(-90deg); 
	    		transform-origin: 0 0;
	    		-moz-transform: rotate(-90deg);
	    		-ms-transform: rotate(-90deg);
	    		-o-transform: rotate(-90deg);
	    		-webkit-transform: rotate(-90deg);*/
	    		display: inline-block;
	    		max-width: 60px;
	    		/*vertical-align: bottom;
	    		position: relative;*/
	    		writing-mode: vertical-rl;
	    		/*min-width: 100px;*/
	    		-webkit-writing-mode: vertical-rl;
	    		text-align: center;
	    		/*height: 7px;*/
	    		/*white-space: nowrap;*/
	    		/*width: 20px;*/

	    	}
	    	

	    	/*.tb-data td p{
				
	    		text-align: center;
	    		height: 50px;
	    		max-height: 50px;
	    		padding-bottom: 0px;
	    		padding-top: 0px;
	    		font-size: 25px;
	    		line-height: 8pt;
	    		width: 20px;

	    	}*/
			

	    	.trh{
	    		/*border-bottom: solid 2px black;*/
	    		/*outline:  2px solid black;*/
	    		border: 2px solid black;
	    	}

	    	.trh2{
	    		border-bottom: solid 3px black;
	    		border-top: solid 3px black;
	    		font-size: 25px;
	    		
	    	}

	 

	    	td, th, p{
	    		height: 10px;
	    		padding-top: 0px;
	    		padding-bottom: 0px;
	    		line-height: 8pt;
	    	}
	    	

	    	table {
	    		width: 100%;
	    		font-size: 25px;
	    		padding-top: 0px;
	    		padding-bottom: 0px;
	    		text-align: center;
	    		height: 50px;
	    		max-height: 50px;
	    	}

		</style>
	</head>
	<body>
		<div id="con1" class="container">
			<center>
				<p>
					<u>بسم الله الرحمن الرحيم</u>
				</p>
				<h3>
					<u>تقرير المركبات</u>
				</h3>
				
			</center>

			<table>
				<tr>
				<td width="200">
					<u>التاريخ:${time.strftime("%Y-%m-%d")}</u>
				</td>
				<td width="700">
				</td>
				</tr>
			</table>
			<br/>
			<center>
				%if vehicle_list(data['form']):
					%for i in range(0, loop_num(data['form'])):
						<table class="tb-data">
							<tr  border="1" >
								<td><p>التصنيف</p></td>
								%for l in vehicle_data(data['form'])['headers']:
									%if header_break(data['form']):
										%if header_count(data['form']) <= len(vehicle_data(data['form'])['headers']):
											<td ><p>${vehicle_data(data['form'])['headers'][header_count(data['form'])-1]}</p></td>
										%endif
										%if header_count(data['form']) % 17 == 0 and header_count(data['form']) >= 17:
											<% break %>
										%endif
									%endif
								%endfor
							</tr>

							<tr>
								<td style="height: 80px;max-height: 80px;"><p style="height: 80px;max-height: 80px;">عدد المركبات</p></td>
								%for l in vehicle_data(data['form'])['data']:
									%if data_break(data['form']):
										%if data_count(data['form']) <= len(vehicle_data(data['form'])['data']):
											<td style="height: 80px;max-height: 80px;">${vehicle_data(data['form'])['data'][data_count(data['form'])-1][0]['count']}</td>
										%endif
										%if data_count(data['form']) % 17 == 0 and data_count(data['form']) >= 17:
											<% break %>
										%endif
									%endif

								%endfor

									
							</tr>
							<!--tr><td style="height: 2px; max-height: 2px;"></td></tr-->
						</table>
						<br/>
						%if (i+1)%2 == 0 and (i+1) >= 2 and i != loop_num(data['form'])-1 :
							<p style="page-break-after: always;">&nbsp;</p>
							<br/>
						%endif
					%endfor
					<p style="text-align: right; font-size: 25px;"><span>اﻹجمالي:${get_sum()}</span></p>

					<!--table class="tb-data" style="margin-left: 50px;">
						<tr  class="trh2">
							<th outline="3px solid black;"><p>التصنيف</p></th>
							<th outline="3px solid black;"><p>عدد المركبات</p></th>
						</tr>
						%for l in vehicle_data(data['form'])['datas']:
							%if page_break(data['form'])['count'] == 25 :
								</table>
								<br/>
								<table class="tb-data" style="margin-left: 50px;">
									<tr  class="trh2">
										<th outline="3px solid black;"><p>التصنيف</p></th>
										<th outline="3px solid black;"><p>عدد المركبات</p></th>
									</tr>
							%endif
							<tr>
								<th><p>${l['model']}</p></th>
								<td><p>${l['count']}</p></td>
							</tr>
						%endfor
						
					</table-->
				%endif	
					
					


		
		</div>
	</body>

<footer>


</footer>

</html>

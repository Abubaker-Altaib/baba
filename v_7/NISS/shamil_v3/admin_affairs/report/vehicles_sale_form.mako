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
	    		padding: 5px;
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
	    		border-bottom: solid 3px black;
	    	}

	    	.custom td{
	    		text-align: right;
	    		font-size: 16px;
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
					<u>بسم الله الرحمن الرحيم</u>
				</p>
				<p>
					<u><b>إشعار دلالة</b></u>
				</p>
				<p>
					<!--<u>Insurance Form</u>-->
				</p>
			</center>

			<table>
				<tr>
				<td width="700">
				</td>
				<td width="200">
					<u>التاريخ:${date}</u>
				</td>
				</tr>
			</table>
			<table class="custom">
				<tr>
				<td width="600"><pre>المرجع:    ${ref}</pre></td>
				<td width="200"><pre>إسم الدلالة:    ${name}</pre></td>
				</tr>

				<tr>
				<td width="600"><pre>تاريخ البيع:   ${sale_date}</pre></td>
				<td width="200"><pre>نوع الدلالة:    ${type}</pre></td>
				</tr>
				
				<tr>
				<td width="600"></td>
				<td width="200"></td>
				</tr>
				
			</table>
			<br/>
			<center>
				<table border="1" class="tb-data">
				<tr class="trh">
				<th>
					م.
				</th>
				<th>
					المركبة
				</th>
				<th>
					الموديل
				</th>
				<th>
					رقم الشاسي
				</th>
				<th>
					تقييم الشركة
				</th>
				<th>
					تقييم اللجنة
				</th>
				<th>
					المبلغ المتفق عليه
				</th>
				<th>
					مبلغ البيع
				</th>
				<th width="200">
					المشتري
				</th>
				<!--th>
					رقم البطاقة
				</th-->
					
				</tr>
				%for i,l in enumerate(lines):
					<tr>
					<td>
						${i+1}
					</td>
					<td>
						${l['vehicle']} 
					</td>
					<td>
						${l['year']} 
					</td>
					<td>
						${l['vin_sn']}
					</td>
					<td>
						${l['company_assess']}
					</td>
					<td>
						${l['committee_assess']}
					</td>
					<td>
						${l['agreed_amount']} 
					</td>
					<td>
						${l['actual_sale_amount']} 
					</td>
					<td width="200">
						${l['purchaser']}
					</td>
					<!--td>
						${l['card_no']}
					</td-->

					</tr>
				%endfor
			</table>
		</center>
			<br/>
			<br/>
			<table class="custom">
				<tr>
					<td width="200"><pre>إجمالي المبلغ المتفق عليه: ${amount_total}</pre></td>
					<td width="300"></td>
					<td width="200"><pre>إجمالي مبلغ البيع الحقيقي: ${actual_sale_amount_total}</pre></td>
				</tr>
				
			</table>


		</div>
	</body>
<footer>


</footer>

</html>

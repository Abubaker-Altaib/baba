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
	    		border-bottom: solid 3px black;
	    	}

	    	.custom td{
	    		text-align: right;
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
					<u>إشعار تأمين مركبات</u>
				</p>
				<p>
					<!--<u>Insurance Form</u>-->
				</p>
			</center>

			<table>
				<tr>
				<td width="200">
					<u>التاريخ:${date}</u>
				</td>
				<td width="700">
				</td>
				</tr>
			</table>
			<table class="custom">
				<tr>
				<td width="900"><pre>المرجع:    ${ref}</pre></td>
				<td width="200"><pre>نوع التأمين:    ${insurance_type}</pre></td>
				</tr>

				<tr>
				<td width="900"><pre>المورد:   ${insurer_id}</pre></td>
				<td width="200"><pre>تاريخ الطلب:    ${insurance_date}</pre></td>
				</tr>
				<tr>
				<td width="900"><pre>تاريخ التأمين:    ${start_date}</pre></td>
				<td width="200"><pre>تاريخ النهاية:   ${expiration_date}</pre></td>
				</tr>
				
				<tr>
				<td width="900"></td>
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
					نوع المركبة
				</th>
				<th>
					رقم الشاسي
				</th>
				<th>
					رقم الماكينة
				</th>
				<th>
					الموديل
				</th>
				</tr>
				%for i,l in enumerate(lines):
					<tr>
					<td>
						${i+1} 
					</td>
					<td>
						${l['type']} 
					</td>
					<td>
						${l['vin_sn']}
					</td>
					<td>
						${(str(u'بدون'.encode('utf-8')) in str(l['machine_no'].encode('utf-8')) and u'بدون') or l['machine_no']}
					</td>
					<td>
						${l['year']} 
					</td>
					</tr>
				%endfor

		
		</div>
	</body>

<footer>


</footer>

</html>

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
	    		text-align: left;
	    		padding: 10px;
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
					<u>إستمارة عمل</u>
				</p>
				<p>
					<u>Job Form</u>
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
				<td width="100">${vehicle_id.license_plate}</td>
				<td width="200">:PLATE NO</td>
				<td width="300"></td>
				<td width="100">${ref}</td>
				<td width="200">:JOB NO</td>
				<td width="100"></td>
				</tr>

				<tr>
				<td width="100">${vehicle_id.model_id.modelname}</td>
				<td width="200">:MODEL YEAR</td>
				<td width="300"></td>
				<td width="100">${vehicle_id.vin_sn}</td>
				<td width="200">:CHASSY NO</pre></td>
				<td width="100"></td>
				</tr>
				<tr>
				<td width="100">${vehicle_id.fuel_type or " "}</td>
				<td width="200">:FUEL TYPE</td>
				<td width="300"></td>
				<td width="100">${vehicle_id.type.name or " "}</td>
				<td width="200">:CAR TYPE</td>
				<td width="100"></td>
				</tr>
				<tr>
				<td width="100"></td>
				<td width="200"></td>
				<td width="300"></td>
				<td width="100">${job_date}</td>
				<td width="200">:JOB DATE</td>
				<td width="100"></td>
				</tr>
				<tr>
				<td width="100"></td>
				<td width="200"></td>
				<td width="300"></td>
				<td width="100"></td>
				<td width="200"></td>
				<td width="100"></td>
				</tr>
				<tr>
				<td width="100" colspan="2">
					%for i in enumerate(eng_ids):
					${i[1]}<br/>
					%endfor
				</td>
				<td width="200">:CHECKED BY
				</td>
				<td width="100">${driver.name or " "}</td>
				<td width="200">:DRIVER</td>
				<td width="100"></td>
			</tr>
				</tr>

			</table>
			<br/>
			<center>
				<table border="1" class="tb-data">
				<tr class="trh">
				<th>
					<u>Remarks</u>
				</th>
				<th>
					<u>Qty</u>
				</th>
				<th>
					<u>Part Description</u>
				</th>
				<th>
					<u>Part Number</u>
				</th>
				</tr>
				%for l in lines:
					<tr>
					<td>
						
					</td>
					<td>
						${l['quantity']} 
					</td>
					<td>
						${l['description']}
					</td>
					<td>
						${l['product_id']}
					</td>
					</tr>
				%endfor

		
		</div>
	</body>

<footer>


</footer>

</html>

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
					<u>إسبيرات المهام الخارجية</u>
				</p>
				<p>
					<u>Mission Spare Parts</u>
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
				<td width="300"><pre>Team Leader:    ${mission_leader}</pre></td>
				<td width="900"><pre>Mission No:    ${mission_no}</pre></td>
				<td width="100"></td>
				</tr>

				<tr>
				<td width="500"><pre>Mission Date:   ${mission_date}</pre></td>
				<td width="900"><pre>Mission To:    ${mission_to}</pre></td>
				</tr>
				
				<tr>
				<td width="500"></td>
				<td width="900"></td>
				</tr>
				
				</tr>

			</table>
			<br/>
			<center>
				<table border="1" class="tb-data">
				<tr class="trh">
				<th>
					Remarks
				</th>
				<th>
					Qty
				</th>
				<th>
					DOC NO (12 س)
				</th>
				<th>
					Part Description
				</th>
				<th>
					Part Number
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
						
					</td>
					<td>
						${l['description']}
					</td>
					<td>
						${l['product_id']}
					</td>
					</tr>
				%endfor
				<br/>
				<br/>
				<table class="custom">
				<tr>
				<td width="150"></td>
				<td width="350"></td>
				<td width="400"></td>
				</tr>
				<tr>
				<td width="150">Approved By    </td>
				<td width="50">Issued By    </td>
				<td width="400">Recieved By    </td>
				</tr>
				<tr>
				<td width="150"></td>
				<td width="350"></td>
				<td width="400"></td>
				</tr>

				<tr>
				<td width="150">    </td>
				<td width="350">   </td>
				<td width="400"><pre>زمن الطباعة:   ${time}</pre></td>
				</tr>

			</table>

		
		</div>
		
	</body>

<footer>


</footer>

</html>

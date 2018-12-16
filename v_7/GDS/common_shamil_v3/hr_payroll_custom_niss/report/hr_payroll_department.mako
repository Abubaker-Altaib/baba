<html dir="rtl" lang="ar">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
    <style type="text/css">
    	table{
    		width: 85%;
    		border-collapse: collapse;
    		text-align: center;
    	}

    	.net{
    		width: 35%;
    		border: 1px solid black;
    	}
    	.state{
    		width: 50%;
    		border: 1px solid black;
    	}
    	th{
    		background-color: #bdc3c7;
    	}
    </style>
</head>

<body>
   <center>
		<h2>
		كشف المرتبات 
		<br />
		شهر ${data['form']['month'] or ""}  عام ${data['form']['year'] or ""}
		</h2>	

		<table>
			<tr>
				<th class="state"> المنطقة </th>
				<th class="net">الاجمالي</th>
			</tr>
			%for dep in department(data) :
			<tr>
				<td class="state">${dep['dep_name']}
				</td>
				<td class="net">
					%for amount in process(data ,dep['dep_id'] ) :
						${amount['net'] or 0}
					%endfor
				</td>
			</tr>
		%endfor
			<tr>
				<th class="state">المجموع الكلي</th>
				<th class="net">${final_amount()}</th>
			</tr>
		</table>

	</center>
</body>

</html>
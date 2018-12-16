<html>

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
    <style type="text/css">
        
        .custom td {
            border: 1px solid black;

        }

        .custom {
            border-collapse: collapse;
            border: 1px solid black;
            width: 100%;
            font-size: 10px;
            font-weight: bold;
            text-align: center;
        }
    </style>
</head>

<body>

	

	
    <center>
        <h4>سري للغاية</h4>
    </center>
    <table>
        <tr>
            <td colspan="2" style="text-align: center;">
               <h4>${from_company2department}</h4>
            </td>
            
            <td width="700">
            </td>
        </tr>
    	<tr>
			<td width="200" style="text-align: right;">
				${number}
			</td>
			<td width="50">
				:النمرة
			</td>
			<td width="700">
			</td>
		</tr>
		<tr>
			<td width="200" style="text-align: right;">
				${date}
			</td>
			<td width="50">
				:التاريخ
			</td>
			<td width="700">
			</td>
		</tr>
	</table>
	<center>
        <h3><u><b>أوامر جزء أول رقم ( ${sequance} ) ${setting}</b></u></h3>
    </center>
    <p style="text-align: right;">${report_header}</p>
        <br/>

    %if emps: 
    	<h3 style="text-align: right;"> -:أساسي</h3>
            <table class="custom">
                    <tr>
                    	<td>
                            <p> الإدارة</p>
                        </td>
                        <td>
                            <p> التلفون</p>
                        </td>
                        <td>
                            <p> اﻹسم</p>
                        </td>
                        <td>
                            <p>الرتبة</p>
                        </td>
                        <td>
                            <p> التاريخ </p>
                        </td>
                        <td>
                            <p> اليوم</p>
                        </td>
                        <td>
                            <p> .م </p>
                        </td>
                    </tr>

                %for i,emp in enumerate(emps):
                <tr>
                    <td>
                        <p> ${emp['department']} </p>
                    </td>
                    <td>
                        <p> ${emp['phone']} </p>
                    </td>
                    <td>
                        <p> ${emp['employee']} </p>
                    </td>
                    <td>
                        <p> ${emp['degree']} </p>
                    </td>
                    <td>
                        <p> ${emp['date']} </p>
                    </td>
                    <td>
                        <p> ${emp['weekday']} </p>
                    </td>
                    <td>
                        <p> ${i+1} </p>
                    </td>
                </tr>
                %endfor
            </table>

                <h3 style="text-align: right;"> -:إحتياطي</h3>
            <table class="custom">

                    <tr>
                    	 <td>
                            <p> الإدارة</p>
                        </td>
                        <td>
                            <p> التلفون</p>
                        </td>
                        <td>
                            <p> اﻹسم</p>
                        </td>
                        <td>
                            <p>الرتبة</p>
                        </td>
                    	<td>
                            <p> .م </p>
                        </td>
                    </tr>

                <tr>
                	<td>
                        <p> ${alternative1.department_id.name} </p>
                    </td>
                    <td>
                        <p> ${alternative1.work_phone or alternative1.mobile_phone} </p>
                    </td>
                    <td>
                        <p> ${alternative1.name} </p>
                    </td>
                    <td>
                        <p> ${alternative1.degree_id.name} </p>
                    </td>
                    <td>
                        <p> 1 </p>
                    </td>
                </tr>

                <tr>
                	<td>
                        <p> ${alternative2.department_id.name} </p>
                    </td>
                    <td>
                        <p> ${alternative2.work_phone or alternative2.mobile_phone} </p>
                    </td>
                    <td>
                        <p> ${alternative2.name} </p>
                    </td>
                    <td>
                        <p> ${alternative2.degree_id.name} </p>
                    </td>
                    <td>
                        <p> 2 </p>
                    </td>
                </tr>
            </table>
    %endif
    				%if report_alerts: 
	                    <h3 style="text-align: right;"> -:تنبيه</h3>
	                    
	                    	<p style="text-align: right;">  ${report_alerts} </p>
	                  
                    %endif
</body>

</html>
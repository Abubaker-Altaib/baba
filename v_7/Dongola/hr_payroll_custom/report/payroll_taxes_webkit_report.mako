<html >
<head>
    <style type="text/css">
        ${css}
.list_main_table {
    border:thin solid #E3E4EA;
    text-align:center;
    border-collapse: collapse;
}
table.list_main_table {
    margin-top: 20px;
}
.list_main_headers {
    padding: 0;
    background-color:#3366CC;
}
.list_main_headers th {
    background-color: #3366CC;
    border: thin solid #110000;
    padding-right:3px;
    padding-left:3px;
    text-align:center;
    font-size:12;
    font-weight:bold;
}
.list_main_table td {
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
}
    </style>
</head>
<body>
        <center><h1>${_("تقرير")} ${ data['form']['process']=='monthly' and u'ضريبة الموظفين الشهرية' or data['form']['process']=='candidate' and u' الموظفين المرشحين للإعفاء الضريبي' or data['form']['process']=='exempted' and u' الموظفين المعفيين من الضريبة'} </h1></center>
        <br/><br/><br/>
         %if  data['form']['process']=='candidate' :
	<table class="basic_table" width="100%" align="center" style="text-align:center" border="1">

	    <tr style="background-color:3366CC">
		<td width="20%">
                        <b>العدد</b>
		</td>
		<td width="70%">
                        <b>الإدارة</b>
		</td>
		<td width="10%">
                        <b>#</b>
		</td>
	    </tr>
           %if dept(data['form']) :
               %for line in dept(data['form']) :
	    <tr>
		<td>
                  <p>${ line['count']} </p>
		</td>
		<td>
                  <p>${ line['department']} </p>
		</td>
		<td>
                  <p>${ line['no']} </p>
		</td>
	   </tr>
                    %endfor
          %endif
		</table>
         %endif
        <br/><br/><br/>
        <br/><br/><br/>
        %if  data['form']['process']!='monthly' and emps(data['form']):
	<table class="basic_table" width="100%" align="center" style="text-align:center" border="1">
	    <tr style="background-color:3366CC">
		<td width="15%">
                        <b>التعيين</b>
		</td>
		<td width="15%">
                        <b>الميلاد</b>
		</td>
		<td width="55%">
                        <b>الموظف</b>
		</td>
		<td width="10%">
                        <b>الرقم</b>
		</td>
		<td width="5%">
                        <b>#</b>
		</td>
	    </tr>

           %for emp in emps(data['form']) :
	    <tr>
		<td>
                 <p>${ emp.first_employement_date or ''  } </p>
		</td>
		<td>
                 <p>${ emp.birthday or ''  } </p>
		</td>
		<td>
                 <p>${ emp.name or ''  } </p>
		</td>
		<td>
                 <p>${ emp.emp_code or ''  } </p>
		</td>
		<td>
                 <p></p>
		</td>
	   </tr>
           %endfor
		</table>
         %endif
		<br/><br/>
        %if data['form']['process']=='monthly' and allowance(data['form']):
	<table class="list_main_table" width="100%" align="center"  border="1">
            %for line in allowance(data['form']) :
            <tr >   
                %for clm in line:
                 <td >
                      <p> ${clm} </p>
                 </td>
                %endfor
           </tr>
        %endfor
    </blockTable>
    %endif
</body>
</html>

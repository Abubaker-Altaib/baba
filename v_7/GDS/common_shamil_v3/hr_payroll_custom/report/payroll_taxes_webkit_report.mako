<html lang="ar">
<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
<head>
     <style type="text/css">
        ${css}
        table, td, th {
            border: 1px solid black;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            font-size: 10px;
            border-spacing: 10px;
            text-align: center;
        }

        th {
            height: 2px;
        }
        tr {
            height: 2px;
            line-height: 7px;
        }
        td{
            margin-top :0px;
            margin-bottom: 0px;
        }
    </style>
</head>
<body>
        <center><h1>${_("تقرير")} ${ data['form']['process']=='monthly' and u'ضريبة الموظفين الشهرية' or data['form']['process']=='candidate' and u' الموظفين المرشحين للإعفاء الضريبي' or data['form']['process']=='exempted' and u' الموظفين المعفيين من الضريبة'} ${ data['form']['process']!='exempted' and u'لشهر'} ${data['form']['process']!='exempted' and data['form']['month']} ${ data['form']['process']!='exempted' and u'عام'} ${ data['form']['process']!='exempted' and data['form']['year']}</h1></center>
        <br/>
         %if  data['form']['process']=='candidate' :
	<table class="basic_table" width="100%" align="center" style="text-align:center" border="1" cellpadding="1">

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
        <br/>
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
		<br/>
        %if data['form']['process']=='monthly' and allowance(data['form']):
	<table class="list_main_table" width="100%" align="center"  border="1" cellpadding="1">
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


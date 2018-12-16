<html >
    <head>
    <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
        <style type="text/css">
            ${css}
        </style>
    </head>
    <body>
        %if emps(data['form']):
        	<center><h1>تقرير التأمين الإجتماعي لشهر ${ data['form']['month']} عام  ${ data['form']['year']}</h1></center>
			<table class="basic_table" width="100%" align="center" style="vertical-align: middle;" border="1">
	            <tr style="font-weight:bold;background:#D1D1ff;">
	                <td width="10%"><p>المجموع</p></td>
	                <td width="10%"><p>نصيب الشركة</p></td>    
	                <td width="10%"><p>إلتزام المؤمن</p></td>
	                <td width="10%"><p>الخاضع للتأمين</p></td>
	                <td width="10%"><p>الأساسي</p></td>
	                <td width="12%"><p>ت. التعيين</p></td>
	                <td width="13%"><p>رقم التأمين</p></td>
	                <td width="25%"><p>الموظف</p></td>
	            </tr>
	            %for rec in  emps(data['form']):
	            <tr>
	                <td><p>${ rec['total'] or '0'  }</p></td>
	                <td><p>${ rec['comm'] or '0'  } </p></td>
	                <td><p>${ rec['insu'] or '0'  } </p></td>           
	                <td><p>${ rec['wage'] or '0'  } </p></td>                      
	                <td><p>${ rec['basic'] or '0'  } </p></td>
	                <td><p>${ rec['E_date'] or ''  } </p></td>          
	                <td><p>${ rec['sn'] or ''  } </p> </td>      
	                <td style="padding-right:10px;text-align:right"><p>${ rec['name'] or ''  } </p> </td>
	            </tr>
	            %endfor
	        </table>
			<table class="basic_table" width="100%" align="center" style="vertical-align: middle;" border="1">
	           <tr style="font-weight:bold">
	                <td  width="10%"><p>${total()['last_total'] or '0'}</p></td>
	                <td width="10%"><p>${total()['comm_total'] or '0'}</p></td>    
	                <td width="10%"><p>${total()['insu_total'] or '0'}</p></td>
	                <td width="70%"><p>الإجمالي</para> </td>
	            </tr>
	        </table>
        %endif
</body>
</html>

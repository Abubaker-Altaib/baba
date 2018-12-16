<html >
    <head>
    <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
        <style type="text/css">
            ${css}
        </style>
    </head>
    <body>
        <center><h1> </h1></center>
        %if emps(data['form']):
        <center><h1>تقرير التأمين الإجتماعي لشهر ${ data['form']['month']} عام  ${ data['form']['year']}</h1></center>
        <br/><br/><br/>
	<table class="basic_table" width="100%" align="center" style="text-align:center" border="1">
            <tr style="background-color:3366CC">
                <td width="10%"><p">المجموع</p></td>
                <td width="8%"><p">نصيب الشركة</p></td>    
                <td width="8%"><p">إلتزام المؤمن</p></td>
                <td width="8%"><p">الخاضع للتأمين</p></td>
                <td width="8%"><p">الأساسي</p></td>
                <td width="8%"><p>ت. التعيين</p></td>
                <td width="7%"><p>رقم التأمين</p></td>
                <td width="30%"><p">الموظف</p></td>
                <td width="7%"><p">الكود</para></td>
                <td width="6%"><p">#</para> </td>
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
                <td><p>${ rec['name'] or ''  } </p> </td>
                <td><p>${ rec['code'] or ''  } </p> </td>
                <td><p>${ rec['no'] or ''  } </p></td>
            </tr>
            %endfor
        </blockTable>
	<table class="basic_table" width="100%" align="center" style="text-align:center" border="1">
           <tr style="background-color:3366CC">
                <td width="10%"><p">${total()['last_total'] or '0'}</p></td>
                <td width="8%"><p">${total()['comm_total'] or '0'}</p></td>    
                <td width="8%"><p">${total()['insu_total'] or '0'}</p></td>
                <td width="76%"><p">الإجمالي</para> </td>
            </tr>
        </blockTable>
         %endif

</body>
</html>

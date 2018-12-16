<html>
    <head>
        <style type="text/css">
            ${css}
        </style>
    </head>
    <body>
        <center><h1> </h1></center>
        <center><h1>${_("تقرير ")} ${ data['form']['soli_insu_id'][1]} ${_("لشهر ")} ${ data['form']['month']} ${_(" عام ")} ${ data['form']['year']}</h1></center>
        <br/><br/><br/>
	<table class="basic_table" width="100%" align="center" style="text-align:center" border="1">
            <tr style="background-color:3366CC">
                <td width="20%"><p">المجموع</p></td>
                <td width="15%"><p>نصيب الشركة</p></td>
                <td width="15%"><p>نصيب الفرد</p></td>
                <td width="7%"><p">العدد</p></td>
                <td width="38%"><p">الإدارة</para></td>
                <td width="5%"><p">#</para> </td>
            </tr>
            %if main(data['form']) :
            %for line in main(data['form']) :
            <tr>
                <td ><p">${ line['share'] or '0'}</p></td>
                <td ><p">${ line['c_share'] or '0'}</p></td>
                <td ><p">${ line['d_share'] or '0'}</p></td>
                <td ><p">${ line['count'] or '0'}</p></td>
                <td ><p">${ line['dep'] or ''}</p></td>
                <td ><p">${ line['no'] or ''}</p></td>
            </tr>
            %endfor
            %endif
        </table>
	<table class="basic_table" width="100%" align="center" style="text-align:center" border="1">
           <tr style="background-color:3366CC">
                <td width="20%"><p">${total()['c_total']+total()['d_total'] }</p></td>
                <td width="15%"><p">${total()['c_total'] or '0'}</p></td>    
                <td width="15%"><p">${total()['d_total'] or '0'}</p></td>
                <td width="7%"><p">${total()['counter'] or '0'}</p></td>
                <td width="43%"><p">الإجمالي</para> </td>
            </tr>
        </blockTable>

</body>
</html>

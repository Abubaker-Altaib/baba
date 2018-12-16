<html >
<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
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
        <center><h1>${_("تقرير إحصائي  حسب الدرجات والوظائف القياسية")} </h1></center>

     %for dept in department(data['form']) :
          <center><h1>${data['form']['company_id'][1]} </h1></center>
          <center><h1>${dept.name} </h1></center>
     %if process(dept.id):  
	<table class="list_main_table" width="100%" align="center"  border="1">
            %for line in process(dept.id) :
            <tr >   
                %for clm in line:
                 <td >
                      <p> ${clm} </p>
                 </td>
                %endfor
           </tr>
        %endfor
	</table>
   %endif
%endfor
</body>
</html>


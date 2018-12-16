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
<div id="header">
            <table id="heading">
                <tr><h1>nnnnnnnnnnnnnnnnn</h1>
                    <td id="head-home"><h1 id="a-home" >Earwig's Copyvio Detector</h1></td>
 
                </tr>
            </table>
        </div>
<body>

     <center><h1>${_("كشف المرتبات التفصيلي لشهر ")}  ${ data['form']['month']} ${_(" عام ")} ${ data['form']['year']}</h1></center>

     %if process(data['form']):  
	<table class="list_main_table" width="100%" align="center"  border="1">
            %for i , line in enumerate(process(data['form'])) :
            <tr >   <th>i </th>
                %for clm in line:
                 <td >
                      <p> ${clm} </p>
                 </td>
                %endfor
           </tr>
        %endfor
	</table>
   %endif
</body>
</html>


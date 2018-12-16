<html >

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
    <style type="text/css">
        ${css}
        td, th ,p{
            height:20px;
            padding-top: 0px;
            padding-bottom: 0px;
            line-height:7pt;
        }
        table, td, th {
            border: 1px solid black;
            
        }

        table {
            border-collapse: collapse;
            width: 100%;
            font-size: 10px;
            font-weight: bold;
            text-align: center;
        }
        
    
        
    </style>
</head>
<body>
    <center><h4>${ data['form']['month']} ${_("كشف الحوافز لشهر ")}</h4></center>
    <center><h4>${_("لسنة")}</h4></center>
    <center><h4>${ data['form']['year']}</h4></center>  
    <center><h4>${ data['form']['allow'][1]}</h4></center>
     %if payroll(data):  
	<table class="list_main_table" cellpadding="1">
            %for line in payroll(data) :
            <tr >   
                %for clm in line:
                 <td height="1">
                      <p> ${clm} </p>
                 </td>
                %endfor
           </tr>
        %endfor
	</table>
   %endif
</body>
</html>


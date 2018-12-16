<html >
<head>
    <style type="text/css">
        ${css}
.list_main_table {
    border:thin solid #000000;
    text-align:center;
    border-collapse: collapse;
}
table.list_main_table {
    
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

  width: 50px;
}

.list_main_table_custom {
    border-left:thin solid #FFFFFF;
    border-bottom:thin solid #FFFFFF;
    border-bottom-width:0px;
    border-left-width:0px;
    /*border-right-width:0px;
    border-top-width:0px;*/
    margin-right:0;
    padding:0;
    /*border-color:thin solid #FF0000;*/
    text-align:center;
    border-collapse: collapse;
}

.list_main_table_custom td {
  border-right:thin solid #000000;
  width: 50px;
}

.list_main_table_custom tr {

  border-right:thin solid #FFFFFF;
}

.list_main2_headers th {
    background-color: #3366CC;
    /*border: thin solid #110000;*/
    padding-right:3px;
    padding-left:3px;
    text-align:center;
    font-size:12;
    font-weight:bold;
}
h1 {
    font-size: 100%;
    margin: 0;
}
body {
    margin: 1cm;
    padding: 0;
    border: 1;
    text-align:center;
}
/*.list_main2_table td {
  border-color:thin solid #FF0000;
  border-collapse :collapse;
  width: 50px;
}
.list_main2_table tr {
  border-color:thin solid #FF0000;
}*/
    </style>
</head>
<body>
     <center><h1>${_("اﻷمانة العامة للمجلس القومي للتدريب ")}</h1></center>
     <center><h1>${_("حصر العاملين بالوحدات والهيئات و المؤسسات الحكومية - استمارة رقم 8 ")}</h1></center>
     <h6 align="right">${_("القطاع: الخدمي")}</h6>
     <h6 align="right">${_("الوحدة: الهيئة القومية للإتصالات")}</h6>
         
     %if line(data['form']):  
	<table class="list_main_table" width="100%" align="center"  border="1">
            %for x in line(data['form']) :
            <tr >   
                %for clm in x:
                 <td >
                    %if isinstance(clm, list):
                    %if clm[0] != '#':
                      <p> ${clm[0]} </p>
                      %endif
                       <table class="list_main_table_custom" width="100%" align="right"  border="1">
                         <tr >
                            %for x1 in clm[1]:
                            <td>
                               <p> ${x1} </p>
                            </td>
                            %endfor
                         </tr>
                       </table>
                    %endif
                    %if not isinstance(clm, list):
                      <p> ${clm} </p>
                    %endif
                 </td>
                %endfor
           </tr>
        %endfor
	</table>
   %endif
</body>
</html>

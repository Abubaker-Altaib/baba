<html lang="ar">
<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>


    <style type="text/css">

.list_main_table {

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
    <head>
        %if info(data)['company']:
            <center><h1 >  ${ info(data)['company'] }</h1></center> 
        %endif         
        <center><h1>${ info(data)['title']  }   </h1></center>
        <hr width="100%" bgcolor="#D1D1FF"/>      
   </head>
   <body dir="rtl">
        %if main(data):
	<table class="list_main_table" width="100%" align="center" >
            %for line in main(data):
              %if line['level']==4:
                 <tr style="text-align:center;padding-right:50px;background:#D1D1ff;" >  
              %else :  
                <tr style="text-align:center;padding-right:50px;" >  
              %endif :  
                    %for clm in sorted(line.keys()):
                        %if line[clm] != line['level']:
                    <td if line['level']==4 : >
                        %if line['level']==1:
                             <p style=" font-weight:bold;font-size:25;padding-right:20px;">  
                                 ${line[clm] and line[clm] or '/'} 
                             </p>
                        %elif line['level']==2 :
                             <p style=" font-weight:bold;font-size:20;padding-right:40px;">
                                   ${line[clm] and line[clm] or '/'} 
                            </p>
                        %elif line['level']==3:
                             <p style="text-align:right;padding-right:200px;" > 
                                 ${line[clm] and line[clm] or '/'}
                             </p>
                        %elif line['level']==4:
                             <p style="text-align:center;font-weight:bold;font-size:18;padding-right:200px;"> 
                                ${line[clm] and line[clm] or '/'} 
                             </p>
                        %endif
                    </td> 
                       %endif
                    %endfor
           </tr>
           %endfor
        </blockTable>
       %endif


</body>
</html>


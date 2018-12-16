<html lang="ar">
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>

    
    <head>
        %if info(data)['company']:
            <center><h1 >  ${ info(data)['company'] }</h1></center> 
        %endif         
        <center><h1>${ info(data)['title'] }</h1></center>
        <hr width="100%" bgcolor="#D1D1FF"/>

        <style type="text/css">
        table.list_main_table {
            margin-top: 20px;
        }
        .list_main_table td {
            padding-right:5px;
            padding-left:5px;
        }
    </style>
    </head>
    <body dir="rtl">
        <table class="list_main_table" width="100%" align="center" border='1'>
            %for line in main(data):
              %if line['level']==4:
                 <tr style="background:#D1D1ff;" >
              %else :
                <tr >
              %endif :
                    %for clm in sorted(line.keys()):
                        %if clm != 'level':
                            %if len(line)-1< info(data).get('col_no',1):
                                <td colspan="${info(data).get('col_no',1)-len(line)+3}" border="0">
                            %else :
                                <td>
                            %endif :
                        %if line['level']==1:
                             <p style="font-weight:bold;font-size:25">  
                                 ${line[clm] and line[clm] or '/'} 
                             </p>
                        %elif line['level']==2 :
                             <p style="font-weight:bold;font-size:20">
                                   ${line[clm] and line[clm] or '/'} 
                            </p>
                        %elif line['level']==3:
                             <p style="text-align:center; "> 
                                 ${line[clm] and line[clm] or '/'}
                             </p>
                        %elif line['level']==4:
                             <p style="font-weight:bold;font-size:18; text-align:center;"> 
                                ${line[clm] and line[clm] or '/'} 
                             </p>
                        %endif
                    </td> 
                       %endif
                    %endfor
           </tr>
           %endfor
        <table>
    </body>
</html>

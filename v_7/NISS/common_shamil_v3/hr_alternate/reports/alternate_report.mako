<html>

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
    <style type="text/css">
        $ {
            css
        }

        td,
        th,
        p {
            height: 15px;
            padding-top: 0px;
            padding-bottom: 0px;
            line-height: 7pt;
        }

        table,
        td,
        th {
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
    <center>
        <h4>${_("المناوبة")}</h4>
    </center>
    %if lines(data): 
        %for line in lines(data) :
        <div align="right">
            <p> ${line.alternative_setting_id.name}: التصنيف</p>
            <p> ${line.date_from}: من</p>
            <p> ${line.date_to}: إلى</p>
        </div>

            <table class="list_main_table" cellpadding="1">

                    <tr>
                        <td height="1">
                            <p> ${_("اليوم")} </p>
                        </td>
                        <td height="1">
                            <p> ${_("التاريخ")} </p>
                        </td>
                        <td height="1">
                            <p> ${_("الرتبة")}  </p>
                        </td>
                        <td height="1">
                            <p> ${_("اﻹسم")}  </p>
                        </td>

                        <td height="1">
                            <p> ${_("الرقم العسكري")}  </p>
                        </td>
                    
                    
                    </tr>

                %for clm in line.lines_ids:
                <tr>
                    <td height="1">
                        <p> ${get_weekday(clm.weekday)} </p>
                    </td>
                
                    <td height="1">
                        <p> ${clm.date} </p>
                    </td>
                    <td height="1">
                        <p> ${clm.degree.name or ''} </p>
                    </td>
                    <td height="1">
                        <p> ${clm.employee_id.name  or ''} </p>
                    </td>

                    <td height="1">
                            <p> ${clm.employee_id.emp_code  or ''} </p>
                        </td>
                
                
                </tr>
                %endfor
            </table>

            <div align="right">
                    <p> ${line.alternative1.name  or ''}: البديل الأول</p>
                    <p> ${line.alternative2.name  or ''}: البديل الثاني</p>
            </div>
            <hr/>
        %endfor 
    %endif
</body>

</html>
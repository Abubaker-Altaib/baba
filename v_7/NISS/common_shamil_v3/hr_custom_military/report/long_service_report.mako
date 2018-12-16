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
            height: 20px;
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

        table td.crossed {
            background-image: linear-gradient(to bottom right, transparent calc(50% - 1px), red, transparent calc(50% + 1px));
        }
    </style>
</head>

<body>
    <center>
        <h1>${ _("تقرير الخدمة الطويلة الممتازة ") }</h1>
    </center>
    %if all_len(data):
    <center>
        ${ _(" من : ") }${ data['form']['start_date'] or _("غير محدد ")}
    </br>
        ${ _(" إلى : ") }${ data['form']['end_date'] or _("غير محدد ")}
    </br>
    %if data['form']['candidate'] == False:
        ${ _("الإجمالي الكلي : ") }${ all_len(data)}
    </center>

    <table>
        <tr>
            <td>
                ${_("المنحة التالية ")}
            </td>
            <td>
                ${_("تاريخ المنحة ")}
            </td>
            <td>
                ${_("تاريخ التعيين")}
            </td>
            <td>
                ${_("نوع المنحة")}
            </td>
            <td>
                ${_("الهيكل")}
            </td>
            <td>
                ${_("الإسم")}
            </td>
            <td>
                ${_("الرتبة")}
            </td>
            <td>
                ${_("ر.البطاقة")}
            </td>
            <td>
                ${_("م")}
            </td>

        </tr>

        %for line in lines() :
        <tr>
            <td>
                ${line['next_allow_date'] or ''}
            </td>

            <td>
                ${line['date']}
            </td>
            <td>
                ${line['employment_date']}
            </td>

            <td>
                ${line['gift_name'] or ''}
            </td>
            <td>
                ${line['dep_name']}
            </td>
            <td>
                ${line['name_related']}
            </td>
            <td>
                ${line['deg_name']}
            </td>
            <td>
                ${line['otherid']}
            </td>
            <td>
                ${get_count()}
            </td>

        </tr>
        %endfor
    </table>


    %endif

    %if data['form']['candidate'] == True:
        ${ _("المرشحين للمنحة : ") }${ data['form']['gift_id'][1]}
        </br>
        ${ _("الإجمالي الكلي : ") }${ all_len(data)}
    </center>

    <table>
        <tr>
            <td>
                ${_("تاريخ التعيين ")}
            </td>
            <td>
                ${_("الهيكل")}
            </td>
            <td>
                ${_("الإسم")}
            </td>
            <td>
                ${_("الرتبة")}
            </td>
            <td>
                ${_("ر.البطاقة")}
            </td>
            <td>
                ${_("م")}
            </td>

        </tr>

        %for line in lines() :
        <tr>

            <td>
                ${line['employment_date']}
            </td>
            <td>
                ${line['dep_name']}
            </td>
            <td>
                ${line['name_related']}
            </td>
            <td>
                ${line['deg_name']}
            </td>
            <td>
                ${line['otherid']}
            </td>
            <td>
                ${get_count()}
            </td>

        </tr>
        %endfor
    </table>


    %endif
    %endif
</body>

</html>

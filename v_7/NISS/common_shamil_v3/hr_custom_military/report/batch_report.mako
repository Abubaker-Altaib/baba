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
        <h1>${ _("تقرير الدفعة ") }</h1>
    </center>
    %if all_len(data):
    <center>
        ${ _("الإجمالي الكلي : ") }${ all_len(data)}
    </center>
    <table>
        <tr>
            <td>
                ${_("الدفعة")}
            </td>
            <td>
                ${_("دفعة التنسيب")}
            </td>
            <td>
                ${_("مجموعة الدفعة")}
            </td>
            <td>
                ${_("الهيكل")}
            </td>
            <td>
                ${_("الوظيفة")}
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
                ${line['batch_name'] or "-"}
            </td>
            <td>
                ${line['placement_batch_name'] or "-"}
            </td>
            <td>
                ${line['parent_batch_name'] or "-"}
            </td>
            <td>
                ${get_name(line['department_id'])}
            </td>
            <td>
                ${line['job_name'] or "-"}
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
</body>

</html>
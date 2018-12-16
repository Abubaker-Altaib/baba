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
        <h1>${ _("تقرير بوضع الخدمة  ") }</h1>
        <h1>${ data['form']['service_state_id'] and data['form']['service_state_id'][1] or "" }</h1>
    </center>
    %if all_len(data):
    <center>
    ${ _("الإجمالي الكلي : ") }${ all_len(data)}
    </center>
        % if data['form']['type'] == 'specific':
            <table>
                <tr>
                    <td>
                        ${_("مدة الخدمة حتى اليوم")}
                    </td>
                    <td>
                        ${_("تاريخ العمل باﻹدارة")}
                    </td>
                    <td>
                        ${_("وضع الخدمة")}
                    </td>
                    <td>
                        ${_("الفرع")}
                    </td>
                    <td>
                        ${_("الوظيفة")}
                    </td>
                    <td>
                        ${_("الدفعة")}
                    </td>
                    <td>
                        ${_("تاريخ التعيين")}
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
                        ${line.total_service_years} ${_("سنة")} <br/> ${line.total_service_months} ${_("شهر")} <br/> ${line.total_service_days} ${_("يوم")}
                    </td>
                    <td>
                        ${line.join_date or ''}
                    </td>
                    <td>
                        ${line.service_state_id.name}
                    </td>
                    <td>
                        ${line.department_id.name_get_custom()[0][1]}
                    </td>
                    <td>
                        ${line.job_id.name or ''}
                    </td>
                    <td>
                        ${line.batch.name or ''}
                    </td>
                    <td>
                        ${line.employment_date}
                    </td>
                    <td>
                        ${line.name_related}
                    </td>
                    <td>
                        ${line.degree_id.name}
                    </td>
                    <td>
                        ${line.otherid}
                    </td>
                    <td>
                        ${get_count()}
                    </td>
                </tr>
                %endfor
            </table>
        %endif
        % if data['form']['type'] == 'takeout':
            <table>
                <tr>
                    <td>
                        ${_("تاريخ الشطب")}
                    </td>
                    <td>
                        ${_("اخر فرع عمل به")}
                    </td>
                    <td>
                        ${_("الوظيفة")}
                    </td>
                    <td>
                        ${_("الدفعة")}
                    </td>
                    <td>
                        ${_("وضع الخدمة")}
                    </td>
                    <td>
                        ${_("تاريخ التعيين")}
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
                        ${line.end_date  or ''}
                    </td>
                    <td>
                        ${line.department_id.name_get_custom()[0][1]}
                    </td>
                    <td>
                        ${line.job_id.name or ''}
                    </td>
                    <td>
                        ${line.batch.name or ''}
                    </td>
                    <td>
                        ${line.service_state_id.name}
                    </td>
                    <td>
                        ${line.employment_date}
                    </td>
                    <td>
                        ${line.name_related}
                    </td>
                    <td>
                        ${line.degree_id.name}
                    </td>
                    <td>
                        ${line.otherid}
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
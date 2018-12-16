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
        <h1>${ _("تقرير التدريب ") }</h1>
    </center>
    %if all_len(data):
        <!-- <center>
            ${ _("الإجمالي الكلي : ") }${ all_len(data)}
        </center> -->
        %if 'form' not in data:
        <table>
            <tr>
                <td>
                    ${_("التقدير")}
                </td>
                <td>
                    ${_("تاريخ النهاية")}
                </td>
                <td>
                    ${_("تاريخ البداية")}
                </td>
                <td>
                    ${_("نوع المشاركة")}
                </td>
                <td>
                    ${_("نوع الدورة")}
                </td>
                <td>
                    ${_("المكان")}
                </td>
                <td>
                    ${_("إسم الكورس")}
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
                    ${to_arabic(line['training_eval'])}
                </td>
                <td>
                    ${line['end_date']}
                </td>
                <td>
                    ${line['start_date']}
                </td>
                <td>
                    ${to_arabic(line['participation_type'])}
                </td>
                <td>
                    ${to_arabic(line['course_type'])}
                </td>
                <td>
                    ${line['place_name']}
                </td>
                <td>
                    ${line['type_name']}
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

        %if 'form' in data:
            %if data['form']['who_not_take'] == False:
            <table>
                <tr>
                    <td>
                        ${_("التقدير")}
                    </td>
                    <td>
                        ${_("تاريخ النهاية")}
                    </td>
                    <td>
                        ${_("تاريخ البداية")}
                    </td>
                    <td>
                        ${_("نوع المشاركة")}
                    </td>
                    <td>
                        ${_("نوع الدورة")}
                    </td>
                    <td>
                        ${_("المكان")}
                    </td>
                    <td>
                        ${_("إسم الكورس")}
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
                        ${to_arabic(line['training_eval'])}
                    </td>
                    <td>
                        ${line['end_date']}
                    </td>
                    <td>
                        ${line['start_date']}
                    </td>
                    <td>
                        ${to_arabic(line['participation_type'])}
                    </td>
                    <td>
                        ${to_arabic(line['course_type'])}
                    </td>
                    <td>
                        ${line['place_name']}
                    </td>
                    <td>
                        ${line['type_name']}
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


            %if data['form']['who_not_take'] == True:
            <table>
                <tr>
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
                        ${line['job_name']}
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

    %endif
</body>

</html>
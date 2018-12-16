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
            font-size: 12px;
            font-weight: bold;
            text-align: center;
        }

        table td.crossed {
            background-image: linear-gradient(to bottom right, transparent calc(50% - 1px), red, transparent calc(50% + 1px));
        }
    </style>
</head>

<body>
    <table style="border:0px;width: 100%;font-size: 14px;padding-top: 0px;padding-bottom: 0px;text-align: center;height: 7px;max-height: 7px;">
        <tr>
            <th width="30%" style="border:0px;">
                <p></p>
            </th>
            <th width="30%" style="border:0px;">
                <p></p>
                <p>بسم الله الرحمن الرحيم</p>
                <p>سري للغاية</p>
            </th>
            <th width="30%" style="border:0px;">
                <p></p>
            </th>


        </tr>
    </table>

    <table style="border:0px;width: 100%;font-size: 14px;padding-top: 0px;padding-bottom: 0px;text-align: center;height: 7px;max-height: 7px;">
        <tr>
            
            <th width="30%" style="border:0px;">
                <p>جهاز اﻷمن و المخابرات الوطني</p>
                <p>هيئة اﻹدارة</p>
                <p>دائرة الخدمات الهندسية</p>
                <p>إدراة المركبات و الوقود</p>
                <p>فرع الوقود</p>
                <p>التاريخ:${time.strftime("%Y-%m-%d")}</p>
            </th>
            <th width="30%" style="border:0px;">
            </th>
            <th width="30%" style="border:0px;">
                
            </th>


        </tr>
    </table>

    %if [x for x in lines(data) if x['fuel_exchange_status'] == 'exchange' ]:
        <center>
            <h4>${ _("تقرير حالة الصرف ") }</h4>
            <h4>${ _("يصرف حالياً ") }</h4>
        </center>


        <table>
            <tr>
                <td>
                    ${_("اﻹدارة")}
                </td>
                <td>
                    ${_("نوع الوقود")}
                </td>
                <td>
                    ${_("الحصة")}
                </td>
                <td>
                    ${_("الموديل")}
                </td>
                <td>
                    ${_("رقم اللوحة")}
                </td>
                <td>
                    ${_("اﻹستخدام")}
                </td>
                <td>
                    ${_("اﻹسم")}
                </td>
                <td>
                    ${_("الرتبة")}
                </td>
                <td>
                    ${_("النمرة")}
                </td>
                <td>
                    ${_("م")}
                </td>

            </tr>

            %for line in [x for x in lines(data) if x['fuel_exchange_status'] == 'exchange' ] :
            <tr>
                <td>
                    ${get_name(line['department_id'])}
                </td>
                <td>
                    ${line['fuel_type'] == 'gasoline' and u'جازولين' or u'بنزين'}
                </td>
                <td>
                    ${line['fuel_amount'] and '{0:,.2f}'.format(abs(line['fuel_amount']) or 0.0) or "/"}
                </td>
                <td>
                    ${line['model_name']}
                </td>
                <td>
                    ${line['license_plate']}
                </td>
                <td>
                    ${line['use_name']}
                </td>
                <td>
                    ${line['emp_name'] or '/'}
                </td>
                <td>
                    ${line['degree_name'] or '/'}
                </td>
                <td>
                    ${line['otherid'] or '/'}
                </td>
                <td>
                    ${get_count()}
                </td>

            </tr>
            %endfor
        </table>
    %endif


    
    %if [x for x in lines(data) if x['fuel_exchange_status'] == 'stop' ]:
    
    %if [x for x in lines(data) if x['fuel_exchange_status'] == 'exchange' ]:
    <p style="page-break-after: always;">&nbsp;</p>
    %endif

        <center>
            <h4>${ _("تقرير حالة الصرف  ") + set_count() }</h4>
            <h4>${ _(" موقوف ") }</h4>
        </center>


        <table>
            <tr>
                <td>
                    ${_("سبب اﻹيقاف")}
                </td>
                <td>
                    ${_("اﻹدارة")}
                </td>
                <td>
                    ${_("نوع الوقود")}
                </td>
                <td>
                    ${_("الحصة")}
                </td>
                <td>
                    ${_("الموديل")}
                </td>
                <td>
                    ${_("رقم اللوحة")}
                </td>
                <td>
                    ${_("اﻹستخدام")}
                </td>
                <td>
                    ${_("اﻹسم")}
                </td>
                <td>
                    ${_("الرتبة")}
                </td>
                <td>
                    ${_("النمرة")}
                </td>
                <td>
                    ${_("م")}
                </td>

            </tr>

            %for line in [x for x in lines(data) if x['fuel_exchange_status'] == 'stop' ] :
            <tr>
                <td>
                    ${line['reason_name']}
                </td>
                <td>
                    ${get_name(line['department_id'])}
                </td>
                <td>
                    ${line['fuel_type'] == 'gasoline' and u'جازولين' or u'بنزين'}
                </td>
                <td>
                    ${line['fuel_amount'] and '{0:,.2f}'.format(abs(line['fuel_amount']) or 0.0) or "/"}
                </td>
                <td>
                    ${line['model_name']}
                </td>
                <td>
                    ${line['license_plate']}
                </td>
                <td>
                    ${line['use_name']}
                </td>
                <td>
                    ${line['emp_name'] or '/'}
                </td>
                <td>
                    ${line['degree_name'] or '/'}
                </td>
                <td>
                    ${line['otherid'] or '/'}
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
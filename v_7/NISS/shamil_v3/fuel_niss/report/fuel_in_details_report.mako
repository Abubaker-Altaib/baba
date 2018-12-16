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
    <center>
        <h4>${ _("تفاصيل الوارد ") }</h4>
        <h4>${ data['date_from']  +_(" للفترة من  ") +data['date_to'] + _("  إلى  ") }</h4>
    </center>
    %for loc in lines(data).values() :

    <h5 style="text-align: right;">${ loc['name']+ set_count() }</h5>

    <table>
        <tr>
            <td>
                ${_("ملاحظات")}
            </td>
            <td>
                ${_("التكلفة بالجنيه")}
            </td>
            <td>
                ${_("سعر الوحدة")}
            </td>
            <td>
                ${_("الفرق")}
            </td>
            <td>
                ${_("تفاصيل المستلم")}
            </td>
            <td>
                ${_("إجمالي المستلم باللتر")}
            </td>
            <td>
                ${_("الكمية المطلوبة باللتر")}
            </td>
            <td>
                ${_("المحطة المستلمة")}
            </td>
            <td>
                ${_("نوع الوقود")}
            </td>
            <td>
                ${_("نوع الطلب")}
            </td>
            <td>
                ${_("رقم الطلب")}
            </td>
            <td>
                ${_("م")}
            </td>

        </tr>

        %for line in loc['lines'] :
        <tr>
            <td>
                ${line['reason'] or "-"}
            </td>
            <td>
                ${'{0:,.2f}'.format(line['sum_price'] or 0.0)}
            </td>
            <td>
                ${'{0:,.2f}'.format(line['standard_price'] or 0.0)}
            </td>
            <td>
                ${'{0:,.2f}'.format(abs(line['div_qty']) or 0.0)}
            </td>
            <td>
                <table>
                    <tr>
                        <td>
                            ${_("المستلم")}
                        </td>
                        <td>
                            ${_("البئر")}
                        </td>
                    </tr>
                    %for well in line['wells'] :
                    <tr>
                        <td>
                            ${'{0:,.2f}'.format(well['recieved_amount'] or 0.0)}
                        </td>
                        <td>
                            ${well['name'] or "-"}
                        </td>
                    </tr>
                    %endfor

                </table>
            </td>
            <td>
                ${'{0:,.2f}'.format(line['recieved_qty'] or 0.0)}
            </td>
            <td>
                ${'{0:,.2f}'.format(line['requested_qty'] or 0.0)}
            </td>
            <td>
                ${line['recieve_location']}
            </td>
            <td>
                ${line['fuel_type'] == 'gasoline' and u'جازولين' or u'بنزين'}
            </td>
            <td>
                ${line['stock_in_type'] == 'claim' and u'مطالبة' or u'مصادر'}
            </td>
            <td>
                ${line['name']}
            </td>
            <td>
                ${get_count()}
            </td>

        </tr>
        %endfor
    </table>
    %endfor
</body>

</html>
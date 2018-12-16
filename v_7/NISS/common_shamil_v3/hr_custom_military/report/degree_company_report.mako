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
            font-size: 15px;
            /*font-weight: bold;*/
            text-align: center;
            /*height: 2px;
            max-height: 2px;*/
        }

        .selection {
            border-collapse: collapse;
            width: 100%;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            height: 7px;
            max-height: 7px;
            outline:  1px solid black;

        }

        .selection td p{
                
                text-align: center;
                height: 7px;
                max-height: 7px;
                padding-bottom: 0px;
                padding-top: 0px;
                /*white-space: nowrap;*/
                font-size: 18px;
                line-height: 8pt;
            }

        .selection td {
                
                text-align: center;
                height: 7px;
                max-height: 7px;
                padding-bottom: 0px;
                padding-top: 0px;
                /*white-space: nowrap;*/
                font-size: 18px;
                line-height: 8pt;
                border: 1px solid black;
                background: #e6e6e6;

            }


        table td.crossed {
            background-image: linear-gradient(to bottom right, transparent calc(50% - 1px), red, transparent calc(50% + 1px));
        }
    </style>
</head>

<body>
    <center>
    <h1>${ _("تقرير بالرتبة و الهيكل") }</h1>
    </center>
    <!-- <table border="1" class="selection"  style="">
        <tr>
            <td>
                <p>${_("الوظيفة")}</p>
            </td>
            <td>
                <p>${_("الادارة")}</p>
            </td>
        </tr>
         %for select in select_data(data) :
            <tr>
                <td>
                    <p>${select['job']}</p>
                </td>
                <td>
                    <p>${select['dept']}</p>
                </td>
            </tr>
         %endfor
    </table> -->
    <br/>
    %if all_len(data):
    <center>
        ${ _("الإجمالي الكلي : ") }${ all_len(data)}
    </center>
    <table>
        <tr style="font-weight: bold">
            <td>
                <p style="font-weight: bold">${_("الوظيفة")}</p>
            </td>
            <td>
                <p style="font-weight: bold">${_("تاريخ دخول الرتبة")}</p>
            </td>
            <td>
                <p style="font-weight: bold">${_("الهيكل")}</p>
            </td>
            <td>
                <p style="font-weight: bold">${_("الإسم")}</p>
            </td>
            <td>
                <p style="font-weight: bold">${_("الرتبة")}</p>
            </td>
            <td>
                <p style="font-weight: bold">${_("ر.البطاقة")}</p>
            </td>
            <td>
                <p style="font-weight: bold">${_("م")}</p>
            </td>

        </tr>

        %for line in lines() :
        <tr>
            <td>
                <p>${line.job_id.name or ''}</p>
            </td>
            <td>
                <p>${line.promotion_date and line.promotion_date or ""}</p>
            </td>
            <td>
                <p>${line.department_id.name_get_custom()[0][1]}</p>
            </td>
            <td>
                <p>${line.name_related}</p>
            </td>
            <td>
                <p>${line.degree_id.name}</p>
            </td>
            <td>
                <p>${line.otherid}</p>
            </td>
            <td>
                <p>${get_count()}</p>
            </td>
        </tr>
        %endfor
    </table>
    %endif
</body>

</html>
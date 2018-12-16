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
        <h1>${ _("تقرير الحالة ") }</h1>
        <h1>${ data['form']['name'] }</h1>
    </center>

    %if all_len(data):
        <table>
            <tr>
                <td>
                    ${_("تم")}
                </td>
                <td>
                    ${_("كل اﻹجراءات")}
                </td>
                <td>
                    ${_("العملية")}
                </td>
                <td>
                    ${_("م")}
                </td>

            </tr>

            %for line in lines() :
            <tr>
                
                <td>
                    ${line['done_res']}
                </td>
                <td>
                    ${line['all_res']}
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
        %endif

</body>

</html>
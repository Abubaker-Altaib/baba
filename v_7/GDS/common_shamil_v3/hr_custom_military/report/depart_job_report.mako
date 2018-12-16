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
        <h1>${_("راجعة لقوة الدعم السريع بالمهنة و الهيئة ")}</h1>
    </center>
    %if lines(data): 
        %if get_count_all():
        <table>
            <tr>
                <td class="crossed">
                    ${sum_name}
                </td>

                %for job in jobs() :
                <td height="1">
                    <p> ${job['name']} </p>
                </td>
                %endfor

                <td colspan='2'>
                    ${ unicode('الهيئة', 'utf-8')  +'/'+ unicode('المهنة', 'utf-8')}
                </td>

            </tr>



            %for department in departments() :
            <tr>
                <td class="crossed">
                    ${get_count_department(department['id'])}
                </td>
                %for job in jobs() :
                <td>
                    ${get_count_department_job(department['id'], job['id'])}
                </td>
                %endfor
                <td height="1">
                    <p> ${department['name']} </p>
                </td>
                <td height="1">
                    <p> ${counter()} </p>
                </td>

            </tr>
            %endfor
            <tr>
                <td class="crossed">
                    ${get_count_all()}
                </td>
                %for job in jobs() :
                <td>
                    ${get_count_job(job['id'])}
                </td>
                %endfor
                <td colspan='2'>
                    ${sum_name}
                </td>
            </tr>
        </table>
        %endif
    %endif
</body>

</html>

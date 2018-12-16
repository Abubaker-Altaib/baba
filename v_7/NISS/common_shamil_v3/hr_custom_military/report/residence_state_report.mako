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
        %if data['form']['type'] == 'state':
            <h1>${_("نموزج راجعة توضح السكن حسب الولايات")}</h1>
        %endif

        %if data['form']['type'] == 'state_local':
            <h1>${_("نموزج راجعة توضح السكن حسب الولاية والمحلية")}</h1>
        %endif
    </center>
    %if lines(data): 
        %if get_count_all():
            %if data['form']['type'] == 'state':
            <table>
              
                <tr style="background-color:#ebebe0;">
                    <td>
                        ${sum_name}
                    </td>

                    %for degree in degrees() :
                    <td height="1">
                        <p> ${degree['name']} </p>
                    </td>
                    %endfor
               
                    <td>
                        ${unicode('الولاية', 'utf-8')+'/'+unicode('الرتب', 'utf-8')}
                    </td>
                    <td>
                        ${unicode('م', 'utf-8')}
                    </td>
                </tr>


                %for state in states() :
                <tr>
                    <td style="background-color:#ebebe0;">
                        ${get_count_state(state['id'])}
                    </td>
                    %for degree in degrees() :
                    <td>
                        ${get_count_state_degree( state['id'],degree['id'])}
                    </td>
                    %endfor
                    <td height="1" style="background-color:#ebebe0;">
                        <p> ${state['name']} </p>
                    </td>
                    <td height="1" style="background-color:#ebebe0;">
                        <p> ${counter()} </p>
                    </td>

                </tr>
                %endfor
                <tr style="background-color:#ebebe0;">
                    <td>
                        ${get_count_all()}
                    </td>
                    %for degree in degrees() :
                    <td>
                        ${get_count_degree(degree['id'])}
                    </td>
                    %endfor
                    <td colspan='2'>
                        ${sum_name}
                    </td>
                </tr>
            </table>
            %endif

        %if data['form']['type'] == 'state_local':
        <table>
          
            <tr style="background-color:#ebebe0;">
                <td>
                    ${sum_name}
                </td>

                %for degree in degrees() :
                <td height="1">
                    <p> ${degree['name']} </p>
                </td>
                %endfor
           
                <td>
                    ${unicode('المحلية', 'utf-8')+'/'+unicode('الرتب', 'utf-8')}
                </td>
                <td>
                    ${unicode('الولاية', 'utf-8')}
                </td>
                
            </tr>

            %for state in states():
                %for local in locals(data,state):
                <tr>
                    <td style="background-color:#ebebe0;">
                        ${get_count_local_state(local['id'],state['id'])}
                    </td>
                    %for degree in degrees() :
                    <td>
                        ${get_count_local_state_degree(local['id'],state['id'],degree['id'])}
                    </td>
                    %endfor
                    <td height="1" style="background-color:#ebebe0;">
                        <p> ${local['name']} </p>
                    </td>
                    <td height="1" style="background-color:#ebebe0;">
                        <p> ${state['name']} </p>
                    </td>

                </tr>
                %endfor
                %endfor
                <tr style="background-color:#ebebe0;">
                    <td>
                        ${get_count_all()}
                    </td>
                    %for degree in degrees() :
                    <td>
                        ${get_count_degree(degree['id'])}
                    </td>
                    %endfor
                    <td colspan='2'>
                        ${sum_name}
                    </td>
                </tr>
        </table>
        %endif

    %endif
%endif
</body>

</html>
<html dir="rtl">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
    <style type="text/css">
        ${css}
        td, th ,p{
            height:15px;
            padding-top: 0px;
            padding-bottom: 0px;
            line-height:7pt;
        }
        table, td, th {
            border: 1px solid black;
            
        }

        th{
            padding: 1px;
            padding-bottom: 2px;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            font-size: 10px;
            font-weight: bold;
            text-align: center;
        }
    
        
    </style>
</head>
<body>
     <center><h1>${_("كشف المرتبات التفصيلي لشهر ")}  ${ data['form']['month']} ${_(" عام ")} ${ data['form']['year']}</h1></center>
     <center><h4>${ data['form']['pay_sheet_name']}</h4></center>  
     <center><h4>${ data['form']['type_name']}</h4></center>    
    %for res in process(data['form']) :  
    	<table class="list_main_table" cellpadding="1">
            <tr><!-- step 1 : print header -->
                <th>#</th>
                <th class="emp_name">الاسم</th>
                %if res['include_bascic_salary']: 
                        <td>الفئة الابتدائية</td>
                %endif 
                %for title in res['headrs'] :
                    <th>${title}</th>
                %endfor
                %if res['include_allow_total']: 
                    <td>اجمالي الاستحقاقات</td>
                %endif
                %if res['include_deduct_total']: 
                    <td>اجمالي الخصومات</td>
                %endif 
                %if res['include_net_total']: 
                    <td>الصافي</td>
                %endif 
            </tr>
            <!-- step 2 : print employee data -->
            %for i , emp_row in enumerate(res['emp_data']) :
                
                <tr>
                    <td>${i+1}</td>  
                    <td class="emp_name" style="min-width:120px;width:120px;">
                    <p> ${emp_row['emp_name']} </p>
                    </td>
                    %if res['include_bascic_salary']: 
                        <td>${emp_row['basic_salary']}</td>
                    %endif 
                    %for amount in emp_row['amounts']:
                        <td>${amount}</td>
                    %endfor
                    %if res['include_allow_total']: 
                        <td>${emp_row['emp_total_allow']}</td>
                    %endif
                    %if res['include_deduct_total']: 
                        <td>${emp_row['emp_total_deduct']}</td>
                    %endif 
                    %if res['include_net_total']: 
                        <td>${emp_row['emp_net']}</td>
                    %endif 

               </tr><!-- step 3 : print header again if need -->
                %if (i+1) % res['BREAK_POINT'] == 0 and i >0 and i != res['len_emp_data'] - 1 :
                   
                    </table>
                     <p style="page-break-after: always;">&nbsp;</p>
                    <table>
                    <tr>
                        <th>-</th>
                        <td>الاجمالي المرحل</td>
                        %if res['include_bascic_salary']: 
                            <td>${res['transfer_total_basics'](i)}</td>
                        %endif 
                        %for amount in res['page_trans_totals'](i):
                            <td>${amount}</td>
                        %endfor
                        %if res['include_allow_total']: 
                        <td>${res['transfer_total']('allow',i)}</td>
                        %endif
                        %if res['include_deduct_total']: 
                                <td>${res['transfer_total']('deduct',i)}</td>
                        %endif 
                        %if res['include_net_total']: 
                                <td>${res['transfer_total']('net',i)}</td>
                        %endif 
                    </tr>
                     <tr>
                        <th>#</th>
                        <th>الاسم</th>
                        %if res['include_bascic_salary']: 
                            <td>الفئة الابتدائية</td>
                        %endif 
                        %for title in res['headrs'] :
                            <th>${title}</th>
                        %endfor
                        %if res['include_allow_total']: 
                            <td>اجمالي الاستحقاقات</td>
                        %endif
                        %if res['include_deduct_total']: 
                            <td>اجمالي الخصومات</td>
                        %endif 
                        %if res['include_net_total']: 
                            <td>الصافي</td>
                %endif 
                    </tr>
                %endif
            %endfor

            <tr><!-- step 4 : print final totals -->
                <th>-</th>
                <th>الاجمالي</th>
                %if res['include_bascic_salary']: 
                            <td>${res['total_basics']}</td>
                        %endif 
                %for value in res['allow_deduct_totals'] :
                    <td>
                    ${value}
                    </td>
                %endfor
                %if res['include_allow_total']: 
                        <td>${res['total_allows']}</td>
                %endif
                %if res['include_deduct_total']: 
                        <td>${res['total_deducts']}</td>
                %endif 
                %if res['include_net_total']: 
                        <td>${res['total_nets']}</td>
                %endif 
            </tr>
    	</table>
   %endfor
</body>
</html>


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

        .allow-total,  .deduct-total, .net-total{
            background-color: #f2f2f2;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            font-size: 10px;
            font-weight: bold;
            text-align: center;
        }
    
        .sign-bolck{
            float: left;
            margin-left: 50px;
            margin-top: 80px;
            text-align: left;
            font-size: 24px;
        }
        
    </style>
</head>
<body>   
    %for res in process(data['form']) : 
        <center><h1>${_("كشف المرتبات التفصيلي لشهر ")}  ${ data['form']['month']} ${_(" عام ")} ${ data['form']['year']}</h1></center>
     <center><h4>${ data['form']['pay_sheet_name']}</h4></center>  
     <center><h4>${ data['form']['type_name']}</h4></center> 
     <center><h4>${ data['form']['company_name']}</h4></center>  
        <center><h2>${res['department_title']}</h2></center> 
    	<table class="list_main_table" cellpadding="1">
            <tr><!-- step 1 : print header -->
                <th>#</th>
                <th class="emp_name">الاسم</th>
                %if res['include_bascic_salary']: 
                        <td>الفئة الابتدائية</td>
                %endif 
                %for i , title in enumerate(res['headrs']) :
                    <!-- check for add allowance total colunm -->
                    %if res['include_allow_total']  and i == res['allow_column_index'] :
                        <td class="allow-total">اجمالي الاستحقاقات</td>
                    %endif
                    <th>${title}</th>
                    
                %endfor
                %if res['include_deduct_total']: 
                    <td class="deduct-total">اجمالي الخصومات</td>
                %endif 
                %if res['include_net_total']: 
                    <td class="net-total">الصافي</td>
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
                    %for c , amount in enumerate(emp_row['amounts']):
                        <!-- check for adding allowance total colunm -->
                        %if res['include_allow_total']  and c == res['allow_column_index'] :
                            <td class="allow-total">${emp_row['emp_total_allow']}</td>
                        %endif
                        <td>${round(amount , 2)}</td>
                        
                    %endfor
                    %if res['include_deduct_total']: 
                        <td class="deduct-total">${emp_row['emp_total_deduct']}</td>
                    %endif 
                    %if res['include_net_total']: 
                        <td class="net-total">${emp_row['emp_net']}</td>
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
                        %for c , amount in enumerate(res['page_trans_totals'](i)):
                            <!-- check for add allowance total colunm -->
                            %if res['include_allow_total']  and c == res['allow_column_index'] :
                                <td class="allow-total">${res['transfer_total']('allow',i)}</td>
                            %endif
                            <td>${round(amount , 2)}</td>
                            
                        %endfor
                        %if res['include_deduct_total']: 
                                <td class="deduct-total">${res['transfer_total']('deduct',i)}</td>
                        %endif 
                        %if res['include_net_total']: 
                                <td class="net-total">${res['transfer_total']('net',i)}</td>
                        %endif 
                    </tr>
                     <tr>
                        <th>#</th>
                        <th>الاسم</th>
                        %if res['include_bascic_salary']: 
                            <td>الفئة الابتدائية</td>
                        %endif 
                        %for c , title in enumerate(res['headrs']) :
                            %if res['include_allow_total']  and c == res['allow_column_index'] :
                                <td class="allow-total">اجمالي الاستحقاقات</td>
                            %endif
                            <th>${title}</th>
                            
                        %endfor
                        %if res['include_deduct_total']: 
                            <td class="deduct-total">اجمالي الخصومات</td>
                        %endif 
                        %if res['include_net_total']: 
                            <td class="net-total">الصافي</td>
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
                %for c , value in enumerate(res['allow_deduct_totals']) :
                    %if res['include_allow_total']  and c == res['allow_column_index'] :
                        <td class="allow-total">${res['total_allows']}</td>
                    %endif
                    <td>
                    ${round(value , 2)}
                    
                    </td>
                %endfor
                %if res['include_deduct_total']: 
                        <td class="deduct-total">${res['total_deducts']}</td>
                %endif 
                %if res['include_net_total']: 
                        <td class="net-total">${res['total_nets']}</td>
                %endif 
            </tr>
    	</table>
   %endfor

   <div class="sign-bolck">
       <p>
        المدير المالي
       </p>
   </div>
</body>
</html>


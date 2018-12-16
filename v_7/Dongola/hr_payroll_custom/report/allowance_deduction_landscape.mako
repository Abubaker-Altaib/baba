<html dir="rtl">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
    <style type="text/css">
        ${css}
        td, th ,p{
            padding-top: 0px;
            padding-bottom: 0px;
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
            font-size: 8px;
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

        .sign-space{
            width: 90px;
        }

        .sign-tb , .sign-tb td{
            border: none;
            margin-top: 25px;
        }
        
    </style>
</head>
<body>   
        <center>
            <p>جمهورية السودان</p>
        </center>

            <p>
                 
                 <span stule="float:left">أورنيك شؤون خدمة 7</span> <span><center>كشف المرتبات</center></span> 
                
            </p>
         
    %for res_index , res in enumerate(process(data['form'])) : 
        %if res_index > 0 :
        <p style="page-break-after: always;">&nbsp;</p>
        %endif
        <p>
         عن الموظفين والمستخدمين التابعين ل${res['department_title'] or data['form']['company_name']} عن شهر ${data['form']['month']} عام ${data['form']['year']}
         </p>
        <table class="list_main_table" cellpadding="1">
            <tr>
                <td style="border-bottom:none"></td>
                <td style="border-bottom:none"></td>
                <td colspan="${res['basic_len']}">الاجر الاساسي</td>
                <td colspan="${res['allow_len']}">علاوات وبدلات</td>
                <td></td>
                <td colspan="${res['deduct_len']}">استقطاعات</td>
                <td><td>
            </tr>
            <tr><!-- step 1 : print header -->
                <th>#</th>
                <th class="emp_name">الاسم</th>
                %if res['include_bascic_salary']: 
                        <td>الفئة الابتدائية</td>
                %endif 
                %for i , title in enumerate(res['headrs']) :
                   
                    <th>${title}</th>
                     <!-- check for add allowance total colunm -->
                    %if res['include_allow_total']  and i == res['allow_column_index'] :
                        <td class="allow-total">اجمالي الاستحقاقات</td>
                    %endif
                    
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
                        
                        <td>${round(amount , 2)}</td>
                        <!-- check for adding allowance total colunm -->
                        %if res['include_allow_total']  and c == res['allow_column_index'] :
                            <td class="allow-total">${emp_row['emp_total_allow']}</td>
                        %endif
                        
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
                            <td>${round(amount , 2)}</td>
                            <!-- check for add allowance total colunm -->
                            %if res['include_allow_total']  and c == res['allow_column_index'] :
                                <td class="allow-total">${res['transfer_total']('allow',i)}</td>
                            %endif
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
                        
                            <th>${title}</th>
                            %if res['include_allow_total']  and c == res['allow_column_index'] :
                                <td class="allow-total">اجمالي الاستحقاقات</td>
                            %endif
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
                    <td>
                    ${round(value , 2)}
                    
                    </td>
                    %if res['include_allow_total']  and c == res['allow_column_index'] :
                        <td class="allow-total">${res['total_allows']}</td>
                    %endif
                %endfor
                %if res['include_deduct_total']: 
                        <td class="deduct-total">${res['total_deducts']}</td>
                %endif 
                %if res['include_net_total']: 
                        <td class="net-total">${res['total_nets']}</td>
                %endif 
            </tr>
        </table>
        %for r in range(res['BREAK_POINT'] -  res['len_emp_data'] % res['BREAK_POINT']) :
            <br />
        %endfor
        <table class="sign-tb">
       <tr>
            <td>
                امضاء رئيس الوحدة
            </td>
            <td class="sign-space">
                
            </td>
            <td>
                امضاء المحاسب
            </td>
            <td class="sign-space">
                
            </td>
            <td>
                المرجع الداخلي
            </td>
            <td class="sign-space">
                
            </td>
            <td>
                المحل ${data['form']['company_name']}
            </td>
            <td class="sign-space">
                
            </td>
            <td>
                التاريخ
            </td>
            <td class="sign-space">
                
            </td>
            <td>
                شئون خدمة
            </td>
            <td class="sign-space">
                
            </td>
       </tr>
   </table>
   %endfor
</body>
</html>


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
        <center style="font-size:25px;">
            <div>جمهورية السودان</div>
            <div>الولاية الشمالية</div>
        </center>
                 
                 <div stule="float:left" style="font-size:20px;">أورنيك شؤون خدمة 7</div> <div><center><span style="font-size:20px;"> كشف المرتبات </span></center></div> 
         
    %for res_index , res in enumerate(process(data['form'])) : 
        %if res_index > 0 :
        <div style="page-break-after: always;">&nbsp;</div>
        %endif
             <div>
                 
                 <span><center><p style="font-size:25px;">${data['form']['company_name']}</p></center></span> 
                
            </div>
        <div style="font-size:25px;">
         عن الموظفين التابعين لـ ${res['department_title'] or data['form']['company_name']} عن شهر ${data['form']['month']} عام ${data['form']['year']}
         </div>
        <table class="list_main_table" cellpadding="1">
            %if res['include_bascic_salary']:
            <tr>
                <td style="border-bottom:none"></td>
                <td style="border-bottom:none"></td>
                <td style="border-bottom:none"></td>
                <td style="border-bottom:none"></td>
                %if res['basic_len'] > 0:
                <td colspan="${res['basic_len']}" style="font-size:15px;">الاجر الاساسي</td>
                %endif
                %if res['allow_len'] > 0:
                <td colspan="${res['allow_len']}" style="font-size:15px;">علاوات وبدلات</td>
                %endif
                %if res['include_allow_total']:
                <td></td>
                %endif
                %if res['deduct_len'] > 0:
                <td colspan="${res['deduct_len']}" style="font-size:15px;">استقطاعات</td>
                %endif
                 %if res['include_net_total'] :
                <td><td>
                %endif
            </tr>
            %endif 
            <tr><!-- step 1 : print header -->
                <th style="min-width:10px;width:10px;">#</th>
                <th class="emp_name" style="font-size:13px;">الاسم</th>
                <th class="emp_name" style="min-width:50px;width:50px;">الوظيفة</th>
                 <th class="emp_name" style="min-width:20px;width:20px;">الدرجة</th>
                %if res['include_bascic_salary']: 
                        <td style="min-width:30px;width:30px;font-size:12px;">الفئة الابتدائية</td>
                %endif 
                %for i , title in enumerate(res['headrs']) :
                   
                    <th style="min-width:30px;width:30px;font-size:12px;">${title}</th>
                     <!-- check for add allowance total colunm -->
                    %if res['include_allow_total']  and i == res['allow_column_index'] :
                        <td class="allow-total" style="min-width:40px;width:40px;font-size:12px;">اجمالي الاستحقاقات</td>
                    %endif
                    
                %endfor
                %if res['include_deduct_total']: 
                    <td class="deduct-total" style="min-width:40px;width:40px;font-size:12px;">اجمالي الخصومات</td>
                %endif 
                %if res['include_net_total']: 
                    <td class="net-total" style="min-width:30px;width:30px;font-size:12px;">الصافي</td>
                %endif 
                    <td>الإمضاء</td>
            </tr>
            <!-- step 2 : print employee data -->
            %for i , emp_row in enumerate(res['emp_data']) :
                
                <tr>
                    <td>${i+1}</td>  
                    <td class="emp_name" style="min-width:120px;width:160px;font-size:14px;">
                    <p style="margin-top:5px;margin-bottom:5px"> ${emp_row['emp_name']} </p>
                    </td>
                    <td class="emp_name" style="min-width:50px;width:50px;">
                    <span> ${emp_row['emp_job']} </span>
                    </td>
                    <td class="emp_name" style="min-width:20px;width:20px;">
                    <span> ${emp_row['emp_degree']} </span>
                    </td>
                    %if res['include_bascic_salary']: 
                        <td style="font-size:15px;">${emp_row['basic_salary']}</td>
                    %endif 
                    %for c , amount in enumerate(emp_row['amounts']):
                        
                        <td style="font-size:15px;">${round(amount , 2)}</td>
                        <!-- check for adding allowance total colunm -->
                        %if res['include_allow_total']  and c == res['allow_column_index'] :
                            <td class="allow-total" style="font-size:15px;">${emp_row['emp_total_allow']}</td>
                        %endif
                        
                    %endfor
                    %if res['include_deduct_total']: 
                        <td class="deduct-total" style="font-size:15px;">${emp_row['emp_total_deduct']}</td>
                    %endif 
                    %if res['include_net_total']: 
                        <td class="net-total" style="font-size:15px;">${emp_row['emp_net']}</td>
                    %endif 
                     <td style="min-width:80px;width:80px;"></td>
               </tr><!-- step 3 : print header again if need -->
                %if (i+1) % res['BREAK_POINT'] == 0 and i >0 and i != res['len_emp_data'] - 1 :
                   
                    </table>
                     <div style="page-break-after: always;">&nbsp;</div>
                    <table>
                    <tr>
                        <th>-</th>
                        <td style="font-size:12px;">الاجمالي المرحل</td>
                        <td>-</td>
                        <td>-</td>
                        %if res['include_bascic_salary']: 
                            <td style="font-size:15px;">${res['transfer_total_basics'](i)}</td>
                        %endif 
                        %for c , amount in enumerate(res['page_trans_totals'](i)):                            
                            <td style="font-size:15px;">${round(amount , 2)}</td>
                            <!-- check for add allowance total colunm -->
                            %if res['include_allow_total']  and c == res['allow_column_index'] :
                                <td class="allow-total" style="font-size:15px;">${res['transfer_total']('allow',i)}</td>
                            %endif
                        %endfor
                        %if res['include_deduct_total']: 
                                <td class="deduct-total" style="font-size:15px;">${res['transfer_total']('deduct',i)}</td>
                        %endif 
                        %if res['include_net_total']: 
                                <td class="net-total" style="font-size:15px;">${res['transfer_total']('net',i)}</td>
                        %endif 
                    </tr>
                     <tr>
                        <th style="min-width:10px;width:10px;">#</th>
                        <th class="emp_name" style="font-size:13px;">الاسم</th>
                        <th style="min-width:50px;width:50px;">الوظيفة</th>
                        <th style="min-width:20px;width:20px;">الدرجة</th>
                        %if res['include_bascic_salary']: 
                            <td style="min-width:30px;width:30px;font-size:12px;">الفئة الابتدائية</td>
                        %endif 
                        %for c , title in enumerate(res['headrs']) :
                        
                            <th style="min-width:30px;width:30px;font-size:12px;">${title}</th>
                            %if res['include_allow_total']  and c == res['allow_column_index'] :
                                <td class="allow-total" style="min-width:40px;width:40px;font-size:12px;">اجمالي الاستحقاقات</td>
                            %endif
                        %endfor
                        %if res['include_deduct_total']: 
                            <td class="deduct-total" style="min-width:40px;width:40px;font-size:12px;">اجمالي الخصومات</td>
                        %endif 
                        %if res['include_net_total']: 
                            <td class="net-total" style="min-width:30px;width:30px;font-size:12px;">الصافي</td>
                %endif 
                     <td>الإمضاء</td>
                    </tr>
                %endif
            %endfor

            <tr><!-- step 4 : print final totals -->
                <th>-</th>
                <th style="font-size:12px;">الاجمالي</th>
                <td>-</td>
                <td>-</td>
                %if res['include_bascic_salary']: 
                            <td style="font-size:15px;">${res['total_basics']}</td>
                        %endif 
                %for c , value in enumerate(res['allow_deduct_totals']) :
                    <td style="font-size:15px;">
                    ${round(value , 2)}
                    
                    </td>
                    %if res['include_allow_total']  and c == res['allow_column_index'] :
                        <td class="allow-total" style="font-size:15px;">${res['total_allows']}</td>
                    %endif
                %endfor
                %if res['include_deduct_total']: 
                        <td class="deduct-total" style="font-size:15px;">${res['total_deducts']}</td>
                %endif 
                %if res['include_net_total']: 
                        <td class="net-total" style="font-size:15px;">${res['total_nets']}</td>
                %endif 
            </tr>
        </table>
        <br>
        <center>${res['amount_in_words']}</center>
        %for r in range(res['additional_rows']-2) :
            <br />
        %endfor

        <table class="sign-tb">
       <tr>
            <td style="font-size:15px;">
                امضاء رئيس الوحدة
            </td>
            <td class="sign-space">
                
            </td>
            <td style="font-size:15px;">
                امضاء المحاسب
            </td>
            <td class="sign-space">
                
            </td>
            <td style="font-size:15px;">
                المراجع الداخلي
            </td>
            <td class="sign-space">
                
            </td>
            <td style="font-size:15px;">
                التاريخ
            </td>
            <td class="sign-space">
                
            </td>
            <td style="font-size:15px;">
               مدير شئون خدمة
            </td>
            <td class="sign-space">
                
            </td>
       </tr>
   </table>
   %endfor
</body>
</html>



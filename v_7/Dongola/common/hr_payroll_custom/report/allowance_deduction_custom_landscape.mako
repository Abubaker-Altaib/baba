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
        <center style="font-size:30px;">
            <p>جمهورية السودان</p>
            <p>الولاية الشمالية</p>
             <p>المرتبات بالمواقع</p>
        </center>

         
    %for res_index , res in enumerate(process(data['form'])) : 
        %if res_index > 0 :
        <p style="page-break-after: always;">&nbsp;</p>
        %endif
             %if data['form']['company_name']:
                 <p>
                     
                     <span><center><p style="font-size:30px;">${data['form']['company_name']}</p></center></span> 
                    
                </p>
            %endif
        <p style="font-size:30px;">
         تسوية مرتبات العاملين عن شهر ${data['form']['month']} عام ${data['form']['year']}
         </p>
        %if res :
            <table class="list_main_table" cellpadding="1">
                %if res['include_bascic_salary']:
                <tr>
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
                    <th class="emp_name" style="font-size:15px;">الاسم</th>
                    <!--th class="emp_name" style="min-width:50px;width:50px;">الوظيفة</th>
                     <th class="emp_name" style="min-width:40px;width:40px;">الدرجة</th-->
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
                </tr>
                <!-- step 2 : print employee data -->
                %for i , emp_row in enumerate(res['emp_data']) :
                    
                    <tr>
                        <td>${i+1}</td>  
                        <td class="emp_name" style="min-width:100px;width:120px;font-size:12px;">
                        <p> ${emp_row['emp_name']} </p>
                        </td>
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
                   </tr><!-- step 3 : print header again if need -->
                    %if (i+1) % res['BREAK_POINT'] == 0 and i >0 and i != res['len_emp_data'] - 1 :
                       
                        </table>
                         <p style="page-break-after: always;">&nbsp;</p>
                        <table>
                        <tr>
                            <th>-</th>
                            <td style="font-size:12px;">الاجمالي المرحل</td>
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
                            <th class="emp_name" style="font-size:15px;">الاسم</th>
                            <!--th style="min-width:50px;width:50px;">الوظيفة</th>
                            <th style="min-width:40px;width:40px;">الدرجة</th-->
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
                        </tr>
                    %endif
                %endfor

                <tr><!-- step 4 : print final totals -->
                    <th>-</th>
                    <th style="font-size:12px;">الاجمالي</th>
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
        %endif 


        
   %endfor
</body>
</html>



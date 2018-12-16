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
        <center style="font-size:20px;">
            <div>جمهورية السودان</div>
            <div>الولاية الشمالية</div>
             <div>المرتبات بالمواقع</div>
        </center>

         
    %for res_index , res in enumerate(process(data['form'])) : 
        %if res_index > 0 :
        <p style="page-break-after: always;">&nbsp;</p>
        %endif
             %if data['form']['company_name']:
                     <center><div style="font-size:20px;">${data['form']['company_name']}</div></center>
                    
            %endif
        <div style="font-size:20px;">
         تسوية مرتبات العاملين عن شهر ${data['form']['month']} عام ${data['form']['year']}
         </div>
        %if res :
            <table class="list_main_table" cellpadding="1">
                <tr>
                    <td style="border-bottom:none"></td>
                    <td style="border-bottom:none"></td>
                    <td colspan="2" style="font-size:15px;">الصافي</td>
                    <td colspan="2" style="font-size:15px;">الإستحقاقات</td>
                    <td colspan="2" style="font-size:15px;">الإستقطاعات</td>
                </tr>
                <tr><!-- step 1 : print header -->
                    <th style="min-width:10px;width:10px;">#</th>
                    <th class="emp_name" style="font-size:15px;">الموقع</th>
                    <!--th class="emp_name" style="min-width:50px;width:50px;">الوظيفة</th>
                     <th class="emp_name" style="min-width:40px;width:40px;">الدرجة</th-->
                         <td class="allow-total" style="min-width:30px;width:30px;font-size:12px;">الشهر الحالي</td>
                         <td style="min-width:30px;width:30px;font-size:12px;">الشهر السابق</td>
                    <!-- check for add allowance total colunm -->
                        <td class="allow-total" style="min-width:40px;width:40px;font-size:12px;">زيادة</td>
                        <td style="min-width:40px;width:40px;font-size:12px;">نقصان</td>
                        <td class="deduct-total" style="min-width:40px;width:40px;font-size:12px;">زيادة</td>
                        <td style="min-width:40px;width:40px;font-size:12px;">نقصان</td>
                </tr>
                <!-- step 2 : print employee data -->
                %for i , emp_row in enumerate(res['emp_data']) :
                    
                    <tr>
                        <td>${i+1}</td>
                        <td class="emp_name" style="min-width:100px;width:120px;font-size:12px;">
                        <span> ${emp_row['emp_name']} </span>
                        </td>
                            <td class="net-total" style="font-size:15px;">${emp_row['emp_curr_net']}</td>
                            <td style="font-size:15px;">${emp_row['emp_pre_net']}</td>
                            <td class="allow-total" style="font-size:15px;">${emp_row['emp_incre_allow']}</td>
                            <td style="font-size:15px;">${emp_row['emp_decre_allow']}</td> 
                            <td class="deduct-total" style="font-size:15px;">${emp_row['emp_incre_deduct']}</td>
                            <td style="font-size:15px;">${emp_row['emp_decre_deduct']}</td>
                    </tr><!-- step 3 : print header again if need -->
                    %if (i+1) % res['BREAK_POINT'] == 0 and i >0 :
                       
                        </table>
                         <div style="page-break-after: always;">&nbsp;</div>
                        <table>
                        <tr>
                            <th>-</th>
                            <td style="font-size:12px;">الاجمالي المرحل</td>
                                <td class="net-total" style="font-size:15px;">${res['transfer_total']('net_curr',i)}</td>
                                <td class="net-total" style="font-size:15px;">${res['transfer_total']('net_pre',i)}</td>
                                <td class="allow-total" style="font-size:15px;">${res['transfer_total']('allow_incre',i)}</td>
                                <td class="allow-total" style="font-size:15px;">${res['transfer_total']('allow_decre',i)}</td>
                                <td class="deduct-total" style="font-size:15px;">${res['transfer_total']('deduct_incre',i)}</td>
                                <td class="deduct-total" style="font-size:15px;">${res['transfer_total']('deduct_decre',i)}</td>

                        </tr>
                         <tr>
                            <th style="min-width:10px;width:10px;">#</th>
                                <th class="emp_name" style="font-size:15px;">الموقع</th>
                                <!--th class="emp_name" style="min-width:50px;width:50px;">الوظيفة</th>
                                <th class="emp_name" style="min-width:40px;width:40px;">الدرجة</th-->
                                <td style="min-width:30px;width:30px;font-size:12px;">الشهر الحالي</td>
                                <td style="min-width:30px;width:30px;font-size:12px;">الشهر السابق</td>
                                <td class="allow-total" style="min-width:40px;width:40px;font-size:12px;">زيادة</td>
                                <td class="allow-total" style="min-width:40px;width:40px;font-size:12px;">نقصان</td>
                                <td class="deduct-total" style="min-width:40px;width:40px;font-size:12px;">زيادة</td>
                                <td class="deduct-total" style="min-width:40px;width:40px;font-size:12px;">نقصان</td>
                        </tr>
                    %endif
                %endfor

                <tr><!-- step 4 : print final totals -->
                    <th>-</th>
                    <th style="font-size:12px;">الاجمالي</th>
                            <td class="net-total" style="font-size:15px;">${res['total_curr_nets']}</td>
                            <td class="net-total" style="font-size:15px;">${res['total_pre_nets']}</td>
                            <td class="allow-total" style="font-size:15px;">${res['total_incre_allows']}</td>
                            <td class="allow-total" style="font-size:15px;">${res['total_decre_allows']}</td>
                            <td class="deduct-total" style="font-size:15px;">${res['total_incre_deducts']}</td>
                            <td class="deduct-total" style="font-size:15px;">${res['total_decre_deducts']}</td>
                </tr>
            </table>
            <br>
        %endif 


        
   %endfor
</body>
</html>



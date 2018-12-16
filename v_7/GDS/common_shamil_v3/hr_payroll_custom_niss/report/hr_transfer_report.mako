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
            background-color: #e6e6e6;
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
            <p style="margin-top:5px;margin-bottom:5px">بسم الله الرحمن الرحيم</p>
            <p style="margin-top:5px;margin-bottom:5px"><b>قوات الدعم السريع</b></p>
            <p style="margin-top:5px;margin-bottom:5px;margin-top:5px;margin-bottom:5px;"><b>تقرير يوضح حالات الانتداب و الإحاق و الاعارة</b></p>
            <p style="margin-top:5px;margin-bottom:5px">
                %if data['form']['date_from']:
                 <b>من تاريخ   ${data['form']['date_from']}</b>
                %endif
                %if data['form']['date_to']:
                 <b>إلى تاريخ   ${data['form']['date_to']}</b>
                %endif
                
            </p>
        </center>

         
    %for res_index , res in enumerate(process(data['form'])) : 

        %if res :
            <table class="list_main_table" cellpadding="1"> 
                <tr><!-- step 1 : print header -->
                    <th class="deduct-total" style="min-width:10px;width:10px;">م</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">رقم البطاقة</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">الرتبة</th>
                    <th class="deduct-total" style="min-width:120px;width:190px;font-size:14px;">الاسم</th>
                    <th class="deduct-total" style="min-width:100px;width:100px;font-size:14px;">الجهة من</th>
                    <th class="deduct-total" style="min-width:100px;width:100px;font-size:14px;">الجهة إلى</th>
                    <th class="deduct-total" style="min-width:70px;width:70px;font-size:14px;">النوع</th>
                    <th class="deduct-total" style="min-width:80px;width:80px;font-size:14px;">تاريخ التبليغ</th>
                    <th class="deduct-total" style="min-width:80px;width:80px;font-size:14px;">تاريخ الإنتهاء</th>
                    <th class="deduct-total" style="min-width:70px;width:70px;font-size:14px;">رقم القرار</th>
                    <th class="deduct-total" style="min-width:70px;width:70px;font-size:14px;">ملحوظات</th>
                </tr>
                <!-- step 2 : print employee data -->
                %for i , emp_row in enumerate(res['emp_data']) :
                    <tr>
                        <td>${i+1}</td>  
                        <td class="emp_name" style="min-width:80px;width:80px;font-size:14px;font-name:Helvetica;">
                        <p style="margin-top:5px;margin-bottom:5px"> ${emp_row['emp_code']} </p>
                        </td>
                        <td class="emp_name" style="min-width:70px;width:70px;font-size:12px;">
                        <p style="margin-top:5px;margin-bottom:5px"> ${emp_row['emp_degree']} </span>
                        </td>
                        <td class="emp_name" style="min-width:150px;width:190px;font-size:14px;font-name:Helvetica;">
                        <p style="margin-top:5px;margin-bottom:5px"> ${emp_row['emp_name']} </p>
                        </td>
                        <td class="emp_name" style="min-width:100px;width:120px;font-size:12px;">
                        <p style="margin-top:5px;margin-bottom:5px"> ${emp_row['prev_com']} </span>
                        </td>
                        <td class="emp_name" style="min-width:100px;width:120px;font-size:12px;">
                        <p style="margin-top:5px;margin-bottom:5px"> ${emp_row['new_com']} </span>
                        </td>
                        <td class="emp_name" style="min-width:70px;width:70px;font-size:12px;">
                         %if emp_row['deleg_type']=='mandate':
			    <p>إنتداب</p>
			 %endif
			 %if emp_row['deleg_type']=='loaned':
			    <p>إعارة</p>
			 %endif
			 %if emp_row['deleg_type']=='transferred':
			    <p>الحاق</p>
			 %endif
                        </td>
                        <td class="emp_name" style="min-width:70px;width:80px;font-size:12px;">
                        <p style="margin-top:5px;margin-bottom:5px"> ${emp_row['move_date']} </span>
                        </td>
                        <td class="emp_name" style="min-width:70px;width:80px;font-size:12px;">
                        <p style="margin-top:5px;margin-bottom:5px"> ${emp_row['move_end_date']} </span>
                        </td>
                        <td class="emp_name" style="min-width:70px;width:70px;font-size:12px;">
                        <p style="margin-top:5px;margin-bottom:5px"> ${emp_row['deleg_num']} </span>
                        </td>
                       <td class="emp_name" style="min-width:70px;width:70px;font-size:12px;">
                        <p style="margin-top:5px;margin-bottom:5px"></span>
                        </td>
                   </tr>
                    %if (i+1)==20 or ((i+1)%25) == 0 and (i+1) !=25:
                     </table>
                     <div style="page-break-after: always;">&nbsp;</div>

                     <table>
                       <tr><!-- step 1 : print header -->
                    <th class="deduct-total" style="min-width:10px;width:10px;">م</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">رقم البطاقة</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">الرتبة</th>
                    <th class="deduct-total" style="min-width:120px;width:160px;font-size:14px;">الاسم</th>
                    <th class="deduct-total" style="min-width:50px;width:50px;font-size:14px;">الجهة من</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">الجهة إلى</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">النوع</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">تاريخ التبليغ</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">تاريخ الإنتهاء</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">رقم القرار</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">ملحوظات</th>
                       </tr>
                    %endif
                %endfor
            </table>
        %endif 


        
   %endfor
</body>
</html>



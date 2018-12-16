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
            <p style="margin-top:5px;margin-bottom:5px"><b><u>وزارة المالية والإقتصاد والقوى العاملة</u></b></p>
            <p style="margin-top:5px;margin-bottom:5px"><b><u>ديوان شئون الخدمة</u></b></p>
            <p style="margin-top:5px;margin-bottom:5px"><b><u>حصر تفصيلي للعاملين</u></b></p>
        </center>
        <p style="float:right;font-size:25px;margin-top:5px;margin-bottom:5px;"><b>الوحدة  ${data['form']['company_id'][1]}</b></p>

         
    %for res_index , res in enumerate(process(data['form'])) : 

        %if res :
            <table class="list_main_table" cellpadding="1"> 
                <tr><!-- step 1 : print header -->
                    <th class="deduct-total" style="min-width:10px;width:10px;">الرقم</th>
                    <th class="deduct-total" style="min-width:120px;width:160px;font-size:14px;">الاسم</th>
                    <th class="deduct-total" style="min-width:50px;width:50px;font-size:14px;">تاريخ الميلاد</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">تاريخ التعيين</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">المؤهل</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">مسمى الوظيفة</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">الدرجة الحالية</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">تاريخ الدخول في الدرجة</th>
                    <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">ملاحظات</th>
 
                </tr>
                <!-- step 2 : print employee data -->
                %for i , emp_row in enumerate(res['emp_data']) :
                    <tr>
                        <td>${i+1}</td>  
                        <td class="emp_name" style="min-width:120px;width:160px;font-size:14px;font-name:Helvetica;">
                        <p style="margin-top:5px;margin-bottom:5px"> ${emp_row['emp_name']} </p>
                        </td>
                        <td class="emp_name" style="min-width:100px;width:120px;font-size:12px;">
                        <p style="margin-top:5px;margin-bottom:5px"> ${emp_row['birth']} </span>
                        </td>
                        <td class="emp_name" style="min-width:100px;width:120px;font-size:12px;">
                        <p style="margin-top:5px;margin-bottom:5px"> ${emp_row['employee_date']} </span>
                        </td>
                        <td class="emp_name" style="min-width:100px;width:120px;font-size:12px;">
                        <p style="margin-top:5px;margin-bottom:5px">${emp_row['qualif']}</span>
                        </td>
                        <td class="emp_name" style="min-width:100px;width:120px;font-size:12px;">
                        <p style="margin-top:5px;margin-bottom:5px"> ${emp_row['emp_job']} </span>
                        </td>
                        <td class="emp_name" style="min-width:100px;width:120px;font-size:12px;">
                        <p style="margin-top:5px;margin-bottom:5px"> ${emp_row['emp_degree']} </span>
                        </td>
                        <td class="emp_name" style="min-width:100px;width:120px;font-size:12px;">
                        <p style="margin-top:5px;margin-bottom:5px"> ${emp_row['degree_date']} </span>
                        </td>
                        <td style="min-width:80px;width:80px;"></td> 
                   </tr>
                    %if (i+1)==27 or ((i+1)%30) == 0 and (i+1) !=30:
                     </table>
                     <div style="page-break-after: always;">&nbsp;</div>
                     <p style="float:right;font-size:25px;margin-top:5px;margin-bottom:5px;"><b>الوحدة  ${data['form']['company_id'][1]}</b></p>
                     <table>
                       <tr><!-- step 1 : print header -->
		            <th class="deduct-total" style="min-width:10px;width:10px;">الرقم</th>
		            <th class="deduct-total" style="min-width:120px;width:160px;font-size:14px;">الاسم</th>
		            <th class="deduct-total" style="min-width:50px;width:50px;font-size:14px;">تاريخ الميلاد</th>
		            <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">تاريخ التعيين</th>
		            <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">المؤهل</th>
		            <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">مسمى الوظيفة</th>
		            <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">الدرجة الحالية</th>
		            <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">تاريخ الدخول في الدرجة</th>
		            <th class="deduct-total" style="min-width:40px;width:40px;font-size:14px;">ملاحظات</th>
	 
                       </tr>
                    %endif
                %endfor
            </table>
        %endif 


        
   %endfor
</body>
</html>



<html dir="rtl" lang="ar">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
    <style type="text/css">
        .tb-data {
            border-collapse: collapse;
            width: 100%;
            outline: 3px solid black;
        }

        .tb-data td,
        .tb-data th {

            text-align: center;
            border: 1px solid black;
            padding: 1px;
        }

        .manager-block {
            text-align: right;
            float: left;
            margin-top: 3px;
            padding: 30px;
            font-size: 18px;
        }



        .right-block {
            float: right;
            margin-top: 80px;
        }

        .com {
            border-collapse: collapse;
            width: 100%;
            outline: 1px solid black;
            text-align: center;

        }

        #con2 {
            margin-top: 30px;
        }

        #con3 {
            margin-top: 30px;
        }
    </style>
</head>

<body>
    <div id="con1" class="container">
        %for employee in records() :
        <center>
            <br/>
            <p>
                بسم الله الرحمن الرحيم
            </p>
            <h3>
                <u>جهاز اﻷمن و المخابرات الوطني</u>
            </h3>
            <h3>
                <u>شهادة خلو طرف</u>
            </h3>
        </center>

        <table>
            <tr>
                <td width="200">
                    رقم البطاقة : ${employee.otherid}
                </td>
                <td width="200">
                    الرتبة : ${employee.degree_id.name}
                </td>
                <td width="500">
                    اﻹسم : ${employee.name}
                </td>

            </tr>

            <tr>
                <td width="800">
                    الهيكل : ${employee.department_id.name_get_custom()[0][1]}
                </td>

            </tr>

            <tr>
                <td width="200">
                    التاريخ : ${date}
                </td>
                <td width="200">
                    رقم الهاتف : ${employee.work_phone or ''}
                </td>


            </tr>
        </table>

        <table border="1" class="com">
            <tr>
                <td width="30" style="text-align: center;">
                    م
                </td>
                <td width="100">
                    الجهة
                </td>
                <td width="300">
                    الرتبة و اﻹسم
                </td>
                <td width="200">
                    التوقيع
                </td>
                <td width="200">
                    الختم
                </td>
            </tr>
            <tr height="150">
                <td width="30" style="text-align: center;">
                    1-
                </td>
                <td width="100">
                    إدارة العضو
                </td>
                <td width="300">
                    لايوجد
                </td>
                <td width="200">
                </td>
                <td width="200">
                </td>
            </tr>
            <tr height="150">
                <td width="30" style="text-align: center;">
                    2-
                </td>
                <td width="100">
                    دائرة العضو
                </td>
                <td width="300">
                    لايوجد
                </td>
                <td width="200">
                </td>
                <td width="200">
                </td>
            </tr>
            <tr height="150">
                <td width="30" style="text-align: center;">
                    3-
                </td>
                <td width="100">
                    إدارة اﻹمداد
                </td>
                <td width="300">
                    ${(has_personal_custody(employee) or employee.house_type == '1') and u'يوجد' or u'لا يوجد'}
                </td>
                <td width="200">
                </td>
                <td width="200">
                </td>
            </tr>
            <tr height="150">
                <td width="30" style="text-align: center;">
                    4-
                </td>
                <td width="100">
                    إدارة الخدمات
                </td>
                <td width="300">
                    لايوجد
                </td>
                <td width="200">
                </td>
                <td width="200">
                </td>
            </tr>
            <tr height="150">
                <td width="30" style="text-align: center;">
                    5-
                </td>
                <td width="100">
                    اﻹدارة القانونية
                </td>
                <td width="300">
                        ${has_un_processed_punish(employee) and u'يوجد' or u'لا يوجد'}
                </td>
                <td width="200">
                </td>
                <td width="200">
                </td>
            </tr>
            <tr height="150">
                <td width="30" style="text-align: center;">
                    6-
                </td>
                <td width="100">
                    دائرة الخدمات الهندسية
                </td>
                <td width="300">
                        ${has_vehicle(employee) and u'يوجد' or u'لا يوجد'}
                </td>
                <td width="200">
                </td>
                <td width="200">
                </td>
            </tr>
            <tr height="150">
                <td width="30" style="text-align: center;">
                    7-
                </td>
                <td width="100">
                    إدارة اﻹتصالات
                </td>
                <td width="300">
                    لايوجد
                </td>
                <td width="200">
                </td>
                <td width="200">
                </td>
            </tr>
        </table>

        <p></p>

        <table border="1" class="com">
            <tr height="150">
                <td width="30" style="text-align: center;">
                    8-
                </td>
                <td width="100">
                    إدارة الخدمات الفنية
                </td>
                <td width="300">
                    ${has_personal_custody(employee) and u'يوجد' or u'لا يوجد'}
                </td>
                <td width="200">
                </td>
                <td width="200">
                </td>
            </tr>
            <tr height="150">
                <td width="30" style="text-align: center;">
                    9-
                </td>
                <td width="100">
                    إدارة أمن المنشأة
                </td>
                <td width="300">
                    ${employee.state=='approved' and employee.otherid or u'لا يوجد'}
                </td>
                <td width="200">
                </td>
                <td width="200">
                </td>
            </tr>
            <tr height="150">
                <td width="30" style="text-align: center;">
                    10-
                </td>
                <td width="100">
                    اﻹدارة الشئون المالية
                </td>
                <td width="300">
                    ${(has_loans(employee) or has_deduct(employee) or f_custody(employee)) and u'يوجد' or u'لا يوجد'}
                </td>
                <td width="200">
                </td>
                <td width="200">
                </td>
            </tr>
            <tr height="150">
                <td width="30" style="text-align: center;">
                    11-
                </td>
                <td width="100">
                    مستشفى الأمل -البطاقة العلاجية أو البطاقة الولائية
                </td>
                <td width="300">
                    ${has_family(employee) and u'يوجد' or u'لا يوجد'}
                </td>
                <td width="200">
                </td>
                <td width="200">
                </td>
            </tr>
            <tr height="150">
                <td width="30" style="text-align: center;">
                    12-
                </td>
                <td width="100">
                    إدارة ${employee.military_type == 'soldier' and u'شئون الرتب الأخرى' or u'إدارة شئون الضباط'}
                </td>
                <td width="300">
                </td>
                <td width="200">
                </td>
                <td width="200">
                </td>
            </tr>
        </table>

        <table>
            <tr>
                <td width="200">
                    المحطة : ${employee.military_type == 'officer' and u'الخرطوم بحري' or ( (employee.military_type == 'soldier' and employee.company_id.hq)
                    and u'الخرطوم بحري' or u'الرياض')}
                </td>
            </tr>
            <tr>
                <td width="200">
                    التاريخ : ${date}
                </td>
            </tr>
        </table>

        <div style="text-align: left;">
            <br/>
            <p>
                مدير إدارة ${employee.military_type == 'soldier' and u'شئون الرتب الأخرى' or u'إدارة شئون الضباط'}
            </p>

        </div>
        <p style="page-break-after: always;">&nbsp;</p>
        %endfor
    </div>
</body>

<footer>


</footer>

</html>
<html dir="rtl" lang="ar">
  <head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
    <style type="text/css">
        .custom td {
            border: 1px solid black;

        }

        .custom {
            border-collapse: collapse;
            border: 1px solid black;
            width: 100%;
            font-size: 10px;
            font-weight: bold;
            text-align: center;
        }

        h2{
          padding: 5px;
          font-family: 'Droid Arabic Kufi', serif;
        }

    </style>
  <body>

    <center>
      <h2>بسم الله الرحمن الرحيم</h2>
      <br/>
    </center>
    <table>
        <tr>
          <td width="30">
            </td>
            <td style="text-align: center;">
               <h4>أورنيك جهاز الأمن و المخابرات الوطني (أ)</h4>
            </td> 
        </tr>
        <tr>
          <td width="30">
            </td>
            <td>
               <h4>نمرة:${seq}</h4>
            </td>            
        </tr>
        <tr>
          <td width="30">
            </td>
            <td>
               <h4>صادر من</h4>
            </td>            
        </tr>
  </table>
  <br/>

  <table>
        <tr>
          <td width="30">
            </td>
            <td width="200">
               رقم البطاقة
            </td>
            <td width="50">
               ${code}
            </td>  
            <td width="100">
               الرتبة
            </td>
            <td width="50">
               ${degree}
            </td>            
        </tr>
        <tr>
          <td width="30">
            </td>
            <td>
               الإسم
            </td>
            <td colspan="3" style="text-align: right;">
               ${name}
            </td>  
                      
        </tr>
        <tr>
            <td colspan="5" style="text-align: center;">
               <h4><b>تصرح له الغياب من مركزه والتوجه الي:إجازة</b></h4>
            </td>
                      
        </tr>
        <tr>
            <td width="30">
            </td>
            <td>
               محطة
            </td>
        </tr>
        <tr>
            <td width="30">
            </td>
            <td>
               الى المدينة/القرية
            </td>
            <td colspan="3" style="text-align: right;">
               ${place}
            </td>
        </tr>
        <tr>
            <td width="30">
            </td>
            <td>
               نمرة إستمارة السفر
            </td>
        </tr>
        <tr>
            <td width="30">
            </td>
            <td>
               تاريخ الإصدار
            </td>
        </tr>
        <tr>
            <td width="30">
            </td>
            <td>
               المنصرفة للسفر من
            </td>
        </tr>
        <tr>
            <td width="30">
            </td>
            <td> 
               إلى
            </td>
            <td colspan="3" style="text-align: center;">
               والعودة
            </td>
        </tr>
        <tr>
            <td width="30">
            </td>
            <td> 
               مدة الإجازة
            </td>
            <td colspan="2" style="text-align: center;">
               ${holi_days}
            </td>
            <td style="text-align: right;">
               يوم
            </td>
        </tr>
        <tr>
            <td width="30">
            </td>
            <td> 
               أيام الطريق
            </td>
            <td colspan="2" style="text-align: center;">
               ${street_days}
            </td>
            <td style="text-align: right;">
               يوم
            </td>
        </tr>
        <tr>
            <td width="30">
            </td>
            <td> 
               إجمالي مدة الإجازة
            </td>
            <td colspan="2" style="text-align: center;">
               ${total_days}
            </td>
            <td style="text-align: right;">
               يوم
            </td>
        </tr>
        <tr>
            <td width="30">
            </td>
            <td> 
               تاريخ الإجازة من
            </td>
            <td colspan="2" style="text-align: center;">
               ${date_from}
            </td>
            <td style="text-align: right;">
               إلى
            </td>
            <td style="text-align: right;">
               ${date_to}
            </td>

        </tr>
        <tr>
            <td width="30">
            </td>
            <td> 
               إعتماد القائد المباشر
            </td>
            <td colspan="3" style="text-align: left;">
               الختم
            </td>
           
        </tr>
        <tr>
            <td colspan="8" >
               --------------------------------------------------------------------------------------------------------------------------------------------
            </td>
        </tr>

        <tr>
            <td width="30">
            </td>
            <td> 
               نوع الإجازة
            </td>
            <td colspan="3" style="text-align: left;">
               ${holi_type}
            </td>
           
        </tr>

  </table>
  <br/>
  
    
  </body>
</html>

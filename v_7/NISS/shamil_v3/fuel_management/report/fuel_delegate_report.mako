<html dir="rtl" lang="ar">
  <head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
    <style type="text/css">

      .tb-data{
        border-collapse: collapse;
        width: 100%;
        outline:  3px solid black;
      }
      .tb-data td , .tb-data th{
        
          text-align: center;
          border: 1px solid black;
          padding: 1px;
        }
      .manager-block{
          text-align: right;
          float: left;
          margin-top: 3px;
          padding: 30px;
          font-size: 18px;
        }

        .right-block{
          float: right;
          margin-top: 80px;
        }

        .trh{
          border-bottom: solid 3px black;
        }

        #con2{
          margin-top: 30px;
        }
        #con3{
          margin-top: 30px;
        }

    </style>
  </head>
  <body>
    <div id="con1" class="container">
      <table style="width: 100%;font-size: 15px;padding-top: 0px;padding-bottom: 0px;text-align: center;height: 7px;max-height: 7px;">
				<tr>
					<th width="30%" >
						<p></p>
					</th>
					<th width="30%" >
						<p>بسم الله الرحمن الرحيم</p>
						<p>سري للغاية</p>
					</th>
					<th width="30%" >
            <p></p>						
					</th>
					
					
				</tr>
			</table>

      <table style="width: 100%;font-size: 15px;padding-top: 0px;padding-bottom: 0px;text-align: center;height: 7px;max-height: 7px;">
				<tr>
					<th width="30%" >
						<p></p>
					</th>
					<th width="30%" >
						<p></p>
						<p></p>
						<p></p>
						<p></p>
					</th>
					<th width="30%" >
            <p></p>
						<p></p>
						<p></p>
						<p></p>
						<p>جهاز اﻷمن و المخابرات الوطني</p>
						<p>هيئة اﻹدارة</p>
						<p>دائرة الخدمات الهندسية</p>
						<p>إدراة المركبات و الوقود</p>
						<p>فرع الوقود</p>
						<p>التاريخ:${time.strftime("%Y-%m-%d")}</p>
					</th>
					
					
				</tr>
			</table>
      <center>
        <!-- <p>
          بسم الله الرحمن الرحيم
        </p> -->
        <p>
           تقرير مناديب الوقود
        </p>

         <p>
            حسب ${to_arabic(delegate['type'])} 
        </p>

        %if delegate['type'] == 'delegate' :
        %for c,i in enumerate(delegate['data']):
        <table class="trh" style="width:100%;">
          <tr>
            <td style="float: right;">
              ${c+1}-${i['name']}
            </td>
          </tr>
        </table>

        <table style="width:100%;">
          <tr>
            <td>
              النمرة العسكرية
            </td>
             <td style="width:30%;">
              ${i['code']}
            </td>
          </tr>
          <tr>
            <td>
              الرتبة 
            </td>
            <td style="width:30%;">
              ${i['degree']}
            </td>
            <td>
              الإدارة
            </td>
            <td style="width:40%;">
              ${i['department']}
            </td>
          </tr>

        </table>
        %if len(i['delegates']) > 0 :
        <table style="width:100%;" border="1">
          <tr>
          <th>
            #
          </th>
          <th>
            صنف الوقود
          </th>
          <th>
            الطلمبة
          </th>
          <th>
            رقم البطاقة
          </th>
          <th>
            كمية الوقود
          </th>
            </tr>
            
              %for l,q in enumerate(i['delegates']):
            <tr>
            <td>
              ${l+1}
            </td>
            <td>
              ${q.product_id.name}
            </td>
            <td>
              ${q.location_id.name}
            </td>
            <td>
              ${q.card_no}
            </td>
            <td>
              ${q.fuel_qty}
            </td>
            
            </tr>
            %endfor
          
        </table>
        <br/>
        <br/>
        %endif
        %endfor
        %endif



        %if delegate['type'] == 'location' :
        %for c,i in enumerate(delegate['data']):
        <table class="trh" style="width:100%;">
          <tr>
            <td style="float: right;">
              ${c+1}-${i['name']}
            </td>
          </tr>
        </table>


        %if len(i['locations']) > 0 :
        <table style="width:100%;" border="1">
          <tr>
          <th>
            #
          </th>
          <th>
            صنف الوقود
          </th>
          <th>
            إسم المندوب
          </th>
           <th>
            الرتبة
          </th>
           <th>
            النمرة العسكرية
          </th>
          <th>
            رقم البطاقة
          </th>
          <th>
            كمية الوقود
          </th>
            </tr>
            
              %for l,q in enumerate(i['locations']):
            <tr>
            <td>
              ${l+1}
            </td>
            <td>
              ${q.product_id.name}
            </td>
            <td>
              ${q.delegate_id.employee_id.name}
            </td>
            <td>
              ${q.delegate_id.degree_id.name}
            </td>
            <td>
              ${q.delegate_id.emp_code}
            </td>
            <td>
              ${q.card_no}
            </td>
            <td>
              ${q.fuel_qty}
            </td>
            
            </tr>
            %endfor
          
        </table>
        <br/>
        <br/>
        %endif
        %endfor
        %endif


        %if delegate['type'] == 'fuel_type' :
        %for c,i in enumerate(delegate['data']):
        <table class="trh" style="width:100%;">
          <tr>
            <td style="float: right;">
              ${c+1}-${i['name']}
            </td>
          </tr>
        </table>


        %if len(i['fuel_types']) > 0 :
        <table style="width:100%;" border="1">
          <tr>
          <th>
            #
          </th>
          <th>
            الطلمبة
          </th>
          <th>
            إسم المندوب
          </th>
           <th>
            الرتبة
          </th>
           <th>
            النمرة العسكرية
          </th>
          <th>
            رقم البطاقة
          </th>
          <th>
            كمية الوقود
          </th>
            </tr>
            
              %for l,q in enumerate(i['fuel_types']):
            <tr>
            <td>
              ${l+1}
            </td>
            <td>
              ${q.location_id.name}
            </td>
            <td>
              ${q.delegate_id.employee_id.name}
            </td>
            <td>
              ${q.delegate_id.degree_id.name}
            </td>
            <td>
              ${q.delegate_id.emp_code}
            </td>
            <td>
              ${q.card_no}
            </td>
            <td>
              ${q.fuel_qty}
            </td>
            
            </tr>
            %endfor
          
        </table>
        <br/>
        <br/>
        %endif
        %endfor
        %endif
        
      </center>
  
    </div>

  </body>

<footer>


</footer>

</html>

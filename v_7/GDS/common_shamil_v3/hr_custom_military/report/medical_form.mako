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
	    		text-align: top;
	    		border: 1px solid black;
	    		padding: 1px;
	    	}
			.manager-block{
	    		text-align: right;
	    		float: left;
	    		margin-top: 3px;
	    		padding: 10px;
	    		font-size: 18px;
	    	}

	    	.right-block{
	    		float: right;
	    		margin-top: 50px;
	    	}

	    	.trh{
	    		border-bottom: solid 3px black;
	    	}

	    	#con2{
	    		margin-top: 190px;
	    	}

		</style>
	</head>
	<body>
		<div id="con1" class="container">
			<center>
				<p>
					بسم الله الرحمن الرحيم
				</p>
				
				<h2>
                                        %if struct =='soldier':
                                          
					 <u>أورنيك مرضي صباحي محرر من ${company_name}</u>
                                        %endif
                                        %if struct =='officer':
                                          <u><p>
					محظور
				         </p></u>
					 <u>أورنيك مرضي محرر من ${company_name}</u>
                                        %endif
				</h2>

				<table border="1" class="tb-data">
					<tr class="trh">
					
					<th colspan="1" rowspan="2">
					${type}
					</th>
					
					<th colspan="1" rowspan="2">
					الرتبة
					</th>
					
					<th colspan="1" rowspan="2">
					الاسم
					</th >
					
                                       %if struct =='officer':
					<th colspan="1" rowspan="2">
						الوحدة
					</th>
                                       
					<th colspan="1" rowspan="2">
					نوع المرض
					</th>
					%endif
					
					%if struct =='soldier':
                                       
					<th colspan="2" rowspan="1">
				النوع
					</th>
					%endif
					
					<th colspan="1" rowspan="2">
					قرار الطبيب
					</th>
					</tr>
					
					<tr class="trh">
					%if struct =='soldier':
					
					<th style="text-align:center;padding:0px 20px 0px 20px;">
					 عمل
					</th>
					<th style="text-align:center;padding:0px 20px 0px 20px;">
					مرض
					</th>
					
					%endif
					</tr>
					
					
					<tr style="text-align: top;">
						<td style="text-align:top;padding-bottom:170px;">${code}
						</td>
						<td style="text-align:top;padding-bottom:170px;">${degree}
						</td>
						<td style="text-align:top;padding-bottom:170px;">${name} 
						%if family : 
							<br /> 
							(${family})
						%endif
						</td>
                                               %if struct =='officer':
						<td style="text-align:top;padding-bottom:170px;">${department}
						</td>
                                               %endif
						<td style="text-align:top;padding-bottom:170px;">${illness}
						</td>
						<td style="text-align:top;padding-bottom:170px;">${comment}
						</td>
					</tr>
				</table>
			</center>

                       
			<div class="right-block">
				<table>
				%if struct =='officer':
					<tr>
                                                <td>
							<u>ملحوظات</u>
						</td>				
                                        </tr>

					<tr>
                                                <td>
						يعاد الأورنيك لهذا الطرف خلال 48 ساعة
						</td>				
                                        </tr>
                                        
					<tr>
                                           <td>
				أي قرار راحة طبية أكثر من أسبوع يكون ممهورا بواسطة الأخصائي  
					   </td>					
                                        </tr>
                                        <tr>
						<td>
							المحطة :................................
						</td>
                                        </tr>
					<tr>
					<td>
						التاريخ : .../.../....
					</td>
					</tr>
                                        %endif
                                        %if struct =='soldier':
					<tr>
						<td>
							المحطة :
						</td>
                                        
						<td>
							................................
						</td></tr>
					<tr>
					<td>
						التاريخ : 
					</td>
                                        <td><p>.../.../....</p><td>
					</tr>
					%endif
				</table>
			</div>
		</div>

			<div class="manager-block">
			        <p>....................</p>
			        <p>.....................................</p>
				<p>مدير  ${company_name}</p>
			</div>
%if struct =='soldier':
		<div id="con2" class="container" >
			<center>
				<p>
					بسم الله الرحمن الرحيم
				</p>
				<h2>
					<u>أورنيك مرضي صباحي محرر من ${company_name}</u>
				</h2>

				<table border="1" class="tb-data">
					<tr class="trh">
					
					<th colspan="1" rowspan="2">
					${type}
					</th>
					<th colspan="1" rowspan="2">
					الرتبة
					</th>
					<th colspan="1" rowspan="2">
					الاسم
					</th >
                                       %if struct =='officer':
					<th colspan="1" rowspan="2">
						الوحدة
					</th>
                                       
					<th colspan="1" rowspan="2">
					نوع المرض
					</th>
					%endif
					%if struct =='soldier':
                                       
					<th colspan="2" rowspan="1">
				النوع
					</th>
					%endif
					<th colspan="1" rowspan="2">
					قرار الطبيب
					</th>
					</tr>
					
					
					%if struct =='soldier':
					<tr class="trh">
					<th style="text-align:center;padding:0px 20px 0px 20px;">
					 عمل   
					</th>
					<th style="text-align:center;padding:0px 20px 0px 20px;">
					مرض   
					</th>
					</tr>
					%endif
					
					<tr style="text-align: top;">
						<td style="text-align:top;padding-bottom:170px;">${code}
						</td >
						<td  style="text-align:top;padding-bottom:170px;">${degree}
						</td>
						<td style="text-align:top;padding-bottom:170px;">${name}
						</td>
						%if struct =='officer':
						<td style="text-align:top;padding-bottom:170px;">${department}
						</td>
						%endif
						<td style="text-align:top;padding-bottom:170px;">${illness}
						</td>
						<td style="text-align:top;padding-bottom:170px;">${comment}
						</td>
					</tr>
				</table>
			</center>
<div class="right-block">
				<table>
                                        
					<tr>
						<td>
							المحطة :
						</td>
                                        
						<td>
							................................
						</td></tr>
					<tr>
					<td>
						التاريخ : 
					</td>
                                        <td><p>.../.../....</p><td>
					</tr>
				</table>
			</div>
		</div>


                     
			<div class="manager-block">
			        <p>....................</p>
			        <p>.....................................</p>
				<p>مدير  ${company_name}</p>
			</div>
%endif
		</div>
	</body>
</html>

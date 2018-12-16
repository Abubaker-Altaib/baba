<html dir="rtl" lang="ar">
	<head>
		<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
		<style type="text/css">

			.val{
				border-bottom: 1px black dotted;
			}

			tr{
				margin-top: 10px;
			}
			
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
	    		margin-top: 20px;
	    	}

	    	.trh{
	    		border-bottom: solid 3px black;
	    	}

	    	#con2{
	    		margin-top: 190px;
	    	}
		</style>
	<body>
	 
	%if struct =='soldier':
	<b>
					اورنيك الجيش نمرة 113(1)
	</b>
	    <table width="100%">
		<tr>
			<th >
				قيادة المجموعة
			</th>
			<th class="val">
			${depart}	
			</th>
		</tr>
		<tr>
			<th>
			نمرة
			</th>
			<td class="val">
			
			${code}
			</td>
			<th>
			الرتبة
			</th>
			<td class="val">
				${degree}
			</td>
		</tr>
		<tr>
			<th>
			الاسم
			</th>
			<td class="val">
			${name}
			</td>
		</tr>
		<tr>
			<th>
			تصرح له بالغياب من مركزه والتوجه إلى 
			</th>
			<td class="val">
				${dest}
			</td>
			<th>
			اجازة/مامورية
			<td class="val">
				${perm_code}
			</td>
		</tr>
		<tr>
			<th>
			من محطة
			</th>
			<td class="val">
			
			${source}
			</td>
		</tr>
		<tr>
			<th>
			إلى (المدينة) أو القرية
			</th>
			<td class="val">
			${dest}
			</td>
		</tr>
		<tr>
			<th>
			المنصرفة للسفر من 
			</th>
			<td class="val">
			${source}
			</td>
		</tr>
		<tr>
			<th>
			إلى
			</th>
			<td class="val">
			${dest}
			</td>
			<th>
			(والعودة)
			</th>
			<td class="val">
			${return_place}
			</td>
		</tr>
		<tr>
			<th>
			مدة الإجازة التي منحت (أيام)
			</th>
			<td class="val">
			${days}
			</td>
		</tr>
		<tr>
			<th>
			أيام الطريق التي منحت
			</th>
			<td class="val">
			${road_days}
			</td>
		</tr>
		<tr>
			<th>
			تاريخ الإجازة من
			</th>
			<td class="val">
			${start_date}
			</td>
			<th>
			إلى
			</th>
			<td class="val">
			${end_date}
			</td>
		</tr>
		<tr>
			<th>
			قائد المجموعة
			</th>
			<td class="val">
				
			</td>
			<th>
			ختم الوحدة
			<td class="val">
				
			</td>
		</tr>
	</table>
	<hr />
	<p>
					وضع نوع الإجازة(سنوية مرضية الخ)
					<br />
					اشطب الذي لايسري مفعوله
	<br /><br /><div class="val"></div>
	</p>
	
	
	
		<b>
					اورنيك الجيش نمرة 113(1)
	</b>
	    <table width="100%">
		<tr>
			<th >
				قيادة المجموعة
			</th>
			<th class="val">
			${depart}	
			</th>
		</tr>
		<tr>
			<th>
			نمرة
			</th>
			<td class="val">
			
			${code}
			</td>
			<th>
			الرتبة
			</th>
			<td class="val">
				${degree}
			</td>
		</tr>
		<tr>
			<th>
			الاسم
			</th>
			<td class="val">
			${name}
			</td>
		</tr>
		<tr>
			<th>
			تصرح له بالغياب من مركزه والتوجه إلى 
			</th>
			<td class="val">
				${dest}
			</td>
			<th>
			اجازة/مامورية
			<td class="val">
				${perm_code}
			</td>
		</tr>
		<tr>
			<th>
			من محطة
			</th>
			<td class="val">
			
			${source}
			</td>
		</tr>
		<tr>
			<th>
			إلى (المدينة) أو القرية
			</th>
			<td class="val">
			${dest}
			</td>
		</tr>
		<tr>
			<th>
			المنصرفة للسفر من 
			</th>
			<td class="val">
			${source}
			</td>
		</tr>
		<tr>
			<th>
			إلى
			</th>
			<td class="val">
			${dest}
			</td>
			<th>
			(والعودة)
			</th>
			<td class="val">
			${return_place}
			</td>
		</tr>
		<tr>
			<th>
			مدة الإجازة التي منحت (أيام)
			</th>
			<td class="val">
			${days}
			</td>
		</tr>
		<tr>
			<th>
			أيام الطريق التي منحت
			</th>
			<td class="val">
			${road_days}
			</td>
		</tr>
		<tr>
			<th>
			تاريخ الإجازة من
			</th>
			<td class="val">
			${start_date}
			</td>
			<th>
			إلى
			</th>
			<td class="val">
			${end_date}
			</td>
		</tr>
		<tr>
			<th>
			قائد المجموعة
			</th>
			<td class="val">
				
			</td>
			<th>
			ختم الوحدة
			<td class="val">
				
			</td>
		</tr>
	</table>
	<hr />
	<p>
					وضع نوع الإجازة(سنوية مرضية الخ)
					<br />
					اشطب الذي لايسري مفعوله
	</p>
	%endif
	 %if struct =='officer':
	 <div id="con1" class="container">
			<center>
				
				
				<h2>
				<p>
					بسم الله الرحمن الرحيم
				</p>
				<p>
				<u>محظور</u>
				</p>
				<p>
				<u>قوات الدعم السريع</u>
				</p>
				<u>شهادة إذن</u>
				
				</h2>
			</center>
			
			<div class="right-block" style="font-size:20px;">
				<table><b>
					<tr>
                                                <td>
							رقم البطاقـــــة : ${code}
						</td>				
                                        </tr>

					<tr>
                                                <td>
						الرتبـــــــة :  ${degree}
						</td>				
                                        </tr>
                                        
					<tr>
                                           <td>
				الإســــــم :  ${name}  
					   </td>					
                                        </tr>
                                        <tr>
						<td>
							الوحـــــدة : ${depart}
						</td>
                                        </tr></b>
					<tr>
					<td>
						المذكور أعلاه مُنح إجازة /إذن لمدة ${days} يوم في الفترة من ${start_date} 
						وحتى ${end_date} ليقضيها بالسودان مع إضافة  ${road_days} أيام طريق. عنوان 
						الضابط أثناء إذن/الإجازة
					</td>
					</tr>
                                        
					
					
				</table>
			</div>
	</div>	
	 
	 
	 	<div style="text-align:left">
			        <p>........................................</p>
			        <p>........................................</p>
				<p>........................................</p>
		</div>
                                   <div style="margin-top:120px;">
					<p>
							نسخة إلى :
					</p>

					<p>
						السيد /
					</p>
                                        
					<p>
				بيد الضابط المذكور
				        </p>
                                        <p>
							المحطة :................................
					</p>
					<p>
						التاريخ :.../.../....
                                        </p>
                                        </div>
                                        <div style="margin-top:120px;">
                                        <center>
					<h2>
					<p>
					<u>محظور</u>
					</h2>
					</center>
					</div>
	%endif
                                        
	</body>
</html>

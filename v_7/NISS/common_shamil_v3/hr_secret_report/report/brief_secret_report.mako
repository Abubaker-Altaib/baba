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
			<center>
				<p>
					بسم الله الرحمن الرحيم
				</p>
				<p>
					 التقرير السري المختصر
				</p>
				
			</center>

			<div>
				%for e,i in enumerate(employees):
				<p>
					${e+1}-
				</p>
				<h2>
					البيانات الأساسية
				</h2>
				
				<table style="width:100%; table-layout: fixed;">
					
					<tr>
					<td width="50">
						الإسم:
					</td>
					<td>
					${i['name']}
					</td>
					<td width="50">
						الرتبة:
					</td>
					<td>
					${i['degree']}
					</td>
					</tr>
					<tr>
					<td width="200">
						النمرة العسكرية:
					</td>
					<td>
					${i['code']}
					</td>
					<td width="50">
						الإدارة:
					</td>
					<td>
					${i['department']}
					</td>
					</tr>

				</table>

				<br/>
				%if len(i['qual']) > 0 :
				<h2>
					المؤهلات
				</h2>

				<table style="width:100%; table-layout: fixed;" border="1">
					
					<tr>
					<th>
						#
					</th>
					<th>
						إسم المؤهل
					</th>
					<th>
						التخصص
					</th>
					<th>
						تاريخ المؤهل
					</th>
				    </tr>
				    
					    %for l,q in enumerate(i['qual']):
						<tr>
						<td>
							${l+1}
						</td>
						<td>
							${q['qual_name']}
						</td>
						<td>
							${q['specialization']}
						</td>
						<td>
							${q['qual_date']}
						</td>
						
						</tr>
						%endfor
					
				</table>
				%endif

				<br/>
				%if len(i['training']) > 0 :
				<h2>
					الدورات التدريبية
				</h2>


				<table style="width:100%; table-layout: fixed;" border="1">
					
					
					<tr>
					<th>
						#
					</th>
					<th>
						المكن
					</th>
					<th>
						النوع
					</th>
					<th>
						تاريخ البداية
					</th>
					<th>
						تاريخ النهاية
					</th>
				    </tr>
				    
					    %for c,t in enumerate(i['training']):
						<tr>
						<td>
							${c+1}
						</td>
						<td>
							${t['place']}
						</td>
						<td>
							${t['type']}
						</td>
						<td>
							${t['start_date']}
						</td>
						<td>
							${t['end_date']}
						</td>
						
						</tr>
						%endfor
				</table>
				%endif
				<br/>
				%if len(i['report']) > 0 :
				<h2>
					التقييم
				</h2>


				<table style="width:100%; table-layout: fixed;" border="1">
					
					
					<tr>
					<th>
						#
					</th>
					<th>
						السنة
					</th>
					<th>
						الضابط المباشر
					</th>
					<th>
						تقييم الضابط المباشر
					</th>
					<th>
						الضابط الاعلى
					</th>
					<th>
						تقييم الضابط الأعلى
					</th>
				    </tr>
				    
					    %for s,r in enumerate(i['report']):
						<tr>
						<td>
							${s+1}
						</td>
						<td>
							${r['year']}
						</td>
						<td>
							${r['direct_leader_id']}
						</td>
						<td>
							${r['direct_final_eval']}
						</td>
						<td>
							${r['supreme_leader_id']}
						</td>
						<td>
							${r['supreme_final_eval']}
						</td>
						
						</tr>
						%endfor
				</table>
				%endif
				%endfor
			</div>
			
				
		</div>


	</body>

<footer>


</footer>

</html>

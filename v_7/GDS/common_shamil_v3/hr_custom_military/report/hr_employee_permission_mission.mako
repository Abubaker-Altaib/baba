<html dir="rtl" lang="ar">
	<head>
		<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
		<style type="text/css">
			body{
				text-align: center;
			}
			.val{
				border-bottom: 1px black dotted;
			}

			tr{
				margin-top: 10px;
			}
		</style>
	<body>
	<table width="100%">
		<tr>
			<th class="val" colspan="4">
				${company_name}
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
			*
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
	</table>
	</body>
</html>
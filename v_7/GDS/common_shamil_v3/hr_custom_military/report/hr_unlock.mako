<html dir="rtl" lang="ar">
	<head>
		<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
		<style type="text/css">
			body {
				font-size:22px;
				font-weight: bold;
			}
			ul {
				list-style: none;
			}
			.left-header-block {
				text-align: justify;
				text-align: left;
			}
			.manager-block{
	    		position: relative;
	    		top:200px;
	    	}
	    	.manager-block p {
	    		left: 0;
	    		position: absolute;
	    		bottom: 0;
	    	}

	    	.right-block{
	    		position: relative;
	    		top:0px;
	    		text-align: right;
	    	}
		</style>
	<body>

		%if state != 'approves' :
		<center>
			<h1>عذراا 
		<br />
		لم يتم التصديق النهائي حتى الآن !!
		</h1>	
		</center>
		%else :
		<center>
					بسم الله الرحمن الرحيم
					<br />
					<u>سري للغاية</u>
				</center>
		<div class="left-header-block">
				<p>
				رئاسة الجمهورية
				<br />
				قيادة قوات الدعم السريع
				<br />
				الدائرة الإدارية
				<br />
				النمرة : ${code}
				<br />
				التاريخ : ${date}
				</p>
		</div>
			<div>
				<center>
					<u>
					<h2>تصريح سفر للخارج خاص
						<br />
						بقوات الدعم السريع
					</h2>
					</u>
				</center>
			</div>
			يسمح بالمذكورين بعد بالمغادرة عبر مطار الخرطوم الدولي إلى ${dest} وهم : 
			<ul>
				%for i in enumerate(emps):
					<li>${i[0] + 1 }. السيد / ${i[1]['name']}</li>
				%endfor
			</ul>
			<div class="manager-block">
				<!--p>{source_manger_degree}</p-->
				<p>قائد قوات الدعم السريع</p>
			</div>

			<div class="right-block">
				<ul>
				<li>1. يسلم لمندوب قوات الدعم السريع بالمطار.</li>
				<li>2. صالح لمدة (72) ساعة من تاريخه.</li>
				<li><u>تلفون المطار : ${phone}</u></li>
				</ul>
			</div>
			%endif
	</body>
</html>
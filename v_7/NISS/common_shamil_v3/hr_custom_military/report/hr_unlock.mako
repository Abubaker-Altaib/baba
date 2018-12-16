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

		%if state != 'approved' :
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

				<br />
				جهاز الأمن والمختبرات الوطني
				<br />

				<br />

				<br />
				التاريخ : ${date}
				</p>
		</div>
			<div>
				<center>
					<u>
					<h2>تصريح سفر للخارج خاص
						<br />
						بجهاز الأمن والمختبرات الوطني
					</h2>
					</u>
				</center>
			</div>
			يسمح للمذكور بعد بالمغادرة عبر مطار الخرطوم الدولي إلى ${dest} : 
			<ul>

					<li> السيد / ${emps['name']} صاحب الرقم ${emps['code']}.</li>

			</ul>
			<div class="manager-block">
				<!--p>{source_manger_degree}</p-->
				<p></p>
			</div>

			<div class="right-block">
				<ul>
				<li>1. يسلم لمندوب جهاز الأمن والمختبرات الوطني بالمطار.</li>
				<li>2. صالح لمدة (72) ساعة من تاريخه.</li>

				</ul>
			</div>
			%endif
	</body>
</html>

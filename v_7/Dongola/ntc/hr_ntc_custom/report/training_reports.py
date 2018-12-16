#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import pooler
from report import report_sxw
from datetime import datetime

class training_report(report_sxw.rml_parse):

    globals()['total_inside']=0.0
    
    globals()['total_out']=0.0
    
    globals()['total_external']=0.0
    
    globals()['total_outextr']=0.0
    
    globals()['total_empinternal']=0.0
    
    globals()['total_empexternal']=0.0
    
    def __init__(self, cr, uid, name, context):
	    super(training_report, self).__init__(cr, uid, name, context=context)
	    self.localcontext.update({
		    'time': time,
            'line_emp':self.get_employee_inside_salary,
            'line_inside':self.get_employee_inside,
            'line_outside':self.get_employee_outside,
            'train':self.get_training,
		    'suggest':self.get_sugested,
		    'approve':self.get_sugested_year,
	        'totals':self.get_employee_total,
	        'sumition':self.total_employee,
	        'user':self._get_user,
           })
           
           
    def _get_user(self,data, header=False):
        if header:
            return self.pool.get('res.company').browse(self.cr, self.uid, 1).logo
        else:
            return self.pool.get('res.users').browse(self.cr, self.uid, self.uid).name


    def get_employee_inside_salary(self,data):
	    start = data['form']['start_date']
	    end = data['form']['end_date']
	    salary = data['form']['salary']
	    employ = data['form']['emp']
	    temp=[]
	    if employ:
	        temp=employ
	    else:
	        temp = self.pool.get('hr.employee').search(self.cr,self.uid,[('payroll_id','=',salary[0])])
	    self.cr.execute('''SELECT distinct resource.name as emp_name
	    from hr_employee_training_line line
	    left join  hr_employee emp on (emp.id=line.employee_id)
	    left join  resource_resource resource on (resource.id=emp.resource_id)
	    where emp.payroll_id=%s and emp.id in %s and to_char(line.start_date,'YYYY-mm-dd')>=%s and 
	    to_char(line.end_date,'YYYY-mm-dd')<=%s order by resource.name ''',(salary[0],tuple(temp),start,end))
	    res = self.cr.dictfetchall()
	    return res
	    
    def get_employee_inside(self,data,emp):
	    start = data['form']['start_date']
	    end = data['form']['end_date']
	    self.cr.execute('''SELECT distinct co.name as course_id ,res.name as partner,
	    training.end_date as end, training.start_date as start ,training.training_place as place
	    from hr_employee_training training left join res_partner res on (training.partner_id = res.id)
	    left join hr_training_course co on (training.course_id = co.id)
	    left join hr_employee_training_line line on (line.training_employee_id=training.id)
	    left join  hr_employee emp on (emp.id=line.employee_id)
	    left join  resource_resource resource on (resource.id=emp.resource_id)
	    where training.type ='hr.approved.course' and training.training_place='inside' and 
	    resource.name=%s and 
	    to_char(training.start_date,'YYYY-mm-dd')>=%s and 
	    to_char(training.end_date,'YYYY-mm-dd')<=%s ''',(emp,start,end))
	    res = self.cr.dictfetchall()
	    return res
	    
    def get_employee_outside(self,data,emp):
	    start = data['form']['start_date']
	    end = data['form']['end_date']
	    self.cr.execute('''SELECT distinct co.name as course_id ,res.name as partner,
	    training.end_date as end, training.start_date as start ,training.training_place as place
	    from hr_employee_training training left join res_partner res on (training.partner_id = res.id)
	    left join hr_training_course co on (training.course_id = co.id)
	    left join hr_employee_training_line line on (line.training_employee_id=training.id)
	    left join  hr_employee emp on (emp.id=line.employee_id)
	    left join  resource_resource resource on (resource.id=emp.resource_id)
	    where training.type ='hr.approved.course' and training.training_place='outside' and 
	    resource.name=%s and 
	    to_char(training.start_date,'YYYY-mm-dd')>=%s and 
	    to_char(training.end_date,'YYYY-mm-dd')<=%s ''',(emp,start,end))
	    res = self.cr.dictfetchall()
	    return res
	
    def get_training(self,data):
	    part = data['form']['partner_id']
	    start = data['form']['start_date']
	    end = data['form']['end_date']
	    self.cr.execute('''SELECT distinct co.name as course_id,res.name as partner,  analit.name as anal, training.course_type as course_type,
                		  sum(
                			(CASE WHEN training.type in ('hr.approved.course') THEN
                         		(train_dept.candidate_no)
                      			ELSE 0.0 
                			END)
            		    ) as approved
	    from hr_employee_training training left join hr_training_course co on (training.course_id = co.id)
	    left join hr_employee_training_department train_dept on (train_dept.employee_training_id=training.id)
	    left join res_partner res on (training.partner_id = res.id)
	    left join res_company comp on (training.company_id = comp.id)
	    left join account_analytic_account analit on (comp.training_analytic_account_id=analit.id)
	    where training.type ='hr.approved.course' and 
	    to_char(training.start_date,'YYYY-mm-dd')>=%s and 
	    to_char(training.end_date,'YYYY-mm-dd')<=%s and training.partner_id=%s 
        GROUP BY co.name , res.name ,training.course_type,analit.name order by training.course_type''',(start,end,part[0]))
	    res = self.cr.dictfetchall()
	    return res

    def get_sugested(self,data):
	    year = data['form']['year']
	    self.cr.execute('''SELECT co.name as course, train.course_id, train.course_type as course_type,
			      sum(
	        			(CASE WHEN train.type in ('hr.suggested.course') THEN
		         		(train_dept.candidate_no)
		      			  ELSE 0.0 
	        			END)
			      ) as suggested,
            		  sum(
                			(CASE WHEN train.type in ('hr.approved.course') THEN
                         		(train_dept.candidate_no)
                      			ELSE 0.0 
                			END)
            		  ) as approved
			    FROM hr_employee_training_department train_dept 
			    LEFT JOIN  hr_employee_training train  ON (train_dept.employee_training_id=train.id)
			    LEFT JOIN hr_training_course co ON (train.course_id=co.id)
			     
			    WHERE cast(to_char(train.end_date,'YYYY') as int)=%s and 
			    cast(to_char(train.end_date,'YYYY') as int)=%s GROUP BY co.name,train.course_type,train.course_id order by train.course_type''',(year,year))
	    res = self.cr.dictfetchall()
	    res_rep = []
	    for cc in res:
	        num = 0
	        training = self.pool.get('hr.training.course')
	        train = training.browse(self.cr, self.uid, cc['course_id'])
	        for job in train.job_ids:
	            num += job.no_of_employee
	        dic = {'course_id':cc['course_id'],
	              'course':cc['course'],
	              'course_type':cc['course_type'],
                  'num_job':num,
                  'approved':cc['approved'],
                  'suggested':cc['suggested'],
                  }
	        res_rep.append(dic)
	    return res_rep
	
    def get_sugested_year(self,data):
	    part = data['form']['partner_id']
	    year = data['form']['year']
	    self.cr.execute('''SELECT co.name as course,res.name as partner,train.course_type as course_type,
			      sum(
	        			(CASE WHEN train.type in ('hr.suggested.course') AND cast(to_char(train.end_date,'YYYY') as int)=%s THEN
		         		(train_dept.candidate_no)
		      			  ELSE 0.0 
	        			END)
			      ) as suggested,
            		  sum(
                			(CASE WHEN train.type in ('hr.approved.course') AND cast(to_char(train.end_date,'YYYY') as int)=%s THEN
                         		(train_dept.candidate_no)
                      			ELSE 0.0 
                			END)
            		  ) as approved
            		  
	    FROM hr_employee_training_department train_dept 
	    LEFT JOIN  hr_employee_training train  ON (train_dept.employee_training_id=train.id)
	    LEFT JOIN hr_training_course co ON (train.course_id=co.id)
	    left join res_partner res on (train.partner_id = res.id)
	    WHERE cast(to_char(train.end_date,'YYYY') as int) BETWEEN '%s' and '%s' and train.partner_id=%s
	    GROUP BY co.name , res.name ,train.course_type order by train.course_type ''',(year,year-1,year-1,year,part[0]))
	    res = self.cr.dictfetchall()
	    
	    return res

    def get_employee_total(self,data):
    
	    globals()['total_inside']=0.0
    
	    globals()['total_out']=0.0
        
	    globals()['total_external']=0.0
        
	    globals()['total_outextr']=0.0
        
	    globals()['total_empinternal']=0.0
        
	    globals()['total_empexternal']=0.0
        
	    start = data['form']['start_date']
	    end = data['form']['end_date']
	    self.cr.execute('''SELECT distinct  co.name as course_id,  plan.type_plan as place_plan,
	    training.training_place as place_approve, (sum(line.final_amount)+training.trainer_cost) as cost,
	    count(line.employee_id) as emp
	    from hr_employee_training training
	    left join hr_training_course co on (training.course_id = co.id)
	    left join hr_training_plan plan on (training.plan_id = plan.id)
	    left join hr_employee_training_line line on (line.training_employee_id=training.id)
	    left join hr_training_enrich en on (training.enrich_id=en.id)
	    where training.type ='hr.approved.course' and 
	    to_char(training.start_date,'YYYY-mm-dd')>=%s and 
	    to_char(training.end_date,'YYYY-mm-dd')<=%s GROUP BY co.name,plan.type_plan,training.training_place, training.trainer_cost''',(start,end))
	    res = self.cr.dictfetchall()
	    res_rep = []
	    for lines in res:
	        if lines['place_plan']== 'external':
	            globals()['total_empexternal']+=lines['emp']
	            
	        if lines['place_plan']== 'internal':
	            globals()['total_empinternal']+=lines['emp']
	        
	        if lines['place_plan']== 'internal' and lines['place_approve']== 'inside':
	            if lines['cost'] !=None:
	                globals()['total_inside'] += lines['cost']
	            dic= {'course_id':lines['course_id'],
	                  'inside_inside':lines['cost'],
	                  'inside_outside':False,
	                  'outside_inside':False,
	                  'outside_outside':False,
	                  'emp_inside':lines['emp'],
	                  'emp_outside':False,}
	            res_rep.append(dic)
	            
	        if lines['place_plan']== 'internal' and lines['place_approve']== 'outside':
	            if lines['cost'] !=None:
	                globals()['total_out'] += lines['cost']
	            dic= {'course_id':lines['course_id'],
	                  'inside_outside':lines['cost'],
	                  'inside_inside':False,
	                  'outside_inside':False,
	                  'outside_outside':False,
	                  'emp_inside':lines['emp'],
	                  'emp_outside':False,}
	            res_rep.append(dic)
	            
	        if lines['place_plan']== 'external' and lines['place_approve']== 'inside':
	            if lines['cost'] !=None:
	                globals()['total_external'] += lines['cost']
	            dic= {'course_id':lines['course_id'],
	                  'outside_inside':lines['cost'],
	                  'outside_outside':False,
	                  'inside_outside':False,
	                  'inside_inside':False,
	                  'emp_inside':False,
	                  'emp_outside':lines['emp'],}
	            res_rep.append(dic)
	            
	        if lines['place_plan']== 'external' and lines['place_approve']== 'outside':
	            if lines['cost'] !=None:
	                globals()['total_outextr'] += lines['cost']
	            dic= {'course_id':lines['course_id'],
	                  'outside_outside':lines['cost'],
	                  'outside_inside':False,
	                  'inside_outside':False,
	                  'inside_inside':False,
	                  'emp_inside':False,
	                  'emp_outside':lines['emp'],}
	            res_rep.append(dic)
	    return res_rep
    
    def total_employee(self):
        dic = []
        dic.append({'total_inside':globals()['total_inside'],
                'total_out':globals()['total_out'],
                'total_external':globals()['total_external'],
                'total_outextr':globals()['total_outextr'],
                'total_empinternal':globals()['total_empinternal'],
                'total_empexternal':globals()['total_empexternal'],
               })
        return dic
	    

report_sxw.report_sxw('report.training.report', 'hr.employee.training','addons/hr_ntc_custom/report/training_reports.rml', parser=training_report, header=False)

report_sxw.report_sxw('report.training.report.file', 'hr.employee.training','addons/hr_ntc_custom/report/training_reports_train.rml', parser=training_report, header=False)



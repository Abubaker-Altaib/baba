import time
import pooler
#import rml_parse
import copy
from report import report_sxw
import pdb
import re

class suggest_vs_approved(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(suggest_vs_approved, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
            'suggest':self._get_emp,
            'dept':self._get_dept,
		})

	def _get_dept(self,data):

         self.cr.execute('''SELECT distinct dept.name as dep , dept.id as d_id
							FROM 
							hr_employee_training_department train_dept
							LEFT JOIN  hr_employee_training train  ON (train_dept.employee_training_id=train.id)
							LEFT JOIN hr_department dept ON (train_dept.department_id=dept.id)
							WHERE 
							train.plan_id = %s AND 
							train.training_place=%s ''',(data['plan_id'][0],data['traing_place']))
        
         res= self.cr.dictfetchall()
         return res

	def _get_emp(self,dept,data):
	
		self.cr.execute('''SELECT 
         						  co.code as code,
         						  co.name as name, 
         						  train.course_id,
         						  train.plan_id,
         						  train.training_place,
         						  train_dept.department_id,
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
         						   
							FROM 
								hr_employee_training_department train_dept
								LEFT JOIN  hr_employee_training train  ON (train_dept.employee_training_id=train.id)
								LEFT JOIN hr_training_course co ON (train.course_id=co.id)

							WHERE 
								train.plan_id = %s AND 
								train.training_place=%s AND 
								train_dept.department_id=%s
								GROUP BY train.plan_id,train.training_place,train_dept.department_id,train.course_id,co.code,co.name''',
								(data['plan_id'][0],data['traing_place'],dept))
		res = self.cr.dictfetchall()
    
		return res



    
report_sxw.report_sxw('report.suggest_vs_approved', 'hr.employee.training',
	'addons/hr_training/report/suggest_vs_approved.rml', parser=suggest_vs_approved, header=True)

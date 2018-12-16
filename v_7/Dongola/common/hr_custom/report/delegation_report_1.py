import time
import pooler
#import rml_parse
import copy
from report import report_sxw
import pdb
import re

class delegation_report_1(report_sxw.rml_parse):
       _name = 'report.emp.delegation'
       def __init__(self, cr, uid, name, context):
		super(delegation_report_1, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
                        '_get_emp':self._get_emp,
               })

       def _get_emp(self,ids):
           p = pooler.get_pool(self.cr.dbname).get('hr.employee.delegation')
           #s=p.search(self.cr, self.uid,[('employee_id','=',ids)])
           emp_id=p.browse(self.cr, self.uid,[ids])[0]
           #print "jjjj",emp_id.category_id.id
           emp=emp_id.category_id.id
           #print "emp",emp
           
           self.cr.execute('select r.name as emp,d.start_date AS date,d.delegated_from AS from,d.delegated_to AS to,d.end_date AS end_date from hr2_delegation_category As cat join hr2_basic_emp_delegation As d on (cat.id=d.category_id) join hr_employee as e on (d.employee_id=e.id) left join resource_resource AS r on (e.resource_id=r.id) where cat.id=%s',(emp,)) 
           res = self.cr.dictfetchall()
           #print "resdd",res
           return res
      
        
       

report_sxw.report_sxw('report.delegation.report.1', 'hr.employee.delegation',
	'hr_process/report/delegation_report_1.rml', parser=delegation_report_1, header=True)

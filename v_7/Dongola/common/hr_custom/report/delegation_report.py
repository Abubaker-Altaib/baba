import time
import pooler
#import rml_parse
import copy
from report import report_sxw
import pdb
import re

class delegation_report(report_sxw.rml_parse):
       _name = 'report.emp.delegation'
       def __init__(self, cr, uid, name, context):
		super(delegation_report, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
                        'lines':self.lines,
                        '_get_emp':self._get_emp,
               })

       def lines(self,form):
	result = []
        periods = []
        emp = pooler.get_pool(self.cr.dbname).get('hr.delegation.category')
        

        result = emp.browse(self.cr,self.uid, form['category_id'])
        print "result",result
        return result
       def _get_emp(self,data,i):
           category=[]
           
           #print "category",c
           
           self.cr.execute('select e.sequence,e.emp_code as code,r.name as emp,d.start_date AS date,d.delegated_from AS from,d.delegated_to AS to,d.end_date AS end_date from hr_delegation_category As cat join hr_employee_delegation As d on (cat.id=d.category_id) join hr_employee as e on (d.employee_id=e.id) left join resource_resource AS r on (e.resource_id=r.id) where cat.id=%s order by e.sequence',(i,)) 
           res = self.cr.dictfetchall()
           #print "resdd",res
           return res
      
        
       

report_sxw.report_sxw('report.delegation.report', 'hr.employee.delegation',
	'addons/hr_process/report/delegation_report.rml', parser=delegation_report, header=True)

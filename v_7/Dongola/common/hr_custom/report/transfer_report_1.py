import time
import pooler
#import rml_parse
import copy
from report import report_sxw
import pdb
import re

class transfer_report_1(report_sxw.rml_parse):
       _name = 'report.transfer.report.1'
       def __init__(self, cr, uid, name, context):
		super(transfer_report_1, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
                        '_get_emp':self._get_emp,

               })
       
    
       
       def _get_emp(self,ids):

           #print "ids",ids
           p = pooler.get_pool(self.cr.dbname).get('hr.process.archive')
           #s=p.search(self.cr, self.uid,[('employee_id','=',ids)])
           emp_id=p.browse(self.cr, self.uid,[ids])[0]
           #print "jjjj",emp_id.employee_id.id
           emp=emp_id.employee_id.id
           comp=emp_id.company_id.id
           #print "emp",emp
           
           
           self.cr.execute('SELECT c.name as company,d.name as department,ar.transfer_date AS date,r.name AS employee_name FROM hr2_basic_transfer_archive AS ar left join hr_employee AS e on (ar.employee_id=e.id) left join  resource_resource AS r on (e.resource_id=r.id) left join hr_department as d  on (ar.department_id=d.id) left join res_company as c on (ar.company_id=c.id) where r.id=%s and c.id=%s order by ar.transfer_date'%(emp,comp)) 
           res = self.cr.dictfetchall()
           #print "transfer",res
           return res
      

report_sxw.report_sxw('report.transfer.report.1', 'hr.process.archive',
	'addons/hr_process/report/transfer_report_1.rml', parser=transfer_report_1, header=True)

import time
from report import report_sxw
import calendar
import datetime

class emp1_delegation(report_sxw.rml_parse):
       _name = 'report.employee.delegation'
       def __init__(self, cr, uid, name, context):
		super(emp1_delegation, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
                        '_get_emp':self._get_emp,
               })

       def _get_emp(self,data):
           c= data['form']['company_id']
           self.cr.execute('SELECT  e.emp_code AS employee_code,resource_resource.name AS employee_name,ed.delegated_to AS delegated_to,ed.delegated_from AS delegated_from,ed.start_date AS start_date,ed.end_date AS end_date,dc.name AS category_name FROM hr2_basic_emp_delegation ed,hr_employee AS e,resource_resource, res_company r, hr2_delegation_category dc where resource_resource.company_id= %s'%(c)) 
           res = self.cr.dictfetchall()
           return res
        

report_sxw.report_sxw('report.emp1.delegation', 'hr.employee.delegation',
	'addons/hr_process/report/emp_delegation.rml', parser=emp1_delegation, header=True)

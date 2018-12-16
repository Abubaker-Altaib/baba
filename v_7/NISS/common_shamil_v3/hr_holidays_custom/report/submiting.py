import time
import re
import pooler
from report import report_sxw
import calendar
import datetime


class submiting(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(submiting, self).__init__(cr, uid, name, context)
        self.localcontext.update({
           'line2':self._getdep,
           'line3':self._getemp,              
        })

    def _getdep(self,data):
        self.cr.execute('SELECT name AS dep_name From hr_department where id=%s'%(data['form']['dep_id'][0]))
        res = self.cr.dictfetchall()
        return res

    def _getemp(self,data):
        self.cr.execute('''
select distinct 
resource_resource."name" AS emp_name,
hr_salary_degree."name" AS degree_name,
hr_job.name  AS job,
hr_employee.work_location AS office
from
  public.hr_employee, 
  public.hr_salary_degree, 
  public.resource_resource, 
  public.hr_job

where
 hr_employee.degree_id = hr_salary_degree.id AND
 hr_employee.resource_id = resource_resource.id AND
 hr_employee.job_id = hr_job.id AND
 hr_employee.id=%s
'''%(data['form']['name_id'][0]))
        res = self.cr.dictfetchall()
        
        return res

report_sxw.report_sxw('report.submiting', 'hr.holidays', 'addons/hr_holidays_custom/report/submiting.rml' ,parser=submiting ,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

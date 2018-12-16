import time
import re
import pooler
from report import report_sxw
import calendar
import datetime
#from hr_common_report import hr_common_report
#from amount_to_text_ar import amount_to_text as amount_to_text_ar
from base_custom import amount_to_text_ar
from openerp.osv import osv, fields, orm
import decimal_precision as dp
from tools.translate import _
class subsidization_notifi(report_sxw.rml_parse):#, hr_common_report
 def __init__(self, cr, uid, name, context):
        super(subsidization_notifi, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'pars':self._pars,
            'employee':self._get_emp,

        })
    
        self.cr = cr
        self.uid = uid
        self.context = context

 def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('hr.subsidy').browse(self.cr, self.uid, ids, self.context):
            if not obj.acc_number:          
		       raise osv.except_osv(_('Error!'), _('You can not print notification. This subsidy is not transferred yet!')) 

        return super(subsidization_notifi, self).set_context(objects, data, ids, report_type=report_type)

 def _pars(self,u):

        res = amount_to_text_ar.amount_to_text(u)

        return res

 def _get_emp(self,h):
        
        i=h.id
        self.cr.execute(''' 
select e.emp_code as code, e.employment_date as emp_date, r.name AS emp_name,
dg.name as degree ,jo.name AS job,dp.name as dept , pdp.name as par_dept

from hr_employee as e
left join resource_resource as r on (e.resource_id=r.id)
left join hr_salary_degree as dg on (e.degree_id=dg.id)
left join hr_job AS jo on (e.job_id=jo.id) 
left join hr_department AS dp on (e.department_id=dp.id)
left join hr_department AS pdp on (dp.parent_id=pdp.id)
left join hr_payroll_main_archive AS a on (e.id=a.employee_id)

where e.id=%s 
Group by e.emp_code,e.employment_date,r.name,dg.name,jo.name,pdp.name,dp.name,e.id

'''%(i))
        nw_res=self.cr.dictfetchall()
        print nw_res,"nw_res"
        return nw_res
    

report_sxw.report_sxw('report.subsidization.notifi', 'hr.subsidy', 'hr_subsidy/report/subsidization_notifi.rml' ,parser=subsidization_notifi ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

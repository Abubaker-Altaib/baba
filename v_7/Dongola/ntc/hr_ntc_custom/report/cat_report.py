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

class cat_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
	super(cat_report, self).__init__(cr, uid, name, context=context)
	self.localcontext.update({
		'time': time,
                'categ':self.get_cat,
                'emp':self._get_emp,
       })

    def get_cat(self,data):
	result = []
        cat_id= data['form']['cat_id']
	emp = pooler.get_pool(self.cr.dbname).get('hr.employee.category')
	result = emp.browse(self.cr,self.uid, cat_id)
	return result

    def _get_emp(self,data,cat_id):
        company_id= data['form']['company_id']

	self.cr.execute("SELECT jo.name as job,e.emp_code AS emp_code,r.name AS emp_name FROM  hr_employee e left join resource_resource r on (e.resource_id=r.id) left join employee_category_rel cat on (e.id=cat.emp_id) left join hr_employee_category ca on (ca.id=cat.category_id) left join hr_job as jo on (e.job_id=jo.id) left join res_company co on (r.company_id=co.id) left join hr_salary_degree as deg on (e.degree_id=deg.id) WHERE e.state='approved' and ca.id = %s and co.id=%s order by deg.sequence",(cat_id,company_id[0])) 

	res = self.cr.dictfetchall()
	return res

report_sxw.report_sxw('report.cat.report', 'hr.employee.category','addons/hr_ntc_custom/report/cat_report.rml', parser=cat_report, header=True)


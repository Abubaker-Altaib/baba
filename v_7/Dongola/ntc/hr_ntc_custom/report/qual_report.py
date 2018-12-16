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

class qual_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(qual_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'qual':self.get_qual,
            'lines':self._get_data,
        })
    
    def get_qual(self,data):
	result = []
        qual_id= data['form']['qual_id']
	emp = pooler.get_pool(self.cr.dbname).get('hr.qualification')
	result = emp.browse(self.cr,self.uid, qual_id)
	return result
        
    def _get_data(self,data,qual_id):
        cat=data['form']['cat_id']

        self.cr.execute("SELECT resource_resource.name AS employee_name,q.qual_date AS start,q.organization AS organization FROM hr_employee_qualification AS q left join hr_qualification b on (q.emp_qual_id=b.id) left join hr_employee e on (q.employee_id=e.id) left join resource_resource on (e.resource_id=resource_resource.id) left join hr_salary_degree as deg on (e.degree_id=deg.id) WHERE e.state='approved' and b.id=%s and b.parent_id=%s order by deg.sequence",(qual_id,cat[0],)) 
   
        res = self.cr.dictfetchall()
        return res

report_sxw.report_sxw('report.qual.report', 'hr.employee.qualification', 'addons/hr_ntc_custom/report/qual_report.rml' ,parser=qual_report, header=False)


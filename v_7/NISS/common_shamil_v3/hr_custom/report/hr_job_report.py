# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp import tools
from report.interface import report_rml
from openerp.tools.translate import _
from openerp.report import report_sxw

class report_hr_job(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(report_hr_job, self).__init__(cr, uid, name, context)
        self.info = {'levels':0, 'company':'','title':''}
        self.localcontext.update({
            'main': self.create_xml,
            'info': self.get_info,

        })
    def get_info(self,data):
        if  data['form']['report_type'] == 'jobs':
            self.info['title']="Based On Jobs"
        else:
            self.info['title']="Based On Departments Managers"
        self.info['company']=u'company' in data['form'].keys() and  data['form']['company'] and data['form']['company'][1]   or ""  
        #print">>>>>>>>>>>>>>>>>>self.info" , data['form']['company'][1]
        return self.info



    def create_xml(self, data):
        append_where = "  "
        if  data['form']['report_type'] == 'jobs':
            label = {u'a1': u'القسم', u'a2': u'المصدق',u'a3': u'المشغول',u'a4': u'الشاغر',u'a51': u'العدد','level':4}                         
            if data['form']['company']:
                append_where += " and j.company_id=%s  " % str(data['form'].get('company')[0])
            if data['form']['job_ids']:
                append_where +=  str(" and j.id in (%s) "   % ','.join(map(str, data['form']['job_ids']))) 
            self.cr.execute(''' SELECT 2 as level, j.id as id, j.name as a1, no_of_employee as a2,
				    no_of_recruitment as a3 ,  expected_employees as4   FROM   hr_job as j 
	                left join department_jobs l on (j.id = l.job)
	                where j.id is not null
	                ''' + append_where)
            res = self.cr.dictfetchall() 
            result = []
            for r in res: 
                self.cr.execute(''' SELECT 3 as level,min(d.name)   as a1,
	                    sum(no_emp) as a2,  count(e.id) as a3
	                    FROM    hr_job as j
	                    left join hr_employee e on (j.id = e.job_id)
	                    left join hr_department d  on (d.id = e.department_id)
	                    left join department_jobs l on (j.id = l.job and d.id = l.department_id)
	                    where j.id=%s group by d.id  ''' ,(r['id'],) )

                jobs = self.cr.dictfetchall() 
                if jobs: result  += [r] + jobs  
        else:

            label = {u'a1': u'القسم',u'a2': u'المدير', 'level':4}  
            append_where = data['form']['department_ids'] and \
                    " where d.id in (%s) " % ','.join(map(str, data['form']['department_ids'])) or "  "
            self.cr.execute("  SELECT 3 as level, r.name as a2,  d.name as a1 FROM\
		            hr_department d \
                    left join hr_employee h on(h.id= d.manager_id)\
		            left join resource_resource r on (h.resource_id = r.id) " +   append_where  )
            result = self.cr.dictfetchall()                
        return  [label] + (result)


 
report_sxw.report_sxw('report.hr.employee.jobs', 'hr.employee', 'hr_custom/report/report/hr_employee_report.mako',parser=report_hr_job)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

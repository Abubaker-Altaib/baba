# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.report import report_sxw

class  injury_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(injury_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'deps':self._get_department,
            'lines':self._get_line,
            'has_lines':self.has_lines,
             })

    def _get_department(self,data):
        return self.pool.get('hr.department').browse(self.cr, self.uid, data['department_id'])

    def _get_line(self,data, dept_id):
        self.cr.execute('''SELECT 
                      resource_resource.name  as name, 
                      hr_injury.injury_date as date , 
                      hr_injury.inability_amount as amount , 
                      (SELECT SUM(treatment_amount) FROM hr_injury_treatment WHERE injury_id=hr_injury.id) as t_amount , 
                      hr_injury.inability_percentage as percentage,
                      hr_employee.emp_code as code,
                      hr_job.name as job_name,
                      hr_injury_type.name as t_name
                FROM 
                      public.hr_injury,
                      public.resource_resource ,
                      public.hr_job,
                      public.hr_employee,
                      public.hr_injury_type
                WHERE 
                      hr_employee.resource_id=resource_resource.id
                      and public.hr_injury.employee_id=public.hr_employee.id  
                      and public.hr_injury.injury_type =public.hr_injury_type.id  
                      and public.hr_injury.department_id = %s
                      and hr_employee.job_id= hr_job.id and  injury_date >= %s and injury_date <=%s ''',(dept_id,str(data['date_from']),str(data['date_to']),))
        res = self.cr.dictfetchall()
        self.has_lines = res and True or False
        return res

    def has_lines(self):
        return self.has_lines
    
report_sxw.report_sxw('report.injury.report', 'hr.injury', 'addons/hr_injury/report/injury_report.rml' ,parser=injury_report ,header=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

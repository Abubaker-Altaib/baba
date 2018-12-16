# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
import calendar
from datetime import datetime
import pooler
from openerp.tools.translate import _



def to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()


class salary_suspend(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.count = 0
        self.context = context
        super(salary_suspend, self).__init__(cr, uid, name, context)
        self.h_deps_ids = []
        self.localcontext.update({
            'all_len': self._get_all_len,
            'lines': self._get_lines,
            'get_count': self._get_count,
            'to_arabic': self._to_arabic,
        })
    
    def _to_arabic(self, data):
        key = _(data)
        key = key == 'suspend' and u'إيقاف' or key
        key = key == 'resume' and u'فك' or key
        return key

    def _get_all_len(self, data):
        employee_id = data['form']['employee_id']
        department_id = data['form']['department_id']
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        company_id = data['form']['company_id']
        suspend_type = data['form']['suspend_type']
        job_id = data['form']['job_id']
        degree_id = data['form']['degree_id']


        clouses = False

        if employee_id:
            employee_id = employee_id[0]
            if clouses:
                clouses += " and salary_suspend.employee_id="+str(employee_id)
            if not clouses:
                clouses = "salary_suspend.employee_id="+str(employee_id)

        if suspend_type:
            if clouses:
                clouses += " and salary_suspend.suspend_type='"+str(suspend_type)+"'"
            if not clouses:
                clouses = "salary_suspend.suspend_type='"+str(suspend_type)+"'"
        
        if department_id:
            department_id = department_id[0]
            if clouses:
                clouses += " and dep.id="+str(department_id)
            if not clouses:
                clouses = "dep.id="+str(department_id)

        if company_id:
            company_id = company_id[0]
            if clouses:
                clouses += " and salary_suspend.company_id="+str(company_id)
            if not clouses:
                clouses = "salary_suspend.company_id="+str(company_id)

        if start_date:
            if clouses:
                clouses += " and salary_suspend.suspend_date>='"+str(start_date)+"'"
            if not clouses:
                clouses = "salary_suspend.suspend_date>='"+str(start_date)+"'"

        if end_date:
            if clouses:
                clouses += " and salary_suspend.suspend_date<='"+str(end_date)+"'"
            if not clouses:
                clouses = "salary_suspend.suspend_date<='"+str(end_date)+"'"
        if job_id:
            job_id = job_id[0]
            if clouses:
                clouses += " and emp.job_id="+str(job_id)
            if not clouses:
                clouses = "emp.job_id="+str(job_id)
        
        if degree_id:
            degree_id = degree_id[0]
            if clouses:
                clouses += " and emp.degree_id="+str(degree_id)
            if not clouses:
                clouses = "emp.degree_id="+str(degree_id)

        readable_emp_ids = self.pool.get('hr.employee').search(self.cr, self.uid, [])
        if readable_emp_ids:
            readable_emp_ids = readable_emp_ids + readable_emp_ids
            readable_emp_ids = tuple(readable_emp_ids)
            if clouses:
                clouses += " and emp.id in"+str(readable_emp_ids)
            if not clouses:
                clouses = "emp.in in"+str(readable_emp_ids)    

        query = """select salary_suspend.suspend_type,salary_suspend.suspend_date,emp.otherid,emp.name_related,
                    deg.name as deg_name,job.name as job_name,dep.name as dep_name 
                    from hr2_basic_salary_suspend_archive salary_suspend 
                    left join hr_employee emp on (salary_suspend.employee_id=emp.id) 
                    left join hr_salary_degree deg on (emp.degree_id=deg.id) 
                    left join hr_job job on(job.id = emp.job_id) 
                    left join hr_department dep on(dep.id = emp.department_id) 
                    """

        if clouses:
            query += "where "+clouses
        query += " ORDER BY deg.sequence DESC,emp.promotion_date,LPAD(emp.otherid,20,'0')"

        self.cr.execute(query)
        res = self.cr.dictfetchall()

        self.all_data = res
        
            
        return len(self.all_data)

    def _get_lines(self):
        return self.all_data

    def _get_count(self):
        self.count = self.count + 1
        return self.count


report_sxw.report_sxw('report.hr.salary_suspend_all.report', 'hr2.basic.salary.suspend.archive',
                      'addons/hr_custom_military/report/salary_suspend_report_all.mako', parser=salary_suspend, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

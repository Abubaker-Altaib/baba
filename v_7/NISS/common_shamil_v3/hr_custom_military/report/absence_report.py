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


class absence(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.count = 0
        self.context = context
        super(absence, self).__init__(cr, uid, name, context)
        self.h_deps_ids = []
        self.localcontext.update({
            'all_len': self._get_all_len,
            'lines': self._get_lines,
            'get_count': self._get_count,
            'to_arabic': self._to_arabic,
        })
    
    def _to_arabic(self, data):
        key = _(data)
        key = key == 'v_good' and 'very good' or key
        key = key == 'u_middle' and 'under middle' or key
        if self.context and 'lang' in self.context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                self.cr, self.uid, [('module','=', 'hr_custom_military'),('type','=', 'selection'),('src','ilike', key), ('lang', '=', self.context['lang'])], context=self.context)
            translation_recs = translation_obj.read(
                self.cr, self.uid, translation_ids, [], context=self.context)
            key = translation_recs and translation_recs[0]['value'] or key
        
        return key

    def _get_all_len(self, data):
        employee_id = data['form']['employee_id']
        department_id = data['form']['department_id']
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        company_id = data['form']['company_id']
        in_absence = data['form']['in_absence']
        first_week = data['form']['first_week']
        second_week = data['form']['second_week']
        third_week = data['form']['third_week']

        job_id = data['form']['job_id']
        degree_id = data['form']['degree_id']


        clouses = "absence.type='absence' "

        # if third_week:
        #     second_week = first_week = in_absence = True
        

        clouses += " and absence.in_absence="+str(in_absence)
        clouses += " and absence.first_week="+str(first_week)
        clouses += " and absence.second_week="+str(second_week)
        clouses += " and absence.third_week="+str(third_week)
        if employee_id:
            employee_id = employee_id[0]
            clouses += " and absence.employee_id="+str(employee_id)
            

        if department_id:
            department_id = department_id[0]
            clouses += " and absence.department_id="+str(department_id)

        
        if company_id:
            company_id = company_id[0]
            clouses += " and absence.company_id="+str(company_id)

        if start_date:
            clouses += " and absence.date_from>='"+str(start_date)+"'"

        if end_date:
            clouses += " and absence.date_to<='"+str(end_date)+"'"

        if job_id:
            job_id = job_id[0]
            clouses += " and emp.job_id="+str(job_id)

        
        if degree_id:
            degree_id = degree_id[0]
            clouses += " and emp.degree_id="+str(degree_id)
            
        readable_emp_ids = self.pool.get('hr.employee').search(self.cr, self.uid, [])
        if readable_emp_ids:
            readable_emp_ids = readable_emp_ids + readable_emp_ids
            readable_emp_ids = tuple(readable_emp_ids)
            if clouses:
                clouses += " and emp.id in"+str(readable_emp_ids)
            if not clouses:
                clouses = "emp.in in"+str(readable_emp_ids) 

        query = """select absence.date_from,absence.date_to,absence.in_absence,absence.first_week,
		            absence.second_week,absence.third_week,
		            emp.otherid,emp.name_related,
                    deg.name as deg_name,job.name as job_name, dep.name as dep_name 
                    from hr_holidays_absence absence 
                    left join hr_employee emp on (absence.employee_id=emp.id) 
                    left join hr_salary_degree deg on (emp.degree_id=deg.id) 
                    left join hr_job job on(job.id = emp.job_id) 
                    left join hr_department dep on(dep.id = absence.department_id) 
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


report_sxw.report_sxw('report.hr.absence.report', 'hr.holidays.absence',
                      'addons/hr_custom_military/report/absence_report.mako', parser=absence, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

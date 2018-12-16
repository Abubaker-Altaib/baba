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


class escape_status(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.count = 0
        self.context = context
        super(escape_status, self).__init__(cr, uid, name, context)
        self.h_deps_ids = []
        self.localcontext.update({
            'all_len': self._get_all_len,
            'lines': self._get_lines,
            'get_count': self._get_count,
            'to_arabic': self._to_arabic,
        })
    
    def _to_arabic(self, data):
        key = _(data)
        if self.context and 'lang' in self.context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                self.cr, self.uid, [('module','=', 'hr_custom_military'),('type','=', 'selection'),('src','ilike', key), ('lang', '=', self.context['lang'])], context=self.context)
            translation_recs = translation_obj.read(
                self.cr, self.uid, translation_ids, [], context=self.context)
            key = translation_recs and translation_recs[0]['value'] or key
        
        return key

    def _get_all_len(self, data):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        company_id = data['form']['company_id']
        service_end = data['form']['service_end']
        courted = data['form']['courted']
        job_id = data['form']['job_id']
        degree_id = data['form']['degree_id']
        department_id = data['form']['department_id']

        clouses = False

        if job_id:
            job_id = job_id[0]
            if clouses:
                clouses += " and emp.job_id="+str(job_id)
            if not clouses:
                clouses = "emp.job_id="+str(job_id)

            who_not_take_clouses = " job_id="+str(job_id)
        
        if degree_id:
            degree_id = degree_id[0]
            if clouses:
                clouses += " and emp.degree_id="+str(degree_id)
            if not clouses:
                clouses = "emp.degree_id="+str(degree_id)

        if service_end:
            if clouses:
                clouses += " and esc.service_end="+str(service_end)
            if not clouses:
                clouses = "esc.service_end="+str(service_end)
        
        if not service_end:
            if clouses:
                clouses += " and esc.service_end!=True"
            if not clouses:
                clouses = "esc.service_end!=True"

        if courted:
            if clouses:
                clouses += " and esc.courted="+str(courted)
            if not clouses:
                clouses = "esc.courted="+str(courted)
        
        if not courted:
            if clouses:
                clouses += " and esc.courted!=True"
            if not clouses:
                clouses = "esc.courted!=True"

        
        if company_id:
            company_id = company_id[0]
            if clouses:
                clouses += " and esc.company_id="+str(company_id)
            if not clouses:
                clouses = "esc.company_id="+str(company_id)

        if date_from:
            if clouses:
                clouses += " and esc.date_from<='"+str(date_from)+"' and esc.date_to>='"+str(date_from)+"'"
            if not clouses:
                clouses = "esc.date_from<='"+str(date_from)+"' and esc.date_to>='"+str(date_from)+"'"

        if date_to:
            if clouses:
                clouses += " and esc.date_from>='"+str(date_to)+"'"
            if not clouses:
                clouses = "esc.date_to<='"+str(date_to)+"'"
        
        if department_id:
            department_id = department_id[0]
            if clouses:
                clouses += " and emp.department_id = "+str(department_id)
            if not clouses:
                clouses = "emp.department_id = "+str(department_id)
        
        readable_emp_ids = self.pool.get('hr.employee').search(self.cr, self.uid, [])
        if readable_emp_ids:
            readable_emp_ids = readable_emp_ids + readable_emp_ids
            readable_emp_ids = tuple(readable_emp_ids)
            if clouses:
                clouses += " and emp.id in"+str(readable_emp_ids)
            if not clouses:
                clouses = "emp.in in"+str(readable_emp_ids) 

        query = """select esc.date_to as escap_date,esc.service_end_date,esc.courte_date,emp.otherid,emp.name_related,
                    deg.name as deg_name,job.name as job_name 
                    from hr_holidays_absence esc 
                    left join hr_employee emp on (esc.employee_id=emp.id) 
                    left join hr_salary_degree deg on (emp.degree_id=deg.id) 
                    left join hr_job job on(job.id = emp.job_id) 
                    where esc.type='escape'
                    """

        if clouses:
            query += " and "+clouses
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


report_sxw.report_sxw('report.hr.escape_status.report', 'hr.holidays.absence',
                      'addons/hr_custom_military/report/escape_status_report.mako', parser=escape_status, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

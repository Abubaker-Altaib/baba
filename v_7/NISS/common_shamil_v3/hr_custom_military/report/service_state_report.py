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


def to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()


class service_state(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.count = 0
        super(service_state, self).__init__(cr, uid, name, context)
        self.h_deps_ids = []
        self.localcontext.update({
            'all_len': self._get_all_len,
            'lines': self._get_lines,
            'to_arabic': self._to_arabic,
            'get_count': self._get_count,
        })

    def _get_all_len(self, data):
        self.emp_obj = self.pool.get('hr.employee')
        self.hr_department_obj = self.pool.get('hr.department')

        type = data['form']['type']

        department_id = data['form']['department_id']

        job_id = data['form']['job_id']
        degree_id = data['form']['degree_id']
        company_id = data['form']['company_id']
        service_state_id = data['form']['service_state_id']

        with_childs = data['form']['with_childs']

        domain = []
        
        if type == 'specific':
            domain = [('state','=','approved')]
        if type == 'takeout':
            domain = [('state','=','refuse')]
            
            
        if department_id:
            department_id = department_id[0]
            if not with_childs:
                domain.append(('department_id','=',department_id))
            if with_childs:
                domain += ('|',('department_id','=',department_id),('department_id','child_of',department_id))

        if job_id:
            job_id = job_id[0]
            domain.append(('job_id','=',job_id))
        
        if degree_id:
            degree_id = degree_id[0]
            domain.append(('degree_id','=',degree_id))
        
        if company_id:
            company_id = company_id[0]
            domain.append(('company_id','=',company_id))
        
        if service_state_id:
            service_state_id = service_state_id[0]
            domain.append(('service_state_id','=',service_state_id))
        print "...................domain",domain
        self.emp_ids = self.emp_obj.search(self.cr, self.uid, domain)
        self.all_data = self.emp_obj.browse(self.cr, self.uid, self.emp_ids)
        self.emp_obj.actual_duration_computation(self.cr, self.uid, self.emp_ids )
        # for emp in self.all_data:
        #     try:
        #         emp.actual_duration_computation()
        #     except:
        #         pass
            
        return len(self.all_data)

    def _get_lines(self):
        return self.all_data

    def _to_arabic(self, data):
        name = (data == 'specific' and unicode('معين', 'utf-8') ) or \
         (data == 'takeout' and unicode('شطب', 'utf-8')) or ""
        return name

    def _get_count(self):
        self.count = self.count + 1
        return self.count


report_sxw.report_sxw('report.hr.service_state.report', 'hr.employee',
                      'addons/hr_custom_military/report/service_state_report.mako', parser=service_state, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

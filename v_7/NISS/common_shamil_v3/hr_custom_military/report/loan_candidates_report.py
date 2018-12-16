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


class loan_candidates(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.count = 0
        super(loan_candidates, self).__init__(cr, uid, name, context)
        self.h_deps_ids = []
        self.localcontext.update({
            'all_len': self._get_all_len,
            'lines': self._get_lines,
            'get_count': self._get_count,
        })

    def _get_all_len(self, data):
        self.emp_obj = self.pool.get('hr.employee')
        self.hr_department_obj = self.pool.get('hr.department')
        self.hr_employee_loan_obj = self.pool.get('hr.employee.loan')

        loan_id = data['form']['loan_id'][0]
        num = data['form']['num']

        self.cr.execute('''select emp.id from hr_employee emp 
        left join hr_loan loan on (loan.id = %s) 
        left join hr_salary_degree degree on (degree.id = emp.degree_id) 
        where emp.id not in (select loan.employee_id from hr_employee_loan loan where loan_id=%s) 
        and emp.total_service_years >= loan.year_employment and emp.state='approved' order by degree.sequence desc,emp.promotion_date,emp.otherid limit %s;'''% (
            loan_id, loan_id, num)    )
        self.emp_ids = self.cr.fetchall()
        self.emp_ids = [x[0] for x in self.emp_ids]

        self.all_data = self.emp_obj.browse(self.cr, self.uid, self.emp_ids)


        return len(self.all_data)

    def _get_lines(self):
        return self.all_data

    def _get_count(self):
        self.count = self.count + 1
        return self.count


report_sxw.report_sxw('report.hr.loan_candidates.report', 'hr.employee',
                      'addons/hr_custom_military/report/loan_candidates_report.mako', parser=loan_candidates, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

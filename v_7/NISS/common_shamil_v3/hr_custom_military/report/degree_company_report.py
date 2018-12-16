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


class degree_company(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.count = 0
        self.name = ''
        self.selection = {'dept':'', 'job':'', 'degree':''}
        super(degree_company, self).__init__(cr, uid, name, context)
        self.h_deps_ids = []
        self.localcontext.update({
            'all_len': self._get_all_len,
            'lines': self._get_lines,
            'get_count': self._get_count,
            'select_data': self.get_selection,

        })

    def _get_all_len(self, data):

        self.emp_obj = self.pool.get('hr.employee')

        company_id = data['form']['company_id']

        job_id = data['form']['job_id']
        gender = data['form']['gender']
        #degree_id = data['form']['degree_id'][0]
        degrees_ids = data['form']['degrees_ids']

        department_id = data['form']['department_id']

        #domain = [('state','=','approved'), ('degree_id','=',degree_id)]
        domain = [('state','=','approved')]

        if company_id:
            company_id = company_id[0]
            domain.append( ('company_id','=',company_id) )
        
        if job_id:
            job_id = job_id[0]
            domain.append( ('job_id','=',job_id) )
        
        if gender:
            domain.append( ('gender','=',gender) )

        if department_id:
            if data['form']['included_department']:
                domain.append( ('department_id','child_of',[department_id[0]]) )
            else:
                domain.append( ('department_id','=',department_id[0]) )
            self.selection['dep'] = department_id[1]

        if degrees_ids:
            domain.append( ('degree_id','in',degrees_ids) )
        


        self.emp_ids = self.emp_obj.search(self.cr, self.uid, domain)
        self.all_data = self.emp_obj.browse(self.cr, self.uid, self.emp_ids)
        
            
        return len(self.all_data)

    def _get_lines(self):
        return self.all_data

    def _get_count(self):
        self.count = self.count + 1
        return self.count

    def get_selection(self,data):
        
        self.selection = {'dept':u'كل الادارات', 'job':u'كل الوظائف', 'degree':u'كل الرتب'}

        company_id = data['form']['company_id']

        job_id = data['form']['job_id']

        degrees_ids = data['form']['degrees_ids']

        department_id = data['form']['department_id']

        if company_id:
            company_id = company_id[0]
        
        if job_id:
            # job_id = job_id[0]
            self.selection['job'] = job_id[0]

        if department_id:
            if data['form']['included_department']:
                self.selection['dep'] = department_id[1] + u' و ادراتها الفرعية'

            else:

                self.selection['dep'] = department_id[1]

        # if degree_id:
        #     self.selection['degree'] = degree_id[1]

        return [self.selection]


report_sxw.report_sxw('report.hr.degree_company.report', 'hr.employee',
                      'addons/hr_custom_military/report/degree_company_report.mako', parser=degree_company, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

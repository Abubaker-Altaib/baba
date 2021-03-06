# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.report import report_sxw

class payroll_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(payroll_report, self).__init__(cr, uid, name, context)
        self.total = {'basic_salary':0.0,'total_allowance':0.0, 'total_deduction':0.0,'total_loans':0.0,'net':0.0,
                      'allowances_tax':0.0,'tax':0.0,'zakat':0.0}
        self.localcontext.update({
            'time': time,
            'payroll':self.payroll,
            'total': self._total, 
        })
    
    def payroll(self,data):
        company= data['form']['company_id']
        payroll_ids= data['form']['payroll_ids']
        self.cr.execute(
            'SELECT emp.id,emp.emp_code AS code, emp.name_related AS name, '\
            'pay.basic_salary AS basic_salary,pay.total_allowance AS total_allowance,pay.total_deduction AS total_deduction,sum(ll.final_amount) AS total_loans,'\
            'pay.allowances_tax AS allowances_tax,pay.tax AS tax,pay.zakat AS zakat,'\
            'pay.net AS net '\
            'FROM hr_payroll_main_archive  pay '\
            'LEFT JOIN hr_employee  emp ON (pay.employee_id = emp.id) '\
            'LEFT JOIN hr_salary_degree deg on (deg.id= emp.degree_id)'\
            'LEFT JOIN hr_loan_archive ll on (ll.main_arch_id= pay.id)'\
            'WHERE pay.month  =%s'\
            'AND pay.year=%s ' \
            'AND pay.company_id in %s'\
            'AND pay.scale_id in %s'\
            'AND pay.in_salary_sheet = True '\
	    'group by emp.id,pay.basic_salary,pay.total_allowance ,pay.total_deduction,pay.allowances_tax,pay.tax,pay.zakat,pay.net,deg.sequence '
            'ORDER BY  deg.sequence,emp.name_related' , (data['form']['month'],data['form']['year'],tuple(company),tuple(payroll_ids)))    
        res = self.cr.dictfetchall()
        self.total['basic_salary']=self.total['total_allowance']=self.total['total_deduction']=self.total['total_loans']=self.total['net'] =0.0
        self.total['allowances_tax']=self.total['tax']=self.total['zakat']=0.0
        co = 0
        for r in res:
          self.total['basic_salary'] += r['basic_salary']

          #r['total_allowance'] += r['basic_salary']
          #self.total['total_allowance'] += r['total_allowance']

          '''self.total['total_loans'] += r['total_loans']
          self.total['allowances_tax'] += r['allowances_tax']
          self.total['tax'] += r['tax']
          self.total['zakat'] += r['zakat']'''
          
          '''self.total['total_deduction'] += r['total_deduction']'''

          r['net'] = r['total_allowance'] - r['total_deduction']
          '''self.total['net'] += r['net']'''

          if r['total_allowance'] == r['total_deduction'] == r['net'] == 0:
              del res[co]
          co += 1
        self.total['total_allowance'] = 0.0
        self.total['total_deduction']  = 0.0
        for r in res:
            if r['total_loans']:
                r['total_deduction'] = r['total_deduction'] + r['total_loans']
            self.total['total_allowance'] += r['total_allowance']
            self.total['total_deduction'] += r['total_deduction']
            r['net'] = r['total_allowance'] - r['total_deduction']
        self.total['net'] = self.total['total_allowance'] - self.total['total_deduction'] 



        return res

    def _total(self):
        return [self.total]  
   
report_sxw.report_sxw('report.payroll.report', 'hr.payroll.main.archive', 'addons/hr_payroll_custom/report/payroll_listing.rml' ,parser=payroll_report)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:




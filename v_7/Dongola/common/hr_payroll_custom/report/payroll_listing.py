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
            'company_id': self.company_id, 
        })
    def company_id(self,data):
      companys=self.pool.get('res.company').browse(self.cr, self.uid, data['form']['company_id'])
      return companys
    
    def payroll(self,data,company):
        #company= data['form']['company_id']
        payroll_ids= data['form']['payroll_ids']
        self.cr.execute(
            'SELECT emp.id,emp.emp_code AS code, emp.name_related AS name, '\
            'pay.basic_salary AS basic_salary,deg.sequence ,pay.total_allowance AS total_allowance,pay.total_deduction AS total_deduction,pay.total_loans AS total_loans,'\
            'pay.allowances_tax AS allowances_tax,pay.tax AS tax,pay.zakat AS zakat,'\
            'pay.net AS net '\
            'FROM hr_payroll_main_archive  pay '\
            'LEFT JOIN hr_employee  emp ON (pay.employee_id = emp.id) '\
            'LEFT JOIN hr_salary_degree deg on (deg.id= emp.degree_id) '\
            'WHERE pay.month  =%s'\
            'AND pay.year=%s ' \
            'AND pay.company_id = %s'\
            'AND pay.scale_id in %s'\
            'AND pay.in_salary_sheet = True '\
            'AND deg.id = emp.degree_id  '\
            'ORDER BY deg.sequence , emp.name_related' , (data['form']['month'],data['form']['year'],company.id,tuple(payroll_ids)))    
        res = self.cr.dictfetchall()
        self.total['basic_salary']=self.total['total_allowance']=self.total['total_deduction']=self.total['total_loans']=self.total['net'] =0.0
        self.total['allowances_tax']=self.total['tax']=self.total['zakat']=0.0
        for r in res:
          self.total['basic_salary'] += r['basic_salary']
          self.total['total_allowance'] += r['total_allowance']
          self.total['total_deduction'] += r['total_deduction']
          self.total['total_loans'] += r['total_loans'] or 0
          self.total['allowances_tax'] += r['allowances_tax']
          self.total['tax'] += r['tax']
          self.total['zakat'] += r['zakat']
          self.total['net'] += r['net']

        return res

    def _total(self):
        return [self.total]  
   
report_sxw.report_sxw('report.payroll.report', 'hr.payroll.main.archive', 'addons/hr_payroll_custom/report/payroll_listing.rml' ,parser=payroll_report)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



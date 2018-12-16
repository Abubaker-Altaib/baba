# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.report import report_sxw

class salary_list_total(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(salary_list_total, self).__init__(cr, uid, name, context)
        self.total = {'sheat1':0.0, 'sheat2':0.0,'deductions':0.0,'taxs':0.0,'net':0 ,'loans' : 0.0}
        self.localcontext.update({
            'time': time,
            'process': self._process,
            'total': self._total,
        })

    def _process(self,data):
  
        year =  data['form']['year']
        month = data['form']['month']
        self.cr.execute('''SELECT emp.id,emp.name_related AS emp_name,emp.emp_code AS emp_code, 
                           (pm.tax + pm.allowances_tax) AS tax,pm.total_deduction AS deductions,pm.total_loans AS loans,pm.basic_salary AS basic,pm.net as net,
                           sum(
                            (CASE WHEN ad.pay_sheet = 'first' AND
                                       ad.name_type = 'allow'
                                  THEN 
                                      rch.amount
                                  ELSE 0.0 
                            END)
                            ) + pm.basic_salary as sheet1_amount,
                           sum(
                            (CASE WHEN ad.pay_sheet = 'second' AND
                                       ad.name_type = 'allow'
                                  THEN
                                       (rch.amount-tax_deducted)
                                  ELSE 0.0 
                            END)
                            ) as sheet2_amount

                           FROM hr_allowance_deduction_archive rch
                           LEFT JOIN hr_allowance_deduction ad ON(ad.id=rch.allow_deduct_id)
                           LEFT JOIN hr_payroll_main_archive pm ON (rch.main_arch_id=pm.id) 
                           LEFT JOIN hr_employee emp ON (pm.employee_id=emp.id)
                           LEFT JOIN hr_salary_degree deg on (deg.id= emp.degree_id)
                           WHERE pm.in_salary_sheet = TRUE AND
                           pm.year = %s AND
                           pm.month = %s 
                           GROUP BY
                           emp.id,emp.name_related ,emp.emp_code, 
                           pm.tax ,pm.allowances_tax,pm.total_deduction ,pm.total_loans,pm.basic_salary,pm.net,
                           deg.sequence
                           ORDER BY  deg.sequence,emp.name_related''',(year,month))
        res = self.cr.dictfetchall()
        self.total['sheat1']=self.total['sheat2']=self.total['deductions']=self.total['loans'] =self.total['taxs'] =self.total['net'] =0.0
        for r in res:
            r['deductions'] -= r['tax']
            self.total['sheat1'] += r['sheet1_amount']
            self.total['sheat2'] += r['sheet2_amount']
            self.total['deductions'] += r['deductions']
            self.total['loans'] += r['loans'] or 0.0
            self.total['taxs'] += r['tax']
            self.total['net'] += r['net']
        return res
    
    def _total(self):
        return [self.total]  

 
        
report_sxw.report_sxw('report.salary_list_total', 'hr.payroll.main.archive', 'addons/hr_payroll_custom/report/salary_list_total.rml' ,parser=salary_list_total)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



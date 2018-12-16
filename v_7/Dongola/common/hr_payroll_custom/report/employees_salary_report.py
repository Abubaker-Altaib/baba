# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp.tools.translate import _


class employees_salary(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(employees_salary, self).__init__(cr, uid, name, context)
        self.total = {'basic':0.0, 'tax':0.0,'loan_total':0.0,
                      'allow_first_total':0.0,'allow_second_total':0.0,
                      'deduct_total':0.0,'net':0.0}
        
        self.localcontext.update({
            'time': time,
            'process':self.process,
            'total':self._total,
        
        })

    def process(self,data,employee_id):
        
        info = {'loans':[],'allow_first':[],'allow_second':[],'deduct':[]}
        
        main_archive_obj=self.pool.get('hr.payroll.main.archive')

        main_arch_ids= main_archive_obj.search(self.cr, self.uid,[('employee_id', '=',employee_id),
                                                                  ('month', '=', data['form']['month']),
                                                                  ('year', '=', data['form']['year']),('in_salary_sheet', '=',True)])
        if not main_arch_ids:
            raise osv.except_osv(_('Error'), _('No  Data Found ...'))
        
        for record in main_archive_obj.browse(self.cr, self.uid,main_arch_ids):
            self.total['tax'] = record.tax + record.allowances_tax
            self.total['basic'] = record.basic_salary
            self.total['loan_total'] =record.total_loans
            self.total['net'] = record.net
        # allowances/deductions
        self.cr.execute('SELECT round(m.amount,2) AS amount,b.name AS name, b.name_type, b.pay_sheet '\
        'FROM  hr_payroll_main_archive  p '\
        'LEFT JOIN hr_allowance_deduction_archive  m on (m.main_arch_id=p.id)'\
        'LEFT JOIN hr_allowance_deduction b on (m.allow_deduct_id=b.id) '\
        'WHERE p.id IN %s '\
        'ORDER BY b.sequence',(tuple(main_arch_ids),))    
        res = self.cr.dictfetchall()

        for r in res:
            if r['amount'] is None: r['amount'] = 0.0
            if r['name_type']=='allow':
                if r['pay_sheet'] == 'first':
                    info['allow_first'].append(r)
                    self.total['allow_first_total'] += r['amount']
                else:
                    info['allow_second'].append(r)
                    self.total['allow_second_total'] += r['amount']
            else:
                info['deduct'].append(r)
                self.total['deduct_total'] += r['amount']
            
        #  loans     
        self.cr.execute('SELECT round(m.loan_amount,2) AS amount,b.name AS name '\
        'FROM  hr_payroll_main_archive AS p '\
        'left join hr_loan_archive AS m on (m.main_arch_id=p.id) '\
        'left join hr_employee_loan b on (m.loan_id=b.id)'\
        'WHERE p.id IN %s',(tuple(main_arch_ids),)) 
        info['loans'] = self.cr.dictfetchall() 
            
        return [info]
    
    def _total(self):
        return self.total

report_sxw.report_sxw('report.employees.salary', 'hr.employee', 'addons/hr_payroll_custom/report/employees_salary_report.rml' ,parser=employees_salary, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

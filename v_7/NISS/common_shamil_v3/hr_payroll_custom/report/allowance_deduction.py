# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.report import report_sxw

class hr_allowance_deduction_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(hr_allowance_deduction_report, self).__init__(cr, uid, name, context)
        self.total = {'amount':0.0, 'tax_deducted':0.0,'imprint':0.0,'net':0.0,'count':0}
        self.localcontext.update({
            'time': time,
            'process':self.process,
            'get_allow_deduct':self.get_allow_deduct,
            'total': self._total,
            'basic': self._basic,
            'loan_total': self._loan_total,
            'total_total': self._total_total,
          
        })  
    def get_allow_deduct(self,data):
        form=data['form']
        report_obj=self.pool.get('hr.allowance.deduction.report')
        if form['by']=='allow':
            allow_deduct_obj = self.pool.get('hr.allowance.deduction')
            if form['allow_deduct_ids']: 
                ids = form['allow_deduct_ids']
            else:
               domain=report_obj.onchange_data(self.cr,self.uid,[],[(6, 0, form['company_id'])],[(6, 0, form['payroll_ids'])],form['type'],form['in_salary_sheet'],form['pay_sheet'])
               ids = allow_deduct_obj.search(self.cr,self.uid, domain['domain']['allow_deduct_ids'])
            result = allow_deduct_obj.browse(self.cr,self.uid, ids)
            
        else:
            emp_obj = self.pool.get('hr.employee')
            if form['employee_ids']:
                ids=form['employee_ids'] 
            else:
                domain=report_obj.onchange_data(self.cr,self.uid,[],[(6, 0, form['company_id'])],[(6, 0, form['payroll_ids'])],form['type'],form['in_salary_sheet'],form['pay_sheet'])
                ids = emp_obj.search(self.cr,self.uid, domain['domain']['employee_ids'])
            result = emp_obj.browse(self.cr,self.uid, ids)
        return result

    def process(self, data ,by_id):
        where_clause = ''
        if data['form']['by']=='allow':
            where_clause='and adr.allow_deduct_id=%s '
        else:
            where_clause='and pm.employee_id=%s '
        
        self.cr.execute(
            'SELECT adr.imprint AS imprint,adr.tax_deducted AS tax_deducted,round(adr.amount,2) AS amount,'\
            'adr.type AS type, emp.name_related AS employee,emp.emp_code AS code, ad.name AS name, ad.code AS sequence, '\
            '(adr.amount-adr.tax_deducted) AS net '\
            'FROM hr_allowance_deduction_archive adr ' \
            'LEFT JOIN hr_allowance_deduction ad ON (adr.allow_deduct_id=ad.id) ' \
            'LEFT JOIN hr_payroll_main_archive pm ON (adr.main_arch_id=pm.id) '\
            'LEFT JOIN hr_employee emp ON (pm.employee_id=emp.id)' \
            'WHERE pm.month =%s and pm.year =%s and emp.payroll_state=%s '\
            'and pm.company_id IN %s'\
            + where_clause +
            'ORDER BY ad.sequence,emp.sequence',(data['form']['month'],data['form']['year'],data['form']['state_id'],tuple(data['form']['company_id']),by_id)) 
        res = self.cr.dictfetchall()
        self.total['amount']=self.total['tax_deducted']=self.total['imprint']=self.total['net'] =0.0
        self.total['count']=0
        for r in res:
          self.total['amount'] += r['amount']
          self.total['tax_deducted'] += r['tax_deducted']
          #self.total['imprint'] += r['imprint']
          self.total['imprint'] += r['tax_deducted']
          self.total['net'] += r['net']
        self.total['count'] = len(res)
        return res


    def _total(self):
        return [self.total]

    def _loan_total(self, data):
        self.cr.execute('SELECT sum(m.loan_amount) AS amount, b.name AS name '\
'FROM  hr_payroll_main_archive AS p '\
 'left join hr_loan_archive AS m on (m.main_arch_id=p.id) '\
 'left join hr_employee_loan b on (m.loan_id=b.id) '\
  'LEFT JOIN hr_employee emp ON (m.employee_id=emp.id)'\
  'WHERE   p.month=%s and  p.year=%s and p.company_id IN %s and m.loan_amount is not null and emp.payroll_state=%s'\
  'GROUP BY b.name ',(data['form']['month'],data['form']['year'],tuple(data['form']['company_id']) ,data['form']['state_id']) )
        res = self.cr.dictfetchall()
        return res


    def _basic(self, data):
        self.cr.execute('SELECT sum(basic_salary) as basic '\
            'from hr_payroll_main_archive pm '\
            'LEFT JOIN hr_employee emp ON (pm.employee_id=emp.id)'\
            'WHERE pm.month =%s and pm.year =%s '\
            'and pm.company_id IN %s and emp.payroll_state=%s ',(data['form']['month'],data['form']['year'],tuple(data['form']['company_id']),data['form']['state_id'])) 
        res = self.cr.dictfetchall()
        #print">>>>>>>>>>>>>>>>>>" ,res
        return res

    def _total_total(self, data):
        self.cr.execute('SELECT sum(net) as net '\
            'from hr_payroll_main_archive pm '\
            'LEFT JOIN hr_employee emp ON (pm.employee_id=emp.id)'\
            'WHERE pm.month =%s and pm.year =%s '\
            'and pm.company_id IN %s and emp.payroll_state=%s ',(data['form']['month'],data['form']['year'],tuple(data['form']['company_id']),data['form']['state_id'])) 
        res = self.cr.dictfetchall()
        return res

report_sxw.report_sxw('report.allowance.deduction', 'hr.allowance.deduction.archive', 'addons/hr_payroll_custom/report/allowance_deduction.rml' ,parser=hr_allowance_deduction_report)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

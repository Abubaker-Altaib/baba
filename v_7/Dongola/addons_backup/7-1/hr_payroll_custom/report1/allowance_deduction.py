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
        globals()['total_amount']=0.0
        globals()['total_net']=0.0
        globals()['total_tax']=0.0
        globals()['total_imprint']=0.0 
        globals()['total_basic']=0.0
        super(hr_allowance_deduction_report, self).__init__(cr, uid, name, context)
        self.total = {'amount':0.0, 'loans_amount' : 0, 'tax_deducted':0.0,'imprint':0.0,'net':0.0,'count':0}
        self.localcontext.update({
            'time': time,
            'process':self.process,
            'get_allow_deduct':self.get_allow_deduct,
            'total': self._total,
            'total_amount': self._total_amount,
            'loan_total': self._loan_total,
            'total_basic': self.total_salary,  
        }) 
        #print "############# " , self._loan_total()
     
    
    def total_salary(self, data):
        if data['form']['by']=='allow' and data['form']['type']!='deduct':
            self.cr.execute(
                '''SELECT  SUM(pm.basic_salary) AS basic_salary ,count(employee_id) as emp
                FROM hr_payroll_main_archive pm 
                WHERE pm.month =%s and pm.year =%s and pm.in_salary_sheet =%s ''',(data['form']['month'],data['form']['year'],data['form']['in_salary_sheet'],)) 
            res = self.cr.dictfetchall()
            globals()['total_basic']= res[0]['basic_salary']
            for x in res:
                x['emp'] = int(x['emp'])

        return res

    def get_allow_deduct(self,data):
        globals()['total_amount']=0.0
        globals()['total_net']=0.0
        globals()['total_tax']=0.0
        globals()['total_imprint']=0.0
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
            '(adr.amount - adr.tax_deducted - adr.imprint) AS net '\
            'FROM hr_allowance_deduction_archive adr ' \
            'LEFT JOIN hr_allowance_deduction ad ON (adr.allow_deduct_id=ad.id) ' \
            'LEFT JOIN hr_payroll_main_archive pm ON (adr.main_arch_id=pm.id) '\
            'LEFT JOIN hr_employee emp ON (pm.employee_id=emp.id)' \
            'WHERE pm.month =%s and pm.year =%s '\
            'and pm.company_id IN %s'\
            'and pm.in_salary_sheet=%s '\
            + where_clause +
            'ORDER BY ad.sequence,emp.sequence',(data['form']['month'],data['form']['year'],tuple([data['form']['company_id'][0]]),data['form']['in_salary_sheet'],by_id)) 
        res = self.cr.dictfetchall()
        self.total['amount']=self.total['tax_deducted']=self.total['imprint']=self.total['net'] =0.0
        self.total['count']=0
        self.total['total'] = {}
        for r in res:
          #r['amount'] = r['type'] == 'deduct' and -r['amount'] or r['amount']
          r['imprint'] = r['imprint'] and r['imprint'] or 0.0
          r['amount'] = r['amount'] and r['amount'] or 0.0
          r['tax_deducted'] = r['tax_deducted'] and r['tax_deducted'] or 0.0
          r['net'] = r['net'] and r['net'] or 0.0
          self.total['amount'] += not data['form']['by']=='allow' and (r['type'] == 'deduct' and -r['amount'] or r['amount']) or r['amount']
          globals()['total_amount'] += r['type'] == 'deduct' and -r['amount'] or r['amount']
          globals()['total_tax'] += r['type'] == 'deduct' and -r['tax_deducted'] or r['tax_deducted']
          globals()['total_net'] += r['type'] == 'deduct' and -r['net'] or r['net']
          globals()['total_imprint'] += r['type'] == 'deduct' and r['imprint'] and -r['imprint'] or r['imprint']
          
          self.total['tax_deducted'] += r['tax_deducted']
          self.total['imprint'] += r['imprint']
          #self.total['imprint'] += r['tax_deducted']
          self.total['net'] += not data['form']['by']=='allow' and (r['type'] == 'deduct' and -r['net'] or r['net']) or r['net']
        self.total['count'] = len(res)
        self.total['total']['amount_total'] = data['form']['type']=='deduct' and globals()['total_amount'] > 0.0 and -globals()['total_amount'] or globals()['total_amount']
        self.total['total']['amount_total'] = abs(self.total['total']['amount_total'])
        self.total['total']['amount_total'] += globals()['total_basic']
        self.total['total']['total_tax'] = data['form']['type']=='deduct' and globals()['total_tax'] > 0.0 and -globals()['total_tax'] or globals()['total_tax']
        self.total['total']['total_net'] = data['form']['type']=='deduct' and globals()['total_net'] > 0.0 and -globals()['total_net'] or globals()['total_net']
        self.total['total']['total_imprint'] = data['form']['type']=='deduct' and globals()['total_imprint'] > 0.0 and -globals()['total_imprint'] or globals()['total_imprint']


        return res


    def _loan_total(self, data):
        self.cr.execute('SELECT sum(m.loan_amount) AS amount, b.name AS name , count(m.employee_id) AS counts '\
'FROM  hr_payroll_main_archive AS p '\
 'left join hr_loan_archive AS m on (m.main_arch_id=p.id) '\
 'left join hr_employee_loan b on (m.loan_id=b.id) '\
  'LEFT JOIN hr_employee emp ON (m.employee_id=emp.id)'\
  'WHERE   p.month=%s and  p.year=%s and p.company_id IN %s and m.loan_amount is not null '\
  'GROUP BY b.name ',(data['form']['month'],data['form']['year'],tuple([data['form']['company_id'][0]])) )
        res = self.cr.dictfetchall()
        sums = 0
        
        for i in res :
            sums += i['amount']
        if data['form']['by']=='deduct': self.total['loans_amount'] =  self.total['loans_amount'] + sums
        else : self.total['loans_amount'] = self.total['loans_amount'] = self.total['loans_amount'] - sums
        return res

    def _total(self):
        #self.total['total']['amount_total'] += self.total['loans_amount']
        return [self.total]

    def _total_amount(self):
        #self.total['total']['amount_total'] += self.total['loans_amount']
        return self.total['total'] 
        #return self.total['amount_total']

   

report_sxw.report_sxw('report.allowance.deduction', 'hr.allowance.deduction.archive', 'addons/hr_payroll_custom/report/allowance_deduction.rml' ,parser=hr_allowance_deduction_report)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

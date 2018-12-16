# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################rrrrrrrrr
import time
from openerp.report import report_sxw

class payroll_listing_department(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(payroll_listing_department, self).__init__(cr, uid, name, context)
        self.total = {'basic_salary':0.0,'total_allowance':0.0, 'total_deduction':0.0,'total_loans':0.0,'net':0.0,
                      'allowances_tax':0.0,'tax':0.0,'zakat':0.0}
        self.total_net = {'net':0}
        self.t = {'t':0}
        self.localcontext.update({
            'time': time,
            'payroll':self.payroll,
            'department':self.get_department,
            'salary':self.get_salary,
            'total':self._total,
        })

    def get_salary(self,data , dep_id=None):
            #self.total_net = {'net':0}
            payroll=tuple(data['form']['payroll_ids'])
            lis=[]
            self.cr.execute(''' SELECT name as salary_name,id as salary_id from hr_salary_scale where id in %s''',(payroll,))
            salary = self.cr.dictfetchall()
            return salary 

    def get_department(self,data):
            department=tuple(data['form']['department_ids'])
            lis=[]
            self.cr.execute(''' SELECT name as dep_name,id as dep_id from hr_department_payroll where id in %s''',(department,))
            do = self.cr.dictfetchall()
            return do

    def payroll(self,data,lis,payroll):
        in_salary_sheet = True
        type=data['form']['type']
        
        allowance_deduction=data['form']['allowance_deduction']
        if type == 'salary':
            self.cr.execute(
                'SELECT d.id,d.name AS degree ,emp.id,emp.emp_code AS code,emp.otherid as otherid,emp.promotion_date, emp.name_related AS name, '\
                'pay.basic_salary AS basic_salary,pay.total_allowance AS total_allowance,pay.total_deduction AS total_deduction,pay.total_loans AS total_loans,'\
                'pay.allowances_tax AS allowances_tax,pay.tax AS tax,pay.zakat AS zakat,'\
                'pay.net AS net '\
                'FROM hr_payroll_main_archive  pay '\
                'LEFT JOIN hr_employee  emp ON (pay.employee_id = emp.id) '\
                'LEFT JOIN hr_department_payroll dep ON (dep.id=pay.payroll_employee_id)'\
                'LEFT JOIN hr_salary_scale sal ON (pay.scale_id = sal.id)'\
                'LEFT JOIN hr_salary_degree d ON (emp.degree_id = d.id)'\
                'WHERE pay.month  =%s'\
                'AND pay.year=%s ' \
                #'AND pay.scale_id in %s'\
                'AND pay.in_salary_sheet = True '\
                'AND dep.id = %s'\
                'AND sal.id = %s'\
                'ORDER BY  d.id desc ,emp.promotion_date,emp.otherid' , (data['form']['month'],data['form']['year'],lis,payroll))


        if type == 'addendum':
            if allowance_deduction:
                allowance_deduction = allowance_deduction[0]
                self.cr.execute(
                    'SELECT d.id,d.name AS degree ,emp.id,emp.emp_code AS code,emp.otherid as otherid,emp.promotion_date, emp.name_related AS name, '\
                    'pay.basic_salary AS basic_salary,pay.total_allowance AS total_allowance,pay.total_deduction AS total_deduction,pay.total_loans AS total_loans,'\
                    'pay.allowances_tax AS allowances_tax,pay.tax AS tax,pay.zakat AS zakat,'\
                    'pay.net AS net '\
                    'FROM hr_payroll_main_archive  pay '\
                    'LEFT JOIN hr_employee  emp ON (pay.employee_id = emp.id) '\
                    'LEFT JOIN hr_department_payroll dep ON (dep.id=pay.payroll_employee_id)'\
                    'LEFT JOIN hr_salary_scale sal ON (pay.scale_id = sal.id)'\
                    'LEFT JOIN hr_salary_degree d ON (emp.degree_id = d.id)'\
                    'LEFT JOIN hr_allowance_deduction_archive ada on (pay.id=ada.main_arch_id)'\
                    'WHERE pay.month  =%s'\
                    'AND pay.year=%s ' \
                    #'AND pay.scale_id in %s'\
                    'AND pay.in_salary_sheet = False '\
                    'AND ada.allow_deduct_id =%s '
                    'AND dep.id = %s'\
                    'AND sal.id = %s'\
                    'ORDER BY  d.id desc ,emp.promotion_date,emp.otherid' , (data['form']['month'],data['form']['year'],allowance_deduction,lis,payroll))
        res = self.cr.dictfetchall()
        self.total['basic_salary']=self.total['total_allowance']=self.total['total_deduction']=self.total['total_loans']=self.total['net'] =0.0
        self.total['allowances_tax']=self.total['tax']=self.total['zakat']=0.0
        for r in res:
          self.total['basic_salary'] += int(r['basic_salary'])
          self.total['total_allowance'] += int(r['total_allowance'])
          self.total['total_deduction'] += int(r['total_deduction'])
          self.total['total_loans'] += int(r['total_loans'] and r['total_loans'] or '0' )
          self.total['allowances_tax'] += int(r['allowances_tax'])
          self.total['tax'] += int(r['tax'])
          #self.total['zakat'] += r['zakat']
          self.total['net'] += (r['net'])





        return res

    def _total(self):
        return [self.total]  

    
   
report_sxw.report_sxw('report.payroll.listing.department', 'hr.payroll.main.archive', 'addons/hr_payroll_custom_niss/report/payroll_listing_department.rml' ,parser=payroll_listing_department,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



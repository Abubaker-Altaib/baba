# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################rrrr
import time
from openerp.report import report_sxw
import pooler

class payroll_department(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.sum = 0.0
        super(payroll_department, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'process': self._process,
            'department':self.get_department,
            'get_sum':self.get_sum,
            'to_arabic': self._to_arabic,
        })
    
    def _to_arabic(self, data):
        key = data == 'khartoum' and u'الخرطوم' or u'الولايات'        
        return key

    
    def get_department(self,data):
            department=tuple(data['form']['department_ids'])
            lis=[]
            self.cr.execute(''' SELECT name as dep_name,id as dep_id from hr_department_payroll where id in %s''',(department,))
            do = self.cr.dictfetchall()
            self.total_net={'net':0}
            return do 

    def _process(self,data,lis):
        year =  data['form']['year']
        month = data['form']['month']
        state = data['form']['states_id']
        in_salary_sheet = True
        type=data['form']['type']
        allowance_deduction=data['form']['allowance_deduction']
        if type == 'salary':
            self.cr.execute('''
                SELECT pay.net AS net 
                FROM hr_payroll_main_archive  pay 
                LEFT JOIN hr_employee  emp ON (pay.employee_id = emp.id) 
                LEFT JOIN hr_department_payroll dep ON (dep.id=pay.payroll_employee_id)
                LEFT JOIN hr_salary_scale sal ON (pay.scale_id = sal.id)
                WHERE pay.month  =%s
                AND pay.year =%s
                AND pay.payroll_state =%s
                AND pay.in_salary_sheet = True 
                AND dep.id =%s  ''' ,(data['form']['month'],data['form']['year'],data['form']['states_id'],lis)) 
        if type == 'addendum':
            if allowance_deduction:
                allowance_deduction = allowance_deduction[0]
                self.cr.execute('''
                SELECT pay.net AS net 
                FROM hr_payroll_main_archive  pay 
                LEFT JOIN hr_employee  emp ON (pay.employee_id = emp.id) 
                LEFT JOIN hr_department_payroll dep ON (dep.id=pay.payroll_employee_id)
                LEFT JOIN hr_salary_scale sal ON (pay.scale_id = sal.id)
                LEFT JOIN hr_allowance_deduction_archive ada on (pay.id=ada.main_arch_id)
                WHERE pay.month  =%s
                AND pay.year =%s
                AND pay.payroll_state =%s
                AND pay.in_salary_sheet = False 
                AND ada.allow_deduct_id =%s 
                AND dep.id =%s  ''' ,(data['form']['month'],data['form']['year'],data['form']['states_id'],allowance_deduction,lis)) 


        
        res = self.cr.dictfetchall() 
        net = 0.0
        for r in res :
            if r['net']:
                net += (r['net'])
                self.sum += (r['net'])
        return [{'net':net}]
    
    def get_sum(self,data):
        return self.sum
    
    
   
    
    
   
report_sxw.report_sxw('report.payroll_department', 'hr.payroll.main.archive', 'addons/hr_payroll_custom_niss/report/payroll_department.rml' ,parser=payroll_department,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



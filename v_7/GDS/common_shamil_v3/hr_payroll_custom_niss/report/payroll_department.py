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
        self.total = 0
        super(payroll_department, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'process': self._process,
            'department':self.get_department,
            'final_amount' : self._final_amount ,
        })
    
    def get_department(self,data):
            department=tuple(data['form']['department_ids'])
            lis=[]
            self.cr.execute(''' SELECT name as dep_name,id as dep_id from hr_department_payroll where id in %s''',(department,))
            do = self.cr.dictfetchall()
            self.total_net={'net':0}
            print "############# do " , do
            return do 

    def _process(self,data,lis):
        year =  data['form']['year']
        month = data['form']['month']
        self.cr.execute('''
            SELECT sum (pay.net) AS net 
            FROM hr_payroll_main_archive  pay  
            WHERE pay.month  =%s
            AND pay.year =%s
            AND pay.in_salary_sheet = True 
            AND pay.payroll_employee_id =%s  ''' ,(data['form']['month'],data['form']['year'],lis)) 
        res = self.cr.dictfetchall() 
        for r in res :
            net=(r['net'])
        self.total += res[0]['net'] or 0
        return res
    def _final_amount(self):
        return self.total
    
'''
SELECT sum (pay.net) AS net 
            FROM hr_payroll_main_archive  pay 
            LEFT JOIN hr_employee  emp ON (pay.employee_id = emp.id) 
            LEFT JOIN hr_department_payroll dep ON (dep.id=emp.payroll_employee_id)
            LEFT JOIN hr_salary_scale sal ON (pay.scale_id = sal.id)
            WHERE pay.month  =%s
            AND pay.year =%s
            AND pay.in_salary_sheet = True 
            AND dep.id =%s
'''
   
    
    
   
report_sxw.report_sxw('report.payroll_department', 'hr.payroll.main.archive', 'addons/hr_payroll_custom_niss/report/hr_payroll_department.mako' ,parser=payroll_department,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



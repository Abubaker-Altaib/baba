# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################rrrrrrrrr
import time
from openerp.report import report_sxw
from osv import fields, osv

class payroll_department_months(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(payroll_department_months, self).__init__(cr, uid, name, context)
        self.total = {'basic_salary':0.0,'total_pref':0.0, 'total_curr':0.0,'total_loans':0.0,'net':0.0,
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
        self.cr.execute(
            '''SELECT distinct d.id,d.name AS degree ,emp.id,emp.emp_code AS code, emp.name_related AS name,
            ((select COALESCE(basic_salary,0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) + (select  COALESCE(basic_salary,0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True)) AS basic_salary,

((select COALESCE(total_allowance,0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) + (select COALESCE(total_allowance,0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True)) AS total_allowance,

((select COALESCE(total_deduction,0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) + (select COALESCE(total_deduction,0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True)) AS total_deduction,

((select COALESCE(total_loans,0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) + (select COALESCE(total_loans,0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True)) AS total_loans,

((select COALESCE(allowances_tax,0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) + (select COALESCE(allowances_tax,0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True)) AS allowances_tax ,

((select COALESCE(tax,0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) + (select COALESCE(tax,0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True)) AS tax,

((select COALESCE(zakat,0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) + (select COALESCE(zakat,0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True)) AS zakat,

(select COALESCE(sum(net),0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) as pref_net,

(select COALESCE(sum(net),0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) as new_net,


((select COALESCE(sum(net),0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True) + (select COALESCE(sum(net),0) from hr_payroll_main_archive where hr_payroll_main_archive.employee_id=emp.id and hr_payroll_main_archive.month=%s and hr_payroll_main_archive.year=%s and hr_payroll_main_archive.in_salary_sheet=True)) AS net 
            FROM hr_payroll_main_archive  pay 
            LEFT JOIN hr_employee  emp ON (pay.employee_id = emp.id) 
            LEFT JOIN hr_department_payroll dep ON (dep.id=pay.payroll_employee_id)
            LEFT JOIN hr_salary_scale sal ON (pay.scale_id = sal.id)
            LEFT JOIN hr_salary_degree d ON (emp.degree_id = d.id)
            WHERE pay.in_salary_sheet = True and ( (pay.month=%s and pay.year=%s) or (pay.month=%s and pay.year=%s) )
            AND dep.id = %s
     
            AND sal.id = %s
            ''',(
data['form']['first_month'],data['form']['year'],data['form']['second_month'],data['form']['year'],
data['form']['first_month'],data['form']['year'],data['form']['second_month'],data['form']['year'],
data['form']['first_month'],data['form']['year'],data['form']['second_month'],data['form']['year'],
data['form']['first_month'],data['form']['year'],data['form']['second_month'],data['form']['year'],
data['form']['first_month'],data['form']['year'],data['form']['second_month'],data['form']['year'],
data['form']['first_month'],data['form']['year'],data['form']['second_month'],data['form']['year'],
data['form']['first_month'],data['form']['year'],data['form']['second_month'],data['form']['year'],
data['form']['first_month'],data['form']['year'],data['form']['second_month'],data['form']['year'],
data['form']['first_month'],data['form']['year'],data['form']['second_month'],data['form']['year'],
data['form']['first_month'],data['form']['year'],data['form']['second_month'],data['form']['year'],lis,payroll))
 
        res = self.cr.dictfetchall()
        self.total['basic_salary']=self.total['total_allowance']=self.total['total_deduction']=self.total['total_loans']=self.total['net'] =0.0
        self.total['allowances_tax']=self.total['tax']=self.total['zakat']=0.0
        for r in res:
          if r['basic_salary']:
             self.total['basic_salary'] += int(r['basic_salary'])
          else:
             self.total['basic_salary'] +=0

          self.total['total_pref'] += round(r['pref_net'],2)

          self.total['total_curr'] += round(r['new_net'],2)
          if self.total['total_loans']:
             self.total['total_loans'] += int(r['total_loans'])
          else:
             self.total['total_loans'] +=0

          if self.total['allowances_tax']:
             self.total['allowances_tax'] += int(r['allowances_tax'])
          else:
             self.total['allowances_tax'] +=0

          if self.total['tax']:
             self.total['tax'] += int(r['tax'])
          else:
             self.total['tax'] +=0

          self.total['net'] +=round(r['net'],2)



        return res

    def _total(self):
        return [self.total]  
   
report_sxw.report_sxw('report.payroll.department.listing.months', 'hr.employee.salary.addendum', 'addons/hr_payroll_custom_niss/report/payroll_listing_department_months.rml' ,parser=payroll_department_months,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



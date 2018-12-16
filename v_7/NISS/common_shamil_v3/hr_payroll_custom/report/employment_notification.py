# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from report import report_sxw
from account_custom.common_report_header import common_report_header

class employment_notification(report_sxw.rml_parse, common_report_header):
    def __init__(self, cr, uid, name, context):
        super(employment_notification, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._get_qualification,
            'line1':self._get_comp,             
            'allowance':self._get_execut,
            'total':self._get_total,
            'total3':self._get_total3,
        })

    def set_context(self, objects, data, ids, report_type=None):
        return super(employment_notification, self).set_context(objects, data, ids, report_type=report_type)
    
    def _get_comp(self,emp1):
          emp=emp1.id
          self.cr.execute('''select res_company.logo_web as logo from res_company,resource_resource,hr_employee where hr_employee.resource_id = resource_resource.id and resource_resource.company_id = res_company.id and hr_employee.id = %s'''%(emp)) 
          
          res_com= self.cr.dictfetchall()
          return res_com


    def _get_qualification(self,emp1):
          emp=emp1.id
          self.cr.execute('''
                  select qa.name AS qua ,s.name AS spc,q.qual_date AS date,q.organization AS org from hr_employee_qualification q 
                  left join hr_employee e on (e.id=q.employee_id)
                  left join hr_specifications s on (s.id=q.specialization)
                  left join hr_qualification qa on (qa.id=q.emp_qual_id)
                  left join resource_resource c on (c.id=e.resource_id) where q.state='approved' and c.id=%s'''%(emp))           
          res= self.cr.dictfetchall()
          return res


    def _get_execut(self,sheet,emp,alw_ded):          
          self.cr.execute('''
SELECT 
 round( (hr_employee_salary.amount-
  hr_employee_salary.tax_deducted),2) as mount,
  hr_allowance_deduction."name" as name
FROM 
  public.hr_employee_salary, 
  public.hr_allowance_deduction
WHERE 
  hr_allowance_deduction.id = hr_employee_salary.allow_deduct_id
  and  hr_allowance_deduction.pay_sheet='%s'
  and hr_employee_salary.employee_id=%s
  and   hr_allowance_deduction.name_type='%s' 
''',(sheet,emp,alw_ded))           
          res= self.cr.dictfetchall()
          return res                
    def _get_total(self,sheet,emp,alw_ded):          
          self.cr.execute('''
SELECT 
 round( sum( hr_employee_salary.amount-
  hr_employee_salary.tax_deducted) ,2) as mount
FROM 
  public.hr_employee_salary,
  hr_allowance_deduction
WHERE 
  hr_allowance_deduction.id = hr_employee_salary.allow_deduct_id
  and  hr_allowance_deduction.pay_sheet='%s'
  and hr_employee_salary.employee_id=%s
  and   hr_allowance_deduction.name_type='%s' 
''',(sheet,emp,alw_ded))           
          res= self.cr.fetchall()
          return res       
    def _get_total3(self,emp,alw_ded):          
          self.cr.execute('''
SELECT 
 round( sum( hr_employee_salary.amount-
  hr_employee_salary.tax_deducted) ,2) as mount
FROM 
  public.hr_employee_salary,
  hr_allowance_deduction
WHERE 
  hr_allowance_deduction.id = hr_employee_salary.allow_deduct_id
  and hr_employee_salary.employee_id=%s
  and   hr_allowance_deduction.name_type='%s' 
''',(emp,alw_ded))           
          res= self.cr.fetchall()
          return res                          
report_sxw.report_sxw('report.employment.notification', 'hr.employee', 'hr_payroll_custom/report/employment_notification.rml' ,parser=employment_notification ,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


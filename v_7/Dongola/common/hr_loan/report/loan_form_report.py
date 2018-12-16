# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
import re
from openerp.osv import osv, fields, orm
from report import report_sxw
from openerp.tools.translate import _
import calendar
import datetime

class loan_form_report(report_sxw.rml_parse):
     def __init__(self, cr, uid, name, context):
        super(loan_form_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'loan':self._get_loan,
            'company1':self._getcom,
            'employee':self._get_emp,
            'giving':self._assign_emp_loan,
        })
        
     def _get_loan(self,data):
           
            self.cr.execute('select name as loan_name from hr_loan where id =%s'%(data['form']['loans'][0]))
            res = self.cr.fetchall()
            return res

     def _getcom(self,form):
            result = []
            emp = self.pool.get('hr.employee')
            result = emp.browse(self.cr,self.uid,form['employee_ids'])
            return result

     def _get_emp(self,data,emp):
                payroll_obj= self.pool.get('hr.payroll.main.archive')
                self.cr.execute (''' select id as id from hr_payroll_main_archive \
                                     where month=(select max(month)from hr_payroll_main_archive where year =(select max(year)\
                                     from hr_payroll_main_archive)) and employee_id= %s '''%(data['form']['employee_ids'][0]))
                try :
                   emp_id=self.cr.dictfetchall()[0]['id']
                except Exception, exc:
                   self.cr.rollback()
                   raise osv.except_osv(_('ERROR'), _('This employee has not salary'))
                emp_detail= payroll_obj.search(self.cr, self.uid,[('id','=',emp_id),])
                archive_obj=payroll_obj.browse(self.cr,self.uid,emp_detail)
                res={}
                for arc in archive_obj: 
                    res={
                         'net':arc.net,
                         'total_deduction':arc.total_deduction,
                         'total_allownce':arc.total_allowance,
                         'total_loans':arc.total_loans,
                         'emp_name':arc.employee_id.name,
                         'emp_code':arc.employee_id.emp_code,
                         'emp_dept':arc.employee_id.department_id.name,
                         'emp_p_dept':arc.employee_id.department_id.parent_id.name,
                         'emp_job':arc.employee_id.job_id.name,
                         'emp_date':arc.employee_id.employment_date,
                         'degree':arc.employee_id.degree_id.name,
                    }
                return [res]


     def _assign_emp_loan(self , data):
        res={}
        list_res=[]
        payroll_obj= self.pool.get('payroll')
        employee_obj=self.pool.get('hr.employee')
        loan_obj = self.pool.get('hr.loan')
        loan_ids= loan_obj.browse(self.cr,self.uid,data['form']['loans'][0])
        all_emp=self.pool.get('hr.employee').search(self.cr,self.uid,[('department_id','=',data['form']['department_id'][0])])
        emp_total_payroll=0
        ids=[]
        payroll_dict={}
        for emp in employee_obj.browse(self.cr,self.uid,all_emp):
           total_payroll = 0
           total_payroll=payroll_obj.read_allowance_deduct(self.cr, self.uid,emp.id,[],'allow')
           if  emp.bonus_id :
              total_payroll+= emp.bonus_id.basic_salary
           emp_total_payroll+=total_payroll 
           payroll_dict.update({'emp%s' % emp.id :total_payroll})
        for e in data['form']['employee_ids']:
           start_date=time.strftime("%d/%m/%Y")
           total_payroll=payroll_dict['emp%s' % e]
           if loan_ids.loan_type=='amount':
              total_loan=loan_ids.amount
              total_per_month=loan_ids.amount
           else:
              if loan_ids.degree_ids:
                 loan_degree=[]
                 for ld in loan_ids.degree_ids:
                    loan_degree.append(ld.id)
           employee=employee_obj.browse(self.cr,self.uid,e)
           code=employee.code
           if (loan_ids.degree_ids and employee.degree_id.id in tuple(loan_degree) ) or not loan_ids.degree_ids:   
              if loan_ids.installment_type=='fixed':
                 total_loan=loan_ids.amount
                 install_amount=loan_ids.amount/loan_ids.installment_no
                 total_per_month=install_amount
              if loan_ids.installment_type=='salary':
                 loan_based_salary=payroll_obj.read_allowance_deduct(self.cr, self.uid,e,[loan_ids.allowances_id.id ],'allow')
                 total_loan=loan_based_salary #*loan_ids.factor
                 install_amount=total_loan/loan_ids.installment_no
                 total_per_month=install_amount
              check=self.pool.get('hr.employee.loan').search(self.cr, self.uid, [('employee_id','=',e),('loan_id','=',loan_ids.id)])
              counter = 0
              if check:
                 check_ids=self.pool.get('hr.employee.loan').browse(self.cr, self.uid,check)
                 for i in check_ids:
                    if i.loan_amount != i.advance_amount:
                       counter=1
              if (loan_ids.loan_limit=='one' and not check) or (loan_ids.loan_limit=='unlimit' and not check) or (loan_ids.loan_limit=='unlimit' and check and counter==0) or (loan_ids.loan_limit=='unlimit' and check and loan_ids.allow_interference) :
                 if total_payroll=='0':
                    total_payroll=payroll_obj.read_allowance_deduct(self.cr, self.uid,e,[],'allow')
                 check=self.pool.get('hr.employee.loan').search(self.cr, self.uid, [('employee_id','=',e)])
                 if check:
                    check_ids=self.pool.get('hr.employee.loan').browse(self.cr, self.uid,check)
                    for c in check_ids:
                       if c.loan_amount != c.advance_amount:
                          total_per_month+=c.installment_amount
                 '''if not employee.company_id.max_employee or not employee.company_id.max_department :
                    raise osv.except_osv('ERROR', 'You Must Enter policy for Company')'''
                 if employee.company_id.max_employee and total_per_month <= (total_payroll*employee.company_id.max_employee)/100 :
                    all_total_per_month=install_amount
                    check=self.pool.get('hr.employee.loan').search(self.cr, self.uid, [('employee_id','in',all_emp)])
                    if check:
                       check_ids=self.pool.get('hr.employee.loan').browse(self.cr, self.uid,check)
                       for h in check_ids:
                          if h.loan_amount != h.advance_amount:
                             all_total_per_month+=h.installment_amount
                    if employee.company_id.max_department and all_total_per_month <= (emp_total_payroll*employee.company_id.max_department)/100 :
                       days= loan_ids.year_employment * 365
                       from_dt = time.mktime(time.strptime(employee.employment_date,'%Y-%m-%d'))
                       to_dt = time.mktime(time.strptime(data['form']['start_date'],'%Y-%m-%d'))
                       diff_day = (to_dt-from_dt)/(3600*24)
                       if diff_day >= days: 
                          if employee.birthday:
                             date1 = time.mktime(time.strptime(employee.birthday,'%Y-%m-%d'))
                             date2 = time.mktime(time.strptime(data['form']['start_date'],'%Y-%m-%d'))
                             years=((date2-date1)/(3600*24)) / 365
                             pension= employee.company_id.age_pension  and employee.company_id.age_pension - years 
                             if pension >= (loan_ids.installment_no / 12 ):                 
                                res={'state':'Available','reason':' '}

                             else:
                                res={'state':'Rejected','reason':'Pension Reached Before Fininshig Loan Installments'}
	        
     
                       else:
                          res={'state':'Rejected','reason':'Employment years for Employee Not Fit employment Years for Thel Loan'}
                    else:
                       if employee.company_id.max_department and all_total_per_month > (emp_total_payroll*employee.company_id.max_department)/100:
                          res={'state':'Rejected','reason':'Total Loans Installments for The Department Exceed Max Percentage'}

                 else:
                    if employee.company_id.max_employee and total_per_month > (total_payroll*employee.company_id.max_employee)/100 :
                       res={'state':'Rejected','reason':'Total Loans Installments for The Employee Exceed Max Percentage'}

              else:
                 if loan_ids.loan_limit=='one' and check: 
                    res={'state':'Rejected','reason':'Loan Limit is Once and Already Taken'}
                 if loan_ids.loan_limit=='unlimit' and check and counter!= 0 and not loan_ids.allow_interference:
                    res= {'state':'Rejected','reason':'Interference Between same Loan Not Allowed'}
           else:
              res= {'state':'Rejected','reason':'Loan Not Allowed for The Degree of Employee'}
           list_res.append(res)
        return list_res
        
     

report_sxw.report_sxw('report.loan.form.report', 'hr.employee.loan', 'hr_loan/report/loan_form_report.rml' ,parser=loan_form_report ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

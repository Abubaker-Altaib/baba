# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.report import report_sxw
from mako.template import Template
from openerp.report.interface import report_rml
from openerp.report.interface import toxml

BREAK_POINT = 15 #controll number of records in each page
class allowance_deduction_landscape(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(allowance_deduction_landscape, self).__init__(cr, uid, name, context)
        self.page_trans_totals = []
        self.transfer_total_basics = []
        self.transfer_totals= {#store total for printing in each page the summation of last pages records
          'loan' : [] , #please init these keys by [0] to avoid some problems!!
          'allow':[] ,
          'deduct':[] ,
          'net' : [] ,
        }
        self.localcontext.update({
            'time': time,
            'process':self._process,  
        })

    def _get_page_trans_totals(self , i):
      index = int(i/BREAK_POINT)
      return self.page_trans_totals[index]

    """
      this method for getting tranferd total for passed page index
      @param key : column name such as loans , basic etc.
      @param i : page index
      @return : tranferd amount or list of amounts
    """
    def _get_transfer_total(self , key , i):
      index = int(i/BREAK_POINT)
      return self.transfer_totals[key][index]

    def _get_transfer_total_basics(self , i):
      index = int(i/BREAK_POINT)
      return self.transfer_total_basics[index]

    def _process(self,data):
        year = data['year']
        month = data['month']

        #step 1 : get all employee in passed month , later get ids of passed employees
        self.cr.execute(
            '''
            SELECT 
              hr_payroll_main_archive.employee_id as emp_id ,
              public.hr_employee.name_related as emp_name ,
              hr_payroll_main_archive.basic_salary as basic_salary
            FROM 
              public.hr_employee, 
              public.hr_payroll_main_archive
            WHERE 
                hr_payroll_main_archive.employee_id = hr_employee.id
                AND hr_payroll_main_archive.month = %s
                AND hr_payroll_main_archive.year = %s;
            '''  %(month , year) )
        emp_res = self.cr.dictfetchall()       

        #step 2 : get all allowaces/deductions in passed month , later get ids of passed allowances/deductions
        self.cr.execute(
            '''
            SELECT 
               distinct hr_allowance_deduction_archive.allow_deduct_id , 
               public.hr_allowance_deduction.sequence , 
               public.hr_allowance_deduction.name ,
               public.hr_allowance_deduction.name_type
            FROM 
              public.hr_allowance_deduction_archive, 
              public.hr_payroll_main_archive , 
              public.hr_allowance_deduction
            WHERE 
             hr_payroll_main_archive.id = hr_allowance_deduction_archive.main_arch_id
             AND hr_payroll_main_archive.month = %s
             AND hr_payroll_main_archive.year = %s 
             AND public.hr_allowance_deduction.id = hr_allowance_deduction_archive.allow_deduct_id

            order by public.hr_allowance_deduction.sequence;
            ''' %(month , year))
        allow_deduct_res = self.cr.dictfetchall() 

        #step 3 : get all allowaces/deductions for employees
        self.cr.execute(
            '''
            SELECT 
               hr_allowance_deduction_archive.allow_deduct_id , 
               hr_payroll_main_archive.employee_id , 
               hr_allowance_deduction_archive.amount 
            FROM 
              public.hr_allowance_deduction_archive, 
              public.hr_payroll_main_archive 
            WHERE 
              hr_payroll_main_archive.id = hr_allowance_deduction_archive.main_arch_id
              AND hr_payroll_main_archive.month = %s 
              AND hr_payroll_main_archive.year = %s;
            ''' %(month , year))
        emp_allows_res = self.cr.dictfetchall() 

        #step 3 : check what I need to show in my report !!
        include_bascic_salary = True
        include_allow_total = True
        include_deduct_total = True
        include_net_total = True


        #step 4 : prepare table data 
        emp_data = [] # array for store employees data
        allow_deduct_totals = [0 for i in range(len(allow_deduct_res))]#prepare array for store totals
        self.page_trans_totals = []#array for transfer pages total to next page
        self.transfer_total_basics = []
        total_basics = 0
        total_allows = 0
        total_deducts = 0
        for j , emp in enumerate(emp_res) :
          amounts = []
          emp_total_allow = 0
          emp_total_deduct = 0
          for i , allow_deduct in enumerate(allow_deduct_res):
            amount_obj = filter(lambda arch : arch['employee_id'] == emp['emp_id'] and arch['allow_deduct_id'] == allow_deduct['allow_deduct_id'] , emp_allows_res)
            emp_amount = amount_obj and amount_obj[0]['amount'] or 0
            if allow_deduct['name_type'] == 'allow' : emp_total_allow += emp_amount
            else : emp_total_deduct += emp_amount
            allow_deduct_totals[i] = allow_deduct_totals[i] + emp_amount
            amounts.append(emp_amount)
          total_basics += emp['basic_salary']
          emp_total_allow += include_bascic_salary and emp['basic_salary'] or 0
          total_allows += emp_total_allow
          total_deducts += emp_total_deduct
          emp_row = {
            'emp_name' : emp['emp_name'] ,
            'amounts' : amounts ,
            'basic_salary' : emp['basic_salary'] , 
            'emp_total_deduct' : emp_total_deduct,
            'emp_total_allow' : emp_total_allow,
            'emp_net' : emp_total_allow - emp_total_deduct,
          }
          #here checking break point for register total amounts of processed records
          if (j+1) % BREAK_POINT == 0:
            self.page_trans_totals.append([i for i in allow_deduct_totals])
            self.transfer_total_basics.append(total_basics)
            self.transfer_totals['allow'].append(total_allows)
            self.transfer_totals['deduct'].append(total_deducts)
            self.transfer_totals['net'].append(total_allows - total_deducts)
          emp_data.append(emp_row)
        
        print "############ trans " , self.transfer_totals
        total_nets =   total_allows - total_deducts
        #step 5 : prepare allowances/deductions header
        header = [] #store headr list for eachpage
        for allow_deduct in allow_deduct_res:
            header.append(allow_deduct['name'])

        
        res = {
            'emp_data' : emp_data ,
            'headrs' : header ,
            'allow_deduct_totals' : allow_deduct_totals ,
            'page_trans_totals' : self.page_trans_totals ,
            'BREAK_POINT' : BREAK_POINT ,
            'page_trans_totals' : self._get_page_trans_totals ,
            'include_bascic_salary' : include_bascic_salary ,
            'total_basics' : total_basics ,
            'transfer_total_basics' : self._get_transfer_total_basics ,
            'len_emp_data' : len(emp_data) ,
            'transfer_total' : self._get_transfer_total ,
            'include_allow_total' : include_allow_total ,
            'include_deduct_total' : include_deduct_total ,
            'include_net_total' : include_net_total ,
            'total_allows' : total_allows ,
            'total_deducts' : total_deducts ,
            'total_nets' : total_nets,
          }
        
        return [res]

report_sxw.report_sxw('report.allowance.deduction.landscape', 'hr.allowance.deduction.archive', 'hr_payroll_custom/report/allowance_deduction_landscape.mako' ,parser=allowance_deduction_landscape,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


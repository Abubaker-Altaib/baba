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

BREAK_POINT = 20 #controll number of records in each page
class allowance_deduction_landscape(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(allowance_deduction_landscape, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'process':self._main_process,  
        })


    def _main_process(self,data):
      if not data['department_cat_id']:
        return [self._process(data)]
      res = []
      outsite_scale = data.get('outsite_scale' , False)
      if outsite_scale :
        for i in  data['department_ids'] :
          r = self._process(data ,[i] ,outsite_scale )
          if r['len_emp_data'] > 0:
            res.append(r)
      else:
        for i in  data['childe_dep_ids'] :
          r = self._process(data ,i)
          if r['len_emp_data'] > 0: 
            res.append(r)
      return res


    def _process(self,data , dep_ids = None, outsite_scale=False):
        allow_column_index = 0 #specify where to show allowance totals 
        department_title = ""
        page_trans_totals = []
        transfer_total_basics = []
        transfer_totals= {#store total for printing in each page the summation of last pages records
          'loan' : [] , 
          'allow':[] ,
          'deduct':[] ,
          'net' : [] ,
        }

        year = data['year']
        month = data['month']
        list_to_str = lambda items : ",".join(str(i) for i in items)
        company_id = data.get('company_id')
        company_ids_str =list_to_str(company_id)


        department_condition = ""
        if dep_ids :
          searching_field = outsite_scale and 'location_id' or 'department_id'
          dep_ids_str = list_to_str(dep_ids)
          department_condition = "AND public.hr_employee."+searching_field+" in (%s)" %(dep_ids_str)
          department_title = self.pool.get('hr.department').read(self.cr,self.uid , [dep_ids[0]] , ['name'])[0]['name']
        #step 1 : get all employee in passed month , later get ids of passed employees
        self.cr.execute(
            '''
            SELECT 
              hr_payroll_main_archive.employee_id as emp_id ,
              public.hr_employee.name_related as emp_name ,
              hr_payroll_main_archive.basic_salary as basic_salary , 
             public.hr_salary_degree.sequence as seq 
            FROM 
              public.hr_employee, 
              public.hr_payroll_main_archive ,
              public.hr_salary_degree

            WHERE 
                hr_payroll_main_archive.employee_id = hr_employee.id
                AND hr_payroll_main_archive.month = %s
                AND hr_payroll_main_archive.year = %s
                AND public.hr_salary_degree.id = public.hr_employee.degree_id
                AND public.hr_payroll_main_archive.company_id in (%s)
                %s
                order by seq , emp_name 
                ;
            '''  %(month , year ,company_ids_str,department_condition) )
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
              public.hr_allowance_deduction ,
              public.hr_employee 
            WHERE 
             hr_payroll_main_archive.id = hr_allowance_deduction_archive.main_arch_id
             AND hr_payroll_main_archive.month = %s
             AND hr_payroll_main_archive.year = %s 
             AND public.hr_allowance_deduction.id = hr_allowance_deduction_archive.allow_deduct_id
             AND public.hr_payroll_main_archive.company_id in (%s)
             AND hr_employee.id = hr_payroll_main_archive.employee_id 
             %s
            order by public.hr_allowance_deduction.name_type , public.hr_allowance_deduction.sequence
            ;
            ''' %(month , year , company_ids_str ,department_condition))
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
              public.hr_payroll_main_archive ,
              public.hr_employee 
            WHERE 
              hr_payroll_main_archive.id = hr_allowance_deduction_archive.main_arch_id
              AND hr_payroll_main_archive.month = %s 
              AND hr_payroll_main_archive.year = %s
              AND hr_employee.id = hr_payroll_main_archive.employee_id 
              AND public.hr_payroll_main_archive.company_id in (%s)
              %s;
            ''' %(month , year,company_ids_str , department_condition))
        emp_allows_res = self.cr.dictfetchall() 

        #step 3 : check what I need to show in my report !!
        include_bascic_salary = True
        include_allow_total = True
        include_deduct_total = True
        include_net_total = True


        #step 4 : prepare table data 
        emp_data = [] # array for store employees data
        allow_deduct_totals = [0 for i in range(len(allow_deduct_res))]#prepare array for store totals
        page_trans_totals = []#array for transfer pages total to next page
        transfer_total_basics = []
        total_basics = 0
        total_allows = 0
        total_deducts = 0
        for j , emp in enumerate(emp_res) :
          amounts = []
          allow_amounts = []
          deduct_amounts = []
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
            'amounts' : [round(am , 2) for am in amounts] ,
            'basic_salary' : emp['basic_salary'] , 
            'emp_total_deduct' : round(emp_total_deduct,2),
            'emp_total_allow' : round(emp_total_allow,2),
            'emp_net' : round(emp_total_allow - emp_total_deduct , 2),
          }
          #here checking break point for register total amounts of processed records
          if (j+1) % BREAK_POINT == 0:
            page_trans_totals.append([round(adt , 2) for adt in allow_deduct_totals])
            transfer_total_basics.append(round(total_basics , 2))
            transfer_totals['allow'].append(round(total_allows,2))
            transfer_totals['deduct'].append(round(total_deducts,2))
            transfer_totals['net'].append(round(total_allows - total_deducts , 2))
          emp_data.append(emp_row)
         
        total_nets =   total_allows - total_deducts
        #step 5 : prepare allowances/deductions header
        header = [] #store headr list for eachpage
        allow_header = []
        deduct_header = []
        for allow_deduct in allow_deduct_res:
            header.append(allow_deduct['name'])
            if allow_deduct['name_type'] == 'allow' :
              allow_header.append(allow_deduct['name'])
              allow_column_index += 1
            else :
              deduct_header.append(allow_deduct['name'])
        
        res = {
            'emp_data' : emp_data ,
            'headrs' : header ,
            'allow_header' : allow_header ,
            'deduct_header' : deduct_header ,
            'allow_deduct_totals' : allow_deduct_totals ,
            'page_trans_totals' : page_trans_totals ,
            'BREAK_POINT' : BREAK_POINT ,
            'page_trans_totals' : lambda index : page_trans_totals[int(index/BREAK_POINT)] ,
            'include_bascic_salary' : include_bascic_salary ,
            'total_basics' : round(total_basics,2) ,
            'transfer_total_basics' : lambda index : transfer_total_basics[int(index/BREAK_POINT)] ,
            'len_emp_data' : len(emp_data) ,
            'transfer_total' : lambda key , index : transfer_totals[key][int(index/BREAK_POINT)] ,
            'include_allow_total' : include_allow_total ,
            'include_deduct_total' : include_deduct_total ,
            'include_net_total' : include_net_total ,
            'total_allows' : round(total_allows,2) ,
            'total_deducts' : round(total_deducts,2) ,
            'total_nets' : round(total_nets,2),
            'department_title' : department_title ,
            'allow_column_index' : allow_column_index ,
          }
        return res

report_sxw.report_sxw('report.allowance.deduction.landscape', 'hr.allowance.deduction.archive', 'hr_payroll_custom/report/allowance_deduction_landscape.mako' ,parser=allowance_deduction_landscape,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


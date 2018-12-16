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
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar
import math

BREAK_POINT = 30#controll number of records in each page
class allowance_deduction_landscape_scale(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(allowance_deduction_landscape_scale, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'process':self._main_process,  
        })

    def _main_process(self,data):
        return [self._process(data)]

    def _process(self,data , dep_ids = None, outsite_scale=False):
        allow_column_index = -1 #specify where to show allowance totals 
        department_title = ""
        page_trans_totals = []
        transfer_total_basics = []
        transfer_totals= {#store total for printing in each page the summation of last pages records
          'loan' : [] , 
          'allow':[] ,
          'deduct':[] ,
          'net' : [] ,
        }

        in_salary_sheet = True
        ad_type = data['type'] #allowance or deduction
        #paysheet = data['pay_sheet']
        list_to_str = lambda items : ",".join(str(i) for i in items)
        payroll_id = data.get('payroll_ids')
        payroll_ids_str =str(data['payroll_ids'])
        
        #ad_ids_condition = ""
        #if data['allow_deduct_ids']:
        #  ad_ids_condition = " and public.hr_allowance_deduction_archive.allow_deduct_id in (%s)" %(list_to_str(data['allow_deduct_ids']))
        ad_condition = ""
        ad_condition = "and public.hr_allowance_deduction.name_type = '%s' "%('allow')

        
        #step 1 : get all employee in passed month , later get ids of passed employees
        self.cr.execute(
            '''
            SELECT 
               distinct public.hr_salary_degree.id as degree_id , 
               public.hr_salary_degree.name as degree_name, 
               public.hr_salary_degree.sequence as degree_seq,
               public.hr_salary_degree.basis as basic_salary 
            FROM 
              hr_salary_degree 
            WHERE
             hr_salary_degree.payroll_id = %s 
                ;
            '''  %(payroll_ids_str) )
        emp_res = self.cr.dictfetchall()       

        #step 2 : get all allowaces/deductions in passed month , later get ids of passed allowances/deductions
        self.cr.execute(
            '''
            SELECT 
               public.hr_allowance_deduction.id ,
               public.hr_allowance_deduction.sequence , 
               public.hr_allowance_deduction.name ,
               public.hr_allowance_deduction.name_type , 
               public.hr_allowance_deduction.is_basic_salary_item
            FROM  
              public.hr_allowance_deduction 
            WHERE  
                public.hr_allowance_deduction.in_salary_sheet=%s   %s
            order by public.hr_allowance_deduction.name_type , public.hr_allowance_deduction.sequence
            ;
            ''' %(in_salary_sheet,ad_condition,))
        allow_deduct_res = self.cr.dictfetchall() 

        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",allow_deduct_res
        #step 3 : get all allowaces/deductions for employees
        self.cr.execute(
            '''
            SELECT 
               hr_salary_allowance_deduction.id,
               hr_salary_allowance_deduction.allow_deduct_id , 
               hr_salary_allowance_deduction.degree_id , 
               hr_salary_allowance_deduction.amount 
            FROM 
              hr_salary_allowance_deduction 
            WHERE  hr_salary_allowance_deduction.payroll_id = %s 
              ;
            ''' %(payroll_ids_str))
        emp_allows_res = self.cr.dictfetchall() 

        #step 3 : check what I need to show in my report !!
        include_bascic_salary = in_salary_sheet and ad_type not in ['deduct']
        include_allow_total = ad_type not in ['deduct'] 
        include_deduct_total = ad_type not in ['allow']
        include_net_total = ad_type not in ['allow' , 'deduct']
        #step 4 : prepare table data 
        emp_data = [] # array for store employees data
        allow_deduct_totals = [0 for i in range(len(allow_deduct_res))]#prepare array for store totals
        page_trans_totals = []#array for transfer pages total to next page
        transfer_total_basics = []
        total_basics = 0
        total_allows = 0
        total_deducts = 0
        for j , emp in enumerate(emp_res) :
          #print "emp>>>>>>>>>>>>>>>>>",emp_res
          amounts = []
          allow_amounts = []
          deduct_amounts = []
          emp_total_allow = 0
          emp_total_deduct = 0
          for i , allow_deduct in enumerate(allow_deduct_res):
            #print "emp>>>>>>>>>>>>>>>>>",emp_res
            #print "alow>>",allow_deduct_res
            amount_obj = filter(lambda arch : arch['degree_id'] == emp['degree_id'] and arch['allow_deduct_id'] == allow_deduct['id'] , emp_allows_res)
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
            'emp_name' : emp['degree_name'] ,
            'emp_job' : ' ',
            'emp_degree':' ',
            'amounts' : [round(am , 2) for am in amounts] ,
            'basic_salary' :  emp['basic_salary'] , 
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
 
        basic_len =  len(filter(lambda ad : ad['name_type'] == 'allow' and ad['is_basic_salary_item']  , allow_deduct_res)) + 1
        allow_len =  len(filter(lambda ad : ad['name_type'] == 'allow' and not ad['is_basic_salary_item']  ,allow_deduct_res))
        deduct_len =  len(filter(lambda ad : ad['name_type'] == 'deduct'  ,allow_deduct_res))
        if len(emp_data) % BREAK_POINT == 0:
          additional_rows = 0
        additional_rows = 0
        #else:
        #  additional_rows = BREAK_POINT - (len(emp_data) % BREAK_POINT)
        
        amount_in_words = amount_to_text_ar(total_nets, 'ar')
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
            'basic_len' : basic_len ,
            'allow_len' : allow_len ,
            'deduct_len' : deduct_len ,
            'additional_rows' :additional_rows ,  
            'amount_in_words' : amount_in_words ,
          }
        return res

report_sxw.report_sxw('report.allowance.deduction.scale.landscape', 'hr.allowance.deduction.archive', 'hr_payroll_custom/report/allowance_deduction_landscape_scale.mako' ,parser=allowance_deduction_landscape_scale,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


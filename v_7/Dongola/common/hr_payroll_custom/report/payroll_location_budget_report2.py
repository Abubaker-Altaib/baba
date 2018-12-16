#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp.report import report_sxw
from mako.template import Template
from openerp.report.interface import report_rml
from openerp.report.interface import toxml
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar
import math
from openerp.osv import fields, osv

BREAK_POINT = 35  # controll number of records in each page
class payroll_location_report2(report_sxw.rml_parse):
    # step 1 : get all employee in passed month , later get ids of passed employees
    def __init__(self, cr, uid, name, context):
        super(payroll_location_report2, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'process': self._main_process,
        })

    def _main_process(self, data):
        # if not data['department_cat_id']:
        return [self._process(data)]
        return res

    def _process(self, data, dep_ids=None, outsite_scale=False):
        allow_column_index = -1  # specify where to show allowance totals
        department_title = ""
        page_trans_totals = []
        transfer_total_basics = []
        transfer_totals = {  # store total for printing in each page the summation of last pages records
            'loan': [],
            'allow_incre': [],
            'deduct_incre': [],
            'allow_decre': [],
            'deduct_decre': [],
            'net_pre': [],
            'net_curr': [],
        }

        res = []

        emp_condition = ""

        year = data['year']
        month = data['month']
        in_salary_sheet = True
        ad_type = data['type']
        if month==1:
           pre_month=12
           pre_year=year-1
        else:
           pre_month=int(month)-1
           pre_year=year
        # allowance or deduction
        # paysheet = data['pay_sheet']
        # list_to_str = lambda items : ",".join(str(i) for i in items)
        company_id = data.get('company_id')
        #raise osv.except_osv(('ERROR'), ('Please enter account  for Allowances/deductions for %s')%(data['department_ids']))
        print ">>", data['department_ids']
        dept_row = {
            'emp_name': '',
            'emp_curr_total_deduct': 0,
            'emp_pre_total_deduct': 0,
            'emp_incre_deduct': 0,
            'emp_decre_deduct': 0,
            'emp_curr_total_allow': 0,
            'emp_pre_total_allow': 0,
            'emp_incre_allow': 0,
            'emp_decre_allow': 0,
            'emp_curr_net': 0,
            'emp_pre_net': 0,
        }
        
        line_res = dict(map(lambda x: (x, {}), data['department_ids']))
        print "prog1>>>",line_res
        # company_ids_str =list_to_str(company_id)
        ad_ids_condition = ""
        # if data['allow_deduct_ids']:
        #  ad_ids_condition = " and public.hr_allowance_deduction_archive.allow_deduct_id in (%s)" %(list_to_str(data['allow_deduct_ids']))
        ad_condition = ""
        # if ad_type :
        #  ad_condition = "and public.hr_allowance_deduction.name_type = '%s' "%(ad_type)

        self.cr.execute(
            '''
            SELECT
              hr_payroll_main_archive.department_id as department_id ,
              public.hr_department.name as dep_name ,
              sum(hr_payroll_main_archive.basic_salary) as basic_salary
            FROM
              public.hr_department,
              public.hr_payroll_main_archive
            WHERE
                hr_payroll_main_archive.department_id = hr_department.id
                AND hr_payroll_main_archive.month = %s
                AND hr_payroll_main_archive.year = %s
                AND public.hr_payroll_main_archive.in_salary_sheet= %s
                AND public.hr_payroll_main_archive.department_id in %s
              group by hr_payroll_main_archive.department_id, hr_department.name
            ''' % (month, year,in_salary_sheet, tuple(data['department_ids'])))
        dep_now_res = self.cr.dictfetchall()

############################################################################################33
        self.cr.execute(
            '''
            SELECT
              hr_payroll_main_archive.department_id as department_id ,
              public.hr_department.name as dep_name ,
              sum(hr_payroll_main_archive.basic_salary) as basic_salary
            FROM
              public.hr_department,
              public.hr_payroll_main_archive
            WHERE
                hr_payroll_main_archive.department_id = hr_department.id
                AND hr_payroll_main_archive.month = %s
                AND hr_payroll_main_archive.year = %s
                AND public.hr_payroll_main_archive.in_salary_sheet= %s
                AND public.hr_payroll_main_archive.department_id in %s
              group by hr_payroll_main_archive.department_id, hr_department.name
            ''' % (pre_month, pre_year,in_salary_sheet, tuple(data['department_ids'])))
        dep_pre_res = self.cr.dictfetchall()
        # step 2 : get all allowaces/deductions in passed month , later get ids of passed allowances/deductions

        self.cr.execute(
            '''
            SELECT
               distinct hr_allowance_deduction_archive.allow_deduct_id ,
               public.hr_allowance_deduction.sequence ,
               public.hr_allowance_deduction.name ,
               public.hr_allowance_deduction.name_type ,
               public.hr_allowance_deduction.is_basic_salary_item
            FROM
              public.hr_allowance_deduction_archive,
              public.hr_payroll_main_archive ,
              public.hr_allowance_deduction ,
              public.hr_employee
            WHERE
             hr_payroll_main_archive.id = hr_allowance_deduction_archive.main_arch_id
             AND hr_payroll_main_archive.month = %s
             AND hr_payroll_main_archive.year = %s
             AND public.hr_payroll_main_archive.in_salary_sheet= %s
             AND public.hr_allowance_deduction.id = hr_allowance_deduction_archive.allow_deduct_id
             AND public.hr_payroll_main_archive.department_id in %s
             AND hr_employee.id = hr_payroll_main_archive.employee_id
            order by public.hr_allowance_deduction.name_type , public.hr_allowance_deduction.sequence

            ''' % (month, year, in_salary_sheet,tuple(data['department_ids'])))
        allow_deduct_now_res = self.cr.dictfetchall()


#######################################################################################
        self.cr.execute(
            '''
            SELECT
               distinct hr_allowance_deduction_archive.allow_deduct_id ,
               public.hr_allowance_deduction.sequence ,
               public.hr_allowance_deduction.name ,
               public.hr_allowance_deduction.name_type ,
               public.hr_allowance_deduction.is_basic_salary_item
            FROM
              public.hr_allowance_deduction_archive,
              public.hr_payroll_main_archive ,
              public.hr_allowance_deduction ,
              public.hr_employee
            WHERE
             hr_payroll_main_archive.id = hr_allowance_deduction_archive.main_arch_id
             AND hr_payroll_main_archive.month = %s
             AND hr_payroll_main_archive.year = %s
             AND public.hr_payroll_main_archive.in_salary_sheet= %s
             AND public.hr_allowance_deduction.id = hr_allowance_deduction_archive.allow_deduct_id
             AND public.hr_payroll_main_archive.department_id in %s
             AND hr_employee.id = hr_payroll_main_archive.employee_id
            order by public.hr_allowance_deduction.name_type , public.hr_allowance_deduction.sequence

            ''' % (pre_month, pre_year,in_salary_sheet, tuple(data['department_ids'])))
        allow_deduct_pre_res = self.cr.dictfetchall()

        # step 3 : get all allowaces/deductions for employees

        self.cr.execute(
            '''
            SELECT
               hr_allowance_deduction_archive.allow_deduct_id ,
               hr_payroll_main_archive.department_id ,
               sum(hr_allowance_deduction_archive.amount) as amount
            FROM
              public.hr_allowance_deduction_archive,
              public.hr_payroll_main_archive ,
              public.hr_allowance_deduction
            WHERE
              hr_payroll_main_archive.id = hr_allowance_deduction_archive.main_arch_id
              AND hr_payroll_main_archive.month = %s
              AND hr_payroll_main_archive.year = %s
              AND public.hr_payroll_main_archive.in_salary_sheet= %s
              AND hr_allowance_deduction.id = hr_allowance_deduction_archive.allow_deduct_id
              AND public.hr_payroll_main_archive.department_id in %s
            GROUP by hr_payroll_main_archive.department_id, hr_allowance_deduction_archive.allow_deduct_id
            ''' % (month, year, in_salary_sheet,tuple(data['department_ids'])))
        dep_allows_now_res = self.cr.dictfetchall()
################################################################################################
        self.cr.execute(
            '''
            SELECT
               hr_allowance_deduction_archive.allow_deduct_id ,
               hr_payroll_main_archive.department_id ,
               sum(hr_allowance_deduction_archive.amount) as amount
            FROM
              public.hr_allowance_deduction_archive,
              public.hr_payroll_main_archive ,
              public.hr_allowance_deduction
            WHERE
              hr_payroll_main_archive.id = hr_allowance_deduction_archive.main_arch_id
              AND hr_payroll_main_archive.month = %s
              AND hr_payroll_main_archive.year = %s
              AND public.hr_payroll_main_archive.in_salary_sheet= %s
              AND hr_allowance_deduction.id = hr_allowance_deduction_archive.allow_deduct_id
              AND public.hr_payroll_main_archive.department_id in %s
            GROUP by hr_payroll_main_archive.department_id, hr_allowance_deduction_archive.allow_deduct_id
            ''' % (pre_month, pre_year, in_salary_sheet,tuple(data['department_ids'])))
        dep_allows_pre_res = self.cr.dictfetchall()

        # step 3 : check what I need to show in my report !!
        include_bascic_salary = in_salary_sheet and ad_type not in ['deduct']
        include_allow_total = ad_type not in ['deduct']
        include_deduct_total = ad_type not in ['allow']
        include_net_total = ad_type not in ['allow', 'deduct']
        # step 4 : prepare table data
        emp_data = []  # array for store employees data
        emp_data_pre=[]
        allow_deduct_totals = [0 for i in range(len(allow_deduct_now_res))]  # prepare array for store totals
        allow_deduct_totals_pre = [0 for i in range(len(allow_deduct_pre_res))]  # prepare array for store totals
        page_trans_totals = []  # array for transfer pages total to next page
        transfer_total_basics = []
        total_basics = 0
        total_basics_pre = 0
        total_allows = 0
        total_allows_pre = 0
        total_deducts = 0
        total_deducts_pre = 0
        # for j , emp in enumerate(emp_res) :
        for j, emp in enumerate(dep_now_res):
            amounts = []
            allow_amounts = []
            deduct_amounts = []
            emp_total_allow = 0
            emp_total_deduct = 0
            for i, allow_deduct in enumerate(allow_deduct_now_res):
                # amount_obj = filter(lambda arch : arch['employee_id'] == emp['emp_id'] and arch['allow_deduct_id'] == allow_deduct['allow_deduct_id'] , emp_allows_res)
                amount_obj = filter(
                    lambda arch: arch['department_id'] == emp['department_id'] and arch['allow_deduct_id'] ==
                                                                                   allow_deduct['allow_deduct_id'],
                    dep_allows_now_res)
                emp_amount = amount_obj and amount_obj[0]['amount'] or 0
                if allow_deduct['name_type'] == 'allow':
                    emp_total_allow += emp_amount
                else:
                    emp_total_deduct += emp_amount
                allow_deduct_totals[i] = allow_deduct_totals[i] + emp_amount
                amounts.append(emp_amount)
            total_basics += emp['basic_salary']
            # emp_total_allow += include_bascic_salary and emp['basic_salary'] or 0
            emp_total_allow += emp['basic_salary']
            total_allows += emp_total_allow
            total_deducts += emp_total_deduct
            emp_row = {
                'emp_name': emp['dep_name'],
                'emp_id': emp['department_id'],
                # 'emp_job' : emp['emp_job'],
                # 'emp_degree':emp['emp_degree'],
                #'amounts': [round(am, 2) for am in amounts],
                #'basic_salary': emp['basic_salary'],
                'emp_total_deduct': round(emp_total_deduct, 2),
                'emp_total_allow': round(emp_total_allow, 2),
                'emp_net': round(emp_total_allow - emp_total_deduct, 2),
            }
            # here checking break point for register total amounts of processed records
            #if (j + 1) % BREAK_POINT == 0:
            #    page_trans_totals.append([round(adt, 2) for adt in allow_deduct_totals])
            #    transfer_total_basics.append(round(total_basics, 2))
            #    transfer_totals['allow'].append(round(total_allows, 2))
            #    transfer_totals['deduct'].append(round(total_deducts, 2))
            #    transfer_totals['net'].append(round(total_allows - total_deducts, 2))
            emp_data.append(emp_row)
            dept_cu_id=emp_row['emp_id']
            """dept_row = {
                'emp_name': '',
                'emp_curr_total_deduct': 0,
                'emp_pre_total_deduct': 0,
                'emp_incre_deduct': 0,
                'emp_decre_deduct': 0,
                'emp_curr_total_allow': 0,
                'emp_pre_total_allow': 0,
                'emp_incre_allow': 0,
                'emp_decre_allow': 0,
                'emp_curr_net': 0,
                'emp_pre_net': 0,
            }"""
            print "##>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",emp_row['emp_total_deduct']
            line_res[dept_cu_id]['emp_name']=emp_row['emp_name']
            line_res[dept_cu_id]['emp_curr_total_deduct']=emp_row['emp_total_deduct']
            line_res[dept_cu_id]['emp_curr_total_allow']=emp_row['emp_total_allow']
            line_res[dept_cu_id]['emp_curr_net']=emp_row['emp_net']
        print "line1>>>", emp_data
        print "line1>>>", line_res
        total_nets = total_allows - total_deducts
##################################################################################################
        for j_pre, emp_pre in enumerate(dep_pre_res):
            amounts_pre = []
            allow_amounts_pre = []
            deduct_amounts_pre = []
            emp_total_allow_pre = 0
            emp_total_deduct_pre = 0
            for i_pre, allow_deduct_pre in enumerate(allow_deduct_pre_res):
                # amount_obj = filter(lambda arch : arch['employee_id'] == emp['emp_id'] and arch['allow_deduct_id'] == allow_deduct['allow_deduct_id'] , emp_allows_res)
                amount_obj_pre = filter(
                    lambda arch: arch['department_id'] == emp_pre['department_id'] and arch['allow_deduct_id'] ==
                                                                                   allow_deduct_pre['allow_deduct_id'],
                    dep_allows_pre_res)
                emp_amount_pre = amount_obj_pre and amount_obj_pre[0]['amount'] or 0
                if allow_deduct_pre['name_type'] == 'allow':
                    emp_total_allow_pre += emp_amount_pre
                else:
                    emp_total_deduct_pre += emp_amount_pre
                allow_deduct_totals_pre[i] = allow_deduct_totals_pre[i] + emp_amount_pre
                amounts_pre.append(emp_amount_pre)
            total_basics_pre += emp_pre['basic_salary']
            # emp_total_allow += include_bascic_salary and emp['basic_salary'] or 0
            emp_total_allow_pre += emp_pre['basic_salary']
            total_allows_pre += emp_total_allow_pre
            total_deducts_pre += emp_total_deduct_pre
            emp_row_pre = {
                'emp_name': emp_pre['dep_name'],
                'emp_id': emp_pre['department_id'],
                # 'emp_job' : emp['emp_job'],
                # 'emp_degree':emp['emp_degree'],
                #'amounts': [round(am, 2) for am in amounts_pre],
                #'basic_salary': emp_pre['basic_salary'],
                'emp_total_deduct': round(emp_total_deduct_pre, 2),
                'emp_total_allow': round(emp_total_allow_pre, 2),
                'emp_pre_net': round(emp_total_allow_pre - emp_total_deduct_pre, 2),
            }
            #if emp_pre['department_id']==1821:
            #   raise osv.except_osv(('ERROR'), ('Please enter account  for Allowances/deductions for %s')%(emp_row_pre))
            # here checking break point for register total amounts of processed records
            #if (j_pre + 1) % BREAK_POINT == 0:
            #    page_trans_totals.append([round(adt, 2) for adt in allow_deduct_totals])
            #    transfer_total_basics.append(round(total_basics, 2))
            #    transfer_totals['allow'].append(round(total_allows, 2))
            #    transfer_totals['deduct'].append(round(total_deducts, 2))
            #    transfer_totals['net'].append(round(total_allows - total_deducts, 2))
            emp_data_pre.append(emp_row_pre)
        
            print "emp>>",emp_row_pre['emp_total_deduct']
            dept_pre_id=emp_row_pre['emp_id']
            if 'emp_name' not in line_res[dept_pre_id].keys():
               line_res[dept_pre_id]['emp_name']=emp_row_pre['emp_name']
            line_res[dept_pre_id]['emp_pre_total_deduct']=emp_row_pre['emp_total_deduct']
            line_res[dept_pre_id]['emp_pre_total_allow']=emp_row_pre['emp_total_allow']
            line_res[dept_pre_id]['emp_pre_net']=emp_row_pre['emp_pre_net']
        print "line2>>>", emp_data_pre
        print "line2>>>", line_res
        
        final_list_dept_row=[]
        total_curr=0
        total_pre=0
        total_allow_dec=0
        total_allow_inc=0
        total_dedu_dec=0
        total_dedu_inc=0
        
        depart_pool = self.pool.get('hr.department')
        breake=0
        for line in line_res:
                breake +=1
                emp_incre_deduct=0
                emp_decre_deduct=0
                emp_incre_allow=0
                emp_decre_allow=0
                if 'emp_name' not in line_res[line].keys():
                    depart=depart_pool.browse(self.cr,self.uid, line)
                    line_res[line]['emp_name']=depart.name
                # Check keys
                if 'emp_pre_total_allow' not in line_res[line].keys():
                    line_res[line]['emp_pre_total_allow']=0
                if 'emp_pre_total_deduct' not in line_res[line].keys():
                    line_res[line]['emp_pre_total_deduct']=0
                if 'emp_curr_total_allow' not in line_res[line].keys():
                    line_res[line]['emp_curr_total_allow']=0
                if 'emp_curr_total_deduct' not in line_res[line].keys():
                    line_res[line]['emp_curr_total_deduct']=0
                if 'emp_curr_net' not in line_res[line].keys():
                    line_res[line]['emp_curr_net']=0
                if 'emp_pre_net' not in line_res[line].keys():
                    line_res[line]['emp_pre_net']=0


                if (line_res[line]['emp_curr_total_allow']-line_res[line]['emp_pre_total_allow']) > 0:
                    emp_incre_allow=line_res[line]['emp_curr_total_allow']-line_res[line]['emp_pre_total_allow']
                else:
                    emp_decre_allow=line_res[line]['emp_curr_total_allow']-line_res[line]['emp_pre_total_allow']
                if (line_res[line]['emp_curr_total_deduct']-line_res[line]['emp_pre_total_deduct']) > 0:
                    emp_incre_deduct=line_res[line]['emp_curr_total_deduct']-line_res[line]['emp_pre_total_deduct']
                else:
                    emp_decre_deduct=line_res[line]['emp_curr_total_deduct']-line_res[line]['emp_pre_total_deduct']
                total_curr +=line_res[line]['emp_curr_net']
                total_pre  +=line_res[line]['emp_pre_net']
                total_allow_dec +=emp_decre_allow
                total_allow_inc +=emp_incre_allow
                total_dedu_dec +=emp_decre_deduct
                total_dedu_inc +=emp_incre_deduct
                final_dept_row = {
                'emp_name': line_res[line]['emp_name'],
                'emp_curr_total_deduct': line_res[line]['emp_curr_total_deduct'] or 0,
                'emp_pre_total_deduct': line_res[line]['emp_pre_total_deduct'] or 0,
                'emp_incre_deduct': emp_incre_deduct or 0,
                'emp_decre_deduct': emp_decre_deduct or 0,
                'emp_curr_total_allow': line_res[line]['emp_curr_total_allow'] or 0,
                'emp_pre_total_allow': line_res[line]['emp_pre_total_allow'] or 0,
                'emp_incre_allow': emp_incre_allow or 0,
                'emp_decre_allow': emp_decre_allow or 0,
                'emp_curr_net': line_res[line]['emp_curr_net'] or 0,
                'emp_pre_net': line_res[line]['emp_pre_net'] or 0,
                }
                final_list_dept_row.append(final_dept_row)
                if (breake) % BREAK_POINT == 0:
                    transfer_totals['allow_incre'].append(round(total_allow_inc, 2))
                    transfer_totals['deduct_incre'].append(round(total_dedu_inc, 2))
                    transfer_totals['allow_decre'].append(round(total_allow_dec, 2))
                    transfer_totals['deduct_decre'].append(round(total_dedu_dec, 2))
                    transfer_totals['net_pre'].append(round(total_pre, 2))
                    transfer_totals['net_curr'].append(round(total_curr, 2))

        #print "FFFFFF>>>",final_list_dept_row

                #print "##>>>",row
        total_nets_pre = total_allows_pre - total_deducts_pre
        #print "Curre>>>>>>>>",emp_data_pre
        #print "Prev>>>>>>>>",emp_data


        """# step 5 : prepare allowances/deductions header
        header = []  # store headr list for eachpage
        allow_header = []
        deduct_header = []
        for allow_deduct in allow_deduct_now_res:
            header.append(allow_deduct['name'])
            if allow_deduct['name_type'] == 'allow':
                allow_header.append(allow_deduct['name'])
                allow_column_index += 1
            else:
                deduct_header.append(allow_deduct['name'])

        basic_len = len(
            filter(lambda ad: ad['name_type'] == 'allow' and ad['is_basic_salary_item'], allow_deduct_now_res)) + 1
        allow_len = len(
            filter(lambda ad: ad['name_type'] == 'allow' and not ad['is_basic_salary_item'], allow_deduct_now_res))
        deduct_len = len(filter(lambda ad: ad['name_type'] == 'deduct', allow_deduct_now_res))
        if len(emp_data) % BREAK_POINT == 0:
            additional_rows = 0
        else:
            additional_rows = BREAK_POINT - (len(emp_data) % BREAK_POINT)"""

        amount_in_words = amount_to_text_ar(total_nets, 'ar')
        res = {
            'emp_data': final_list_dept_row,
            #'headrs': header,
            #'allow_header': allow_header,
            #'deduct_header': deduct_header,
            'allow_deduct_totals': allow_deduct_totals,
            #'page_trans_totals': page_trans_totals,
            'BREAK_POINT': BREAK_POINT,
            #'page_trans_totals': lambda index: page_trans_totals[int(index / BREAK_POINT)],
            #'include_bascic_salary': include_bascic_salary,
            #'total_basics': round(total_basics, 2),
            #'transfer_total_basics': lambda index: transfer_total_basics[int(index / BREAK_POINT)],
            #'len_emp_data': len(emp_data),
            'transfer_total': lambda key, index: transfer_totals[key][int(index / BREAK_POINT)],
            #'include_allow_total': include_allow_total,
            #'include_deduct_total': include_deduct_total,
            #'include_net_total': include_net_total,
            'total_decre_allows': round(total_allow_dec, 2),
            'total_decre_deducts': round(total_dedu_dec, 2),
            'total_incre_allows': round(total_allow_inc, 2),
            'total_incre_deducts': round(total_dedu_inc, 2),
            'total_pre_nets': round(total_pre, 2),
            'total_curr_nets': round(total_curr, 2),
            #'department_title': department_title,
            #'allow_column_index': allow_column_index,
            #'basic_len': basic_len,
            #'allow_len': allow_len,
            #'deduct_len': deduct_len,
            #'additional_rows': additional_rows,
            'amount_in_words': amount_in_words,
        }
        return res

report_sxw.report_sxw('report.payroll.location.budget.report2', 'hr.allowance.deduction.archive','hr_payroll_custom/report/payroll_location_budget_report2.mako',parser=payroll_location_report2, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



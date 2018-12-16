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
from openerp.osv import fields, osv, orm
import math

BREAK_POINT = 24  # controll number of records in each page


class allowance_deduction_landscape(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(allowance_deduction_landscape, self).__init__(cr, uid, name, context)
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
            'allow': [],
            'deduct': [],
            'net': [],
        }

        res = []

        emp_condition = ""

        year = data['year']
        month = data['month']
        in_salary_sheet = True
        ad_type = data['type']  # allowance or deduction
        # paysheet = data['pay_sheet']
        # list_to_str = lambda items : ",".join(str(i) for i in items)
        company_id = data.get('company_id')
        # company_ids_str =list_to_str(company_id)
        ad_ids_condition = ""
        # if data['allow_deduct_ids']:
        #  ad_ids_condition = " and public.hr_allowance_deduction_archive.allow_deduct_id in (%s)" %(list_to_str(data['allow_deduct_ids']))
        ad_condition = ""
        # if ad_type :
        #  ad_condition = "and public.hr_allowance_deduction.name_type = '%s' "%(ad_type)


        if data['type'] == 'company' and data['company_idss']:
            # step 1 : get all employee in passed month , later get ids of passed employees
            if len(data['company_idss']) > 1:
                self.cr.execute(
                    '''
                    SELECT
                      hr_payroll_main_archive.company_id as company_id ,
                      public.res_company.name as company_name ,
                      sum(hr_payroll_main_archive.basic_salary) as basic_salary
                    FROM
                      public.res_company,
                      public.hr_payroll_main_archive
                    WHERE
                        hr_payroll_main_archive.company_id = res_company.id
                        AND hr_payroll_main_archive.month = %s
                        AND hr_payroll_main_archive.year = %s
                        AND public.hr_payroll_main_archive.in_salary_sheet= %s
                        AND public.hr_payroll_main_archive.company_id in %s
                      group by hr_payroll_main_archive.company_id, res_company.name
                    ''' % (month, year,in_salary_sheet,tuple(data['company_idss'])))
                comp_res = self.cr.dictfetchall()

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
                     AND public.hr_payroll_main_archive.company_id in %s
                     AND hr_employee.id = hr_payroll_main_archive.employee_id
                    order by public.hr_allowance_deduction.name_type , public.hr_allowance_deduction.sequence

                    ''' % (month, year,in_salary_sheet, tuple(data['company_idss'])))
                allow_deduct_res = self.cr.dictfetchall()

                # step 3 : get all allowaces/deductions for employees

                self.cr.execute(
                    '''
                    SELECT
                       hr_allowance_deduction_archive.allow_deduct_id ,
                       hr_payroll_main_archive.company_id ,
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
                      AND public.hr_payroll_main_archive.company_id in %s
                    GROUP by hr_payroll_main_archive.company_id, hr_allowance_deduction_archive.allow_deduct_id
                    ''' % (month, year,in_salary_sheet, tuple(data['company_idss'])))
                comp_allows_res = self.cr.dictfetchall()

            elif len(data['company_idss']) == 1:
                data['company_idss']=data['company_idss'][0]
                self.cr.execute(
                    '''
                    SELECT
                      hr_payroll_main_archive.company_id as company_id ,
                      public.res_company.name as company_name ,
                      sum(hr_payroll_main_archive.basic_salary) as basic_salary
                    FROM
                      public.res_company,
                      public.hr_payroll_main_archive
                    WHERE
                        hr_payroll_main_archive.company_id = res_company.id
                        AND hr_payroll_main_archive.month = %s
                        AND hr_payroll_main_archive.year = %s
                        AND public.hr_payroll_main_archive.in_salary_sheet= %s
                        AND public.hr_payroll_main_archive.company_id = %s
                      group by hr_payroll_main_archive.company_id, res_company.name
                    ''' % (month, year,in_salary_sheet,data['company_idss']))
                comp_res = self.cr.dictfetchall()

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
                     AND public.hr_payroll_main_archive.company_id = %s
                     AND hr_employee.id = hr_payroll_main_archive.employee_id
                    order by public.hr_allowance_deduction.name_type , public.hr_allowance_deduction.sequence

                    ''' % (month, year,in_salary_sheet,data['company_idss']))
                allow_deduct_res = self.cr.dictfetchall()

                # step 3 : get all allowaces/deductions for employees

                self.cr.execute(
                    '''
                    SELECT
                       hr_allowance_deduction_archive.allow_deduct_id ,
                       hr_payroll_main_archive.company_id ,
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
                      AND public.hr_payroll_main_archive.company_id = %s
                    GROUP by hr_payroll_main_archive.company_id, hr_allowance_deduction_archive.allow_deduct_id
                    ''' % (month, year, in_salary_sheet,data['company_idss']))
                comp_allows_res = self.cr.dictfetchall()

            # step 3 : check what I need to show in my report !!
            include_bascic_salary = in_salary_sheet and ad_type not in ['deduct']
            include_allow_total = ad_type not in ['deduct']
            include_deduct_total = ad_type not in ['allow']
            include_net_total = ad_type not in ['allow', 'deduct']
            # step 4 : prepare table data
            emp_data = []  # array for store employees data
            allow_deduct_totals = [0 for i in range(len(allow_deduct_res))]  # prepare array for store totals
            page_trans_totals = []  # array for transfer pages total to next page
            transfer_total_basics = []
            total_basics = 0
            total_comp_basic = 0
            total_allows = 0
            total_deducts = 0
            # for j , emp in enumerate(emp_res) :
            for j, emp in enumerate(comp_res):
                amounts = []
                allow_amounts = []
                deduct_amounts = []
                emp_total_allow = 0
                emp_total_deduct = 0
                for i, allow_deduct in enumerate(allow_deduct_res):
                    # amount_obj = filter(lambda arch : arch['employee_id'] == emp['emp_id'] and arch['allow_deduct_id'] == allow_deduct['allow_deduct_id'] , emp_allows_res)
                    amount_obj = filter(
                        lambda arch: arch['company_id'] == emp['company_id'] and arch['allow_deduct_id'] ==
                                                                                 allow_deduct['allow_deduct_id'],
                        comp_allows_res)
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
                total_comp_basic += emp['basic_salary']
                total_allows += emp_total_allow
                total_deducts += emp_total_deduct
                emp_row = {
                    'emp_name': emp['company_name'],
                    # 'emp_job' : emp['emp_job'],
                    # 'emp_degree':emp['emp_degree'],
                    'amounts': [round(am, 2) for am in amounts],
                    'basic_salary': emp['basic_salary'],
                    'emp_total_deduct': round(emp_total_deduct, 2),
                    'emp_total_allow': round(emp_total_allow, 2),
                    'emp_net': round(emp_total_allow - emp_total_deduct, 2),
                }
                # here checking break point for register total amounts of processed records
                if (j + 1) % BREAK_POINT == 0:
                    page_trans_totals.append([round(adt, 2) for adt in allow_deduct_totals])
                    transfer_total_basics.append(round(total_basics, 2))
                    transfer_totals['allow'].append(round(total_allows, 2))
                    transfer_totals['deduct'].append(round(total_deducts, 2))
                    transfer_totals['net'].append(round(total_allows - total_deducts, 2))
                emp_data.append(emp_row)

            total_nets = total_allows - total_deducts
            # step 5 : prepare allowances/deductions header
            header = []  # store headr list for eachpage
            allow_header = []
            deduct_header = []
            for allow_deduct in allow_deduct_res:
                header.append(allow_deduct['name'])
                if allow_deduct['name_type'] == 'allow':
                    allow_header.append(allow_deduct['name'])
                    allow_column_index += 1
                else:
                    deduct_header.append(allow_deduct['name'])
 
            basic_len = len(
                filter(lambda ad: ad['name_type'] == 'allow' and ad['is_basic_salary_item'], allow_deduct_res)) + 1
            allow_len = len(
                filter(lambda ad: ad['name_type'] == 'allow' and not ad['is_basic_salary_item'], allow_deduct_res))
            deduct_len = len(filter(lambda ad: ad['name_type'] == 'deduct', allow_deduct_res))
            if len(emp_data) % BREAK_POINT == 0:
                additional_rows = 0
            else:
                additional_rows = BREAK_POINT - (len(emp_data) % BREAK_POINT)

            amount_in_words = amount_to_text_ar(total_nets, 'ar')
            res = {
                'emp_data': emp_data,
                'headrs': header,
                'allow_header': allow_header,
                'deduct_header': deduct_header,
                'allow_deduct_totals': allow_deduct_totals,
                'page_trans_totals': page_trans_totals,
                'BREAK_POINT': BREAK_POINT,
                'page_trans_totals': lambda index: page_trans_totals[int(index / BREAK_POINT)],
                'include_bascic_salary': include_bascic_salary,
                'total_basics': round(total_basics, 2),
                'transfer_total_basics': lambda index: transfer_total_basics[int(index / BREAK_POINT)],
                'len_emp_data': len(emp_data),
                'transfer_total': lambda key, index: transfer_totals[key][int(index / BREAK_POINT)],
                'include_allow_total': include_allow_total,
                'include_deduct_total': include_deduct_total,
                'include_net_total': include_net_total,
                'total_allows': round(total_allows, 2),
                'total_deducts': round(total_deducts, 2),
                'total_nets': round(total_nets, 2),
                'department_title': department_title,
                'allow_column_index': allow_column_index,
                'basic_len': basic_len,
                'allow_len': allow_len,
                'deduct_len': deduct_len,
                'additional_rows': additional_rows,
                'amount_in_words': amount_in_words,
            }
        if (data['type'] == 'location' or data['type'] == 'department' )  and data['department_ids']:
            # step 1 : get all employee in passed month , later get ids of passed employees
            if len(data['department_ids']) > 1:
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
                    ''' % (month, year, in_salary_sheet,tuple(data['department_ids'])))
                dep_res = self.cr.dictfetchall()

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

                    ''' % (month, year,in_salary_sheet, tuple(data['department_ids'])))
                allow_deduct_res = self.cr.dictfetchall()

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
                dep_allows_res = self.cr.dictfetchall()
            if len(data['department_ids']) == 1:
                data['department_ids']=data['department_ids'][0]
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
                        AND public.hr_payroll_main_archive.department_id = %s
                      group by hr_payroll_main_archive.department_id, hr_department.name
                    ''' % (month, year,in_salary_sheet,data['department_ids']))
                dep_res = self.cr.dictfetchall()

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
                     AND public.hr_payroll_main_archive.department_id = %s
                     AND hr_employee.id = hr_payroll_main_archive.employee_id
                    order by public.hr_allowance_deduction.name_type , public.hr_allowance_deduction.sequence

                    ''' % (month, year,in_salary_sheet,data['department_ids']))
                allow_deduct_res = self.cr.dictfetchall()

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
                      AND public.hr_payroll_main_archive.department_id = %s
                    GROUP by hr_payroll_main_archive.department_id, hr_allowance_deduction_archive.allow_deduct_id
                    ''' % (month, year,in_salary_sheet,data['department_ids']))
                dep_allows_res = self.cr.dictfetchall()  

            # step 3 : check what I need to show in my report !!
            include_bascic_salary = in_salary_sheet and ad_type not in ['deduct']
            include_allow_total = ad_type not in ['deduct']
            include_deduct_total = ad_type not in ['allow']
            include_net_total = ad_type not in ['allow', 'deduct']
            # step 4 : prepare table data
            emp_data = []  # array for store employees data
            allow_deduct_totals = [0 for i in range(len(allow_deduct_res))]  # prepare array for store totals
            page_trans_totals = []  # array for transfer pages total to next page
            transfer_total_basics = []
            total_basics = 0
            total_allows = 0
            total_deducts = 0
            # for j , emp in enumerate(emp_res) :
            for j, emp in enumerate(dep_res):
                amounts = []
                allow_amounts = []
                deduct_amounts = []
                emp_total_allow = 0
                emp_total_deduct = 0
                for i, allow_deduct in enumerate(allow_deduct_res):
                    # amount_obj = filter(lambda arch : arch['employee_id'] == emp['emp_id'] and arch['allow_deduct_id'] == allow_deduct['allow_deduct_id'] , emp_allows_res)
                    amount_obj = filter(
                        lambda arch: arch['department_id'] == emp['department_id'] and arch['allow_deduct_id'] ==
                                                                                       allow_deduct['allow_deduct_id'],
                        dep_allows_res)
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
                    # 'emp_job' : emp['emp_job'],
                    # 'emp_degree':emp['emp_degree'],
                    'amounts': [round(am, 2) for am in amounts],
                    'basic_salary': emp['basic_salary'],
                    'emp_total_deduct': round(emp_total_deduct, 2),
                    'emp_total_allow': round(emp_total_allow, 2),
                    'emp_net': round(emp_total_allow - emp_total_deduct, 2),
                }
                # here checking break point for register total amounts of processed records
                if (j + 1) % BREAK_POINT == 0:
                    page_trans_totals.append([round(adt, 2) for adt in allow_deduct_totals])
                    transfer_total_basics.append(round(total_basics, 2))
                    transfer_totals['allow'].append(round(total_allows, 2))
                    transfer_totals['deduct'].append(round(total_deducts, 2))
                    transfer_totals['net'].append(round(total_allows - total_deducts, 2))
                emp_data.append(emp_row)

            total_nets = total_allows - total_deducts
            # step 5 : prepare allowances/deductions header
            header = []  # store headr list for eachpage
            allow_header = []
            deduct_header = []
            for allow_deduct in allow_deduct_res:
                header.append(allow_deduct['name'])
                if allow_deduct['name_type'] == 'allow':
                    allow_header.append(allow_deduct['name'])
                    allow_column_index += 1
                else:
                    deduct_header.append(allow_deduct['name'])

            basic_len = len(
                filter(lambda ad: ad['name_type'] == 'allow' and ad['is_basic_salary_item'], allow_deduct_res)) + 1
            allow_len = len(
                filter(lambda ad: ad['name_type'] == 'allow' and not ad['is_basic_salary_item'], allow_deduct_res))
            deduct_len = len(filter(lambda ad: ad['name_type'] == 'deduct', allow_deduct_res))
            if len(emp_data) % BREAK_POINT == 0:
                additional_rows = 0
            else:
                additional_rows = BREAK_POINT - (len(emp_data) % BREAK_POINT)

            amount_in_words = amount_to_text_ar(total_nets, 'ar')
            res = {
                'emp_data': emp_data,
                'headrs': header,
                'allow_header': allow_header,
                'deduct_header': deduct_header,
                'allow_deduct_totals': allow_deduct_totals,
                'page_trans_totals': page_trans_totals,
                'BREAK_POINT': BREAK_POINT,
                'page_trans_totals': lambda index: page_trans_totals[int(index / BREAK_POINT)],
                'include_bascic_salary': include_bascic_salary,
                'total_basics': round(total_basics, 2),
                'transfer_total_basics': lambda index: transfer_total_basics[int(index / BREAK_POINT)],
                'len_emp_data': len(emp_data),
                'transfer_total': lambda key, index: transfer_totals[key][int(index / BREAK_POINT)],
                'include_allow_total': include_allow_total,
                'include_deduct_total': include_deduct_total,
                'include_net_total': include_net_total,
                'total_allows': round(total_allows, 2),
                'total_deducts': round(total_deducts, 2),
                'total_nets': round(total_nets, 2),
                'department_title': department_title,
                'allow_column_index': allow_column_index,
                'basic_len': basic_len,
                'allow_len': allow_len,
                'deduct_len': deduct_len,
                'additional_rows': additional_rows,
                'amount_in_words': amount_in_words,
            }
        if data['type'] == 'state' and data['company_idss']:
            emp_data = []  # array for store employees data
            page_trans_totals = []  # array for transfer pages total to next page
            transfer_total_basics = []
            total_basics = 0
            total_allows = 0
            total_deducts = 0
            all_child_ids = self.pool.get('res.company').search(self.cr, self.uid,
                                                                [(('parent_id', '=', data['company_idss']))])
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
                 AND public.hr_payroll_main_archive.company_id in %s
                 AND hr_employee.id = hr_payroll_main_archive.employee_id
                order by public.hr_allowance_deduction.name_type , public.hr_allowance_deduction.sequence

                ''' % (month, year,in_salary_sheet, tuple(all_child_ids)))
            allow_deduct_res = self.cr.dictfetchall()
            allow_deduct_totals = [0 for i in range(len(allow_deduct_res))]  # prepare array for store totals
            pr=0
            for comp_id in data['company_idss']:
                pr+=1
                curr_com = self.pool.get('res.company').browse(self.cr, self.uid, comp_id).name
                # step 1 : get all employee in passed month , later get ids of passed employees
                # Get Child Company
                # make for to sum child company
                # define amount over for
                #print "parent>>>", data['company_idss']
                child_ids = self.pool.get('res.company').search(self.cr, self.uid, [(('parent_id', '=', comp_id))])
                #print "Child Comp>>>", child_ids
                if len(child_ids) >1:
                    self.cr.execute(
                        '''
                        SELECT
                          hr_payroll_main_archive.company_id as company_id ,
                          public.res_company.name as company_name ,
                          sum(hr_payroll_main_archive.basic_salary) as basic_salary
                        FROM
                          public.res_company,
                          public.hr_payroll_main_archive
                        WHERE
                            hr_payroll_main_archive.company_id = res_company.id
                            AND hr_payroll_main_archive.month = %s
                            AND hr_payroll_main_archive.year = %s
                            AND public.hr_payroll_main_archive.in_salary_sheet= %s
                            AND public.hr_payroll_main_archive.company_id in %s
                          group by hr_payroll_main_archive.company_id, res_company.name
                        ''' % (month, year, in_salary_sheet,tuple(child_ids)))
                    comp_res = self.cr.dictfetchall()
                    # print "basic>>>", comp_res
                    # step 2 : get all allowaces/deductions in passed month , later get ids of passed allowances/deductions

                    # print "Allow_deduct>>", allow_deduct_res

                    # step 3 : get all allowaces/deductions for employees

                    self.cr.execute(
                        '''
                        SELECT
                           hr_allowance_deduction_archive.allow_deduct_id ,
                           hr_payroll_main_archive.company_id ,
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
                          AND public.hr_payroll_main_archive.company_id in %s
                        GROUP by hr_payroll_main_archive.company_id, hr_allowance_deduction_archive.allow_deduct_id
                        ''' % (month, year, in_salary_sheet,tuple(child_ids)))
                    comp_allows_res = self.cr.dictfetchall()
                # print "Comp Allow_ded>>", comp_allows_res
                elif len(child_ids)==1:
                    child_ids=child_ids[0]
                    self.cr.execute(
                        '''
                        SELECT
                          hr_payroll_main_archive.company_id as company_id ,
                          public.res_company.name as company_name ,
                          sum(hr_payroll_main_archive.basic_salary) as basic_salary
                        FROM
                          public.res_company,
                          public.hr_payroll_main_archive
                        WHERE
                            hr_payroll_main_archive.company_id = res_company.id
                            AND hr_payroll_main_archive.month = %s
                            AND hr_payroll_main_archive.year = %s
                            AND public.hr_payroll_main_archive.in_salary_sheet= %s
                            AND public.hr_payroll_main_archive.company_id = %s
                          group by hr_payroll_main_archive.company_id, res_company.name
                        ''' % (month, year, in_salary_sheet,child_ids))
                    comp_res = self.cr.dictfetchall()
                    # print "basic>>>", comp_res
                    # step 2 : get all allowaces/deductions in passed month , later get ids of passed allowances/deductions

                    # print "Allow_deduct>>", allow_deduct_res

                    # step 3 : get all allowaces/deductions for employees

                    self.cr.execute(
                        '''
                        SELECT
                           hr_allowance_deduction_archive.allow_deduct_id ,
                           hr_payroll_main_archive.company_id ,
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
                          AND public.hr_payroll_main_archive.company_id = %s
                        GROUP by hr_payroll_main_archive.company_id, hr_allowance_deduction_archive.allow_deduct_id
                        ''' % (month, year,in_salary_sheet ,child_ids))
                    comp_allows_res = self.cr.dictfetchall()
                # step 3 : check what I need to show in my report !!
                include_bascic_salary = in_salary_sheet and ad_type not in ['deduct']
                include_allow_total = ad_type not in ['deduct']
                include_deduct_total = ad_type not in ['allow']
                include_net_total = ad_type not in ['allow', 'deduct']
                # step 4 : prepare table data
                # For All Company

                # for j , emp in enumerate(emp_res) :
                # Basic Salary>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.
                amounts = []
                allow_amounts = []
                deduct_amounts = []
                emp_total_allow = 0
                emp_total_deduct = 0
                total_company_basic = 0
                allow_deduct_com_totals = [0 for i in range(len(allow_deduct_res))]
                for j, emp in enumerate(comp_res):
                    # Alow Ded Name=Header>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                    for i, allow_deduct in enumerate(allow_deduct_res):
                        # amount_obj = filter(lambda arch : arch['employee_id'] == emp['emp_id'] and arch['allow_deduct_id'] == allow_deduct['allow_deduct_id'] , emp_allows_res)
                        amount_obj = filter(
                            lambda arch: arch['company_id'] == emp['company_id'] and arch['allow_deduct_id'] ==
                                                                                     allow_deduct['allow_deduct_id'],
                            comp_allows_res)
                        emp_amount = amount_obj and amount_obj[0]['amount'] or 0
                        if allow_deduct['name_type'] == 'allow':
                            emp_total_allow += emp_amount
                        else:
                            emp_total_deduct += emp_amount
                        allow_deduct_totals[i] = allow_deduct_totals[i] + emp_amount
                        allow_deduct_com_totals[i] = allow_deduct_com_totals[i] + emp_amount
                        amounts.append(emp_amount)
                    total_basics += emp['basic_salary']
                    total_company_basic += emp['basic_salary']
                    # emp_total_allow += include_bascic_salary and emp['basic_salary'] or 0
                    emp_total_allow += emp['basic_salary']
                total_allows += emp_total_allow
                total_deducts += emp_total_deduct
                # create company Row
                emp_row = {
                    'emp_name': curr_com,
                    # 'emp_job' : emp['emp_job'],
                    # 'emp_degree':emp['emp_degree'],
                    'amounts': allow_deduct_com_totals,
                    'basic_salary': total_company_basic,
                    'emp_total_deduct': round(emp_total_deduct, 2),
                    'emp_total_allow': round(emp_total_allow, 2),
                    'emp_net': round(emp_total_allow - emp_total_deduct, 2),
                }
                # here checking break point for register total amounts of processed records
                if (pr + 1) % BREAK_POINT == 0:
                    page_trans_totals.append([round(adt, 2) for adt in allow_deduct_totals])
                    transfer_total_basics.append(round(total_basics, 2))
                    transfer_totals['allow'].append(round(total_allows, 2))
                    transfer_totals['deduct'].append(round(total_deducts, 2))
                    transfer_totals['net'].append(round(total_allows - total_deducts, 2))
                # add Company Row
                emp_data.append(emp_row)

            total_nets = total_allows - total_deducts
            # step 5 : prepare allowances/deductions header
            header = []  # store headr list for eachpage
            allow_header = []
            deduct_header = []
            for allow_deduct in allow_deduct_res:
                header.append(allow_deduct['name'])
                if allow_deduct['name_type'] == 'allow':
                    allow_header.append(allow_deduct['name'])
                    allow_column_index += 1
                else:
                    deduct_header.append(allow_deduct['name'])

            basic_len = len(
                filter(lambda ad: ad['name_type'] == 'allow' and ad['is_basic_salary_item'], allow_deduct_res)) + 1
            allow_len = len(
                filter(lambda ad: ad['name_type'] == 'allow' and not ad['is_basic_salary_item'], allow_deduct_res))
            deduct_len = len(filter(lambda ad: ad['name_type'] == 'deduct', allow_deduct_res))
            if len(emp_data) % BREAK_POINT == 0:
                additional_rows = 0
            else:
                additional_rows = BREAK_POINT - (len(emp_data) % BREAK_POINT)

            amount_in_words = amount_to_text_ar(total_nets, 'ar')
            res = {
                'emp_data': emp_data,
                'headrs': header,
                'allow_header': allow_header,
                'deduct_header': deduct_header,
                'allow_deduct_totals': allow_deduct_totals,
                'page_trans_totals': page_trans_totals,
                'BREAK_POINT': BREAK_POINT,
                'page_trans_totals': lambda index: page_trans_totals[int(index / BREAK_POINT)],
                'include_bascic_salary': include_bascic_salary,
                'total_basics': round(total_basics, 2),
                'transfer_total_basics': lambda index: transfer_total_basics[int(index / BREAK_POINT)],
                'len_emp_data': len(emp_data),
                'transfer_total': lambda key, index: transfer_totals[key][int(index / BREAK_POINT)],
                'include_allow_total': include_allow_total,
                'include_deduct_total': include_deduct_total,
                'include_net_total': include_net_total,
                'total_allows': round(total_allows, 2),
                'total_deducts': round(total_deducts, 2),
                'total_nets': round(total_nets, 2),
                'department_title': department_title,
                'allow_column_index': allow_column_index,
                'basic_len': basic_len,
                'allow_len': allow_len,
                'deduct_len': deduct_len,
                'additional_rows': additional_rows,
                'amount_in_words': amount_in_words,
            }
            # print "Final RES>>>>>", res
        return res


report_sxw.report_sxw('report.allowance.deduction.custom.landscape', 'hr.allowance.deduction.archive',
                      'hr_payroll_custom/report/allowance_deduction_custom_landscape.mako',
                      parser=allowance_deduction_landscape, header=False)
report_sxw.report_sxw('report.allowance.deduction.custom.landscape.company', 'hr.allowance.deduction.archive',
                      'hr_payroll_custom/report/allowance_deduction_custom_landscape_company.mako',
                      parser=allowance_deduction_landscape, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


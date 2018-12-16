# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
import calendar
from datetime import datetime
import pooler
from openerp.tools.translate import _



def to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()


class allow_deduct_loan_sum(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.count = 0
        self.context = context
        super(allow_deduct_loan_sum, self).__init__(cr, uid, name, context)
        self.h_deps_ids = []
        self.localcontext.update({
            'all_len': self._get_all_len,
            'lines': self._get_lines,
            'get_count': self._get_count,
            'to_arabic': self._to_arabic,
        })
    
    def _to_arabic(self, data):
        key = _(data)
        key = key == 'v_good' and 'very good' or key
        key = key == 'u_middle' and 'under middle' or key
        if self.context and 'lang' in self.context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                self.cr, self.uid, [('module','=', 'hr_payroll_custom_niss'),('type','=', 'selection'),('src','ilike', key), ('lang', '=', self.context['lang'])], context=self.context)
            translation_recs = translation_obj.read(
                self.cr, self.uid, translation_ids, [], context=self.context)
            key = translation_recs and translation_recs[0]['value'] or key
        
        return key

    def _get_all_len(self, data):
        company_id = data['form']['company_id']
        payroll_ids = data['form']['payroll_ids']
        allow_ids = data['form']['allow_ids']
        deduct_ids = data['form']['deduct_ids']
        loan_ids = data['form']['loan_ids']
        month = data['form']['month']
        year = data['form']['year']
        type = data['form']['type']
        state_id = data['form']['state_id']


        clouses = False
        allow_clouses = False
        deduct_clouses = False
        loan_clouses = False

        
        if month:
            if clouses:
                clouses += " and pm.month='"+str(month)+"'"
            if not clouses:
                clouses = " pm.month='"+str(month)+"'"

        if year:
            if clouses:
                clouses += " and pm.year='"+str(year)+"'"
            if not clouses:
                clouses = " pm.year='"+str(year)+"'"
        
        if company_id:
            company_id += company_id
            company_id = tuple(company_id)
            if clouses:
                clouses += " and pm.company_id IN "+str(company_id)
            if not clouses:
                clouses = " pm.company_id IN "+str(company_id)
        
        if payroll_ids:
            payroll_ids += payroll_ids
            payroll_ids = tuple(payroll_ids)
            if clouses:
                clouses += " and pm.scale_id IN "+str(payroll_ids)
            if not clouses:
                clouses = " pm.scale_id IN "+str(payroll_ids)
        
        if state_id:
            if clouses:
                clouses += " and emp.payroll_state='"+str(state_id)+"'"
            if not clouses:
                clouses = " emp.payroll_state='"+str(state_id)+"'"
        
        allow_clouses = deduct_clouses = loan_clouses = clouses 

        if allow_clouses:
            allow_clouses += " and ad.name_type='allow'"
        if not allow_clouses:
            allow_clouses += " ad.name_type='allow'"

        if deduct_clouses:
            deduct_clouses += " and ad.name_type='deduct'"
        if not deduct_clouses:
            deduct_clouses += " ad.name_type='deduct'"

        if loan_clouses:
            loan_clouses += " and m.loan_amount is not null "
        if not loan_clouses:
            loan_clouses += " m.loan_amount is not null "

        if allow_ids:
            allow_ids += allow_ids
            allow_ids = tuple(allow_ids)
            if allow_clouses:
                allow_clouses += " and adr.allow_deduct_id in "+str(allow_ids)
            if not allow_clouses:
                allow_clouses = " adr.allow_deduct_id in "+str(allow_ids)
        
        if deduct_ids:
            deduct_ids += deduct_ids
            deduct_ids = tuple(deduct_ids)
            if deduct_clouses:
                deduct_clouses += " and adr.allow_deduct_id in "+str(deduct_ids)
            if not deduct_clouses:
                deduct_clouses = " adr.allow_deduct_id in "+str(deduct_ids)

        if loan_ids:
            loan_ids += loan_ids
            loan_ids = tuple(loan_ids)
            if loan_clouses:
                loan_clouses += " and b.loan_id in "+str(loan_ids)
            if not loan_clouses:
                loan_clouses = " b.loan_id in "+str(loan_ids)
        


        
        query = """SELECT ad.id, ad.name, 
                    sum(adr.amount-adr.tax_deducted) AS net 
                    FROM hr_allowance_deduction_archive adr 
                    LEFT JOIN hr_allowance_deduction ad ON (adr.allow_deduct_id=ad.id) 
                    LEFT JOIN hr_payroll_main_archive pm ON (adr.main_arch_id=pm.id) 
                    LEFT JOIN hr_employee emp ON (pm.employee_id=emp.id)
                    """

        if allow_clouses:
            query += "where "+allow_clouses
        query += " group by ad.id"

        self.cr.execute(query)
        res_allow = self.cr.dictfetchall()


        query = """SELECT sum(adr.amount-adr.tax_deducted) AS net 
                    FROM hr_allowance_deduction_archive adr 
                    LEFT JOIN hr_allowance_deduction ad ON (adr.allow_deduct_id=ad.id) 
                    LEFT JOIN hr_payroll_main_archive pm ON (adr.main_arch_id=pm.id) 
                    LEFT JOIN hr_employee emp ON (pm.employee_id=emp.id)
                    """

        if allow_clouses:
            query += "where "+allow_clouses

        self.cr.execute(query)
        res_allow_sum = self.cr.dictfetchall()


        query = """SELECT ad.id, ad.name, 
                    sum(adr.amount-adr.tax_deducted) AS net 
                    FROM hr_allowance_deduction_archive adr 
                    LEFT JOIN hr_allowance_deduction ad ON (adr.allow_deduct_id=ad.id) 
                    LEFT JOIN hr_payroll_main_archive pm ON (adr.main_arch_id=pm.id) 
                    LEFT JOIN hr_employee emp ON (pm.employee_id=emp.id)
                    """

        if deduct_clouses:
            query += "where "+deduct_clouses
        query += " group by ad.id"

        self.cr.execute(query)
        res_deduct = self.cr.dictfetchall()


        query = """SELECT sum(adr.amount-adr.tax_deducted) AS net 
                    FROM hr_allowance_deduction_archive adr 
                    LEFT JOIN hr_allowance_deduction ad ON (adr.allow_deduct_id=ad.id) 
                    LEFT JOIN hr_payroll_main_archive pm ON (adr.main_arch_id=pm.id) 
                    LEFT JOIN hr_employee emp ON (pm.employee_id=emp.id)
                    """

        if deduct_clouses:
            query += "where "+deduct_clouses

        self.cr.execute(query)
        res_deduct_sum = self.cr.dictfetchall()




        query = """SELECT sum(m.loan_amount) AS net, b.name AS name 
                    FROM  hr_payroll_main_archive AS pm 
                    left join hr_loan_archive AS m on (m.main_arch_id=pm.id) 
                    left join hr_employee_loan b on (m.loan_id=b.id) 
                    LEFT JOIN hr_employee emp ON (m.employee_id=emp.id)
                    """

        if loan_clouses:
            query += "where "+loan_clouses
        query += " group by b.name"

        self.cr.execute(query)
        res_loan = self.cr.dictfetchall()


        query = """SELECT sum(m.loan_amount) AS net 
                    FROM  hr_payroll_main_archive AS pm 
                    left join hr_loan_archive AS m on (m.main_arch_id=pm.id) 
                    left join hr_employee_loan b on (m.loan_id=b.id) 
                    LEFT JOIN hr_employee emp ON (m.employee_id=emp.id)
                    """

        if loan_clouses:
            query += "where "+loan_clouses

        self.cr.execute(query)
        res_loan_sum = self.cr.dictfetchall()


        query = """SELECT sum(basic_salary) as basic 
                    from hr_payroll_main_archive pm 
                    LEFT JOIN hr_employee emp ON (pm.employee_id=emp.id)
                    """

        if clouses:
            query += "where "+clouses

        self.cr.execute(query)
        res_basic = self.cr.dictfetchall()
        sum = 0.0
        final_res = []
        if type == 'allow':
            final_res = res_allow
            if 'net' in res_allow_sum[0] and res_allow_sum[0]['net']:
                final_res.append({'name':u'الإجمالي', 'net': res_allow_sum[0]['net']})

        elif type == 'deduct':
            final_res = res_deduct
            if 'net' in res_deduct_sum[0] and res_deduct_sum[0]['net']:
                final_res.append({'name':u'الإجمالي', 'net': res_deduct_sum[0]['net']})

        elif type == 'loan':
            final_res = res_loan
            if 'net' in res_loan_sum[0] and res_loan_sum[0]['net']:
                final_res.append({'name':u'الإجمالي', 'net': res_loan_sum[0]['net']})
        else:
            if res_basic:
                if 'basic' in res_basic[0] and res_basic[0]['basic']:
                    final_res.append({'name':u'اﻷساسي', 'net': res_basic[0]['basic']})
                    sum += res_basic[0]['basic']

            final_res += res_allow
            final_res += res_deduct
            final_res += res_loan
            if 'net' in res_allow_sum[0] and res_allow_sum[0]['net']:
                sum += res_allow_sum[0]['net']
            if 'net' in res_deduct_sum[0] and res_deduct_sum[0]['net']:
                sum -= res_deduct_sum[0]['net']
            if 'net' in res_loan_sum[0] and res_loan_sum[0]['net']:
                sum -= res_loan_sum[0]['net']

            final_res.append({'name':u'الإجمالي', 'net': sum})








        self.all_data = final_res
        
            
        return len(self.all_data)

    def _get_lines(self):
        return self.all_data

    def _get_count(self):
        self.count = self.count + 1
        return self.count


report_sxw.report_sxw('report.hr.allow_deduct_loan_sum.report', 'hr.employee',
                      'addons/hr_payroll_custom_niss/report/allow_deduct_loan_sum_report.mako', parser=allow_deduct_loan_sum, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import time
from datetime import datetime
from tools.translate import _


class allow_deduct_loan_sum_report_wizard(osv.osv_memory):
    _name = "allow_deduct_loan_sum_report.wizard"

    def _get_months(self, cr, uid, context):
        months=[(n,n) for n in range(1,13)]
        return months

    _columns = {
        'company_id': fields.many2many('res.company', 'allow_deduct_loan_sum_company_rel', 'report_id', 'company_id', 'Company'),
        'payroll_ids': fields.many2many('hr.salary.scale', 'allow_deduct_loan_sum_payroll_rel', 'pay_bonus', 'pay_id', 'Salary Scale'),
        'allow_ids': fields.many2many('hr.allowance.deduction', 'allow_deduct_loan_sum_allow_rel', 'report_id', 'allow_id', 'Allowances'),
        'deduct_ids': fields.many2many('hr.allowance.deduction', 'allow_deduct_loan_sum_deduct_rel', 'report_id', 'deduct_id', 'Deductions'),
        'loan_ids': fields.many2many('hr.loan', 'allow_deduct_loan_sum_loan_rel', 'report_id', 'loan_id', 'Loans'),
        'month': fields.selection(_get_months, "Month", required=True),
        'year': fields.integer("Year", required=True),
        'type': fields.selection([('allow', 'Allowance'), ('deduct', 'Deductions'), ('loan', 'Loans')], "Type"),
        'state_id': fields.selection([('khartoum', 'khartoum'), ('states', 'States')], "States or Khartoum", required=False),
    }

    def _default_company(self, cr, uid, context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    def _get_companies(self, cr, uid, context=None):
        return [self.pool.get('res.users').browse(cr, uid, uid).company_id.id]

    _defaults = {
        'year': int(time.strftime('%Y')),
        'month': int(time.strftime('%m')),
        'company_id': _get_companies,
    }

    def print_report(self, cr, uid, ids, context={}):
        data = {'form': self.read(cr, uid, ids, [])[0]}
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.allow_deduct_loan_sum.report', 'datas': data}

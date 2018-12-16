# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from datetime import date,datetime
from openerp.osv import osv, fields
from openerp.tools.translate import _


class operator_wizard(osv.osv_memory):
    _name = "operator.report"

    _description = "Operators Report"

    _columns = {
        'start_date':fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'customer_ids':fields.many2many('res.partner',string='Partners'),
        'account_ids':fields.many2many('account.account',string='Accounts'),
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'operator.report',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'operator_report.report',
            'datas': datas,
            }

    def print_collecting_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'operator.report',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'operator_collecting_report.report',
            'datas': datas,
            }
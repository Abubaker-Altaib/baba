# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp.osv import osv, fields

class account_analytic_balance(osv.osv_memory):
    
    _name = 'account.analytic.balance'
    _description = 'Account Analytic Balance'

    _columns = {
        'date1': fields.date('Start of period', required=True),
        'date2': fields.date('End of period', required=True),
        'empty_acc': fields.boolean('Empty Accounts ? ', help='Check if you want to display Accounts with 0 balance too.'),
    }

    _defaults = {
        'date1': lambda *a: time.strftime('%Y-01-01'),
        'date2': lambda *a: time.strftime('%Y-%m-%d')
    }
    def check_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'account.analytic.account',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.analytic.account.balance.arabic',
            'datas': datas,
            }
        
account_analytic_balance()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

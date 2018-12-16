# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields

class account_print_journal(osv.osv_memory):

    _inherit = "account.common.journal.report"
    _name = "account.account.statement.arabic"
    _description = 'Account Statement'

    _columns = {
        'sort_selection': fields.selection([('date', 'Date'), ('ref', 'Reference Number')], 'Entries Sorted By', required=True),
        'account_id': fields.many2one('account.account', 'Account', required=True, domain=[('type', '<>', 'view'), ('type', '<>', 'closed')]),
        'initial_balance': fields.boolean("Include initial balances",
                                    help='It adds initial balance row on report which display previous sum amount of debit/credit/balance'),
        'type_selection': fields.selection([('detailed', 'Detailed'), ('total', 'Total')], 'Report Type', required=True),
        'reverse': fields.boolean("With Reversed Moves"),
    }

    _defaults = {
        'sort_selection': 'date',
        'type_selection': 'detailed',
        'reverse': False,
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['sort_selection', 'account_id', 'initial_balance', 'type_selection', 'reverse' ],)[0])
        if data['form']['type_selection'] == 'detailed':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.statement.detailed', 'datas': data}
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.statement.total', 'datas': data}

account_print_journal()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

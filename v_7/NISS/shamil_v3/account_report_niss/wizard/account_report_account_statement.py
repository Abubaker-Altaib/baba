# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields

class account_print_journal(osv.osv_memory):

    _inherit = "account.account.statement.arabic"
    _name = "account.account.statement.total"
    _description = 'Account Statement'

    _columns = {
        'account_id': fields.many2one('account.account', 'Account',  domain=[('type', '<>', 'view'), ('type', '<>', 'closed')]),
    }


    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['sort_selection', 'account_id', 'initial_balance', 'type_selection', 'reverse' ],)[0])
        if data['form']['type_selection'] == 'detailed':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.statement.detailed.inherit', 'datas': data}
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.statement.total.inherit', 'datas': data}

account_print_journal()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields

class account_print_reconcile(osv.osv_memory):
    """
    Inherit common journal report to use for printing bank statement report
    """
    _inherit = "account.common.journal.report"

    _name = "account.account.reconcile"

    _description = 'Bank Reconcilation'

    _columns = {
        'close_balance': fields.boolean("Include Bank Balances", help=''),
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['close_balance'],)[0])
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.reconcile.statement', 'datas': data}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

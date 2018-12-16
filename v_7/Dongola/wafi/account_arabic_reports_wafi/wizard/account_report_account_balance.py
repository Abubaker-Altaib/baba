# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv

class account_balance_report(osv.osv_memory):
    """
    Inherited report to change service name (report rml) to print wafi report
    """
    _inherit = "account.balance.report"

    def _print_report(self, cr, uid, ids, data, context=None):
        res = super(account_balance_report,self)._print_report(cr, uid, ids, data, context=context)
        data = res['datas']
        if data['form']['acc_balances']:
            res.update({'report_name': 'account.account.just.balance.arabic.wafi'})
        else:
            res.update({'report_name': 'account.account.balance.arabic.wafi'})
        return res  


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

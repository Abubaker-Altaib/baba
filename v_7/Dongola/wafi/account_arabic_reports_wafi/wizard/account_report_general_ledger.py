# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv

class account_report_general_ledger(osv.osv_memory):
    """
    Inherited report to change service name (report rml) to print wafi report
    """
    _inherit = "account.report.general.ledger"

    def _print_report(self, cr, uid, ids, data, context=None):
        res = super(account_report_general_ledger,self)._print_report(cr, uid, ids, data, context=context)
        data = res['datas']
        if data['form']['landscape']:
            res.update({'report_name': 'account.general.ledger_landscape.arabic.wafi'})
        else:
            res.update({'report_name': 'account.general.ledger.arabic.wafi'})
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

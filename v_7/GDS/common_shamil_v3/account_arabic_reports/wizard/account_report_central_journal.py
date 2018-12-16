# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv

class account_central_journal(osv.osv_memory):
#    _name = 'account.central.journal.arabic'
#    _description = 'Account Central Journal'
    _inherit = "account.central.journal"

    def _print_report(self, cr, uid, ids, data, context=None):
        res = super(account_central_journal, self)._print_report(cr, uid, ids, data, context=context)
        res.update({'report_name': 'account.central.journal.arabic'})
        return res


account_central_journal()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
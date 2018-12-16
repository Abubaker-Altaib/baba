# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv

class account_general_journal(osv.osv_memory):
    _inherit = "account.general.journal"
#    _name = 'account.general.journal.arabic'
#    _description = 'Account General Journal'

    def _print_report(self, cr, uid, ids, data, context=None):
        res = super(account_general_journal, self)._print_report(cr, uid, ids, data, context=context)
        res.update({'report_name': 'account.general.journal.arabic'})
        return res

account_general_journal()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields

class account_print_journal(osv.osv_memory):
    _inherit = "account.print.journal"

    _defaults = {
        'sort_selection': 'date',
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        res = super(account_print_journal,self)._print_report(cr, uid, ids, data, context=context)
        res.update({'report_name': 'account.journal.period.print.arabic'})
        return res

account_print_journal()
#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
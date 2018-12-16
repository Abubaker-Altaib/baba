# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields

class account_common_journal_report(osv.osv_memory):
#    _description = 'Account Common Journal Report'
    _inherit = 'account.common.journal.report'
#    _columns = {
#        'amount_currency': fields.boolean("With Currency", help="Print Report with the currency column if the currency is different then the company currency"),
#               }

    def _build_context(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = super(account_common_journal_report, self)._build_context(cr, uid, ids, data, context=context)
        if data['form']['filter'] == 'filter_date':
            cr.execute('SELECT period_id FROM account_move_line WHERE date >= %s AND date <= %s', (data['form']['date_from'], data['form']['date_to']))
            result['periods'] = map(lambda x: x[0], cr.fetchall())
        return result


account_common_journal_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

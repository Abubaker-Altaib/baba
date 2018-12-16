# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields

class account_common_account_report(osv.osv_memory):
#    _name = 'account.common.account.report'
#    _description = 'Account Common Account Report'
    _inherit = "account.common.report"
    _columns = {
        'display_account': fields.selection([('bal_all', 'All'), ('bal_movement', 'With movements'),
                                            ('bal_solde', 'With balance is not equal to 0'),
                                            ], 'Display accounts', required=True),

    }
    _defaults = {
        'display_account': 'bal_all',
    }

    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data['form'].update(self.read(cr, uid, ids, ['display_account'], context=context)[0])
        return data

account_common_account_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

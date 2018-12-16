# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv

class account_common_account_report(osv.osv_memory):
    #TODO: useless should delete
    _name = 'account.common.account.balance.report'

    _description = 'Account Common Account Balance Report'

    _inherit = "account.common.account.report"
#    _columns = {
#        'display_account': fields.selection([('bal_all', 'All Accounts'), ('bal_movement', 'Parents Accounts'), ('bal', 'With Balance not equal Zero'),
#                                            ('bal_solde', 'By Categories'),
#                                            ], 'Display accounts', required=True),
#
#               }
#    _defaults = {
#        'display_account': 'bal_all',
#    }
#
#    def pre_print_report(self, cr, uid, ids, data, context=None):
#        if context is None:
#            context = {}
#        data['form'].update(self.read(cr, uid, ids, ['display_account'], context=context)[0])
#        return data


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

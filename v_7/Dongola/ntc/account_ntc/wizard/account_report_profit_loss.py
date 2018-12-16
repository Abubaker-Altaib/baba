# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields

class account_pl_report(osv.osv_memory):
    """
    This wizard will provide the account profit and loss report by periods, between any two dates.
    """
    _inherit = "account.common.account.report"
    _name = "account.pl.report.arabic"
    _description = "Account Profit And Loss Report"
    _columns = {
        'display_account': fields.selection([('bal_all','All'), ('bal_movement','With movements'),
                                            ('bal_solde','With balance is not equal to 0'),
                                            ],'Display accounts', required=True, readonly=True),
        'display_type': fields.boolean("Landscape Mode"),
        'regular_account': fields.boolean("Regular Account"),
    }

    _defaults = {
        'display_account':'bal_solde',
        'display_type': True,     
        'regular_account': True,
        'target_move': 'all'
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['display_type', 'regular_account'])[0])
        
        if data['form']['display_type']:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'pl.account.horizontal.arabic',
                'datas': data,
            }
        else:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'pl.account.arabic',
                'datas': data,
            }

account_pl_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

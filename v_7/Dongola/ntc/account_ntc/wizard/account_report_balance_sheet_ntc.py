# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields
#from tools.translate import _

class account_bs_report(osv.osv_memory):
    """
    This wizard will provide the account balance sheet report by periods, between any two dates.
    """
    _name = 'account.bs.report.ntc'
    _inherit = "account.common.account.report"
    _description = 'Account Balance Sheet Report'
   
    _columns = {
        'display_account': fields.selection([('bal_all','All'), ('bal_movement','With movements'),
                                            ('bal_solde','With balance is not equal to 0'),
                                            ],'Display accounts', required=True),
        'display_type': fields.boolean("Landscape Mode"),
        'regular_account': fields.boolean("Regular Accounts"),
    }

    _defaults={
        'display_account':'bal_solde',
        'display_type': True,
        'regular_account': False,
        'target_move': 'all',
        #'journal_ids': [],
        #'reserve_account_id': _get_def_reserve_account,
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data['form'].update(self.read(cr, uid, ids, ['display_type',  'regular_account'])[0])
        #if not data['form']['reserve_account_id']:
            #raise osv.except_osv(_('Warning'),_('Please define the Reserve and Profit/Loss account for current user company !'))
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        if data['form']['display_type']:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.balancesheet.horizontal.ntc',
                'datas': data,
            }
       
account_bs_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

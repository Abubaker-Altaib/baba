# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class account_balance_report(osv.osv_memory):
    """
    Inherit balance report wizard to add some displaying options:
        * Print the report for specific accounts
        * Display initial balance
        * Display balances as Dr (positive balance) & Cr (negative balance)
        * Display all accounts or just view account or accounts with balance only or the main categories accounts 
    """
    _inherit = "account.balance.report"

    _columns = {
        'display_account': fields.selection([('bal_all','All Accounts'), ('bal_movement','Parents Accounts'),('bal','With Balance not Equal Zero'),
                                            ('bal_solde','By Categories'), ],'Display accounts', required=True,readonly=True),
        'unit': fields.selection([('balance','balance'),('assist','assist'),('normal','normal'),('common','common'),('consol','consol'),('consol_sub','consol_sub'),('asset','asset'),
                                             ],'Report Type',),
        'moves': fields.boolean('With Moves'),
        'initial_balance': fields.boolean('Initial Balance Column',readonly=True),
        'acc_balances':fields.boolean('With Just Balances',invisible=True),
        'account_ids': fields.many2many('account.account', 'account_common_account_rel', 'account_id_6_1', 'account_id', 'Accounts',domain="[('parent_id', 'child_of', chart_account_id)]"),
    }

    _defaults = {
        'display_account': 'bal_all',
        'target_move': 'all',
        'unit': 'balance',
        'moves': False,
        'initial_balance': True,
        'acc_balances': False,
    }

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear=False, context=None):
        res = {}
        if not fiscalyear:
            res['value'] = {'initial_balance': False}
        return res

    def onchange_display_account(self, cr, uid, ids, display_account='False', context=None):
        res = {}
        if display_account != 'bal':
            res['value'] = {'acc_balances': False}
        return res

     


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

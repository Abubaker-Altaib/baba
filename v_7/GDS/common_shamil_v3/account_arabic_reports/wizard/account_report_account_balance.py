# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class account_balance_report(osv.osv_memory):
    
    _inherit = "account.balance.report"

    _columns = {
                'display_account': fields.selection([('bal_all','All Accounts'), ('bal_movement','Parents Accounts'),('bal','With Balance not Equal Zero'),
                                            ('bal_solde','By Categories'), ],'Display accounts', required=True),
        'moves': fields.boolean('With Moves'),
        'initial_balance': fields.boolean('Initial Balance Column'),
        'acc_balances':fields.boolean('With Just Balances'),
        'account_ids': fields.many2many('account.account', 'account_common_balance_account_rel', 'account_bal_id', 'account_id', 'Accounts'),
    }

    _defaults = {
        'display_account': 'bal_all',
        'moves': False,
        'initial_balance': False,
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
     
    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['moves', 'initial_balance', 'account_ids', 'acc_balances', 'landscape'])[0])
        #if not data['form']['fiscalyear_id']:  # GTK client problem onchange does not consider in save record
        #    data['form'].update({'initial_balance': False})
        if data['form']['acc_balances']:
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.just.balance.arabic', 'datas': data}
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance.arabic', 'datas': data}

account_balance_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

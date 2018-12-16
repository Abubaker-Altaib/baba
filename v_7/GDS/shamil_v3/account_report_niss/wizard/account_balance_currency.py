# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields

class account_balance_currency(osv.osv_memory):

    _inherit = "account.balance.report"
    _description = 'Account Balance'

    _columns = {
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'display_account': fields.selection([('bal_all','All Accounts'),('with_currency','with currency'), ('bal_movement','Parents Accounts'),('bal','With Balance not Equal Zero'),
                                            ('bal_solde','By Categories'), ],'Display accounts', required=True),
        'moves': fields.boolean('With Moves'),
        'initial_balance': fields.boolean('Initial Balance Column'),
        'acc_balances':fields.boolean('With Just Balances'),
        'account_ids': fields.many2many('account.account', 'account_common_balance_account_rel', 'account_bal_id', 'account_id', 'Accounts'),
        'all_account': fields.boolean('All account'),
        'account_id': fields.many2one('account.account', 'Account'),
    }

    _defaults = {
        'display_account': 'bal_all',
        'moves': False,
        'initial_balance': False,
        'acc_balances': False,
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['initial_balance','currency_id', 'moves', 'acc_balances', 'account_ids', 'display_account', 'all_account','account_id'],)[0])

        if data['form']['acc_balances']:
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.just.balance.arabic', 'datas': data}
        if data['form']['display_account']=='with_currency':
           return {'type': 'ir.actions.report.xml', 'report_name': 'account.trial.balance', 'datas': data}
        if data['form']['display_account']=='bal_all':
           return {'type': 'ir.actions.report.xml', 'report_name': 'account.balance.arabic.inherit', 'datas': data}
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance.arabic', 'datas': data}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

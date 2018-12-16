# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class account_report_general_ledger(osv.osv_memory):
    """
    Inherit general ledger wizard to provide the report for specific accounts & 
    ability to print it with or without journal items, beside the ability to grouping journal items by analytic account
    """
    _inherit = "account.report.general.ledger"

    _columns= {
        'move': fields.boolean('With Move'),
        'account_ids': fields.many2many('account.account', 'account_common_account_rel2', 'account_id1', 'account_id2', 'Accounts'),
        'analytic_account_ids': fields.many2many('account.analytic.account','gen_led_analytic_rel2','gn_ldgr_pr_id','analytic_ch_id','Analytic Accounts'),
        'analytic_view': fields.boolean('Analytic view'),

              }
    _defaults = {
        'amount_currency': False,
        'move': True,
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        res = super(account_report_general_ledger,self)._print_report(cr, uid, ids, data, context=context)
        data = res['datas']
        data['form'].update(self.read(cr, uid, ids, ['move','account_ids','analytic_view','analytic_account_ids'])[0])
        if data['form']['landscape'] and not data['form']['analytic_view']:
            res.update({'report_name': 'account.general.ledger_landscape.arabic'})
        elif data['form']['analytic_view']:
            res.update({'report_name': 'account.general.ledger.analytic'})
        else:
            res.update({'report_name': 'account.general.ledger.arabic'})
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

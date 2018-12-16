# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class account_partner_balance(osv.osv_memory):
    """
        Inherit partner balance wizard to provide the partner balance report by periods, between any two dates.
    """
    _inherit = 'account.partner.balance'

    _columns = {
        'acc_ids': fields.many2many('account.account', 'account_common_partner_balance_account_rel', 'partner_bal_id', 'account_id', 'Accounts', required=True),
        'partner_ids': fields.many2many('res.partner', 'account_partner_balance_partner_rel', 'partner_bal_id', 'partner_id', 'Partners'),
    }

    def _get_partner(self, cr, uid, context=None):
        return self.pool.get('res.partner').search(cr, uid, [], context=context)

    def onchange_partner_account(self, cr, uid, ids, result_selection='customer', chart_account_id= -1, context=None):
        res = {}
        result = ['receivable']
        account_obj = self.pool.get('account.account')
        if result_selection == 'supplier':
            result = ['payable']
        elif result_selection == 'customer_supplier':
            result = ['receivable', 'payable']
        children = account_obj._get_children_and_consol(cr, uid, chart_account_id)
        res['value'] = {'acc_ids': account_obj.search(cr, uid, [('id', 'in', tuple(children)), ('type', 'in', tuple(result))], context=context)}
        return res

    def onchange_chart_id(self, cr, uid, ids, chart_account_id= -1, context=None):
        res = {}
        if chart_account_id:
            account_obj = self.pool.get('account.account')
            children = account_obj._get_children_and_consol(cr, uid, chart_account_id, context=context)
            company_id = self.pool.get('account.account').browse(cr, uid, chart_account_id, context=context).company_id.id
            res['value'] = {'company_id': company_id, 'acc_ids': account_obj.search(cr, uid, [('id', 'in', tuple(children)),('type','not in',('view','consolidation'))], context=context)}
        return res 

    _defaults = {
        'display_partner': 'non-zero_balance',
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        res = super(account_partner_balance, self)._print_report(cr, uid, ids, data, context=context)
        data = res['datas']
        data['form'].update(self.read(cr, uid, ids, ['acc_ids', 'initial_balance', 'partner_ids'])[0])
        res.update({'datas':data, 'report_name': 'account.partner.balance.arabic'})
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields

class account_print_journal(osv.osv_memory):

    _inherit = "account.account.statement.arabic"

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic account'),
    }

    def onchange_currency_id(self, cr, uid, ids,currency_id):
        """ 
        Change the field amount currency to true when select currency.
 
        @param currency_id: Changed currency id
        @return: Dictionary of values of amount_currency field
        """
        res = {}
        if currency_id:
            result= {'amount_currency': True}
            res = {'value': result}
        return res

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['sort_selection', 'account_id', 'initial_balance', 'type_selection', 'reverse','partner_id','currency_id','analytic_account_id'],)[0])
        if data['form']['type_selection'] == 'detailed':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.statement.detailed.inherit', 'datas': data}
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.statement.total', 'datas': data}

account_print_journal()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

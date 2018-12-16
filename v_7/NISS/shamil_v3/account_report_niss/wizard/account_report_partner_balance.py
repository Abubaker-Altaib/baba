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
        This wizard will provide the partner balance report by periods, between any two dates.
    """
    _inherit = 'account.partner.balance'

    def onchange_chart_id(self, cr, uid, ids, chart_account_id= -1, context=None):
        res = {}
        if chart_account_id:
            account_obj = self.pool.get('account.account')
            children = account_obj._get_children_and_consol(cr, uid, chart_account_id, context=context)
            company_id = self.pool.get('account.account').browse(cr, uid, chart_account_id, context=context).company_id.id
            #Remove defaults accounts from report
            res['value'] = {'company_id': company_id,}
        return res 

account_partner_balance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

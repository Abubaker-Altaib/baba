# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class account_budget_update(osv.osv_memory):
    """
	Wizard object to allow user closing more one budget in same time. 
	"""

    _name = "account.budget.update"
    _description = 'Budget update'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', type='many2one', required="True"),
        'analytic_account_ids': fields.many2many('account.analytic.account', 'account_update_analytic_account_rel', 
                                                 'budget_report_id', 'analytic_account_id', 'Cost Centers', required="True"),
                                                 
        'period_id': fields.many2one('account.period', 'Period', type='many2one', required="True"),
    }

    _defaults = {
            'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
    }
    
    def onchange_company_id(self, cr, uid, ids):
       """
		Method to reset the analytic_account_ids and period_id field to False
        Whenever user change the company field

        @return: dictionary of values of fields to be updated
       """

       return {'value': {'analytic_account_ids':False,'period_id':False}}

    def update(self, cr, uid, ids, context={}):
        """
		Method to do the action of closing selected budget based on selected 
        analytic accounts and selected periods.

        @return: dictionary that perform closing the wizard action
        """
        ids = not isinstance(ids, list) and [ids] or ids
        budget_obj = self.pool.get('account.budget.lines')
        wiz = self.browse(cr, uid, ids, context=context)[0]
        budget_ids = budget_obj.search(cr, uid, 
                [('analytic_account_id', 'in', [analytic_account.id for analytic_account in wiz.analytic_account_ids]),
                 ('period_id','=',wiz.period_id.id)], context=context)
        for l in budget_obj.browse(cr, uid, budget_ids,  context=context):
            budget_obj.write(cr, uid, l.id, {'code':l.code}, context=context)
        return {'type':'ir.actions.act_window_close'}




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

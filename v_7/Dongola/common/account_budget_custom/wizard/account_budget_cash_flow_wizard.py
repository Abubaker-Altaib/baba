# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import time

class account_budget_cash_flow_wizard(osv.osv_memory):
    """
    Object to divide to fiscal budget into selected periods.
    """
    _name = "account.budget.cash.flow.wizard"

    _description = 'Budget Flow'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'chart_analytic_account_id': fields.many2one('account.analytic.account', 'Chart of Cost Center', 
                                                     help='Select Charts of Cost Centers', required=True,
                                                     domain = [('parent_id','=',False)] ),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscalyear', required=True),
        'analytic_account_ids': fields.many2many('account.analytic.account', 'account_cash_flow_analytic_account_rel', 
                                                 'budget_cash_flow_id', 'analytic_account_id', 'Cost Centers', required=True),
        'account_ids': fields.many2many('account.account', 'account_cash_flow_account_rel',
                                        'budget_cash_flow_id', 'account_id', 'Accounts', required=True),
        'period_ids': fields.many2many('account.period', 'account_cash_flow_account_period_rel',
                                        'budget_cash_flow_id', 'account_period_id', 'Periods', required=True),
    }

    def _get_fiscalyear_id(self, cr, uid, company_id=False, context=None):
        """Method to return fiscal year based on current system time and company send

        @param company_id: ID of the company 
        @return: ID of fiscal year or boolean False
        """
        now = time.strftime('%Y-%m-%d')
        fiscalyear = company_id and self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now),
                                                                          ('company_id', '=', company_id)], context=context, limit=1)
        return fiscalyear and fiscalyear[0] or False

    def _get_analytic_account(self, cr, uid, context=None):
        """
        Method to get default value of field analytic by searching the 
        analytic account based on the user company 

        @return: analytic ID or boolean False
        """
       
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        dummy, analytic_account_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_custom', 'normal_analytic_account')
        return analytic_account_id

    _defaults = {
        'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
        'chart_analytic_account_id': _get_analytic_account,
    }

    def onchange_fiscalyear_id(self, cr, uid, ids, context=None):
        """
        Method to reset the value of periods field to False whenever any 
        change on fiscalyear happens

        @return: dictionary of values of fields to be updated
        """

        return {'value': {'period_ids': False}}

    def onchange_analytic_chart(self, cr, uid, ids, context=None):
        """
        Method to reset the value of ananlytic accounts field to False whenever any 
        change on analytic chart happens

        @return: dictionary of values of fields to be updated
        """
        return {'value': {'analytic_account_ids': False}}

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        """
        Method to reset the value of accounts and periods fields to False
        and to set fiscal year whenever any change on company happens.

        @return: dictionary of values of fields to be updated
        """
        return {'value': {'fiscalyear_id': self._get_fiscalyear_id(cr, uid, company_id, context=context),
                          'analytic_account_ids': False, 'account_ids': False, 'period_ids': False}}

    def compute(self, cr, uid, ids, context=None):
        """
        Method to do the action of equaly dividing selected account and fiscal budget into 
        selected periods.

        @return: dictionary that perform closing the wizard action
        """
        fiscalyear_budget_pool = self.pool.get('account.fiscalyear.budget')
        wiz = self.read(cr, uid, ids, [], context=context)[0]
        fiscalyear_id = wiz['fiscalyear_id'][0]
        analytic_account_ids = wiz['analytic_account_ids']
        account_ids = wiz['account_ids']
        period_ids = wiz['period_ids']

        FY_budget_ids = fiscalyear_budget_pool.search(cr, uid, [('fiscalyear_id', '=', fiscalyear_id),
                                                                ('analytic_account_id', 'in', analytic_account_ids)], context=context)
        fiscalyear_budget_pool.budget_flow(cr, uid, FY_budget_ids, period_ids, account_ids, context=context)
        return {'type':'ir.actions.act_window_close'}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

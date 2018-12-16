# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc

class account_budget_operation(osv.Model):
    """
    Account Budget Operation.
    Allow accountant to transfer special amount from multiple budget lines to another for cash/plan budgets, Beside budget increase operation.   
    """
    _inherit = "account.budget.operation"

    _columns = {

        'budget_type': fields.selection([('plan', 'Plan Budget'), ('cash', 'Cash Budget')],'Budget Type', 
                                        required=True, readonly=True, states={'draft':[('readonly', False)]}),
    }

    _defaults = {

        'budget_type': 'plan',

    }
    def complete(self, cr, uid, ids, context={}):
        """
        Workflow function change state to complete and compute amount value & set operation number
        @return: True
        """
        budget_pool = self.pool.get('account.budget')
        budget_line_pool = self.pool.get('account.budget.lines')
        for r in self.browse(cr, uid, ids, context=context):
            if r.type=='transfer' and not r.line_ids:
                raise osv.except_osv(_('Error!'),_('You cannot complete Transfer Operations without any Budget line.'))
            if r.budget_type=='cash':
                budget_ids = budget_pool.search(cr, uid,[('analytic_account_id', '=', r.analytic_account_id.id), 
                                                       ('period_id', '=', r.period_id.id)], context=context)
                budget_line_id = budget_line_pool.search(cr, uid,[('general_account_id', '=', r.account_id.id), 
                                                                 ('account_budget_id', 'in', tuple(budget_ids))], context=context)
                if budget_line_id:
                     line=budget_line_pool.browse(cr, uid, budget_line_id, context=context)[0]
                     if line.planned_amount+line.total_operation < line.cash_total_operation + r.amount:
                        raise orm.except_orm(_('Error!'),
                            _("Cash budget (%s) can't be more than planned budget (%s)!") % \
                             ( line.cash_total_operation+ r.amount,line.planned_amount+line.total_operation ,))
                     if line.cash_residual_balance + r.amount <=0:
                        raise orm.except_orm(_('Error!'),
                            _("The amount you try to transfer (%s) is more than %s residual (%s)!") % \
                             (r.amount, line.name, line.cash_residual_balance,))
                for e in r.line_ids:
                    if line.planned_amount+line.total_operation < line.cash_total_operation - r.amount:
                        raise orm.except_orm(_('Error!'),
                            _("Cash budget (%s) can't be more than planned budget (%s)!") % \
                             ( e.cash_total_operation- r.amount,line.planned_amount+line.total_operation ,))
                    if e.line_id.cash_residual_balance - e.amount <=0:
                        raise orm.except_orm(_('Error!'),
                            _("The amount you try to transfer (%s) is more than %s residual (%s)!") % \
                             (e.amount, e.line_id.name, e.line_id.cash_residual_balance,))
                return self.write(cr, uid, ids,{'state':'complete','name': r.name == '/' and 
                                     self.pool.get('ir.sequence').get(cr, uid, 'account.budget.operation') or 
                                     r.name, 'amount': r.type=='increase' and r.amount or sum([l.amount for l in r.line_ids])}, context=context)
                
        return super(account_budget_operation, self).complete(cr, uid, ids, context=context)
    def done(self, cr, uid, ids, context=None):
        """
        Execute the operation by calling transfer function in budget line and change state to done.
        """
        budget_line = self.pool.get('account.budget.lines')
        budget_line_id = False       
        for r in self.browse(cr, uid, ids, context=context):
            to = {'analytic_account': r.analytic_account_id.id,
                  'account_id': r.account_id.id,
                  'period_id': r.period_id.id,
                  'company': r.company_id.id,
                  'amount' : r.amount
                  }
                  
            budget_line_id ,history_ids=budget_line.transfer(cr, uid, {'type':r.type, 'budget_type':r.budget_type, 'line_ids': r.line_ids, 'to':to, 'reference':self._name+','+str(r.id)}, context=context)
        return self.write(cr, uid, ids,{'state':'done', 'budget_line':budget_line_id}, context=context)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

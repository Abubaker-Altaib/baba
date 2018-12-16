# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp import netsvc
from openerp.tools.translate import _
from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp

class account_budget_operation(osv.Model):
    """
    Account Budget Operation.
    Allow accountant to transfer special amount from multiple budget lines to another for plan budgets, Beside budget increase operation.   
    """
    _name = "account.budget.operation"
    
    _description = 'Budget Operations'

    def _get_period(self, cr, uid, context=None):
        """
		Method to get period ID

        @return: period ID or False
        """
        periods = self.pool.get('account.period').find(cr, uid, context=context)
        return periods and periods[0] or False

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        
        'type': fields.selection([('transfer', 'Transfer'), ('increase', 'Increase')],'Operation Type', 
                                 required=True, readonly=True, states={'draft':[('readonly', False)]}),
        
        'from_company_id': fields.many2one('res.company', 'Details Company', required=True, readonly=True, 
                                           states={'draft':[('readonly', False)]}),

        'analytic_account_id': fields.many2one('account.analytic.account', 'Cost Center', required=True, 
                                                  readonly=True, states={'draft':[('readonly', False)]}),

        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True, 
                                         states={'draft':[('readonly', False)]}),

        'account_id': fields.many2one('account.account', 'Account', required=True, readonly=True, 
                                         states={'draft':[('readonly', False)]}),

        'period_id': fields.many2one('account.period', 'Period', required=True, readonly=True, 
                                        states={'draft':[('readonly', False)]}),
        
        'amount':fields.float('Amount', digits_compute=dp.get_precision('Account'), readonly=True, 
                                 states={'draft':[('readonly', False)]}, help="If the it's positive that's mean the amount  will increase this budget or it will decrease it."),

        'budget_line': fields.many2one('account.budget.lines', 'Budget Line'),
    
        'line_ids': fields.one2many('account.budget.operation.line', 'operation_id', 'Details',
                                      readonly=True, states={'draft':[('readonly', False)]}),
        
        'state' : fields.selection([('draft', 'Draft'), ('complete', 'Waiting for Financial Manager Confirm'), 
                                    ('confirm', 'Waiting for General Manager Approve'), ('approve', 'Waiting for Execution'),
                                    ('done','Done'), ('cancel', 'Canceled')], 'Status', required=True, readonly=True),
    }

    _defaults = {
        'name': '/',
        'state': 'draft',
        'type': 'transfer',
        'from_company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
        'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
    } 
    _sql_constraints = [('amount_check', "CHECK ( (type='transfer') OR (amount > 0) )",  _("Wrong amount, they must be positive")),
                        
    ]
    def unlink(self, cr, uid, ids, context = None):
        for s in self.read(cr, uid, ids, ['state'], context = context):
            if s['state'] != 'draft':
                raise orm.except_orm(_('Invalid action !'), _('Can not  delete none draft  operation !'))
        return super(account_budget_operation, self).unlink(cr, uid, ids, context = context)

    def onchange_company_id(self, cr, uid, ids, company):
        """ 
		On change method when change the from/to company fields then 
        reset from_budget_line to False when from_company_id changed
        reset fields corresponding to company_to when to_company_id changed
        
        @param company: char 'from' or 'to'
        @return: dictionary of values to be change
        """
        return {'value': company == 'from' and {'from_budget_line':False} or
                        {'analytic_account_id':False, 'account_id':False, 
                         'period_id':self._get_period(cr, uid)}}

    def onchange_line_ids(self, cr, uid, ids, line_ids):
        """ 
		On change used to update to_amount when any change happened in 
            the account.budget.operation.line corresponding to account.budget.operation
            record
        
        @param line_ids: list of tuple of the all operation line values
        @return: dictionary of to_amount value to be change
        """
        return {'value': {'amount': sum([l[2]['amount'] for l in line_ids if l[2]])}}

    def onchange_ttype(self, cr, uid, ids, ttype):
        line_pool = self.pool.get('account.budget.operation.line')
        if ttype=='increase':
           line_ids = ids and line_pool.search(cr, uid, [('operation_id', '=', ids[0])]) or False
           if line_ids:
                line_pool.unlink(cr, uid, line_ids)
                return{'value': {'line_ids': [] } }
        return True
 
    def action_cancel_draft(self, cr, uid, ids,context=None):
        """
        Workflow function change record state to 'draft', 
        delete old workflow instance and create new one 
        @return: boolean True    
        """
        if not isinstance(ids,list): 
            ids = [ids]
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'account.budget.operation', id, cr)
            wf_service.trg_create(uid, 'account.budget.operation', id, cr)
        return True
     
    def copy(self, cr, uid, ids, default={}, context=None):
        """Inherit copy method to reset name to /.
        
        @return: super copy method
        """
        default.update({'name': '/'})
        return super(account_budget_operation, self).copy(cr, uid, ids, default=default, context=context)
    
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
            budget_ids = budget_pool.search(cr, uid,[('analytic_account_id', '=', r.analytic_account_id.id), 
                                                   ('period_id', '=', r.period_id.id)], context=context)
            budget_line_id = budget_line_pool.search(cr, uid,[('general_account_id', '=', r.account_id.id), 
                                                             ('account_budget_id', 'in', tuple(budget_ids))], context=context)
            if budget_line_id:
                 line=budget_line_pool.browse(cr, uid, budget_line_id, context=context)[0]
                 if line.residual_balance + r.amount <=0:
                    raise orm.except_orm(_('Error!'),
                        _("The amount you try to transfer (%s) is more than %s residual (%s)!") % \
                         (r.amount, line.name, line.residual_balance,))
            for e in r.line_ids:
                if e.line_id.residual_balance - e.amount <0:
                    raise orm.except_orm(_('Error!'),
                        _("The amount you try to transfer (%s) is more than %s residual (%s)!") % \
                         (e.amount, e.line_id.name, e.line_id.residual_balance,))
            self.write(cr, uid, ids,{'state':'complete','name': r.name == '/' and 
                                     self.pool.get('ir.sequence').get(cr, uid, 'account.budget.operation') or 
                                     r.name, 'amount': r.type=='increase' and r.amount or sum([l.amount for l in r.line_ids])}, context=context)
        return True

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
            budget_line_id,history_ids=budget_line.transfer(cr, uid, {'type':r.type, 'line_ids': r.line_ids, 'to':to, 'reference':self._name+','+str(r.id)}, context=context)
        return self.write(cr, uid, ids,{'state':'done', 'budget_line':budget_line_id}, context=context)


class account_budget_line_ids(osv.Model):
    """
    Budget lines which want to transfer from and the amount to transfer from each one. 
    """
    _name = "account.budget.operation.line"
    
    _description = 'Budget Line Transfer From'

    def _check_amount(self, cr, uid, ids, context=None):
        """
		Constrain method to prohibit user from entering negative number.

        @return: Boolean True or False
        """

        for line in self.browse(cr, uid, ids, context=context):
            if line.amount<=0:
                    return False
        return True

    _columns = {
        'line_id': fields.many2one('account.budget.lines', 'Budget Line', required=True),

        'amount':fields.float('Amount', digits_compute=dp.get_precision('Account'), required=True,
                                help="If the it's positive that's mean the amount  will transfer from this budget to the main one and vice versa."),

        'operation_id': fields.many2one('account.budget.operation', 'Operation'),
    }

    _constraints = [
        (_check_amount, 'Wrong amount, they must be positive!', ['amount']),
    ]

class budget_operation_history(osv.Model):
    
    _inherit = "account.budget.operation.history"
    
    _columns = {
        'reference': fields.reference('Event Ref', selection=[('account.budget.operation', 'account.budget.operation')],size=128),
    }

    def unlink(self, cr, uid, ids, context = None):
        for s in self.read(cr, uid, ids, ['reference'], context = context):
            if s['reference'] is not None:
                raise orm.except_orm(_('Invalid action !'), _('Can not  delete operation history while it has a related operation !'))
        return super(budget_operation_history, self).unlink(cr, uid, ids, context = context)
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp import netsvc
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import operator

def _budget_name_code(self, cr, uid, ids, field_name, arg=None, context=None):
    """ 
    Global Function to get NAME & CODE for Budget, FiscalYear Budget & Budget Lines
    base on general_account, analytic_account, period & fiscalyear.
    
    @param char field_name: functional field name,
    @param list arg: additional arguments,
    @return: dictionary name & code of each record    
    """
    result = {}
    columns = self._columns.keys()
    
    for budget in self.browse(cr, uid, ids, context=context): 
        analytic = budget.analytic_account_id
        account = 'general_account_id' in columns and budget.general_account_id or False
        period_fiscalyear = 'period_id' in columns and budget.period_id or 'fiscalyear_id' in columns and budget.fiscalyear_id or False
        result[budget.id] = {
            'name': (account and account.code + ' ' + account.name + ' / ' or '') + (analytic.name or ' ') + '-' + \
                                 (period_fiscalyear and period_fiscalyear.name or ' '),
            'code': (analytic.code or ' ') + '-' + (period_fiscalyear and period_fiscalyear.code or ' ')
        }
    return result


def _get_line_ids(self, cr, uid, ids, context={}, args={}):
    """ 
    Global Function used by functional field to return the ids of record based on object send.
    It search the send object where the field in ids
    
    @param args: dictionary contain object name and field,
    @return: list of IDS    
    """
    result = (args.get('obj', False) and args.get('field', False)) and \
             self.pool.get(args.get('obj')).search(cr, uid, [(args.get('field'), 'in', ids)], context=context) or []
    return result


#----------------------------------------------------------
# Account Analytic (Inherit)
#----------------------------------------------------------
class account_analytic(osv.Model):
    """
	Inherit analytic object to add boolean field to allow user to configure
        if it is required to have budget for the corresponding analytic account or not.
    """

    _inherit = "account.analytic.account"

    _columns = {
        'budget': fields.boolean('Budget Required'),
    }

    _defaults = {
        'budget': True,
    }

#---------------------------------------------------
# Account Budget
# --------------------------------------------------
class account_budget(osv.Model):
    """
    Account Period's Budget.
    It identifies the cost center and the period which the budget belongs to,
    and the linked lines of detail with the accounts planned amount.
    """
    
    _name = "account.budget"
    
    _description = "Budget"

    _columns = {
        'name': fields.function(_budget_name_code, method=True, type='char', size=128, string='Name',
                                readonly=True, store=True, multi='name_code'),
        
        'code': fields.function(_budget_name_code, method=True, type='char', size=128, string='Code',
                                readonly=True, store=True, multi='name_code'),
        
        'creating_user_id': fields.many2one('res.users', 'Responsible User', readonly=True),
        
        'period_id': fields.many2one('account.period', 'Period', required=True, readonly=True,
                                     states={'draft':[('readonly', False)]}, ondelete='restrict'),
        
        'validating_user_id': fields.many2one('res.users', 'Validate User', readonly=True),
        
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account',
                                               readonly=True, states={'draft':[('readonly', False)]},
                                               ondelete='restrict'),
        
        'state' : fields.selection([('draft', 'Draft'), ('confirm', 'Confirm'),('validate', 'Validated'), ('done', 'Done'), ('cancel', 'Cancelled')],
                                   'Status', required=True, readonly=True),
        
        'account_budget_line': fields.one2many('account.budget.lines', 'account_budget_id', 'Budget Lines',
                                               readonly=True, states={'draft':[('readonly', False)]}),
        
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True,
                                      states={'draft':[('readonly', False)]}, ondelete='restrict'),
    }
    
    _sql_constraints = [('analytic_period_uniq', 'unique (period_id,analytic_account_id)',
                        _("You cann't create more than one budget for the same Cost Center in the same Period!"))
    ]
    
    _defaults = {
        'name': '/',
        'code': '/',
        'state': 'draft',
        'creating_user_id': lambda self, cr, uid, context: uid,
        'company_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
    }
    
    def copy(self, cr, uid, id, default={}, context=None):
        """
		Inherit copy method to reset state and analytic_account_id to default value.
        
        @return: super copy method
        """
        default.update({'state': 'draft', 'analytic_account_id': False})
        return super(account_budget, self).copy(cr, uid, id, default=default, context=context)
    
    def budget_draft(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'draft'.
        @return: boolean True    
        """
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True
        
    def budget_confirm(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'confirm'.
        @return: boolean True    
        """
        self.write(cr, uid, ids, {'state': 'confirm'}, context=context)
        return True

    def budget_validate(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'validate' and 
        set current user as validating user for budget record.
        
        @return: boolean True    
        """
        self.write(cr, uid, ids, {'state': 'validate', 'validating_user_id': uid}, context=context)
        return True

    def budget_cancel(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'cancel'.
        @return: boolean True    
        """
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def budget_done(self, cr, uid, ids, context={}):
        """
        This Method Transfer the residual_balance for each budget_line to the next periods budget_line
        Then close "done state" the budget & prevents any update on it.
        
        @return: boolean True
        """
        account_budget_lines = self.pool.get('account.budget.lines')
        period_pool = self.pool.get('account.period')
        budgets = self.browse(cr, uid, ids, context=context)
        for budget in budgets:
            next_period = period_pool.search(cr, uid,
                                            [('date_start', '>', budget.period_id.date_start),
                                             ('fiscalyear_id', '=', budget.period_id.fiscalyear_id.id)],
                                            context=context, limit=1)
    
            if next_period:
                to = {
                    'analytic_account' : budget.analytic_account_id.id,
                    'period_id' : next_period and next_period[0],
                    'company' : budget.analytic_account_id.company_id.id
                }
                for line in budget.account_budget_line:
                    to['account_id'] = line.general_account_id.id
                    if line.residual_balance > 0:
                        account_budget_lines.transfer(cr, uid, {'type':'close_transfer','to':to,
                                                                'line_ids':[{'line_id':line, 'amount':line.residual_balance}]}, context=context)
                    
                self.write(cr, uid, budget.id, {'state': 'done'}, context=context)
        return True 

    def write(self, cr, uid, ids, vals, context={}):
        """
        Before changing Budget analytic_account_id or/and period_id, 
        must check if its lines havn't any transfer/increase/expense operation.
        
        @return: modify record values
        """
        if ids and not isinstance(ids,list): 
            ids = [ids]
        budget_line_pool = self.pool.get('account.budget.lines')
        if vals.has_key('analytic_account_id') or vals.has_key('period_id'):
            line_ids = budget_line_pool.search(cr, uid,[('account_budget_id','in',ids)], context=context)
            budget_line_pool._check_operation(cr, uid, line_ids, context=context)
        return super(account_budget, self).write(cr, uid, ids, vals, context=context)

#---------------------------------------------------
# Account Budget Lines
# --------------------------------------------------
class account_budget_lines(osv.Model):
    """
    Account Budget Lines / Period's Budget Details
    One line of detail of the Period Budget representing planned amount 
    for special account in period Budget which it belong to
    """
    _name = "account.budget.lines"
    
    _description = "Budget Line"
    
    def _check_operation(self, cr, uid, ids, context={}):
        """ Raise an exception if Budge Lines have any transfer/increase operations. """
        if ids and not isinstance(ids,list): 
            ids = [ids]
        if self.pool.get('account.budget.operation.history').search(cr, uid, ['|',('budget_line_id_from', 'in', ids),
                                                                            ('budget_line_id_to', 'in', ids)],context=context):
            raise orm.except_orm(_('Warning!'), _("You cann't modify budget which has transfer or increase operation!"))
        
        for line in self.browse(cr, uid, ids, context=context):
            if line.residual_balance != line.planned_amount:
                raise orm.except_orm(_('Warning!'), _("You cann't modify budgets which already expense from it!"))
    
    def transfer(self, cr, uid, vals={}, context=None):
        """
        This Method execute any increase or transfer operation.
                                
        @param dictionary vals: all operation values (type, line_ids, to, reference),
        @return: dictionary (budget_line_id, history_ids
        """
        type = vals.get('type','')
        line_ids = vals.get('line_ids',[])
        to = vals.get('to',{})
        reference = vals.get('reference','')
        budget_pool = self.pool.get('account.budget')
        budget_line_pool = self.pool.get('account.budget.lines')
        budget_history_pool = self.pool.get('account.budget.operation.history')
        wf_service = netsvc.LocalService("workflow")
        analytic_account = to.get('analytic_account')
        account_id = to.get('account_id')
        period_id = to.get('period_id')
        company = to.get('company')
        history_ids = []
        budget_ids = budget_pool.search(cr, uid,[('analytic_account_id', '=', analytic_account), 
                                                   ('period_id', '=', period_id)], context=context)
        budget_line_ids = budget_line_pool.search(cr, uid,[('general_account_id', '=', account_id), 
                                                             ('account_budget_id', 'in', tuple(budget_ids))], context=context)
        budget_id = budget_ids and budget_ids[0] or False
        budget_line_id = budget_line_ids and budget_line_ids[0] or False
        if not budget_id:
                budget_id = budget_pool.create(cr, uid, {
                    'creating_user_id': uid, 'period_id': period_id,
                    'validating_user_id': uid, 'analytic_account_id': analytic_account,
                    'company_id': company}, context=context)
                wf_service.trg_validate(uid, 'account.budget', budget_id, 'confirm', cr)
                wf_service.trg_validate(uid, 'account.budget', budget_id, 'validate', cr)
        if not budget_line_id: 
            budget_line_id = budget_line_pool.create(cr, uid, {'account_budget_id':budget_id,'analytic_account_id': analytic_account,
                                                                  'period_id': period_id,'general_account_id':account_id}, context=context)
        if len(line_ids) > 0:
            for line in line_ids:
                if line['line_id'].residual_balance < line['amount']:
                    raise orm.except_orm(_('Error!'), _("The amount you try to transfer (%s) is more than %s residual (%s)!") % (line['amount'], line['line_id'].name, line['line_id'].residual_balance,))
    
                vals = {
                    'budget_line_id_from': line['line_id'].id,
                    'budget_line_id_to': budget_line_id,
                    'amount': line['amount'],
                    'name': type,
                    'reference': reference,
                    }
                    
                history_id = budget_history_pool.create(cr, uid, vals, context=context)
                history_ids.append(history_id)
        else:
            vals = {
                    'budget_line_id_from': False,
                    'budget_line_id_to': budget_line_id,
                    'amount': to.get('amount'),
                    'name': type,
                    'voucher_id': to.get('voucher_id'),
                    'reference': reference,
            }

            history_id = budget_history_pool.create(cr, uid, vals, context=context)
            history_ids.append(history_id)
        
        return budget_line_id ,history_ids
    
    def _total_operation(self, cr, uid, ids, field_name, arg=None, context=None):
        """
        This Method use to compute the tranfer, increase amount from the operation object.
        
        @param char field_name: functional field name,
        @param list arg: additional arguments,
        @return: dictionary, amount of total operation for each line
        """ 
        result = {}
        for id in ids:
            cr.execute("SELECT sum(COALESCE(amount,0))  \
                 FROM   (SELECT CASE WHEN  budget_line_id_from=%s \
                                THEN -amount \
                                ELSE amount \
                            END AS amount \
                        FROM    account_budget_operation_history h \
                        where budget_line_id_from=%s or budget_line_id_to=%s) \
                        as result " % (id, id, id))
            result[id] = cr.fetchone()[0] or 0.0
        return result

    def _residual_balance(self, cr, uid, ids, field_name, arg=None, context=None):
        """
        This Method use to compute the actual_balance & the residual_balance for each budget_line.
                    
        @param char field_name: functional field name,
        @param list arg: additional arguments,
        @return: dictionary of residual balance for each budget line
        """
        cr.execute('SELECT id,planned_amount+total_operation-balance FROM account_budget_lines WHERE id IN (%s)'% (','.join(map(str,ids)),))
        return dict(cr.fetchall()) 
        
    def _balance_amount(self, cr, uid, ids, field_name, arg=None, context={}):
        """
        This Method use to compute the actual_balance & the residual_balance for each budget_line.
                    
        @param char field_name: functional field name,
        @param list arg: additional arguments,
        @return: dictionary of expense balance for each budget line
        """
        result = {}
        account_pool = self.pool.get('account.account')
        move_line_obj = self.pool.get('account.move.line')
        for line in self.browse(cr, uid, ids, context=context):
            move_line_ids = move_line_obj.search(cr, uid, [('account_id','=',line.general_account_id.id),
                                                           ('analytic_account_id', '=', line.analytic_account_id.id),
                                                           ('period_id', '=', line.period_id.id),
                                                            ('move_id.state', 'in', ('draft','completed','closed','posted'))],
                                                       context=context)            
            ctx = context.copy()
            ctx.update({'move_line_ids': move_line_ids })
            result[line.id] = ctx.get('move_line_ids') and account_pool.read(cr, uid, line.general_account_id.id, ['balance'], context=ctx)['balance'] or 0.0
            if not context.get('update_buget',False) and line.planned_amount + line.total_operation -result[line.id]<0:
                 raise orm.except_orm(_('Error!'), _("Budget can't go overdrow!"))        
        return result
        
    def fnct_residual_search(self, cr, uid, obj, name, domain=None, context=None):
        """
        Method to allow user to advanced search functional residual_balance by recalculate the 
        field amount and search based on entered criteria.         
                    
        @param obj: object,
        @param name: char field name,
        @param domain: tuple of the entered search criteria,
        @return: list of tuple of the domain by record IDS
        """
        if context is None:
            context = {}
        if not domain:
            return []
        field, operator, value = domain[0]
        cr.execute('SELECT id FROM account_budget_lines \
                    WHERE planned_amount+total_operation-balance '+operator+str(value))
        res = cr.fetchall()
        return [('id', 'in', [r[0] for r in res])]
        
    def _get_operation_line_ids(self, cr, uid, ids, context=None):
        """ 
        Method used by functional field to return budget line IDs which where found on the
        operation history object.
        Budget line ID could be found on budget_line_id_from or budget_line_id_to fiels in 
        history object based on operation type.

        @return: list of IDS    
        """
        lines = self.pool.get('account.budget.operation.history').read(cr, uid, ids, 
                                    ['budget_line_id_from','budget_line_id_to'], context=context)
        return reduce(operator.add,[[l['budget_line_id_from'] and l['budget_line_id_from'][0],l['budget_line_id_to'] and l['budget_line_id_to'][0]] for l in lines])


    def _get_ids(self, cr, uid, ids, context={}):
        """
        get records of budget line to be updated
        @param ids: ids in account asset history
        return dictionary Keys
        """               
        result = []
        for line in self.pool.get('account.move.line').browse(cr, uid, ids, context=context):
            result = result + self.pool.get('account.budget.lines').search(cr, uid, [('general_account_id','=',line.account_id.id),
                                                    ('analytic_account_id', '=', line.analytic_account_id.id),
                                                    ('period_id', '=', line.period_id.id)],
                                            context=context)
        return result

    def _get_move_ids(self, cr, uid, ids, context={}):
        """
        get records of budget line to be updated
        @param ids: ids in account asset history
        return dictionary Keys
        """               
        lines = self.pool.get('account.move.line').search(cr, uid, [('move_id','in',ids)], context=context)   
        return self.pool.get('account.budget.lines')._get_ids(cr, uid, lines, context)

    _columns = {
        'name': fields.function(_budget_name_code, method=True, type='char', size=128, string='Name',
                                readonly=True, store=True, multi='name'),
                
        'code': fields.function(_budget_name_code, method=True, type='char', size=128, string='Code',
                                readonly=True, store=True, multi='name'),
        
        'account_budget_id': fields.many2one('account.budget', 'Budget', ondelete='cascade', required=True),
        
        'general_account_id': fields.many2one('account.account', 'Account', required=True, ondelete='restrict'),

        'planned_amount':fields.float('Planned Amount', required=True, digits_compute=dp.get_precision('Account')),
        
        'company_id': fields.related('account_budget_id', 'company_id', type='many2one', relation='res.company', string='Company',
                                     store={'account.budget': (lambda self, cr, uid, ids, c={}:
                                                                 _get_line_ids(self, cr, uid, ids, context=c,
                                                                                args={
                                                                                      'obj':'account.budget.lines',
                                                                                      'field':'account_budget_id'
                                                                                   }),
                                                                ['company_id'], 10),
                                            'account.budget.lines': (lambda self, cr, uid, ids, c={}: ids, ['account_budget_id'], 10),
                                    }, readonly=True),
        
        'analytic_account_id': fields.related('account_budget_id', 'analytic_account_id', type='many2one',
                                              relation='account.analytic.account', string='Analytic Account',
                                              store={'account.budget': (lambda self, cr, uid, ids, c={}:
                                                                         _get_line_ids(self, cr, uid, ids, context=c,
                                                                                       args={
                                                                                             'obj':'account.budget.lines',
                                                                                             'field':'account_budget_id'
                                                                                             }),
                                                                        ['analytic_account_id'], 10),
                                                    'account.budget.lines': (lambda self, cr, uid, ids, c={}: ids, ['account_budget_id'], 10),
                                                }, readonly=True),
        
        'period_id': fields.related('account_budget_id', 'period_id', type='many2one',
                                    relation='account.period', string='Period',
                                    store={'account.budget': (lambda self, cr, uid, ids, c={}:
                                                               _get_line_ids(self, cr, uid, ids, context=c,
                                                                             args={
                                                                                   'obj':'account.budget.lines',
                                                                                   'field':'account_budget_id'
                                                                                   }),
                                                                ['period_id'], 10),
                                        'account.budget.lines': (lambda self, cr, uid, ids, c={}: ids, ['account_budget_id'], 10),
                                    }, readonly=True),

        'total_operation': fields.function(_total_operation, method=True, digits_compute=dp.get_precision('Account'), string='In/De-crease Amount',
                            store={'account.budget.operation.history': (_get_operation_line_ids,['budget_line_id_from','budget_line_id_to'], 10),},),
                            
        'move_line_ids': fields.one2many('account.move.line', 'budget_line_id', 'Move lines'),
        
        'balance': fields.function(_balance_amount, type='float',  digits_compute=dp.get_precision('Account'), string='Exchange Amount',
            store={
                'account.budget.lines': (lambda self, cr, uid, ids, c={}: ids, 
                                        ['code','general_account_id', 'analytic_account_id','period_id'], 10),
                'account.move.line': (_get_ids, ['account_id', 'analytic_account_id','period_id', 'debit','credit'], 20),
                'account.move': (_get_move_ids, ['state'], 20),
            } ),
        
        'residual_balance': fields.function(_residual_balance, fnct_search=fnct_residual_search, method=True,
                                                     digits_compute=dp.get_precision('Account'), string='Residual Balance'),
                    
        'state': fields.related('account_budget_id', 'state', string='State', type='char', readonly=True),
                

    }

    _defaults = {
        'planned_amount': 0.0,
        'total_operation': 0.0,
        'residual_balance':0.0

    }
    #FIXME: budget_check when close budget
    _sql_constraints = [
                        #('residual_check', 'CHECK ((planned_amount+total_operation-balance)>=0)',  _("Budget can't go overdrow!")),
                        ('analytic_account_period_uniq', 'unique (period_id,analytic_account_id,general_account_id)',_("You can't duplicate the account for the same budget!")),
    ]
    '''def _check_balance(self, cr, uid, ids, context={}):
        """
        Check budget in less than zero
        @return: boolean True or False 
        """
        for obj in self.browse(cr, uid, ids, context=context):
            print '........................', context
            if obj.balance < 0 and not context.get('update_buget',False):
                 return True
        return True    
    _constraints = [
         (_check_balance, "planned Budget cann't go overdrow!", ['balance']), 
    ]'''
    def write(self, cr, uid, ids, vals, context={}):
        """
        Before changing general_account_id/analytic_account_id/period_id of budget line,
        must check if it has any operation (transfer, increase,...)
        @return: Update Line values
        """
        general_account = False
        if vals.has_key('general_account_id'):
            for budget_line in self.browse(cr, uid, ids, context=context):
                if vals.get('general_account_id') != budget_line.general_account_id.id:
                    general_account = True
                    break                
        if general_account or  vals.has_key('analytic_account_id') or vals.has_key('period_id'):
            self._check_operation(cr, uid, budget_line.id, context=context)
        return super(account_budget_lines, self).write(cr, uid, ids, vals, context=context)
# ---------------------------------------------------------
#  Account move line (Inherit)
# ---------------------------------------------------------

class account_move_line(osv.Model):
    """ 
	Inherit move line object to  add budget line id to allow calculate the actual balance
    in the budget line object.
	"""
    _inherit = 'account.move.line'

    _columns = {
           'budget_line_id': fields.many2one('account.budget.lines', 'Budget Line'),
    }

# ---------------------------------------------------------
#  Account move  (Inherit)
# --------------------------------------------------------- 
    
class account_move(osv.Model):
    """ 
	Inherit move object to change workflow to go analytic activity based on configuration
    of the account type.
	"""

    _inherit = 'account.move'
    
    def test_analytic(self, cr, uid, ids,  context={}):
        """
        Workflow condition method to determine whether to go throw analytic workflow
        or not in move object. 
        It return True if user set analytic_wk field  in account type to False.
        and it return False if the user set analytic_wk field in account type to False.
                    
        @return: Boolean True or False
        """
        if not(self.validate(cr, uid, ids, context) and len(ids)):
            raise orm.except_orm(_('Integrity Error !'), _('You can not Complete a non-balanced entry !\nMake sure you have configured Payment Term properly !\nIt should contain atleast one Payment Term Line with type "Balance" !'))              
        for mv in self.browse(cr, uid, ids):
            for line in mv.line_id:
                if line.account_id.user_type.analytic_wk and not line.analytic_account_id and line.debit:
                    raise orm.except_orm(_('Error!'), _('You must add analytic account for %s accounts!'%(line.account_id.user_type.name,)))
                if line.account_id.user_type.analytic_wk:
                    return True
        return False
    
# ---------------------------------------------------------
# FiscalYear Budgets
# ---------------------------------------------------------
class account_fiscalyear_budget(osv.Model):
    """
    Account fiscalyear's Budget.
    It identifies the cost center and the fiscalyear which the budget belongs to,
    and the linked lines of detail with the accounts planned amount.
    """
    
    _name = "account.fiscalyear.budget"
    
    _description = "Fiscal Year Budget"

    _columns = {
        'name': fields.function(_budget_name_code, method=True, type='char', size=128, string='Name', multi='name_code'),
        
        'code': fields.function(_budget_name_code, method=True, type='char', size=128, string='Code', multi='name_code'),
        
        'creating_user_id': fields.many2one('res.users', 'Responsible User', readonly=True),
        
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'fiscalyear', required=True, readonly=True,
                                         states={'draft':[('readonly', False)]}, ondelete='restrict'),
                                         
        'validating_user_id': fields.many2one('res.users', 'Validate User', readonly=True),
        
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', readonly=True,
                                               states={'draft':[('readonly', False)]}, ondelete='restrict'),
                                               
        'state' : fields.selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('validate', 'Validated'), ('done', 'Done'),
                                    ('cancel', 'Cancelled')], 'Status', required=True, readonly=True),
                                    
        'account_fiscalyear_budget_line': fields.one2many('account.fiscalyear.budget.lines', 'account_fiscalyear_budget_id',
                                                          'Budget Lines', readonly=True, states={'draft':[('readonly', False)]}),
                                                          
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True,
                                      states={'draft':[('readonly', False)]}, ondelete='restrict'),
    }

    _sql_constraints = [('analytic_fiscalyear_uniq', 'unique (fiscalyear_id,analytic_account_id)',
                        _("You cann't create more than one budget for the same Cost Center in the same FiscalYear!"))
    ]
    
    _defaults = {
        'name': '/',
        'code': '/',
        'state': 'draft',
        'creating_user_id': lambda self, cr, uid, context: uid,
        'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
        'account_fiscalyear_budget_line': lambda self, cr, uid, context:
                [{'general_account_id': acc, 'planned_amount': 1.0} for acc in self.pool.get('account.account').search(cr, uid,[('budget_classification','!=',False)],context=context)],
    }
        
    def copy(self, cr, uid, id, default={}, context=None):
        """
		Inherit copy method to reset state and analytic_account_id to default value.
        
        @return: super copy method
        """
        default.update({'state': 'draft', 'analytic_account_id': False})
        return super(account_fiscalyear_budget, self).copy(cr, uid, id, default=default, context=context)
    
   
    def budget_confirm(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'confirm'.
        @return: boolean True    
        """
        self.write(cr, uid, ids, {'state': 'confirm'}, context=context)
        return True

    def budget_draft(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'draft'.
        @return: boolean True    
        """
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True
     
    def budget_validate(self, cr, uid, ids, period_ids=False, account_ids=False, context=None):
        """
        Workflow function change record state to 'validate', 
        and create period's budget from fiscalyear budget
        @return: boolean True    
        """
        period_pool = self.pool.get('account.period')
        budget_pool = self.pool.get('account.budget')
        budget_line_pool = self.pool.get('account.budget.lines')
        fiscalyear_budget_line_pool = self.pool.get('account.fiscalyear.budget.lines')
        wf_service = netsvc.LocalService("workflow")
        
        for fiscalyear_budget in self.browse(cr, uid, ids, context=context):
            period_ids = period_ids or period_pool.search(cr, uid, [('fiscalyear_id', '=', fiscalyear_budget.fiscalyear_id.id),
                                                                    ('special','=',False)], context=context)
            if not period_ids:
                raise osv.except_osv(_('Invalid Action!'), _('Sorry there are no periods to divided the amount among them.'))
            for period_id in period_ids:
                budget_vals = {
                    'creating_user_id': fiscalyear_budget.creating_user_id.id,
                    'period_id': period_id,
                    'validating_user_id': fiscalyear_budget.validating_user_id.id,
                    'analytic_account_id': fiscalyear_budget.analytic_account_id.id,
                    'company_id': fiscalyear_budget.company_id.id,
                }
                budget_ids = budget_pool.search(cr, uid, [('analytic_account_id', '=', fiscalyear_budget.analytic_account_id.id),
                                                          ('period_id', '=', period_id)], context=context)
                period_budget_id = budget_ids and budget_ids[0] or budget_pool.create(cr, uid, budget_vals, context=context)
                for budget_line in fiscalyear_budget.account_fiscalyear_budget_line:
                    account_id =  budget_line.general_account_id.id
                    if (account_ids and budget_line.general_account_id.id not in account_ids) or budget_line.devided:
                        continue
                    budget_line_id = budget_line_pool.search(cr, uid, [('account_budget_id', '=', period_budget_id), 
                                                                       ('general_account_id', '=', account_id)], context=context)
                    budget_line_vals = {
                        'account_budget_id': period_budget_id,
                        'general_account_id':budget_line.general_account_id.id,
                        'planned_amount':budget_line.planned_amount / len(period_ids),
                    }
                    if budget_line_id:
                        budget_line_pool.write(cr, uid, budget_line_id, budget_line_vals, context=context)
                    else:
                        budget_line_pool.create(cr, uid, budget_line_vals, context=context)
                    fiscalyear_budget_line_pool.write(cr, uid, budget_line.id, {'devided': True}, context=context)
                wf_service.trg_validate(uid, 'account.budget', period_budget_id, 'confirm', cr)
                wf_service.trg_validate(uid, 'account.budget', period_budget_id, 'validate', cr)
        self.write(cr, uid, ids, {'state': 'validate', 'validating_user_id': uid}, context=context)
        return True


    def budget_cancel(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'cancel'.
        @return: boolean True    
        """
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def unlink(self, cr, uid, ids, context=None):
        budgets = self.read(cr, uid, ids, ['state'], context=context)
        for s in budgets:
            if s['state'] not in ['draft','cancel']:
                raise osv.except_osv(_('Invalid Action!'), _('In order to delete a budget, you must cancel it first.'))
        return super(account_fiscalyear_budget, self).unlink(cr, uid, ids, context=context)
# ---------------------------------------------------------
# FiscalYear Budget lines
# ---------------------------------------------------------

class account_fiscalyear_budget_lines(osv.Model):
    """
    Account FiscalYear Budget Lines / FiscalYear Budget Details
    One line of detail of the FiscalYear Budget representing planned amount 
    for special account in Fiscalyear Budget which it belong to
    """
    _name = "account.fiscalyear.budget.lines"
    
    _description = "Fiscal Year Budget Line"
    
    _rec_name = 'general_account_id'

    _columns = {
        'account_fiscalyear_budget_id': fields.many2one('account.fiscalyear.budget', 'Fiscal Year Budget',
                                                         ondelete='cascade', required=True),
                                                         
        'general_account_id': fields.many2one('account.account', 'Account', required=True, ondelete='restrict'),
         
        'planned_amount':fields.float('Planned Amount', required=True, digits_compute=dp.get_precision('Account')),
        
        'company_id': fields.related('account_fiscalyear_budget_id', 'company_id', type='many2one', relation='res.company', string='Company',
                                     store={'account.fiscalyear.budget': (lambda self, cr, uid, ids, c={}:
                                                                           _get_line_ids(self, cr, uid, ids, context=c,
                                                                                         args={
                                                                                               'obj':'account.fiscalyear.budget.lines',
                                                                                               'field':'account_fiscalyear_budget_id'
                                                                                               }),
                                                                            ['company_id'], 10),
                                     }, readonly=True),
        
        'analytic_account_id': fields.related('account_fiscalyear_budget_id', 'analytic_account_id', type='many2one',
                                              relation='account.analytic.account', string='Analytic Account',
                                              store={'account.fiscalyear.budget': (lambda self, cr, uid, ids, c={}:
                                                                                   _get_line_ids(self, cr, uid, ids, context=c,
                                                                                                 args={
                                                                                                        'obj':'account.fiscalyear.budget.lines',
                                                                                                        'field':'account_fiscalyear_budget_id'
                                                                                                        }),
                                                                                    ['analytic_account_id'], 10),
                                                    'account.fiscalyear.budget.lines': 
                                                    (lambda self, cr, uid, ids, c={}: ids, ['account_fiscalyear_budget_id'], 10),
                                               },
                                               readonly=True),
        
        'fiscalyear_id': fields.related('account_fiscalyear_budget_id', 'fiscalyear_id', type='many2one',
                                    relation='account.fiscalyear', string='FiscalYear',
                                    store={'account.fiscalyear.budget': (lambda self, cr, uid, ids, c={}:
                                                                          _get_line_ids(self, cr, uid, ids, context=c,
                                                                                        args={
                                                                                              'obj':'account.fiscalyear.budget.lines',
                                                                                              'field':'account_fiscalyear_budget_id'
                                                                                              }),
                                                                        ['fiscalyear_id'], 10),
                                        'account.fiscalyear.budget.lines': 
                                        (lambda self, cr, uid, ids, c={}: ids, ['account_fiscalyear_budget_id'], 10),
                                    },
                                    readonly=True),
                
        'devided': fields.boolean('Flow Created!'),
    }

    _defaults = {
        'planned_amount': 1.0,
    }
    
    _sql_constraints = [('analytic_account_fiscalyear_uniq', 'unique (fiscalyear_id,analytic_account_id,general_account_id)',
                         _("You cann't create more than one budget for the same Cost Center in the same FiscalYear!")),
    ]
    

# ---------------------------------------------------------
#  Budget Operation History
# ---------------------------------------------------------

class budget_operation_history(osv.Model):
    """ This Class use for Keeping a record as log for each Budget operation (increase, transfer, ...) """
    
    _name = "account.budget.operation.history"
    
    _description = 'Budget Operation History'

    #TODO: Delete all from & to columns exept budget_line
    _columns = {
        'analytic_account_id_from': fields.related('budget_line_id_from', 'analytic_account_id', type='many2one',
                                                   relation='account.analytic.account', string='From Cost Center',
                                                   store={'account.budget.lines': (lambda self, cr, uid, ids, c={}:
                                                            _get_line_ids(self, cr, uid, ids, context=c,
                                                                          args={
                                                                                'obj':'account.budget.operation.history',
                                                                                'field':'budget_line_id_from'
                                                                          }),['analytic_account_id'], 10),
                                                        'account.budget.operation.history': (lambda self, cr, uid, ids, c={}:ids, 
                                                                                             ['budget_line_id_from'], 10),}, readonly=True),
        
        'account_id_from':  fields.related('budget_line_id_from', 'general_account_id', type='many2one',
                                            relation='account.account', string='From Account',
                                            store={'account.budget.lines': (lambda self, cr, uid, ids, c={}:
                                                            _get_line_ids(self, cr, uid, ids, context=c,
                                                                          args={
                                                                                'obj':'account.budget.operation.history',
                                                                                'field':'budget_line_id_from'
                                                                          }),['general_account_id'], 10),
                                                        'account.budget.operation.history': (lambda self, cr, uid, ids, c={}:ids, 
                                                                                             ['budget_line_id_from'], 10),}, readonly=True),
        
        'period_id_from':  fields.related('budget_line_id_from', 'period_id', type='many2one',
                                          relation='account.period', string='From Period',
                                          store={'account.budget.lines': (lambda self, cr, uid, ids, c={}:
                                                            _get_line_ids(self, cr, uid, ids, context=c,
                                                                          args={
                                                                                'obj':'account.budget.operation.history',
                                                                                'field':'budget_line_id_from'
                                                                          }),['period_id'], 10),
                                                        'account.budget.operation.history': (lambda self, cr, uid, ids, c={}:ids, 
                                                                                             ['budget_line_id_from'], 10),}, readonly=True),
        
        'budget_line_id_from': fields.many2one('account.budget.lines', 'From Budget line', readonly=True, ondelete='restrict'),
        
        'analytic_account_id_to': fields.related('budget_line_id_to', 'analytic_account_id', type='many2one',
                                                relation='account.analytic.account', string='To Cost Center',
                                                store={'account.budget.lines': (lambda self, cr, uid, ids, c={}:
                                                            _get_line_ids(self, cr, uid, ids, context=c,
                                                                          args={
                                                                                'obj':'account.budget.operation.history',
                                                                                'field':'budget_line_id_to'
                                                                          }),['analytic_account_id'], 10),
                                                        'account.budget.operation.history': (lambda self, cr, uid, ids, c={}:ids, 
                                                                                             ['budget_line_id_to'], 10),}, readonly=True), 
        
        'account_id_to':  fields.related('budget_line_id_to', 'general_account_id', type='many2one',
                                        relation='account.account', string='To Account',
                                        store={'account.budget.lines': (lambda self, cr, uid, ids, c={}:
                                                            _get_line_ids(self, cr, uid, ids, context=c,
                                                                          args={
                                                                                'obj':'account.budget.operation.history',
                                                                                'field':'budget_line_id_to'
                                                                          }),['general_account_id'], 10),
                                                        'account.budget.operation.history': (lambda self, cr, uid, ids, c={}:ids, 
                                                                                             ['budget_line_id_to'], 10),}, readonly=True),
        
        
        'period_id_to':  fields.related('budget_line_id_to', 'period_id', type='many2one',
                                        relation='account.period', string='To Period',
                                        store={'account.budget.lines': (lambda self, cr, uid, ids, c={}:
                                                            _get_line_ids(self, cr, uid, ids, context=c,
                                                                          args={
                                                                                'obj':'account.budget.operation.history',
                                                                                'field':'budget_line_id_to'
                                                                          }),['period_id'], 10),
                                                        'account.budget.operation.history': (lambda self, cr, uid, ids, c={}:ids, 
                                                                                             ['budget_line_id_to'], 10),}, readonly=True),
        
        'budget_line_id_to': fields.many2one('account.budget.lines', 'To Budget line', readonly=True, ondelete='restrict'),
        
        'amount':fields.float('Amount', digits_compute=dp.get_precision('Account'), readonly=True),
        
        'company_id': fields.related('budget_line_id_to', 'company_id', type='many2one', relation='res.company', string='Company',
                                     store={'account.budget.lines': (lambda self, cr, uid, ids, c={}:
                                             _get_line_ids(self, cr, uid, ids, context=c,
                                                           args={
                                                                 'obj':'account.budget.operation.history',
                                                                 'field':'budget_line_id_to'
                                                            }),['company_id'], 10),
                                            'account.budget.operation.history': (lambda self, cr, uid, ids, c={}:ids, 
                                                                                ['budget_line_id_to'], 10),}, readonly=True),
        
        'user_id': fields.many2one('res.users', 'User', readonly=True),
        
        'date': fields.date('Date', readonly=True),
        
        'name': fields.selection([('transfer', 'Transfer'), ('increase', 'Increase'),
                                  ('confirm_transfer', 'Confirmation Transfer'),
                                  ('close_transfer', 'Closing Budget Transfer')],
                                  'Type' , readonly=True),
                                  
    }

    _defaults = {
        'date': lambda *args: time.strftime('%Y-%m-%d'),
        'user_id': lambda self, cr, uid, ctx: uid,
    }

# ---------------------------------------------------------
#  Budget Classification
# ---------------------------------------------------------

class budget_classification(osv.Model):
    """ This Class for grouping accounts which will define Budget to it in classifications """

    _name = "account.budget.classification"
    
    _description = 'Budget classification'
    
    _order = 'sequence'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        
        'code': fields.char('Code', size=16, required=True),
        
        'sequence': fields.integer('Sequence', required=True, help="The sequence field is used to order the account in budget report"),
        
        'company_id': fields.many2one('res.company', 'Company', ondelete='restrict'),
        
        #MAY HAS TO BE PROPERTY FIELD one2many
        'account_ids': fields.many2many('account.account', 'account_budget_classification_rel', 'classification_id', 'account_id', 'Accounts'),
    }

    _sql_constraints = [('classification_code_uniq', 'unique (company_id,code)',
                        _("The classification code must be unique per company!"))
    ]
    

# ---------------------------------------------------------
#  Account (Inherit)
# ---------------------------------------------------------

class account_account(osv.Model):
    """
	Inherit account to add budget_classification field.
	"""

    _inherit = "account.account"

    _columns = {
        'budget_classification': fields.many2many('account.budget.classification', 'account_budget_classification_rel',
                                                  'account_id', 'classification_id', 'Classification'),
    }


# ---------------------------------------------------------
# Account Type (Inherit)
# ---------------------------------------------------------
#TODO: analytic_wk changed to analytic_wk & analytic_requied
class account_account_type(osv.Model):
    """
	Inherit account type object to add analytic_wk field to allow user to 
    configure whether to go throw analytic workflow or not in move object
    based on selected account in the move. 
	"""

    _inherit =  "account.account.type"

    _columns = {
            'analytic_wk': fields.boolean('Budget Check', help="Check if this type of account has to go through budget confirmation check."),
    }

    _defaults = {
         'analytic_wk':True,
    }

# ---------------------------------------------------------
# Analytic Account
# ---------------------------------------------------------
class account_analytic(osv.Model):
    _inherit = "account.analytic.account"
    _description = "Budget"

    _columns = {
        'main_dept': fields.boolean('Main Department'), 
    }

account_analytic()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

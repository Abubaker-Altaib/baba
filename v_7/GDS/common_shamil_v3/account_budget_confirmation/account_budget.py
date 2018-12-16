# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import netsvc

    
# ---------------------------------------------------------
# Budget Confirmation
# ---------------------------------------------------------
class account_budget_confirmation(osv.Model):
    """ Object of reserve some amount from the budget  """

    _name = "account.budget.confirmation"
    
    _order = 'id desc'
    
    def _check_company(self, cr, uid, ids, context={}):
        """ 
        This method to check that all the confirmation attributes belong to same company            
        @return: boolean True if all belong to same company, or False  
        """
        ids = not isinstance(ids,list) and [ids] or ids
        for budget_confirm in self.browse(cr, uid, ids, context=context):
            companies = []
            companies += budget_confirm.general_account_id and [budget_confirm.general_account_id.company_id] or []
            companies += budget_confirm.analytic_account_id and [budget_confirm.analytic_account_id.company_id] or []
            companies += budget_confirm.period_id and [budget_confirm.period_id.company_id] or []
            if len(set(companies)) > 1:
                return False
        return True

    def _residual_amount(self, cr, uid, ids, field_name, arg=None, context={}):
        """
        This method calculate the confirmed amount which doesn't turn to actual expense yet
        
        @param char field_name: functional field name,
        @param list arg: additional arguments,
        @return: dictionary residual amount for each record    
        """
        result = {}
        for budget_confirm in self.browse(cr, uid, ids, context=context):
            lines = 0.0
            account = budget_confirm.general_account_id
            analytic = budget_confirm.analytic_account_id
            for line in budget_confirm.line_id:
                lines += account == line.account_id and analytic == line.analytic_account_id and \
                         line.debit - line.credit or 0.0
            result[budget_confirm.id] = budget_confirm.amount - lines
        return result

    _columns = {
        'name': fields.char('Name', size=64, readonly=True),
        
        'reference': fields.char('Reference', size=64, readonly=True),
        
        'period_id': fields.many2one('account.period', 'Period', required=True, 
                                     readonly=True, states={'draft':[('readonly',False)]}),
                                     
        'general_account_id': fields.many2one('account.account', 'Account', readonly=True, 
                                              states={'draft':[('readonly',False)]}),
                                              
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', 
                                               readonly=True, states={'draft':[('readonly',False)]}, 
                                               domain=[('type','!=','view')]),
                                               
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, 
                                      states={'draft':[('readonly',False)]}),
                                      
        'residual_amount': fields.function(_residual_amount, digits_compute=dp.get_precision('Account'), 
                                           method=True, string='Residual Balance'),
        
        'amount':fields.float('Amount', required=True, digits_compute=dp.get_precision('Account'), 
                              readonly=True, states={'draft':[('readonly',False)]}),
        
        'state' : fields.selection([('draft','Draft'),('complete','Waiting For Approve'),
                                    ('check','Waiting Check'),('valid','Approved'),
                                    ('unvalid','Not Approved'),('cancel', 'Cancelled')], 
                                    'Status', required=True, readonly=True),
                                    
        'type' : fields.selection([('stock_in','Stock IN'),('stock_out','Stock OUT'),
                                   ('purchase','Purchase'),('other','Others')], 'Type'),
                                   
        'date':fields.date('Date', readonly=True, states={'draft':[('readonly',False)]}),
        
        'creating_user_id': fields.many2one('res.users', 'Responsible User'),
        
        'validating_user_id': fields.many2one('res.users', 'Validate User', readonly=True),
        
        'line_id': fields.one2many('account.move.line', 'budget_confirm_id', 'Entries'),
        
        'note':fields.text('Note', required=True),
        
        'company_id': fields.related('period_id', 'company_id', type='many2one', relation='res.company', 
                                     string='Company', readonly=True),
                                     
        'budget_residual':fields.float('Budget Residual', required=True, readonly=True, 
                                       digits_compute=dp.get_precision('Account')),
                                       
        'budget_line_id': fields.many2one('account.budget.lines', 'Budget Line'),
    }

    _defaults = {
        'reference': '/',
        'name': '/',
        'type':'other',
        'state': 'draft',
        'budget_residual': 0.0,
        'creating_user_id': lambda self, cr, uid, context: uid,
    }
    
    def copy(self, cr, uid, ids, default={}, context={}):
        """
        Inherit copy method reset name, line_id and reference when copying confirmation record
        
        @param default: dictionary of the values of record to be created,
        @return: super method of copy    
        """
        default.update({'name': '/', 'line_id': False, 'reference': '/'})
        return super(account_budget_confirmation, self).copy(cr, uid, ids, default=default, context=context)

    def create(self, cr, uid, vals, context={}):
        """
        Inherit create method set name from sequence if exist
        and to prohibit the user from entering account, period and cost center of different company
        
        @param default: dictionary of the values of record to be created,
        @return: super method of copy    
        """
        vals.update({'name': vals.get('name','/') == '/' and 
                     self.pool.get('ir.sequence').get(cr, uid, 'account.budget.confirmation') or 
                     vals.get('name')})
        res = super(account_budget_confirmation, self).create(cr, uid, vals, context=context)
        if not self._check_company(cr, uid, res, context=context):
            raise orm.except_orm(_('Warning!'), _('Account, Period and Cost Center must be belong to same Company!'))
        return res
   

    def write(self, cr, uid, ids, vals, context={}):
        """
        The Approved confirmations must be added to confirmation_ids of the effected budget line
        @return: Update confirmation record    
        """
        budget_line_pool = self.pool.get('account.budget.lines')
        ids = not isinstance(ids,list) and [ids] or ids
        for confirmation in self.browse(cr, uid, ids, context=context):
            budget_line_vals = {}
            line_ids = budget_line_pool.search(cr, uid,[('analytic_account_id','=', confirmation.analytic_account_id.id),
                                                           ('general_account_id','=',confirmation.general_account_id.id),
                                                           ('period_id','=', confirmation.period_id.id)], context=context)
            '''if  vals.get('state','') in ['valid']:
                budget_line_vals = {'confirmation_ids':[(1,int(confirmation.id),{'budget_line_id':line_ids and line_ids[0]})]}
                
            elif confirmation.budget_line_id:
                budget_line_vals = {'confirmation_ids':[(3,int(confirmation.id))]}
            budget_line_pool.write(cr, uid, line_ids and line_ids[0] or [], budget_line_vals, context=context)'''
            line_obj = budget_line_pool.browse(cr, uid, line_ids, context=context)
            vals.update({'budget_residual': line_obj and line_obj[0].residual_balance or 0.0})
        res = super(account_budget_confirmation, self).write(cr, uid, ids, vals, context=context)
        if not self._check_company(cr, uid, ids, context=context):
            raise orm.except_orm(_('Warning!'), _('Account, Period and Cost Center must be belong to same Company!'))
        return res

    def action_cancel_draft(self, cr, uid, ids,context={}):
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
            wf_service.trg_delete(uid, 'account.budget.confirmation', id, cr)
            wf_service.trg_create(uid, 'account.budget.confirmation', id, cr)
        return True

    def check_budget(self, cr, uid, ids, context={}):
        """
        This method check whether the budget line residual allow to validate this confirmation or not
        @return: boolean True if budget line residual more that confirm amount, or False
        """
        line_obj = self.pool.get('account.budget.lines')
        for confirmation in self.browse(cr, uid, ids, context=context):
            budget_line = line_obj.search(cr, uid,[('analytic_account_id','=', confirmation.analytic_account_id.id),
                                                   ('period_id','=', confirmation.period_id.id),
                                                   ('general_account_id','=',confirmation.general_account_id.id)], context=context)
            if budget_line:
                if confirmation.residual_amount > line_obj.browse(cr, uid, budget_line, context=context)[0].residual_balance:
                    return False
            elif confirmation.analytic_account_id.budget:
                raise orm.except_orm(_('Warning!'), _('This account has no budget!'))
        return True
    
    def budget_complete(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'complete'
        @return: boolean True    
        """
        self.write(cr, uid, ids, {'state': 'complete'}, context=context)
        return True

    def budget_valid(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'valid'
        @return: boolean True    
        """
        self.write(cr, uid, ids, {'state': 'valid','validating_user_id': uid}, context=context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_trigger(uid, 'account.budget.confirmation', id, cr)
        return True

    def budget_unvalid(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'unvalid'
        @return: boolean True    
        """
        self.write(cr, uid, ids, {'state': 'unvalid'},context=context)
        return True

    def budget_cancel(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'cancel'
        @return: boolean True    
        """
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            if  self.browse(cr, uid, id, context=context).line_id:
                raise orm.except_orm(_('Error!'), _('This confirmation already have posted moves'))
            wf_service.trg_trigger(uid, 'account.budget.confirmation', id, cr)
        return True

account_budget_confirmation()

# ---------------------------------------------------------
# Account Budget Lines
# ---------------------------------------------------------
class account_budget_lines(osv.Model):
    """Inherit the budget line object to add fields of confirmation reflect it's 
    amount on residual balance"""
 
    _inherit = "account.budget.lines"

    def _confirmed_amount(self, cr, uid, ids, field_name, arg=None, context={}):
        """
        This Method use to compute the confirm_amount from confirmation_ids
                    
        @param char field_name: functional field name,
        @param list arg: additional arguments,
        @return: dictionary {record_id: confirmation amount}
        """
        result = {}
        budget_confirm_obj = self.pool.get('account.budget.confirmation')
        for line in self.browse(cr, uid, ids, context=context):
            budget_line_vals = {}
            line_ids = budget_confirm_obj.search(cr, uid,[
                                            ('analytic_account_id','=', line.analytic_account_id.id),
                                            ('general_account_id','=',line.general_account_id.id),
                                            ('period_id','=', line.period_id.id),('state','=','valid')], context=context)
            result[line.id] = sum([l.residual_amount for l in budget_confirm_obj.browse(cr, uid, line_ids,context)])
            if not context.get('update_buget',False) and line.planned_amount + line.total_operation - line.balance - result[line.id]  <0:
                     raise orm.except_orm(_('Error!'), _("Budget can't go overdrow!"))   
        return result

    
    def _residual_balance(self, cr, uid, ids, field_name, arg=None, context={}):
        """
        Recalcute Budget Lines residual_amount by substract confirm amount  
                    
        @param char field_name: functional field name,
        @param list arg: additional arguments,
        @return: dictionary {record_id: residual amount}
        """
        
        cr.execute('SELECT id,planned_amount+total_operation-balance-confirm FROM account_budget_lines WHERE id IN (%s)'% (','.join(map(str,ids)),))
        return dict([(l[0],{'residual_balance':l[1] }) for l in cr.fetchall()])
    
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
                    WHERE planned_amount+total_operation-balance-confirm '+operator+str(value))
        res = cr.fetchall()
        return [('id', 'in', [r[0] for r in res])]

    def _get_confirm_ids(self, cr, uid, ids, context={}):
        """
        get records of budget line to be updated
        @param ids: ids in account asset history
        return dictionary Keys
        """               
        result = []
        for line in self.pool.get('account.budget.confirmation').browse(cr, uid, ids, context=context):
            result = result + self.pool.get('account.budget.lines').search(cr, uid, [
                                         ('general_account_id','=',line.general_account_id.id),
                                         ('analytic_account_id', '=', line.analytic_account_id.id),
                                         ('period_id', '=', line.period_id.id)],
                                            context=context)
        return result        

    _columns = {
        'confirm': fields.function(_confirmed_amount, type='float',  digits_compute=dp.get_precision('Account'), 
                        string='Exchange Amount',
                        store={
                            'account.budget.lines': (lambda self, cr, uid, ids, c={}: ids, 
                                                    ['code','general_account_id', 'analytic_account_id','period_id'], 10),
                            'account.budget.confirmation': (_get_confirm_ids, ['state','line_id'], 20),
                        } ),

        'residual_balance': fields.function(_residual_balance, fnct_search=fnct_residual_search, method=True, multi='residual', 
                                            digits_compute=dp.get_precision('Account'), string='Residual Balance'),
                       
        'confirmation_ids': fields.one2many('account.budget.confirmation', 'budget_line_id', 'Confirmations'),
    }

    #_sql_constraints = [('residual_check_confirm', 'CHECK ((planned_amount+total_operation-balance-confirm)>=0)',  _("Planned Budget cann't go overdrow!"))]

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
         (_check_balance, "lanned Budget cann't go overdrow!", ['balance']), 
    ]'''
account_budget_lines()

# ---------------------------------------------------------
# Account Move Line
# ---------------------------------------------------------
class account_move_line(osv.Model):
    """Inherit account move line object to add budject confirmation field and
        to check the constrains on the created move line with the confirmation line"""

    _inherit = 'account.move.line'

    _columns = {
        'budget_confirm_id': fields.many2one('account.budget.confirmation', 'Confirmation'),
    }

    
    def create(self, cr, uid, vals, context={}, check=True):
        """
        When creating move line with confirmation_id, some constraints has to be check
        1. Confirmation state must be 'approve'.
        2. Move line (account and analytic account) same as (account and analytic account) in confirmation record.
        3. Move Line amount not greater than Confirmed amount.
        4. Move Line and Confirmation in same period. 
        """
        budget_line_pool = self.pool.get('account.budget.lines')
        confirmation_pool = self.pool.get('account.budget.confirmation')
        analytic_pool = self.pool.get('account.analytic.account')
        analytic_budget = vals.get('analytic_account_id', False) and \
                          analytic_pool.read(cr, uid, [vals['analytic_account_id']],['budget'],context=context)[0]['budget'] or False
        confirmation_id = vals.get('budget_confirm_id', False)
        if not context.get('reverse_move',False) and confirmation_id and vals.get('analytic_account_id', False) :
            confirmation_vals = confirmation_pool.read(cr, uid, [confirmation_id], 
                            ['residual_amount', 'period_id', 'type','analytic_account_id',
                             'company_id','general_account_id', 'state'],context=context)[0]

            # Check Confirmation state
            if confirmation_vals['state'] != 'valid':
                raise orm.except_orm(_('Error!'), _('The budget confirmation is not approved'))
            

            # Check if the confirmation (account and analytic account) is not like the move to be create
            analytic_move = vals.get('analytic_account_id', False) 
            analytic_confirm = confirmation_vals['analytic_account_id'][0]
            account_move = vals.get('account_id', False)
            account_confirm = confirmation_vals['general_account_id'][0]
            msg = account_move != account_confirm and 'account /' or ''
            msg += analytic_move != analytic_confirm and ' analytic' or ''
            if msg:
                raise orm.except_orm(_('Warning!'), _('The %s of the move is not like the confirmation!')%(msg,))


            # Check if confirmation amount is less than move amount
            transfer = vals.get('debit', 0) - vals.get('credit', 0)
            if round(confirmation_vals['residual_amount'], 2) < round(transfer, 2) and confirmation_vals['type'] not in ('stock_in', 'stock_out'):
                    raise orm.except_orm(_('Error!'), _('The confirmed amount is less than actual!\n %s - %s')%( round(confirmation_vals['residual_amount'], 2),round(transfer, 2) ))


            # Check if confirmation period and move period are same
            period_move = vals.get('period_id', False) 
            period_confirm = confirmation_vals['period_id'][0]
            confirmation_pool.write(cr, uid, confirmation_id, {'state': 'cancel'}, context=context)
            if period_confirm != period_move and round(transfer, 2) > 0:
                #raise orm.except_orm(_('Warning!'), _('The confirmation period and the move are different!'))
                # NEED TO REVIEW
                # Transfer the confirmed amount from the confirmed period to the move period
                
                from_budget_id = budget_line_pool.search(cr, uid,[('period_id', '=', period_confirm),
                                                                ('analytic_account_id', '=', analytic_confirm),
                                                                ('general_account_id', '=', account_confirm)], 
                                                                context=context)
                if from_budget_id:
                    to = {
                          'company': confirmation_vals['company_id'][0], 
                          'analytic_account': analytic_move,
                          'account_id': account_move,
                          'period_id': period_move
                    }
                    #TEST: test transfer
                    values = {
                        'type':'transfer','to':to,
                        'line_ids':[{'line_id':budget_line_pool.browse(cr, uid, from_budget_id, context)[0],
                                      'amount':transfer}]
                    }
                    budget_line_pool.transfer(cr, uid, values, context=context)
        if context.get('reverse_move', False) and vals['budget_confirm_id']:
            self.pool.get('account.budget.confirmation').write(cr, uid, vals['budget_confirm_id'], {'state':'cancel'}, context=context)
        result = super(account_move_line, self).create(cr, uid, vals, context=context, check=check)
        if confirmation_id and not  context.get('reverse_move', False) :
            confirmation_pool.write(cr, uid, confirmation_id, {'state': 'valid'}, context=context)
        return result

account_move_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

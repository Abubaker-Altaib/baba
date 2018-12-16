# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields, models,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

# ---------------------------------------------------------
# Budget Confirmation
# ---------------------------------------------------------

class AccountBudgetConfirmation(models.Model):
    """ Object of reserve some amount from the budget  """
    _name = "account.budget.confirmation" 
    _inherit = ['mail.thread']
    _order = 'id desc'
    _track = {
              'state': {
            'AccountBudgetConfirmation.mt_budget_state_change': lambda self: True,
            },
        }

    @api.multi
    def _check_company(self):
        """ 
        This method to check that all the confirmation attributes belong to same company            
        @return: boolean True if all belong to same company, or False  
        """
        for budget_confirm in self:
            companies = []
            companies += budget_confirm.account_id and [budget_confirm.account_id.company_id] or []
            companies += budget_confirm.analytic_account_id and [budget_confirm.analytic_account_id.company_id] or []
            if len(set(companies)) > 1:
                return False
        return True

    @api.multi
    @api.depends('account_id', 'analytic_account_id','line_id','line_id.debit','line_id.credit')
    def _residual_amount(self):
        """
        This method calculate the confirmed amount which doesn't turn to actual expense yet
        """
        for budget_confirm in self:
            lines = 0.0
            account = budget_confirm.account_id
            analytic = budget_confirm.analytic_account_id
            for line in budget_confirm.line_id:
                lines += line.debit - line.credit or 0.0
            budget_confirm.residual_amount=budget_confirm.amount - lines

    name= fields.Char('Name', size=64, readonly=True,default='/')
        
    reference= fields.Char('Reference', size=64, readonly=True,default='/')
        
    account_id= fields.Many2one('account.account', 'Account', readonly=True, 
                                               states={'draft':[('readonly',False)]},domain="[('user_type_id.type', '!=', 'view')]")
    analytic_account_id= fields.Many2one('account.analytic.account', 'Analytic Account', 
                                               readonly=True, states={'draft':[('readonly',False)]})
    partner_id= fields.Many2one('res.partner', 'Partner', readonly=True, 
                                      states={'draft':[('readonly',False)]})
    #v11 need to store funtional fields to report purpose 
    residual_amount= fields.Float(compute='_residual_amount', digits_compute=dp.get_precision('Account'),string='Residual Balance',store=True)
    amount=fields.Float('Amount', digits_compute=dp.get_precision('Account'), 
                               states={'draft':[('readonly',False)]})
    state=fields.Selection([('draft','Draft'),('complete','Waiting For Approve'),
                                    ('check','Waiting Check'),('valid','Approved'),
                                    ('unvalid','Not Approved'),('cancel', 'Cancelled')], 
                                    'Status', required=True, readonly=True,default='draft')
    type= fields.Selection([('stock_in','Stock IN'),('stock_out','Stock OUT'),
                                   ('purchase','Purchase'),('other','Others')], 'Type',default='other')
    date=fields.Date('Date', readonly=True, states={'draft':[('readonly',False)]})
    creating_user_id= fields.Many2one('res.users', 'Responsible User',default=lambda self: self.env.user)
    validating_user_id= fields.Many2one('res.users', 'Validate User', readonly=True)
    line_id= fields.One2many('account.move.line', 'budget_confirm_id', 'Entries')
    note=fields.Text('Note', required=True, states={'draft':[('readonly',False)]})
    company_id= fields.Many2one(related='account_id.company_id',string='Company',store=True)
    budget_residual=fields.Float('Budget Residual', required=True, readonly=True, 
                                       digits_compute=dp.get_precision('Account'),default=0.0)
    budget_line_id= fields.Many2one('crossovered.budget.lines', 'Budget Line')

    @api.multi
    @api.constrains('amount')
    def _check_amount(self):
        for obj in self:
            if obj.amount < 0:
                raise ValidationError(_('The amount must be greater than zero.'))

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self,default=None):
        """
        Inherit copy method reset name, line_id and reference when copying confirmation record
        
        @param default: dictionary of the values of record to be created,
        @return: super method of copy    
        """
        default.update({'name': '/', 'line_id': False, 'reference': '/'})
        return super(AccountBudgetConfirmation, self).copy(default)

    @api.model
    def create(self, vals):
        """
        Inherit create method set name from sequence if exist
        and to prohibit the user from entering account, period and cost center of different company
        @param default: dictionary of the values of record to be created,
        @return: super method of copy    
        """
        vals.update({'name': vals.get('name','/') == '/' and 
                     self.env['ir.sequence'].next_by_code('account.budget.confirmation') or 
                     vals.get('name')})
        res = super(AccountBudgetConfirmation, self).create(vals)
        if not self._check_company():
            raise ValidationError(_('Account, Period and Cost Center must be belong to same Company!'))
        return res

    @api.multi
    def write(self, vals):
        """
        The Approved confirmations must be added to confirmation_ids of the effected budget line
        @return: Update confirmation record    
        """
        budget_line_pool = self.env['crossovered.budget.lines']
        for confirmation in self:
            conf_date=confirmation.date
            budget_line_vals = {}
            position = self.env['account.budget.post']._get_budget_position(confirmation.account_id.id)
            if position:
                line_ids = budget_line_pool.search([('analytic_account_id','=', confirmation.analytic_account_id.id),
                                                               ('general_budget_id','=',position.id),
                                                               ('date_from','<=', conf_date),
                                                               ('date_to','>=', conf_date)]
                                                               )
                if  vals.get('state','') in ['valid'] and line_ids:
                    vals.update({'budget_line_id': line_ids.ids[0]})
                    #if not confirmation.budget_line_id:
                    #    budget_line_vals = {'confirmation_ids':[(1,int(confirmation.id),{'budget_line_id':line_ids and line_ids.ids[0]})]}
                    #elif confirmation.budget_line_id:
                    #    budget_line_vals = {'confirmation_ids':[(3,int(confirmation.id))]}

                
                #res = super(AccountBudgetConfirmation, self).write(vals)
                line_obj = budget_line_pool.browse(line_ids.ids)
                #line_obj.write(budget_line_vals)
                vals.update({'budget_residual': line_obj and line_obj[0].residual or 0.0})
        
        if not self._check_company():
            raise ValidationError(_('Account, Period and Cost Center must be belong to same Company!'))
        res = super(AccountBudgetConfirmation, self).write(vals)
        return res

    @api.multi
    def action_cancel_draft(self):
        """
        Workflow function change record state to 'draft', 
        @return: boolean True    
        """
        self.write({'state': 'draft'})

    @api.multi
    def check_budget(self):
        """
        This method check whether the budget line residual allow to validate this confirmation or not
        @return: boolean True if budget line residual more that confirm amount, or False
        """
        budget_line=[]
        line_obj = self.env['crossovered.budget.lines']
        for confirmation in self:
            position = self.env['account.budget.post']._get_budget_position(confirmation.account_id.id)
            
            if not position:
                self.budget_valid()
            else:
                budget_line = line_obj.search([('analytic_account_id','=', confirmation.analytic_account_id.id),
                                                   ('date_from','<=', confirmation.date),
                                                   ('date_to','>=', confirmation.date),
                                                   ('general_budget_id','=',position.id),
                                                   ('crossovered_budget_id.state','=','validate')])
            if budget_line:
                #FIXME: allow_budget_overdraw
                allow_budget_overdraw = budget_line.crossovered_budget_id.allow_budget_overdraw 
                if  not allow_budget_overdraw and confirmation.residual_amount > budget_line.residual: 
                    self.budget_unvalid()
                elif confirmation.residual_amount <= budget_line.residual:
                    self.budget_valid()
                else:
                    self.budget_valid()
            elif confirmation.analytic_account_id.budget:#v9: test me
                raise ValidationError(_('This account has no budget!'))
        return True

    @api.multi
    def budget_complete(self):
        """
        Workflow function change record state to 'complete'
        @return: boolean True    
        """
        self.write({'state': 'complete'})

    @api.multi
    def budget_valid(self):
        """
        Workflow function change record state to 'valid'
        """
        self.write({'state': 'valid','validating_user_id': self.env.user.id})

    @api.multi
    def budget_unvalid(self):
        """
        Workflow function change record state to 'unvalid'
        """
        self.write({'state': 'unvalid'})

    @api.multi
    def budget_cancel(self):
        """
        Workflow function change record state to 'cancel'
        """
        self.write({'state': 'cancel'})
        if self.line_id:
            raise ValidationError(_('This confirmation already have posted moves'))

# ---------------------------------------------------------
# Account Move Line
# ---------------------------------------------------------
class AccountMoveLine(models.Model):
    """Inherit account move line object to add budject confirmation field and
        to check the constrains on the created move line with the confirmation line"""
    _inherit = 'account.move.line'

    budget_confirm_id= fields.Many2one('account.budget.confirmation', 'Confirmation')

    #v11 this method need review after migrate account_custom in reverse_move
    @api.model
    def create(self, vals):
        """
        When creating move line with confirmation_id, some constraints has to be check
        1. Confirmation state must be 'approve'.
        2. Move line (account and analytic account) same as (account and analytic account) in confirmation record.
        3. Move Line amount not greater than Confirmed amount.
        4. Move Line and Confirmation in same period. 
        """
        confirmation_pool = self.env['account.budget.confirmation']
        analytic_pool = self.env['account.analytic.account']
        '''analytic_budget = vals.get('analytic_account_id', False) and \
                                                  analytic_pool.read( [vals['analytic_account_id']],['budget'])[0]['budget'] or False'''
        confirmation_id = vals.get('budget_confirm_id', False)
        #v11 add context (reverse_move) in account custom after migrate it 
        if not self._context.get('reverse_move',False) and confirmation_id and vals.get('analytic_account_id', False) :
            confirmation_vals = confirmation_pool.browse([confirmation_id])
            # Check Confirmation state
            if confirmation_vals.state != 'valid':
                raise UserError(_('The budget confirmation is not approved'))
            # Check if the confirmation (account and analytic account) is not like the move to be create
            analytic_move = vals.get('analytic_account_id', False) 
            analytic_confirm = confirmation_vals.analytic_account_id.id
            account_move = vals.get('account_id', False)
            account_confirm = confirmation_vals.account_id.id
            msg = account_move != account_confirm and 'account /' or ''
            msg += analytic_move != analytic_confirm and ' analytic' or ''
            if msg:
                raise UserError(_('The %s of the move is not like the confirmation!')%(msg,))
            # Check if confirmation amount is less than move amount
            transfer = vals.get('debit', 0) - vals.get('credit', 0)
            if round(confirmation_vals.residual_amount, 2) < round(transfer, 2) and confirmation_vals.type not in ('stock_in', 'stock_out'):
                    raise ValidationError(_('The confirmed amount is less than actual!\n %s - %s')%( round(confirmation_vals.residual_amount, 2),round(transfer, 2) ))
            # Check if confirmation period and move period are same
            period_move = vals.get('date', False) 
            period_confirm = confirmation_vals.date
            #v11 why to cancel budget confirmation??
            #confirmation_vals.write({'state': 'cancel'})
        if self._context.get('reverse_move', False) and vals['budget_confirm_id']:
            confirmation_vals.budget_cancel()
            vals.update({'budget_confirm_id':False})     
        result = super(AccountMoveLine, self).create(vals)
        #v11 when post voucher confirmation must be valid is this true???
        #if confirmation_id:
            #confirmation_pool.browse(confirmation_id).write({'state': 'valid'})
        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

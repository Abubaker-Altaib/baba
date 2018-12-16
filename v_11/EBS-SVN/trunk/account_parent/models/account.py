# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 Steigend IT Solutions
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
from odoo import api, fields, models,exceptions, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    _sql_constraints = [('type_name_uniq', 'unique (name)', 'Account Type Name must be unique!')]

    type = fields.Selection(selection_add=[('view','View')])

    @api.constrains('name')
    def check_name(self):
        if not all(x.isalpha() or x.isspace() for x in self.name):
            raise UserError(_("Invalid Account Type:\nthe Account Type must be letters"))

    '''
    override the write method and excute write(vals) method 
    '''
    @api.multi
    def write(self, vals):
        for account_type in self :
            move =self.env['account.move.line'].search([('account_id.user_type_id','=',account_type.id)])
          
        if move :
            raise ValidationError(_('Can not edit type of account that have journal items!'))
        else:
            return super(AccountAccountType, self).write(vals)


class AccountAccount(models.Model):
    _inherit = "account.account"
    
    @api.model
    def _move_domain_get(self, domain=None):
        context = dict(self._context or {})
        domain = domain and safe_eval(str(domain)) or []
        date_field = 'date'
        if context.get('aged_balance'):
            date_field = 'date_maturity'
        if context.get('date_to'):
            domain += [(date_field, '<=', context['date_to'])]
        if context.get('date_from'):
            if not context.get('strict_range'):
                domain += ['|', (date_field, '>=', context['date_from']), ('account_id.user_type_id.include_initial_balance', '=', True)]
            elif context.get('initial_bal'):
                domain += [(date_field, '<', context['date_from'])]
            else:
                domain += [(date_field, '>=', context['date_from'])]
        if context.get('journal_ids'):
            domain += [('journal_id', 'in', context['journal_ids'])]
        state = context.get('state')
        if state and state.lower() != 'all':
            domain += [('move_id.state', '=', state)]
        if context.get('company_id'):
            domain += [('company_id', '=', context['company_id'])]
        if 'company_ids' in context:
            domain += [('company_id', 'in', context['company_ids'])]
        if context.get('reconcile_date'):
            domain += ['|', ('reconciled', '=', False), '|', ('matched_debit_ids.create_date', '>', context['reconcile_date']), ('matched_credit_ids.create_date', '>', context['reconcile_date'])]
        return domain

    @api.multi
    @api.depends('move_line_ids','move_line_ids.amount_currency','move_line_ids.debit','move_line_ids.credit')
    def compute_values(self):
        default_domain = self._move_domain_get()
        for account in self:
            sub_accounts = self.with_context({'show_parent_account':True}).search([('id','child_of',[account.id])])
            balance = 0.0
            credit = 0.0
            debit = 0.0
            search_domain = default_domain[:]
            search_domain.insert(0,('account_id','in',sub_accounts.ids))
            for aml in self.env['account.move.line'].search(search_domain):
                balance += aml.debit - aml.credit
                credit += aml.credit
                debit += aml.debit
            account.balance = balance
            account.credit = credit
            account.debit = debit

    move_line_ids = fields.One2many('account.move.line','account_id','Journal Entry Lines')
    balance = fields.Float(compute="compute_values", digits=dp.get_precision('Account'), string='Balance')
    credit = fields.Float(compute="compute_values",digits=dp.get_precision('Account'), string='Credit')
    debit = fields.Float(compute="compute_values",digits=dp.get_precision('Account'), string='Debit')
    parent_id = fields.Many2one('account.account','Parent Account',ondelete="set null")
    child_ids = fields.One2many('account.account','parent_id', 'Child Accounts')
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)
    next_child = fields.Integer('next child', default=1)


    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'code, name'
    _order = 'parent_left'

    #specify a constrain on user_type_id to prevent user from changing type of parent if it has childs
    @api.constrains('user_type_id')
    def _check_child_id(self):
        child_ids=self.env['account.account'].search([('parent_id','in',self.ids)])
        if child_ids and self.ids:
            raise ValidationError(_("You can't change account type from view to another type when it has children"))

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        if not context.get('show_parent_account',False):
            args += [('user_type_id.type', '!=', 'view')]
        return super(AccountAccount, self).search(args, offset, limit, order, count=count)


    @api.one
    @api.constrains('next_child')
    def _check_nex_child(self):
        if self.next_child<=0:
            raise Warning(_('The Next child  must be more than zero !!!!!'))

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        '''
        This function generates the account number automatically with the possibility to modify it
        '''
        par_code=""
        if self.parent_id:
            par_code = self.parent_id.code
            count= self.parent_id.next_child
            serial=int(count)
            self.code = par_code+str(serial)
            serial+=1
            self.parent_id.write({'next_child':serial})

    @api.onchange('code')
    def onchange_code(self):
        child_ids=self.env['account.account'].search([('parent_id','=',self._origin.id)])
        if child_ids and self._origin.id:
            self.next_child=1
            par_code_self=self.code
            for r in child_ids:
                count_child= self.next_child
                seria=int(count_child)
                new_code= par_code_self+str(seria)
                r.code=new_code
                r.write({'code':new_code})
                seria+=1
                self.next_child=seria

        '''This function generates the account number automatically with the possibility to modify it
        '''



class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    _sql_constraints = [
        ('name_inherit_uniq', 'unique (name,company_id)', 'The name of the journal must be unique per company !')
    ]

    @api.model
    def _prepare_liquidity_account(self, name, company, currency_id, type):
        res = super(AccountJournal, self)._prepare_liquidity_account(name, company, currency_id, type)
        # Seek the next available number for the account code
        code_digits = company.accounts_code_digits or 0
        if type == 'bank':
            account_code_prefix = company.bank_account_code_prefix or ''
        else:
            account_code_prefix = company.cash_account_code_prefix or company.bank_account_code_prefix or ''

        liquidity_type = self.env.ref('account_parent.data_account_type_view')
        parent_id = self.env['account.account'].search([('code','=',account_code_prefix),
                                                        ('company_id','=',company.id),('user_type_id','=',liquidity_type.id)], limit=1)

        if parent_id:
            res.update({'parent_id':parent_id.id})
        return res


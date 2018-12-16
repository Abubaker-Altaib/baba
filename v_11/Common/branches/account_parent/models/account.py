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

    type = fields.Selection(selection_add=[('view','View')])
    close_year = fields.Selection([
        ('profit_loss', 'profit and loss'),
        ('balance', 'balance')], string='close year',required=True, default='balance',)
    nature = fields.Selection([("debit","Debit"),("credit","Credit")],"Nature",)
    active = fields.Boolean('Active', default=True)
    code = fields.Char('Code')
    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id, )', 'Account Type name must be unique !'),
        ('code_company_uniq', 'unique(code, company_id, )', 'Account Type code must be unique !'),
    ]

class AccountAccount(models.Model):
    _inherit = "account.account"
    
    external_code = fields.Char('External user code')
    level = fields.Integer('Level', compute='compute_level', store=True)
    close_year = fields.Selection( [('profit_loss', 'profit and loss'),
        ('balance', 'balance')],related='user_type_id.close_year', store=True)
    nature = fields.Selection([("debit","Debit"),("credit","Credit")],"Nature",related='user_type_id.nature', store=True)


    @api.multi
    @api.depends('code')
    def compute_level(self):
        for account in self:
            account.level = account.parent_id and account.parent_id.level + 1 or 0

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


class AccountJournal(models.Model):
    _inherit = "account.journal"


    default_debit_account_id = fields.Many2one('account.account', string='Default Debit Account',
    domain=[('deprecated', '=', False), ('user_type_id.type', '!=', 'view')], help="It acts as a default account for debit amount")
    default_credit_account_id = fields.Many2one('account.account', string='Default Credit Account',
    domain=[('deprecated', '=', False), ('user_type_id.type', '!=', 'view')], help="It acts as a default account for credit amount")

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




class AccountInvoice(models.Model):
    _inherit = "account.invoice"


    account_id = fields.Many2one('account.account', string='Account',
    required=True, readonly=True, states={'draft': [('readonly', False)]},
    domain=[('deprecated', '=', False), ('user_type_id.type', '!=', 'view')], help="The partner account used for this invoice.")

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    account_id = fields.Many2one('account.account', string='Account',
    required=True, domain=[('deprecated', '=', False), ('user_type_id.type', '!=', 'view')],
    help="The income or expense account related to the selected product.")


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    account_id = fields.Many2one('account.account', string='Account', required=True, index=True,
    ondelete="cascade", domain=[('deprecated', '=', False), ('user_type_id.type', '!=', 'view')], default=lambda self: self._context.get('account_id', False))

class AccountTax(models.Model):
    _inherit = 'account.tax'

    account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False), ('user_type_id.type', '!=', 'view')], string='Tax Account', ondelete='restrict',
    help="Account that will be set on invoice tax lines for invoices. Leave empty to use the expense account.", oldname='account_collected_id')


class res_partner (models.Model):
    _inherit = "res.partner"

    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
    string="Account Payable", oldname="property_account_payable",
    domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False), ('user_type_id.type', '!=', 'view')]",
    help="This account will be used instead of the default one as the payable account for the current partner",
    required=True)

    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
    string="Account Receivable", oldname="property_account_receivable",
    domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False), ('user_type_id.type', '!=', 'view')]",
    help="This account will be used instead of the default one as the receivable account for the current partner",
    required=True)


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"

    account_id = fields.Many2one('account.account', string='Account', ondelete='cascade', domain=[('deprecated', '=', False), ('user_type_id.type', '!=', 'view')])
    second_account_id = fields.Many2one('account.account', string='Second Account', ondelete='cascade', domain=[('deprecated', '=', False), ('user_type_id.type', '!=', 'view')])

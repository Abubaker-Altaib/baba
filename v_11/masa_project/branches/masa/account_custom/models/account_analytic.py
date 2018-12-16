# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields, exceptions, tools, models,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

class account_analytic(models.Model):

    _inherit = "account.analytic.account"

    type = fields.Selection([("view","View"),("normal","Normal")],"Type" ,required=True, default='normal')
    cost_type=fields.Selection([("restricted","Restricted"),("unrestricted","Unrestricted"),("awqaf","Awqaf")],"Cost Type" )
    parent_id = fields.Many2one('account.analytic.account',string='Parent',required=False)
    child_ids = fields.One2many('account.analytic.account', 'parent_id',string= 'childs')
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)
    
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'code, name'
    _order = 'parent_left'
    
    _sql_constraints = [
        ('name_company_uniq', 'unique(name,type,company_id)', 'The name must be unique per  company!'),
        ('code_company_uniq', 'unique(code,type,company_id)', 'The code must be unique per  company!'),
    ]

    @api.onchange('child_ids')
    def onchange_child_ids(self):
        childs_user_ids = [(4,[child_ids.user_id])]               
            
    @api.multi
    def _compute_debit_credit_balance(self):
        analytic_line_obj = self.env['account.analytic.line']
        for account in self:
            sub_accounts = self.with_context({'show_parent_account': True}).search([('id', 'child_of', [account.id])])
            credit = 0.0
            debit = 0.0
            domain = [('account_id', 'in', sub_accounts.ids)]
            if self._context.get('from_date', False):
                domain.append(('date', '>=', self._context['from_date']))
            if self._context.get('to_date', False):
                domain.append(('date', '<=', self._context['to_date']))
            for aal in analytic_line_obj.search(domain):
                if aal.amount < 0.0:
                    debit += aal.amount
                else:
                    credit += aal.amount
            account.credit = credit
            account.debit = abs(debit)
            account.balance = account.credit - account.debit
            

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    account_analytic_id = fields.Many2one('account.analytic.account',
    string='Analytic Account')


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    credit = fields.Monetary('Credit', required=True,compute='_compute_debit_credit')
    debit = fields.Monetary('Debit', required=True,compute='_compute_debit_credit')
    
    @api.one
    @api.depends('move_id')
    def _compute_debit_credit(self):
        if self.move_id:
            self.debit=self.move_id.debit
            self.credit=self.move_id.credit




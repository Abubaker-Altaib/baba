# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields, exceptions, tools, models,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError,UserError
        
class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    move = fields.Selection([('normal','Normal'),('view','View')],"Type" ,required=True, default='normal')
    close_year = fields.Selection([
        ('profit_loss', 'Profit and loss'),
        ('balance', 'Balance')], string='Close Year',required=True, default='balance',)
    nature = fields.Selection([("debit","Debit"),("credit","Credit")],"Nature",)
    active = fields.Boolean('Active', default=True, help="Set active to false to hide the Account Type without removing it.")
    code = fields.Char(size=64, required=True, index=True)
    parent_id = fields.Many2one('account.account.type','Parent Type',ondelete="set null")
    child_ids = fields.One2many('account.account.type','parent_id', 'Child Accounts')
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)
    account_ids = fields.One2many('account.account','user_type_id','Accounts')
    balance = fields.Float(compute="compute_values", digits=dp.get_precision('Account'), string='Balance')
    credit = fields.Float(compute="compute_values",digits=dp.get_precision('Account'), string='Credit')
    debit = fields.Float(compute="compute_values",digits=dp.get_precision('Account'), string='Debit')
    level = fields.Integer(compute='_get_level', string='Level', store=True)
    next_child = fields.Integer('Next child', default=1)

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'code, name'
    _order = 'parent_left'

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Account Type name must be unique !'),
        ('code_uniq', 'unique(code)', 'Account Type code must be unique !'),
    ]

    @api.multi
    @api.depends('parent_id', 'parent_id.level')
    def _get_level(self):
        for rec in self:
            level = 0
            if rec.parent_id:
                level = rec.parent_id.level + 1
            rec.level = level
            
    @api.multi
    @api.depends('account_ids','account_ids.move_line_ids','child_ids')
    def compute_values(self):
        for acc_type in self:
            balance = 0.0
            credit = 0.0
            debit = 0.0
            if acc_type.type == 'normal':
                for child in acc_type.child_ids:
                    balance += child.balance
                    credit += child.credit
                    debit += child.debit
            else:
                for account in acc_type.account_ids:
                    balance += account.balance
                    credit += account.credit
                    debit += account.debit
            acc_type.balance = balance
            acc_type.credit = credit
            acc_type.debit = debit

    @api.onchange('parent_id')
    def onchange_parent_id_code(self):
        '''
        This function generates the account Type code automatically with the possibility to modify it
        '''
        if self.parent_id:
            # get code size from company data
            code_size  = self.env.user.company_id.account_code_size

            parent_code = self.parent_id.code
            #to make new code start with 1
            count = self.parent_id.next_child
            serial = int(count)
            code_length = len(str(parent_code)) + len(str(serial))
            #Insert zeros between main parent code and new code
            zeros = '0'
            #you can multiple strings , PYTHON IS AWOSOME ^_^
            self.code = parent_code + (zeros * (code_size - code_length)) +str(serial)
            serial += 1
            self.parent_id.next_child=serial
            #self.parent_id.write({'next_child': serial})
        # elif self.parent_id :
        #     parent_id = self.parent_id
        #     count = parent_id.next_child
        #     serial = int(count)
        #     self.code = parent_id.code + str(serial)
        # else:
        #    self.code = None
                
    
class AccountJournal(models.Model):
    _inherit = "account.journal"

    type = fields.Selection(selection_add=[('pl_close','Profit and loss close')])
    bank_statements_source = fields.Selection([('undefined', 'Undefined Yet'),('manual', 'Record Manually'),('file_import','File Import')], string='Bank Feeds',default='file_import')
    parent_id = fields.Many2one('account.journal',string='Journal Parent')
    financial_era = fields.Boolean(string="Financial era")

    @api.multi
    @api.depends('name')
    def name_get(self):
        res = []
        for journal in self:
            name = journal.name
            res += [(journal.id, name)]
        return res


class AccountAccount(models.Model):
    _inherit ='account.account'

    active = fields.Boolean(default=True, help="Set active to false to hide the Account without removing it.")
    analytic = fields.Boolean("Analytic")
    analytic_account_ids = fields.Many2many('account.analytic.account', string='Analytic Account',
         domain="[('type', '=', 'normal')]")
    external_code = fields.Char('External user code')
    close_year = fields.Selection( [('profit_loss', 'Profit and loss'),
        ('balance', 'Balance')],related='user_type_id.close_year', store=True)
    nature = fields.Selection([("debit","Debit"),("credit","Credit")],"Nature",related='user_type_id.nature', store=True)
    move_line_ids = fields.One2many('account.move.line','account_id','Journal Entry Lines')
    balance = fields.Float(compute="_compute_account_balance", digits=dp.get_precision('Account'), string='Balance')
    credit = fields.Float(compute="_compute_account_balance",digits=dp.get_precision('Account'), string='Credit')
    debit = fields.Float(compute="_compute_account_balance",digits=dp.get_precision('Account'), string='Debit')
    
        
    @api.multi
    @api.depends('move_line_ids','move_line_ids.amount_currency','move_line_ids.debit','move_line_ids.credit')
    def _compute_account_balance(self):
        for account in self:
            report_acc_obj = self.env['report.account.report_financial']
            rec = report_acc_obj._compute_account_balance(account)[account.id]
            account.debit = rec['debit']
            account.credit = rec['credit']
            account.balance = rec['balance']

    @api.multi
    def write(self, vals):
        for account in self:
            if ('code' in vals and account.code != vals['code']):
                if account.move_line_ids:
                    raise UserError(_('You cannot edit name or code of account that have journal entries.'))
        return super(AccountAccount, self).write(vals)

class AccountTax(models.Model):
    _inherit ='account.tax'

    code = fields.Char(string ="Code")
    date =fields.Date(string ="Date")
    type_tax_use  = fields.Selection([("purchase","Out"),("sale","In")],"Tax Scope" ,required=True)
    
    _sql_constraints = [
        ('code_uniq', 'unique(code,company_id)', 'The code must be unique per company !')
    ]

    @api.multi
    @api.constrains('amount')
    def _not_equel_zero(self):
        for record in self:
            if record.amount_type:
                if record.amount_type != 'group' and record.amount == 0:
                    raise Warning(_("The amount can not be zero!"))
                    
    @api.multi
    def unlink(self):
        parameter_obj = self.env['ir.config_parameter']
        sale_tax=parameter_obj.search([('key','=','account.default_sale_tax_id'),('value','=',self.id)])
        purchase_tax=parameter_obj.search([('key','=','account.default_purchase_tax_id'),('value','=',self.id)])
        if sale_tax or purchase_tax:
            raise ValidationError(_("can't delete this record, Because it is referred to in Default Taxes!"))
        return super(AccountTax, self).unlink()

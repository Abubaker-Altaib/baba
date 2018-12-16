# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields,exceptions, tools, models,_
from odoo.exceptions import ValidationError

class AccountJournal(models.Model):
    _inherit = "account.journal"

    bank_statements_source = fields.Selection([('undefined', 'Undefined Yet'),('manual', 'Record Manually'),('file_import','File Import')], string='Bank Feeds',default='file_import')
    financial_era = fields.Boolean(string="Financial era")

    @api.multi
    @api.depends('name')
    def name_get(self):
        res = []
        for journal in self:
            name = journal.name
            res += [(journal.id, name)]
        return res

class resPartner(models.Model):
    _inherit = 'res.partner'

    code = fields.Char(strin="code",required=True)

    _sql_constraints = [
        ('code_name_uniq', 'unique (code,name,company_id)', 'The code,name must be unique per company !')
    ]

    @api.constrains('email')
    def _validate_email(self):
        for partner in self:
            if partner.email and not tools.single_email_re.match(partner.email):
                raise Warning(_("Please enter a valid email address."))
        return True

class AccountTax(models.Model):
    _inherit ='account.tax'

    code = fields.Char(string ="Code")
    date =fields.Date(string ="Date")
    type_tax_use  = fields.Selection([("purchase","Out"),("sale","In")],"Tax Scope" ,required=True)
    
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


class account_account(models.Model):
    _inherit ='account.account'

    nature = fields.Selection([("debit","Debit"),("credit","Credit")],"Nature")

    @api.multi
    @api.constrains('code', 'name')
    def _check_name_code(self):
        for account in self:
            if account.move_line_ids:
                raise ValidationError(_('You cannot edit name or code of account that have journal entries.'))



class account_move_line(models.Model):
    _inherit ='account.move.line'


    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account' ,domain="[('type', '=', 'normal')]")

    @api.multi
    @api.constrains('account_id')
    def _nature_move_line_account(self):
        for record in self:
            if record.account_id.nature =='debit' and record.account_id.balance < 0 :
                raise Warning(_("The balance of debit account should not be less than zero !!!!!  \n -account:%s \n-balance:%s ")%(record.account_id.name,record.account_id.balance))

            elif record.account_id.nature =='credit' and record.account_id.balance > 0 :
                raise Warning(_("The balance of credit account should not be more than zero  !!!!!  \n -account:%s \n-balance:%s ")%(record.account_id.name,record.account_id.balance))


    @api.multi
    @api.constrains('period_id')
    def _not_close_period(self):
        for line in self:
            if line.period_id.state=='done':
                raise Warning(_("Can not create move in close period!"))


class account_analytic(models.Model):
    """
    Inherit analytic object to add selection field type which options (view, normal)
    """

    _inherit = "account.analytic.account"

    type = fields.Selection([("view","View"),("normal","Normal")],"Type" ,required=True, default='normal')
    cost_type=fields.Selection([("restricted","Restricted"),("unrestricted","Unrestricted"),("awqaf","Awqaf")],"Cost Type" ,required=True)
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


    
class account_payment(models.Model):
    _inherit = "account.payment"

    payment_transfer_date = fields.Date(string='Payment Transfer Date', default=fields.Date.context_today,required=True, copy=False)
    name = fields.Char(readonly=True, copy=False, default=_("Draft Payment"))

    @api.multi
    def send(self):
        for rec in self:
            # Use the right sequence to set the name
            sequence_code = 'account.payment.transfer'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
            if not rec.name :
                raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)
            transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
            rec.write({'state': 'sent', 'move_name': move.name})

    @api.multi
    def confirm(self):
        for rec in self:
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            transfer_debit_aml = rec._create_transfer_entry(amount)
            rec.write({'state': 'posted'})

    def _create_transfer_entry(self, amount):
        """ Create the journal entry corresponding to the 'incoming money' part of an internal transfer, return the reconciliable move line
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, dummy = aml_obj.with_context(date=self.payment_transfer_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
        amount_currency = self.destination_journal_id.currency_id and self.currency_id.with_context(date=self.payment_date).compute(amount, self.destination_journal_id.currency_id) or 0

        dst_move = self.env['account.move'].create(self._get_move_vals(self.destination_journal_id, self.payment_transfer_date))

        dst_liquidity_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, dst_move.id)
        dst_liquidity_aml_dict.update({
            'name': _('Transfer from %s') % self.journal_id.name,
            'account_id': self.destination_journal_id.default_credit_account_id.id,
            'currency_id': self.destination_journal_id.currency_id.id,
            'journal_id': self.destination_journal_id.id})
        aml_obj.create(dst_liquidity_aml_dict)

        transfer_debit_aml_dict = self._get_shared_move_line_vals(credit, debit, 0, dst_move.id)
        transfer_debit_aml_dict.update({
            'name': self.name,
            'account_id': self.company_id.transfer_account_id.id,
            'journal_id': self.destination_journal_id.id})
        if self.currency_id != self.company_id.currency_id:
            transfer_debit_aml_dict.update({
                'currency_id': self.currency_id.id,
                'amount_currency': -self.amount,
            })
        transfer_debit_aml = aml_obj.create(transfer_debit_aml_dict)
        dst_move.post()
        return transfer_debit_aml

    def _get_move_vals(self, journal=None,date=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'), _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)
        name = self.move_name or journal.with_context(ir_sequence_date=self.payment_date).sequence_id.next_by_id()
        if date:
            return {
                'name': name,
                'date':date,
                'ref': self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
                 }
        else:
            return {
                'name': name,
                'date': self.payment_date,
                'ref': self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
                 }

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


class AccountMoveCustom(models.Model):
    _inherit = 'account.move'

    payment_id = fields.Many2one('account.payment', string="Payment")


class AccountMoveReversalCustom(models.TransientModel):
    _inherit = 'account.move.reversal'

    @api.multi
    def reverse_moves(self):
        ac_move_ids = self._context.get('active_ids', False)
        move = self.env['account.move'].search([('id', 'in', ac_move_ids)])
        for voucher in move.payment_id.voucher_ids:
            voucher.state = 'cancel'
        move.payment_id.state = 'cancelled'
        for budget_confirm in move.line_ids:
            budget_confirm.budget_confirm_id.write({'state': 'cancel'})
        return super(AccountMoveReversalCustom, self).reverse_moves()



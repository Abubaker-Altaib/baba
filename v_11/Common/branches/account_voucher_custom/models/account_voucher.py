# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo.exceptions import Warning, ValidationError, UserError
from odoo import api, fields, models, _ 
from odoo.addons.account_check_printing_custom.models import amount_to_text_ar


class AccountPayment(models.Model):
    _inherit = "account.payment"

    voucher_ids = fields.One2many('account.voucher', 'payment_id' ,copy=False, ondelete='restrict')
    state = fields.Selection([('draft', 'Draft'),('paid', 'Paid'),('sent', 'Sent'),('posted', 'Posted'),('reconciled', 'Reconciled'), ('cancelled', 'Cancelled')], readonly=True, default='draft', copy=False, string="Status")
    

    @api.multi
    def pay(self):
        for payment in self:
            if payment.voucher_ids:
                payment.voucher_ids.write({'state':'paid'})
            payment.write({'state': 'paid'})

    @api.multi
    def check_consistency(self):
        for rec in self:
            vouchers = rec.voucher_ids
            if not vouchers:
                continue
            if any(voucher.currency_id != rec.currency_id for voucher in vouchers):
                raise UserError(_("Voucher must belong to the same Currency."))
            if rec.amount != sum(rec.mapped('voucher_ids.amount')):
                raise UserError(_("Payment Amount is incorect."))

    @api.onchange('voucher_ids')
    def onchange_voucher_ids(self):
        if self.voucher_ids:
            self.amount = sum(self.mapped('voucher_ids.amount'))

    @api.multi
    def unmark_sent(self):
        self.write({'state': 'paid'})


    @api.multi
    def post(self):
        for payment in self:
            if payment.voucher_ids:
                pay_now = payment.voucher_ids.mapped('pay_now')
                pay_now = list(set(pay_now))
                if len(pay_now) == 1:
                    payment.voucher_ids.proforma_voucher()
                    payment.write({'state': 'posted'})
                    return True
            else:
                # Add this line to avoid exception in post
                payment.state='draft'
                return super(AccountPayment, self).post()
        return True

 
class AccountVoucher(models.Model):
    _inherit = 'account.voucher'
    
    @api.model
    def _default_journal(self):
        return super(AccountVoucher, self)._default_journal()
        
    currency_id = fields.Many2one('res.currency', compute=False,
        string='Currency', readonly=True, required=True, default=lambda self: self._get_currency(),
        states={'draft': [('readonly', False)],'req_draft': [('readonly', False)]})  
    journal_id = fields.Many2one('account.journal', 'Journal',
        required=True, readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange', default=_default_journal)  
    pay_now = fields.Selection([
        ('pay_now', 'Pay Directly'),
        ('pay_later', 'Pay Later')], 'Payment', index=True, default='pay_now')
    payment_id = fields.Many2one('account.payment', 'Payment', readonly=True, copy=False) 
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type',track_visibility='onchange')
    payment_method_code = fields.Char(related='payment_method_id.code',
        help="Technical field used to adapt the interface to the payment type selected.", readonly=True)
    account_id = fields.Many2one('account.account', 'Account', required=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('proforma', 'Pro-forma'),
        ('no_budget', 'Budget Not Appoved'),
        ('review', 'To Review'),
        ('confirm', 'To Confirm'),
        ('final_confirm', 'To Final Confirm'),
        ('approve', 'To Approve'),
        ('pay', 'To Pay'),
        ('paid', 'Paid'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
        ],string='Status', readonly=True, size=32,default="draft", track_visibility='onchange')
               
    check_lines=fields.Boolean(compute='_check_lines',string="Check Lines")
    partner_id = fields.Many2one('res.partner', compute='_compute_partner_id', string="Partner", store=True, readonly=True)
    amount_in_words = fields.Char(string="Amount in Words", compute='_onchange_amount')
    outbound_payment_method_ids=fields.Many2many(related='payment_journal_id.outbound_payment_method_ids',readonly=True)
    @api.model
    def create(self, vals):
        journal = vals['journal_id']
        sequence = self.env['account.journal'].browse(journal).sequence_id
        if 'date' in vals:
            date=vals['date']
        else:
            date=fields.Date.today()
        vals['number'] = sequence.with_context(ir_sequence_date=date).next_by_id()
        return super(AccountVoucher, self).create(vals)

    @api.model
    def create(self, vals):
        if 'journal_id' in vals:
            journal = vals['journal_id']
            sequence = self.env['account.journal'].browse(journal).sequence_id
            if 'date' in vals:
                date=vals['date']
            else:
                date=fields.Date.today()
            vals['number'] = sequence.with_context(ir_sequence_date=date).next_by_id()
        return super(AccountVoucher, self).create(vals)

    @api.multi
    def unlink(self):
        if self.payment_id.state !='draft':
                raise UserError(_('You can not delete none draft voucher.'))
        return super(AccountVoucher, self).unlink()

    @api.multi
    def voucher_reject_reason(self,reason):
        for voucher in self:
            voucher.message_post_with_view('account_voucher_custom.voucher_template_reject_reason',
                values={'reason': reason.name, 'name':voucher.number})
            voucher.write({'state': 'refused'})

    @api.one
    @api.depends('amount')
    def _onchange_amount(self):
        if self._context.get('lang') == 'ar_SY':
            units_name=self.currency_id.currency_unit_label
            cents_name=self.currency_id.currency_subunit_label
            self.amount_in_words = amount_to_text_ar.amount_to_text(self.amount, 'ar',units_name,cents_name)

    @api.multi
    @api.depends('line_ids.partner_id')
    def _compute_partner_id(self):
        for voucher in self:
            partner = voucher.line_ids.mapped('partner_id')
            voucher.partner_id = partner.id if len(partner) == 1 else False
    
    @api.multi
    @api.depends('line_ids','line_ids.state')
    def _check_lines(self):
        check_lines = False
        for voucher in self:
            if voucher.voucher_type == 'purchase':
                check_lines = all(l.state =='approve' for l in voucher.line_ids)
            voucher.check_lines = check_lines
            
    @api.one
    @api.depends('move_id.line_ids.reconciled', 'move_id.line_ids.account_id.internal_type','payment_id.state')
    def _check_paid(self):
        self.paid = False
        if self.pay_now == 'pay_now':
          if self.payment_id.state in ['posted','reconciled']:
             self.paid = True
        else:
            self.paid = any([((line.account_id.internal_type, 'in', ('receivable', 'payable')) and line.reconciled) for line in self.move_id.line_ids]) 
            
    @api.onchange('payment_journal_id')
    def onchange_payment_journal_id(self):
        if self.payment_journal_id:
            if self.pay_now == 'pay_now':
                self.account_id = self.payment_journal_id.default_debit_account_id \
                    if self.voucher_type == 'sale' else self.payment_journal_id.default_credit_account_id
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.voucher_type == 'sale' and self.payment_journal_id.inbound_payment_method_ids or self.payment_journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = self.voucher_type == 'purchase' and 'outbound' or 'inbound'
            return {'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}
        return {}
               
    @api.multi
    @api.constrains('amount')
    def _total_amount_check(self):
        for voucher in self:
            if voucher.state not in ['draft','cancel','no_approve' ,'submit'] and voucher.amount==0.0:
                raise ValidationError(_("Operation is not completed, Total amount shouldn't be zero!"))

    @api.multi
    def unlink(self):
        for record in self:
            if record.state not in ('draft', 'req_darft') or record.create_uid.id != self.env.user.id:
                raise Warning(_('Cannot delete voucher(s) which are already opened or you are not the user that created this record'))
        return super(AccountVoucher, self).unlink()

    @api.multi
    def voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
        for line in self.line_ids:
            #create one move line per voucher line where amount is not 0.0
            if not line.price_subtotal:
                continue
            line_subtotal = line.price_subtotal
            if self.voucher_type == 'sale':
                line_subtotal = -1 * line.price_subtotal
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context,
            # so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(line.price_unit*line.quantity)
            move_line = {
                'journal_id': self.journal_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': line.partner_id.commercial_partner_id.id,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': abs(amount) if self.voucher_type == 'sale' else 0.0,
                'debit': abs(amount) if self.voucher_type == 'purchase' else 0.0,
                'date': self.account_date,
                'tax_ids': [(4,t.id) for t in line.tax_ids],
                'amount_currency': line_subtotal if current_currency != company_currency else 0.0,
                'currency_id': company_currency != current_currency and current_currency or False,
                'payment_id': self._context.get('payment_id'),
                'budget_confirm_id': line.budget_confirm_id and line.budget_confirm_id.id or False,
                'budget_line_id': line.budget_confirm_id and line.budget_confirm_id.budget_line_id.id
            }
            self.env['account.move.line'].with_context(apply_taxes=True).create(move_line)
        return line_total

    @api.multi
    def account_move_get(self):
        if self.number:
            name = self.number
        elif self.journal_id.sequence_id:
            if not self.journal_id.sequence_id.active:
                raise UserError(_('Please activate the sequence of selected journal !'))
            name = self.journal_id.sequence_id.with_context(ir_sequence_date=self.date).next_by_id()
        else:
            raise UserError(_('Please define a sequence on the journal.'))

        move = {
            'name': name,
            'journal_id': self.journal_id.id,
            'narration': self.narration,
            'payment_id': self.payment_id.id,
            'date': self.account_date,
            'ref': self.reference,
        }
        return move
                
    @api.multi
    def action_move_line_create(self):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        journal = self.mapped('journal_id')
        currency = self.mapped('currency_id')
        account_date = self.mapped('account_date')
        account_date = list(set(account_date))[0]
        payment = self.mapped('payment_id')
        pay_now = self.mapped('pay_now')
        pay_now = list(set(pay_now))[0]
        voucher_type = self.mapped('voucher_type')
        voucher_type = list(set(voucher_type))[0]
        company = self.mapped('company_id')
        account_id = self.mapped('account_id')
        narration= str(v.narration + str("\n") for v in self)
        
        amount = sum(voucher.amount for voucher in self)
        first_move_line={}
        account_move={}

        local_context = dict(self._context, force_company=journal.company_id.id)

        company_currency = journal.company_id.currency_id.id
        current_currency = currency.id or company_currency
        # we select the context to use accordingly if it's a multicurrency case or not
        # But for the operations made by _convert_amount, we always need to give the date in the context
        ctx = local_context.copy()
        ctx['date'] = payment.payment_date
        ctx['check_move_validity'] = False
        # Create a payment to allow the reconciliation when pay_now = 'pay_now'.
        if pay_now == 'pay_now' and amount > 0:
            ctx['payment_id'] = payment.id
        
        if len(self) == 1:
            account_move = self.account_move_get()
            name=""
            if payment.check_number:
                name=payment.check_number
            if not payment.check_number and journal.sequence_id:
                if not journal.sequence_id.active:
                    raise UserError(_('Please activate the sequence of selected journal !'))
                name = journal.sequence_id.with_context(ir_sequence_date=account_date).next_by_id()
            else:
                raise UserError(_('Please define a sequence on the journal.'))
            account_move.update({'name': name})
        else:
            if payment.check_number:
                name=payment.check_number
            if not payment.check_number and journal.sequence_id:
                if not journal.sequence_id.active:
                    raise UserError(_('Please activate the sequence of selected journal !'))
                name = journal.sequence_id.with_context(ir_sequence_date=account_date).next_by_id()
            else:
                raise UserError(_('Please define a sequence on the journal.'))
            account_move = {
                'name': name,
                'journal_id': journal.id,
                'narration': narration,
                'payment_id': payment.id,
                'date': payment.payment_date,
            }


        # Create the account move record.  
        move = self.env['account.move'].create(account_move)

        # Use the right sequence to set the Payment name in case of pay later
        if payment.payment_type == 'transfer':
            sequence_code = 'account.payment.transfer'
        else:
            if payment.partner_type == 'customer':
                if payment.payment_type == 'inbound':
                    sequence_code = 'account.payment.customer.invoice'
                if payment.payment_type == 'outbound':
                    sequence_code = 'account.payment.customer.refund'
            if payment.partner_type == 'supplier':
                if payment.payment_type == 'inbound':
                    sequence_code = 'account.payment.supplier.refund'
                if payment.payment_type == 'outbound':
                    sequence_code = 'account.payment.supplier.invoice'
        payment.name = self.env['ir.sequence'].with_context(ir_sequence_date=payment.payment_date).next_by_code(sequence_code)
        if not payment.name and payment.payment_type != 'transfer':
            raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

        if len(self) == 1:
            first_move_line=self.with_context(ctx).first_move_line_get(move.id, company_currency, current_currency)
        else: 
            debit = credit = 0.0
            if voucher_type == 'purchase':
                credit = currency.compute(amount, company.currency_id)
            elif voucher_type == 'sale':
                debit = currency.compute(amount, company.currency_id)
            if debit < 0.0: debit = 0.0
            if credit < 0.0: credit = 0.0
            sign = debit - credit < 0 and -1 or 1
            #set the first line of the voucher
            first_move_line = {
                    'name': payment.name or '/',
                    'debit': debit,
                    'credit': credit,
                    'account_id': account_id.id,
                    'move_id': move.id,
                    'journal_id': journal.id,
                    'partner_id': payment.partner_id.commercial_partner_id.id,
                    'currency_id': company_currency != current_currency and current_currency or False,
                    'amount_currency': (sign * abs(amount)  # amount < 0 for refunds
                        if company_currency != current_currency else 0.0),
                    'date': payment.payment_date,
                    'payment_id': payment.id,
                }

       
        # Create the first line of the voucher
        move_line = self.env['account.move.line'].with_context(ctx).create(first_move_line)
        for voucher in self:
            if voucher.move_id:
                continue
            line_total = move_line.debit - move_line.credit
            if voucher.voucher_type == 'sale':
                line_total = line_total - voucher._convert_amount(voucher.tax_amount)
            elif voucher.voucher_type == 'purchase':
                line_total = line_total + voucher._convert_amount(voucher.tax_amount)
            # Create one move line per voucher line where amount is not 0.0
            line_total = voucher.with_context(ctx).voucher_move_line_create(line_total, move.id, company_currency, current_currency)
            # Add tax correction to move line if any tax correction specified
            if voucher.tax_correction != 0.0:
                tax_move_line = self.env['account.move.line'].search([('move_id', '=', move.id), ('tax_line_id', '!=', False)], limit=1)
                if len(tax_move_line):
                    tax_move_line.write({'debit': tax_move_line.debit + voucher.tax_correction if tax_move_line.debit > 0 else 0,
                        'credit': tax_move_line.credit + voucher.tax_correction if tax_move_line.credit > 0 else 0})
        # We post the voucher.
        self.write({
            'move_id': move.id,
            'state': 'posted',
            'name': payment.name
        })
        payment.write({
            'move_name': move.name
        })
        move.post()
        return True

    @api.multi
    def voucher_pay_now_payment_create(self):
        if not self.payment_method_id:
            raise UserError(_('Please Enter Payment Method.'))
        if self.voucher_type == 'sale':
            payment_method = self.payment_method_id
            payment_type = 'inbound'
            partner_type = 'customer'
            sequence_code = 'account.payment.customer.invoice'
        else:
            payment_method = self.payment_method_id
            payment_type = 'outbound'
            partner_type = 'supplier'
            sequence_code = 'account.payment.supplier.invoice'
        name = self.env['ir.sequence'].with_context(ir_sequence_date=self.date).next_by_code(sequence_code)
        return {
            'name': name,
            'payment_type': payment_type,
            'payment_method_id': payment_method and payment_method.id or False,
            'partner_type': partner_type,
            'partner_id': self.partner_id.commercial_partner_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'payment_date': self.date,
            'journal_id': self.payment_journal_id.id,
            'company_id': self.company_id.id,
            'communication': self.number,
            'state': 'draft',
        }
        
    @api.multi
    def action_payment_create(self):  
        if self.pay_now == 'pay_now' and self.amount > 0 and not self.payment_id:
            if self.payment_method_code == 'check_printing' and not self.partner_id:
                raise ValidationError(_('There is no beneficiary to create a Check payment for it!'))
            else:
                payment_id = self.env['account.payment'].create(self.voucher_pay_now_payment_create())
                #Update amount_in_words
                payment_id.write({'check_amount_in_words':payment_id._onchange_amount()})
                self.write({'payment_id':payment_id.id})
        return True
         
    @api.multi    
    def budget_confirmation_create(self):
        for voucher in self:
            if voucher.journal_id.type == 'purchase':
                for line in voucher.line_ids:
                    if not line.account_analytic_id:
                        continue
                    amount = self._convert_amount(line.price_subtotal)
                    vals = {
                         'reference': voucher.number,
                         'partner_id': line.partner_id.id,
                         'account_id': line.account_id.id,
                         'date': voucher.account_date or voucher.date,
                         'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id,
                         'amount': amount,
                         'type':self._context.get('type','other'),
                         'note':line.name or '/',
                         'state':'draft',
                    }
                    if line.budget_confirm_id:
                        line.budget_confirm_id.write(vals)
                        new_confirm_id = line.budget_confirm_id
                    else:
                        new_confirm_id = self.env['account.budget.confirmation'].create(vals)
                        line.write({'budget_confirm_id':new_confirm_id.id})
                    if voucher.company_id.auto_budget:
                        new_confirm_id.check_budget()
        return True        
        
    @api.multi
    def action_proforma(self):
        self.write({'state': 'proforma'})
        
    @api.multi
    def action_check_budget(self):
        self.budget_confirmation_create()
        for line in self.line_ids:
            if not line.partner_id:
                raise ValidationError(_('Please Enter partner in all Voucher line!'))
        if self.check_lines:
            self.write({'state': 'review'})
        else:
            self.write({'state': 'no_budget'})
        return True

    @api.multi
    def action_recheck_budget(self):
        if self.check_lines:
            self.write({'state': 'review'})
        else:
            raise ValidationError(_('The Budget confirmation Not Appove yet!'))
            
    @api.multi
    def action_confirm(self):
        self.write({'state': 'final_confirm'})
        
    @api.multi
    def action_final_confirm(self):
        if self.amount > self.company_id.double_approval_amount:
            self.write({'state': 'approve'})
        else:
            self.write({'state': 'pay'})
            
    @api.multi
    def action_review(self):
        self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        self.write({'state': 'pay'})
        
        
    @api.multi
    def proforma_voucher(self):
        if any(voucher.state != 'paid' for voucher in self):
            raise UserError(_("You cannot post non paid voucher!"))
        journal = self.mapped('journal_id')
        payment_journal_id = self.mapped('payment_journal_id')
        currency = self.mapped('currency_id')
        account_date = self.mapped('account_date')
        account_date = list(set(account_date))
        payment = self.mapped('payment_id')

        pay_now = self.mapped('pay_now')
        pay_now = list(set(pay_now))
        company = self.mapped('company_id')
        account_id = self.mapped('account_id')
        voucher_type = self.mapped('voucher_type')
        voucher_type = list(set(voucher_type))[0]
        if not account_id:
            account_id = payment_journal_id.default_debit_account_id \
                if voucher_type == 'sale' else payment_journal_id.default_credit_account_id
            for rec in self:
                rec.account_id=account_id

        if len(journal) != 1:
            raise UserError(_("The Posted Voucher must Belong to The same Journal!"))
        elif len(currency) != 1:
            raise UserError(_("The Posted Voucher must Have to The same Currency!"))
        elif len(payment) != 1:
            raise UserError(_("The Posted Voucher must Have to The same Payment!"))
        elif len(pay_now) != 1:
            raise UserError(_("The Posted Voucher must Have to The same Payment Type!"))
        elif len(company) != 1:
            raise UserError(_("The Posted Voucher must Belong to The same Company!"))
        elif len(account_id) != 1 and account_id:
            raise UserError(_("The Posted Voucher must Have The same Account!"))
        return super(AccountVoucher, self).proforma_voucher()

    @api.multi
    def action_cancel_draft(self):
        for voucher in self:
            for l in voucher.line_ids:
                if l.budget_confirm_id:
                    l.budget_confirm_id.write({'state':'draft'})
        self.write({'state': 'draft'})
            

    @api.multi
    def cancel_voucher(self):
        for voucher in self:
            for l in voucher.line_ids:
               if l.budget_confirm_id:
                  l.budget_confirm_id.budget_cancel()
        return super(AccountVoucher, self).cancel_voucher()
        

class AccountVoucherLine(models.Model):

    _inherit = 'account.voucher.line'
    
    @api.model
    def default_get(self, fields):
        rec = super(AccountVoucherLine, self).default_get(fields)
        if 'line_ids' not in self._context:
            return rec
        if self._context['line_ids']:
            last = self._context['line_ids'][-1]
            if last[2]:  
                product_id = last[2].get('product_id')
                amount=0.0
                account_analytic_id=last[2].get('account_analytic_id')
                name=last[2].get('name')
                account_id=last[2].get('account_id')
                rec.update({'product_id': product_id,
                    'price_unit':amount,
                    'account_analytic_id':account_analytic_id,
                    'name':name,
                    'account_id':account_id})
                return rec
    @api.model
    def _default_account(self):
        if self._context.get('journal_id'):
            journal = self.env['account.journal'].browse(self._context.get('journal_id'))
            if self._context.get('voucher_type') =='sale':
                return journal.default_credit_account_id.id
            return journal.default_debit_account_id.id

    account_id = fields.Many2one('account.account', string='Account',
        required=True, domain=[('deprecated', '=', False), ('user_type_id.type', '!=', 'view')],
        default=_default_account,
        help="The income or expense account related to the selected product.")
    budget_confirm_id= fields.Many2one('account.budget.confirmation', 'Confirmation', copy=False, ondelete="restrict")
    state=fields.Selection([
        ('complete','Waiting for Approve'),
        ('approve','Approved'),
        ('no_approve','Budget Not Approved'),
        ('cancel','Canceled')], 'State', required=True, readonly=True,default='complete')
    partner_id = fields.Many2one('res.partner',string="Partner")

    @api.onchange('account_analytic_id')
    def onchange_account_analytic_id(self):
        if self.account_analytic_id and self.account_analytic_id.budget_post_ids:
            self.account_id=False
            accounts=[]
            for post in self.account_analytic_id.budget_post_ids:
                accounts+= post.account_ids.ids 
            return {'domain': {'account_id': [('id', 'in', accounts)]}}

    @api.multi
    @api.constrains('account_id')
    def _check_account_company(self):
        for rec in self:
            if rec.account_id.company_id !=  rec.voucher_id.company_id:
                raise ValidationError(_('The account company is not like the voucher company!'))

    @api.multi
    @api.constrains('account_analytic_id', 'account_id')
    def _check_analytic_required(self):
        for rec in self:
            if rec.account_id.analytic_required and not rec.account_analytic_id:
                raise ValidationError(_('The %s must have  Analytic Account ')%(rec.account_id.name))
                
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            if not self.name:
                self.name = self.product_id.display_name or ''
            self.price_unit = self.product_id.price_compute('list_price')[self.product_id.id]
            self.product_uom_id = self.product_id.uom_id
            self.tax_ids = self.product_id.supplier_taxes_id
            account = self.product_id.product_tmpl_id._get_product_accounts()['expense']
            if account:
                self.account_id = account

    @api.multi
    def unlink(self):
        confirmation_ids = [l.budget_confirm_id for l in self if l.budget_confirm_id]
        if confirmation_ids:
            confirmation_ids.unlink()
        return super(AccountVoucherLine, self).unlink()


class AccountBudgetConfirmation(models.Model):

    _inherit = "account.budget.confirmation"

    voucher_line_ids=fields.One2many('account.voucher.line', 'budget_confirm_id', 'Voucher Lines')

    @api.multi
    def budget_valid(self):
        """
        overwrite to change vocher line state to approve
        """
        for conf in self:
            for line in conf.voucher_line_ids:
                line.write({'state': 'approve'})
        return super(AccountBudgetConfirmation, self).budget_valid()

    @api.multi
    def budget_unvalid(self):
        """
        overwrite to change vocher line state to no_approve
        """
        for conf in self:
            for line in conf.voucher_line_ids:
                line.write({'state': 'no_approve'})
        return super(AccountBudgetConfirmation, self).budget_unvalid()

    @api.multi
    def budget_cancel(self):
        """
        overwrite to change vocher line state to cancel
        """
        super(AccountBudgetConfirmation, self).budget_cancel()
        for conf in self:
            for line in conf.voucher_line_ids:
                line.write({'state': 'cancel'})


class AccountRejectReason(models.Model):
    _name='account.reject.reason'

    name=fields.Char(string="Name" , copy=False)
    code=fields.Char(string="Code")
    description=fields.Text(string="Description")

    _sql_constraints = [
        ('name_reason_uniq', 'unique (name)', 'The name must be unique !')
    ]
    
    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_('%s (copy)') % self.name)
        return super(AccountRejectReason, self).copy(default)

class AccountMove(models.Model):
    _inherit ='account.move'

    voucher_ids = fields.One2many('account.voucher','move_id', string='Vouchers',readonly=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

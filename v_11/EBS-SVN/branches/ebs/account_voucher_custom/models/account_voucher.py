# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import netsvc
from odoo.exceptions import Warning,UserError, ValidationError
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.addons import decimal_precision as dp
from num2words import num2words
import calendar



class AccountVoucher(models.Model):

    _inherit = 'account.voucher'

    #currency_label=fields.Char(related='currency_id_ebs.currency_unit_label',string='currency label' , readonly="True")

    @api.one
    @api.depends(
        'state', 'currency_id', 'line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        residual = 0.0
        residual_company_signed = 0.0
        sign = 1
        for line in self.sudo().move_id.line_ids:
            if line.account_id == self.account_id:
                residual_company_signed += line.amount_residual
                if line.currency_id == self.currency_id:
                    residual += line.amount_residual_currency if line.currency_id else line.amount_residual
                else:
                    from_currency = (line.currency_id and line.currency_id.with_context(date=line.date)) or line.company_id.currency_id.with_context(date=line.date)
                    residual += from_currency.compute(line.amount_residual, self.currency_id)
        self.residual_company_signed = abs(residual_company_signed) * sign
        self.residual_signed = abs(residual) * sign
        self.residual = abs(residual)
        digits_rounding_precision = self.currency_id.rounding
        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False

    @api.one
    @api.depends('move_id.line_ids.amount_residual')
    def _compute_payments(self):
        payment_lines = set()
        for line in self.move_id.line_ids.filtered(lambda l: l.account_id.id == self.account_id.id):
            payment_lines.update(line.mapped('matched_credit_ids.credit_move_id.id'))
            payment_lines.update(line.mapped('matched_debit_ids.debit_move_id.id'))
        self.payment_move_line_ids = self.env['account.move.line'].browse(list(payment_lines))

    installment_type = fields.Selection([('payable','Payables'),
                                         ('pre_paid_expense','Pre Paid Expense'),
                                         ('middle_payment','Middle Payments')])
    middle_payment_account = fields.Many2one('account.account')
    pre_paid_exp_account = fields.Many2one('account.account',string="Pre Paid Expense Account")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('proforma', 'Pro-forma'),
        #('no_approve','Waiting For Budget Appove'),
        #('no_approve2','Budget Not Appoved'),
        #('approved','Budget Approved'),
        ('submit','To submit'),
        ('requested','Waiting for approve (Ratification List)'),
        ('service','Waiting Service Manager'),
        ('completed','Waiting Head of Expenditure Unit'),
        ('confirmed','Waiting Head of Financial Section'),
        ('approved','Waiting Internal Auditor'),
        ('reviewed','Waiting Financial Manager'),
        ('posted', 'Posted'),
        ('waiting', 'Waiting for payment and post to Complete'),
        ('paid', 'Paid')
        ], 'Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Voucher.\n"
             " * The 'Pro-forma' status is used when the voucher does not have a voucher number.\n"
             " * The 'Posted' status is used when user create voucher,a voucher number is generated and voucher entries are created in account.\n"
             " * The 'Cancelled' status is used when user cancel voucher.\n"
             " * The 'Waiting For Budget Appove' status is when all budget confirmations related to this voucher didn\'t approve yet.\n"
             " * The 'Budget Not Appoved' status is when at least one of budget confirmations related to this voucher didn\'t approve.\n"
             " * The 'approved' status is when all budget confirmations are approved.\n"
             " * The 'Paid' status is when voucher is totally paid.\n")
    
    pay_now = fields.Selection(selection_add=[('installments', 'Installments')])
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type',
        help="Manual: Get paid by cash, check or any other method outside of Odoo.\n"\
        "Electronic: Get paid automatically through a payment acquirer by requesting a transaction on a card saved by the customer when buying or subscribing online (payment token).\n"\
        "Check: Pay bill by check and print it from Odoo.\n"\
        "Batch Deposit: Encase several customer checks at once by generating a batch deposit to submit to your bank. When encoding the bank statement in Odoo, you are suggested to reconcile the transaction with the batch deposit.To enable batch deposit,module account_batch_deposit must be installed.\n"\
        "SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit to your bank. To enable sepa credit transfer, module account_sepa must be installed ",
        domain=lambda self: self._get_payment_method_id())
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True, string='Company Currency')
    
    reconciled = fields.Boolean(string='Paid/Reconciled', store=True, readonly=True, compute='_compute_residual',
        help="It indicates that the voucher has been paid and the journal entry of the invoice has been reconciled with one or several journal entries of payment.")
    residual = fields.Monetary(string='Amount Due',
        compute='_compute_residual', store=False, help="Remaining amount due.")
    
    residual_signed = fields.Monetary(string='Amount Due In Invoice Currency', currency_field='currency_id',
       compute='_compute_residual', store=True, help="Remaining amount due in the currency of the invoice.")
    
    residual_company_signed = fields.Monetary(string='Amount Due In Company Currency', currency_field='company_currency_id',
        compute='_compute_residual', store=True, help="Remaining amount due in the currency of the company.")
    
    payment_complete = fields.Boolean(default=False,copy=False)
    payment_ids = fields.Many2many('account.payment', 'account_voucher_payment_rel', 'voucher_id', 'payment_id', 
        string="Payments", copy=False, readonly=True)
    payment_move_line_ids = fields.Many2many('account.move.line', string='Payment Move Lines', compute='_compute_payments', store=True)
    department_id =fields.Many2one('hr.department', string='Department', readonly=True, states={'draft': [('readonly', False)]},)
    payment_id = fields.Many2one('account.payment', 'Payment', readonly=True, copy=False)
    currency_id = fields.Many2one('res.currency', compute=False,
        string='Currency', readonly=False, required=True, default=lambda self: self._get_currency())
    payment_journal_id = fields.Many2one('account.journal', string='Payment Journal', readonly=True, store=False,
        states={'draft': [('readonly', False)]}, domain="[('type', 'in', ['cash', 'bank'])]",
        compute='_compute_payment_journal_id', inverse='_inverse_payment_journal_id')
    move_ids = fields.One2many('account.move','voucher_id',readonly=1,string='Journal Items')
    user_id = fields.Many2one('res.users', 'User',default=lambda self: self.env.user)

    @api.model
    def _get_currency(self):
        journal = self.env['account.journal'].browse(self.env.context.get('default_journal_id', False))
        if journal.currency_id:
            return journal.currency_id.id
        return self.env.user.company_id.currency_id.id


    @api.model
    def _get_payment_method_id(self):
        """
        """
        domain = [('id','in',[])]
        if self.payment_journal_id:
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.voucher_type == 'sale' and self.payment_journal_id.inbound_payment_method_ids or self.payment_journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            domain = [('id','in',payment_methods.ids)]
            #return {'domain': {'payment_method_id': [('id', 'in', payment_methods.ids)]}}
        return domain


    @api.model
    def default_get(self, fields):
        res = super(AccountVoucher, self).default_get(fields)
        user = self.env['res.users'].search([('id','=',self._uid)]).name
        emp = self.env['hr.employee'].search([('name', '=', user)])
        if emp:
            res.update({'department_id': emp.department_id.id})
        return res
        
    @api.onchange('payment_journal_id')
    def _onchange_payment_journal_id(self):
        """
        Function change payment_method_id based on payment_journal_id
        """
        payment_type = self.voucher_type == 'sale' and 'inbound' or 'outbound'
        self.payment_method_id = False
        if self.payment_journal_id:
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.voucher_type == 'sale' and self.payment_journal_id.inbound_payment_method_ids or self.payment_journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            return {'domain': {'payment_method_id': [('id', 'in', payment_methods.ids)]}}
        return {}

    @api.one
    @api.depends('move_id.line_ids.reconciled', 'move_id.line_ids.account_id.internal_type','payment_id.state')
    def _check_paid(self):
        self.paid = False
        if self.pay_now == 'pay_now':
          if self.payment_id.state in ['posted','reconciled']:
             self.paid = True
        else:
            self.paid = any([((line.account_id.internal_type, 'in', ('receivable', 'payable')) and line.reconciled) for line in self.move_id.line_ids])

    @api.multi
    @api.constrains('amount')
    def _check_amount(self):
        """
        Constraint method that doesn't allow voucher's amount being Zero when state is not draft, cancel or no_approve
        
        @return: boolean
        """
        for voucher in self:
            if voucher.state not in ['draft','cancel','no_approve','completed'] and voucher.amount==0.0:
                raise ValidationError(_("Operation is not completed, Total amount should be more than zero!"))

    @api.multi
    def action_confirmed(self):
        # if self.filtered(lambda voucher: voucher.state != 'draft'):
        #     raise UserError(_('Voucher must be in Draft state ("To Submit") in order to confirm it.'))
        self.ensure_one()
        write = self.write({'state': 'confirmed'})
        # filter line which required budget
        line_ids = self.line_ids.filtered(lambda r: r.account_id.budget_required and r.analytic_account_id and r.analytic_account_id.budget)
        if line_ids:
            line_ids.check_voucher_line_account_budget()
            self.create_budget_confirmation()
        return write

    @api.multi
    def action_approved(self):
        return self.write({'state': 'approved'})

    @api.multi
    def action_reviewed(self):
        return self.write({'state': 'reviewed'})

    @api.multi
    def cancel_voucher(self):
        for voucher in self:
            voucher.move_id.button_cancel()
            voucher.move_id.unlink()
        self.write({'state': 'cancel', 'move_id': False})


    # TO DO: canceled voucher can be deleted ??
    @api.multi
    def unlink(self):
        """
        Inherit unlink method to delete all confirmations that belong to the deleted voucher lines
        @return: super unlink
        """
        for record in self:
            if record.state not in ('draft', 'cancel'):
                raise Warning(_('Cannot delete voucher(s) which are already opened.'))

            confirmation_ids = self.get_confirmation_ids()
            if confirmation_ids: confirmation_ids.unlink()
        return super(AccountVoucher, self).unlink()



    ## Open if payment created from voucher should be in posted state not reconsilled
    ## Also to update journal_id of payment, payment_method_id of the payment
    @api.multi
    def voucher_pay_now_payment_create(self):
        """
        Overwrite to update state of payment dict to be draft
        """
        #vals = super(AccountVoucher,self).voucher_pay_now_payment_create
        #vals['state'] = 'post'
        #return vals
        if self.voucher_type == 'sale':
            payment_methods = self.journal_id.inbound_payment_method_ids
            payment_type = 'inbound'
            partner_type = 'customer'
            sequence_code = 'account.payment.customer.invoice'
        else:
            payment_methods = self.journal_id.outbound_payment_method_ids
            payment_type = 'outbound'
            partner_type = 'supplier'
            sequence_code = 'account.payment.supplier.invoice'
        name = self.env['ir.sequence'].with_context(ir_sequence_date=self.date).next_by_code(sequence_code)
        return {
            'name': name,
            'payment_type': payment_type,
            #'payment_method_id': payment_methods and payment_methods[0].id or False,
            'payment_method_id': self.payment_method_id.id or False,
            'partner_type': partner_type,
            'partner_id': self.partner_id.commercial_partner_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'payment_date': self.date,
            'journal_id': self.payment_journal_id.id,
            'company_id': self.company_id.id,
            'communication': self.name,
            'state': 'reconciled',
        }
        
        

    @api.multi
    def voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        voucher_line_pool = self.env['account.voucher.line']
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
                'partner_id': self.partner_id.commercial_partner_id.id,
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
    def action_move_line_create(self):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        for voucher in self:
            local_context = dict(self._context, force_company=voucher.journal_id.company_id.id)
            if voucher.move_id:
                continue
            company_currency = voucher.journal_id.company_id.currency_id.id
            current_currency = voucher.currency_id.id or company_currency
            # we select the context to use accordingly if it's a multicurrency case or not
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = local_context.copy()
            ctx['date'] = voucher.account_date
            ctx['check_move_validity'] = False
            # Create a payment to allow the reconciliation when pay_now = 'pay_now'.
            if self.pay_now == 'pay_now' and self.amount > 0:
                ctx['payment_id'] = self.env['account.payment'].create(self.voucher_pay_now_payment_create()).id
            # Create the account move record.
            move = self.env['account.move'].create(voucher.account_move_get())
            # Get the name of the account_move just created
            # Create the first line of the voucher
            move_line = self.env['account.move.line'].with_context(ctx).create(voucher.with_context(ctx).first_move_line_get(move.id, company_currency, current_currency))
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
            voucher.write({
                'move_id': move.id,
                'state': 'posted',
                'number': move.name,
                'payment_id': 'payment_id' in ctx and ctx['payment_id'] or False
            })
            move.post()
        return True

    @api.multi
    def register_payment(self, payment_line, writeoff_acc_id=False, writeoff_journal_id=False):
        """ Reconcile payable/receivable lines from the voucher with payment_line """
        line_to_reconcile = self.env['account.move.line']
        for inv in self:
            line_to_reconcile += inv.move_id.line_ids.filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
        return (line_to_reconcile + payment_line).reconcile(writeoff_acc_id, writeoff_journal_id)

    def proforma_voucher(self):
        """
        override proforma voucher tomake required operation to  pay_later and  installments
        :return:
        """
        # company_currency = voucher.journal_id.company_id.currency_id.id
        # current_currency = voucher.currency_id.id or company_currency
        if self.pay_now == 'installments':
            #create sequence

            #make it like standar , give voucher sequence name
            self.name =  self.env['ir.sequence'].with_context(ir_sequence_date=self.date).next_by_code('account.payment.supplier.invoice')
            self.number = self.name


            voucher_date = self.date
            # we can set date with function datetime :TODO
            current_month = int(voucher_date[5:7])
            current_year = int(voucher_date[0:4])

            #month numbers to div amount
            div = 12 - (current_month-1)

            #in case div = zero that means date in  month 12 so only one move will be created
            if div == 0:
                div = 1


            #create moves
            #12 is number of month in a year
            currency = self.currency_id
            while current_month <= 12:
                #print("<>>>>>>>>>>>>>>>>>>>>>>>>>>",self.env['res.company'].search([('id','=',1)]).currency_id.name,self.currency_id_ebs.name)
                lines = [(0, 6, {
                    'name': _('Middle Account'),
                    'account_id': self.account_id.id,
                    'debit': 0.0,
                    'credit': self.currency_id.compute(round(self.amount/div,2),self.company_id.currency_id),
                    'partner_id': self.partner_id.id if self.partner_id else None ,
                    'currency_id': currency.id,
                    'amount_currency': round(self.amount/div,2) * -1
                })]
                #voucher lines
                for line in self.line_ids:

                    lines += [(0, 6, {
                        'name': _('Service Account'),
                        'account_id': line.account_id.id,
                        'debit': self.currency_id.compute(round(line.price_subtotal/div,2),self.company_id.currency_id),
                        'credit': 0.0,
                        'partner_id': self.partner_id.id if self.partner_id else None ,
                        'analytic_account_id': line.account_analytic_id.id if line.account_analytic_id else None,
                        'currency_id': currency.id,
                        'amount_currency':round(line.price_subtotal/div,2)
                    })]

                #we can set date with function datetime:TODO BY Mudathir
                move_id = self.env['account.move'].with_context(check_move_validity=False).create({
                    'ref': self.number,
                    'date': ""+str(current_year)+"-"+str(current_month)+"-"+str(calendar.monthrange(current_year, current_month)[1]),
                    'company_id': self.company_id.id,
                    'partner_id': self.partner_id.id if self.partner_id else None ,
                    'journal_id': self.journal_id.id,
                    'line_ids': lines,
                    'voucher_id': self.id
                })



                current_month += 1
            #change voucher state to waiting
            self.state = 'waiting'
        else:
            super(AccountVoucher,self).proforma_voucher()

    
    ## TO DO: This function is based on automatic confirmation , 
    ## if not automatic the need to changed and even confirmation workflow
    @api.multi
    def create_budget_confirmation(self):
        """ 
        This Method for creating Budget Confirmation for each Voucher Line with analytic account
        @return: boolean True it any confirmation created, or return False
        """
        confirmation_obj = self.env['account.budget.confirmation']
        for voucher in self:
            if voucher.voucher_type == 'purchase':
                line_ids = self.line_ids.filtered(lambda r: r.account_id and r.account_id.budget_required \
                    and r.analytic_account_id and r.analytic_account_id.budget)
                for line in line_ids:
                    ## check when there is tax and its account_id same as line account_id
                    total_amount = 0
                    tax_ids = False
                    if line.tax_ids:
                        tax_ids = line.tax_ids.filtered(lambda tax: tax.account_id and tax.account_id.id == line.account_id.id)
                        tax_info = tax_ids.compute_all(line.price_unit, voucher.currency_id, line.quantity, line.product_id, voucher.partner_id)
                        total_amount += tax_info.get('total_included', 0.0)
                        tax_amount += sum([t.get('amount',0.0) for t in tax_info.get('taxes', False)])     
                    ## confirmation amount is total of tax + price_subtotal
                    total_amount = tax_amount + line.price_subtotal
                    if tax_ids:
                        amount = total_amount
                    else:
                        amount = voucher.currency_id.with_context(date=voucher.date).compute(total_amount, voucher.company_id.currency_id)
                    val = {
                         'reference': voucher.number,
                         'partner_id': voucher.partner_id.id,
                         'account_id': line.account_id.id,
                         'date': voucher.date,
                         'analytic_account_id': line.account_analytic_id and voucher_line.account_analytic_id.id,
                         'amount': amount,
                         'residual_amount': amount,
                         'type':self._context.get('type','other'),
                         'note':line.name or '/',
                    }
                    new_confirm_id = False
                    if not line.budget_confirm_id:
                        new_confirm_id = confirmation_obj.create(val)
                        line.write({'budget_confirm_id': new_confirm_id})
                        if new_confirm_id and voucher.company_id.auto_budget:
                            new_confirm_id.action_cancel_draft()
                            new_confirm_id.budget_complete()
                            new_confirm_id.check_budget()
                            
        return True

    @api.multi
    def get_confirmation_ids(self):
        """
        This method return all voucher lines that have a budget confirmation.
        
        @return: list of all budget_confirm_ids for voucher lines 
        """
        return [voucher_line.budget_confirm_id for voucher in self for voucher_line in voucher.line_ids if voucher_line.budget_confirm_id]

    def cancel_voucher(self):
        """
        Object button method which canceling all  budget confirmation
        and change voucher state to "cancel"
        
        @return: super cancel_voucher
        """
        super(AccountVoucher, self).cancel_voucher()
        confirmation_ids = self.get_confirmation_ids()
        confirmation_ids.budget_cancel()
        return True

    def _get_currency_rate_date(self):
        """
        Function to return date required to get last currency rate to create move 
        or to compute line price with company currency
        """
        return self.date


    def check_installments_voucher_done(self,voucher_id):
        """
        Cheak if installment voucher done to change voucher state to done if installments and moves get paid and posted
        :param voucher_id:
        :return:
        """
        voucher = self.search([('id','=',voucher_id)])
        moves = True
        payment = True
        for line in voucher.move_ids:
            if line.payment_state == 'draft':
                payment = False
                break
            elif line.state == 'draft':
                moves = False
                break

        if payment == True:
            self.payment_complete = True
        if moves == True and payment == True:
            self.state = 'posted'



    def open_payment_view(self):
        """
        To open payment view to pay all residual moves
        :return:
        """
        view = self.env.ref('account.view_account_payment_invoice_form')

        residual_move_amount = sum(line.line_ids[0].amount_currency if line.line_ids[
                                                                                   0].amount_currency > 0 else line.amount if line.amount > 0 else line.amount * -1 for line in self.env['account.move'].search([('voucher_id','=',self.id),('payment_state','=','draft')]))

        return {
            'name': _('Payment'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
        #    'res_id': wiz.id,
            'context': {
                        'account_id':self.account_id.id,
                        'default_partner_id':self.partner_id.id if self.partner_id else None,
                        'default_payment_type':'outbound',
                        'default_amount':round(residual_move_amount,2),
                        #'voucher_active_id':self.id,
                'residual_moves_amount':round(residual_move_amount,2),
                'move_residual':True,
                'voucher_id':self.id
                        },
        }

   

class AccountVoucherLine(models.Model):

    _inherit = 'account.voucher.line'

    @api.multi
    def unlink(self):
        """
        Inherit unlink method to delete budget confirmation that belong to the deleted voucher line.
        
        @return: Deleting selected records
        """
        confirmation_ids = [voucher_line.budget_confirm_id.id for voucher_line in self if voucher_line.budget_confirm_id]
        line = super(AccountVoucherLine, self).unlink()
        if confirmation_ids:
            self.env['account.budget.confirmation'].browse(confirmation_ids).unlink()
        return line

    
    name = fields.Char('Description', size=256, required=True,default='/')
    budget_confirm_id = fields.Many2one('account.budget.confirmation', 'Confirmation', select=2, ondelete="restrict")
    state = fields.Selection([('complete','Waiting for Approve'),('approve','Approved'),('no_approve','Budget Not Approved'),
                                  ('cancel','Canceled')], 'State', required=True, readonly=True,default='complete')
    total_amount = fields.Float('Total Amount')
    price_subtotal = fields.Monetary(string='Amount',store=True, readonly=True, compute='_compute_subtotal')
    price_total_signed = fields.Monetary(string='Amount Signed', currency_field='company_currency_id',
        store=True, readonly=True, compute='_compute_subtotal',
        help="Total amount in the currency of the company, negative for credit note.")
    company_currency_id = fields.Many2one('res.currency', related='voucher_id.company_currency_id', readonly=True, related_sudo=False)
    account_budget_required = fields.Boolean(related='account_id.budget_required')


    @api.one
    @api.depends('price_unit', 'tax_ids', 'quantity', 'product_id', 'voucher_id.currency_id', 'voucher_id.company_id')
    def _compute_subtotal(self):
        """
        Function was overwrite to compute price_subtotal_signed 
        which is price_subtotal in company currency
        """
        self.price_subtotal = price_total_signed = self.quantity * self.price_unit
        if self.tax_ids:
            taxes = self.tax_ids.compute_all(self.price_unit, self.voucher_id.currency_id, self.quantity, product=self.product_id, partner=self.voucher_id.partner_id)
            self.price_subtotal = taxes['total_excluded']
            price_total_signed = taxes['total_included']
        if self.voucher_id.currency_id and self.voucher_id.currency_id != self.voucher_id.company_id.currency_id:
            price_total_signed = self.voucher_id.currency_id.with_context(date=self.voucher_id._get_currency_rate_date()).compute(price_total_signed, self.voucher_id.company_id.currency_id)
        sign = 1
        self.price_total_signed = price_total_signed * sign


    @api.multi
    @api.constrains('price_unit','quantity')
    def _check_line(self):
        """
        Constraint method that doesn't allow voucher line price and quantity to be equal or less than zero
        
        @return: boolean
        """
        for line in self:
            #if voucher.state not in ['draft','cancel','no_approve' ] and voucher.amount==0.0:
            if line.price_unit < 0.0:
                raise UserError(_("Price in line should be more than zero!"))
            if line.quantity <= 0.0:
                raise UserError(_("Quantity in line should be more than zero!"))


    @api.multi
    def check_voucher_line_account_budget(self):
        """
        Function check if the account_id in line which require budget is has enough budget
        :param self: Voucher line
        @return: Boolean
        """
        line_obj = self.env['crossovered.budget.lines']
        #for line in self.filtered(lambda r: r.account_id.budget_required and r.analytic_account_id and r.analytic_account_id.budget):
        for line in self:
            date = line.voucher_id.date
            analytic_account_id = line.analytic_account_id
            account_id = line.account_id
            budget_line = line_obj.search([
                ('analytic_account_id','=', analytic_account_id.id),
                ('date_from','<=', date),
                ('date_to','>=', date),
                ('general_budget_id.account_id','=',account_id.id),
                ('state','=','validate')], limit=1)
            if budget_line:
                allow_budget_overdraw = budget_line.crossovered_budget_id.allow_budget_overdraw 
                if allow_budget_overdraw or budget_line.residual >= line.price_subtotal: 
                    return True
                else:
                    raise ValidationError(_('The account %s has no enough residual, residual = %s')%(account_id.name,budget_line.residual))

            else :
                raise ValidationError(_('The account %s has no validated budget in voucher date for analytic account %s !')%(account_id.name,analytic_account_id.name))

    

    @api.multi
    @api.constrains('account_analytic_id', 'account_id')
    def _check_analytic_required(self):
        for rec in self:
            if rec.account_id.analytic_required and not rec.account_analytic_id :
                raise ValidationError(_('The %s must have  Analytic Account ')%(rec.account_id.name))

            if rec.account_id.budget_required and not rec.account_analytic_id :
                raise ValidationError(_('The %s is budget required so you must select Analytic Account ')%(rec.account_id.name))

    @api.model
    def create(self,vals):
        """
        Inherited - create method to be sure that account and voucher company
        are the same.

        @return: list creating voucher lines
        """
        vals.update({'budget_confirm_id':False})
        if vals.get('account_id',False) and vals.get('voucher_id',False):
            account_company = self.env['account.account'].browse(vals['account_id']).company_id.id
            voucher_company = self.env['account.voucher'].browse(vals['voucher_id']).company_id.id
            if account_company != voucher_company:
                raise orm.except_orm(_('Entry Error!'), _('The account company is not like the voucher company!'))
        return super(AccountVoucherLine, self).create(vals)


# ---------------------------------------------------------
# Budget Confirmation Inherit
# ---------------------------------------------------------
class AccountBudgetConfirmation(models.Model):
    """ Inherit to overwrite workflow mothods to reflect confirmation state in voucher line  """

    _inherit = "account.budget.confirmation" 

    #v11 link budget confirmation with voucher line to reflect workflow in voucher line
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



class AccountMove(models.Model):
    _inherit = 'account.move'

    voucher_id = fields.Many2one('account.voucher')
    payment_state = fields.Selection([('draft', 'Draft'),('done', 'Payment Done')],default='draft',string='Payment State')

    def post(self):
        """
        override post func to set required constraints to installment voucher
        :return:
        """
        if self.voucher_id and self.voucher_id.pay_now == 'installments':

            if str(fields.datetime.now()) < self.date :
                raise UserError(_("""you can't post this move yet untill move date come %s"""%(self.date)))
            else:

                #change values to currency rate in case user change rates
                self.line_ids.with_context(check_move_validity=False)._onchange_amount_currency()
                super(AccountMove, self).post()
                self.voucher_id.check_installments_voucher_done(self.voucher_id.id)
        else:
            super(AccountMove,self).post()


    def open_payment_view(self):
        """
        open register payment wizard
        :return:
        """
        view = self.env.ref('account.view_account_payment_invoice_form')
        #wiz = self.env['account.payment'].create({'voucher_id': [(4, self.voucher_id.id)]})
        print(">>>>>>>>>>>>>>>>>>>>>>>>>",self.line_ids[0].amount_currency if self.line_ids[0].amount_currency > 0 else self.amount if self.amount > 0 else self.amount * -1)
        return {
            'name': _('Payment'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
        #    'res_id': wiz.id,
            'context': {'account_id':self.voucher_id.account_id.id,
                        'default_partner_id':self.partner_id.id if self.partner_id else None,
                        'default_payment_type':'outbound',
                        'default_amount':self.line_ids[0].amount_currency if self.line_ids[0].amount_currency > 0 else self.amount if self.amount > 0 else self.amount * -1,
                        'voucher_active_id':self.voucher_id.id},
                        'voucher_installment_type':self.voucher_id.installment_type if self.voucher_id.installment_type else False,
        }
         


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

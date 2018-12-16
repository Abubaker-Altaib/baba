# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import models, fields, api , _
from odoo.exceptions import Warning,UserError, ValidationError



class account_payment(models.Model):
    _inherit = 'account.payment'



    hide_account_id = fields.Boolean(default=False)
    readonly_amount = fields.Boolean(default=False)

    # def action_validate_invoice_payment(self):
    #     """ Posts a payment used to pay an invoice. This function only posts the
    #     payment by default but can be overridden to apply specific post or pre-processing.
    #     It is called by the "validate" button of the popup window
    #     triggered on invoice form by the "Register Payment" button.
    #     """
    #     if len(self.voucher_ids) > 0:
    #         if self.amount > self.voucher_ids.residual:
    #             raise UserError(_("You Can't pay with amount more than residual %s")%(self.voucher_ids.residual))


    #         print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>|| ",self.amount,self.voucher_ids.residual)
    #         if self.amount == self.voucher_ids.residual:
    #             self.voucher_ids.payment_complete = True
    #         self.post1()
    #     else:
    #         super(account_payment,self).action_validate_invoice_payment()


    def post_installment(self,voucher_id,pay_residual=False):
        """
        Func Porpose : we no longer need standar payment whenvoucher type is installments so we get
        important code from standar post payment and change created move according to our requirements
        :return:
        """
        #create payment sequence
        if self.partner_type == 'supplier':
            if self.payment_type == 'inbound':
                sequence_code = 'account.payment.supplier.refund'
            if self.payment_type == 'outbound':
                sequence_code = 'account.payment.supplier.invoice'
        #set sequence name for payment
        self.name = self.env['ir.sequence'].with_context(ir_sequence_date=self.payment_date).next_by_code(sequence_code)

        if not self.name and self.payment_type != 'transfer':
            raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))


        #pay all residual payment
        if pay_residual == True:
            if voucher_id.installment_type == 'payable':

                self.post()

            elif voucher_id.installment_type == 'pre_paid_expense':
                lines = [(0, 6, {
                    'name': _('Bank Account'),
                    'account_id': self.journal_id.default_credit_account_id.id,
                    'debit': 0.0,
                    'credit': self.currency_id.compute(round(self.amount, 2), self.company_id.currency_id),
                    # 'partner_id': self.partner_id.id if self.partner_id else None,
                    'currency_id': self.currency_id.id,
                    'amount_currency': round(self.amount, 2) * -1
                })]

                payable_total_amount = 0
                pre_exp_total_amount = 0

                for line in voucher_id.move_ids.filtered(lambda self:self.payment_state == 'draft'):
                    if line.state == 'posted':
                        #we need just amount currency
                        for move_line in line.line_ids:
                            pre_exp_total_amount += move_line.amount_currency if move_line.amount_currency > 0 else 0
                    else:
                        for move_line in line.line_ids:
                            payable_total_amount += move_line.amount_currency if move_line.amount_currency > 0 else 0

                # payable
                if pre_exp_total_amount != 0:
                    lines += [(0, 6, {
                        'name': _('Pre Expense Account'),
                        'account_id': voucher_id.pre_paid_exp_account.id,
                        'debit': self.currency_id.compute(round(pre_exp_total_amount, 2), self.company_id.currency_id),
                        'credit': 0.0,
                        # 'partner_id': self.partner_id.id if self.partner_id else None,
                        # 'analytic_account_id': line.account_analytic_id.id if line.account_analytic_id else None,
                        'currency_id': self.currency_id.id,
                        'amount_currency': round(pre_exp_total_amount, 2)
                    })]
                if payable_total_amount != 0:
                    lines += [(0, 6, {
                        'name': _('Payable Account'),
                        'account_id': voucher_id.account_id.id ,
                        'debit': self.currency_id.compute(round(payable_total_amount, 2),
                                                          self.company_id.currency_id),
                        'credit': 0.0,
                        # 'partner_id': self.partner_id.id if self.partner_id else None,
                        # 'analytic_account_id': line.account_analytic_id.id if line.account_analytic_id else None,
                        'currency_id': self.currency_id.id,
                        'amount_currency': round(payable_total_amount, 2)
                    })]

                move_id = self.env['account.move'].with_context(check_move_validity=False).create({
                    'ref': self.name,
                    'date': self.payment_date,
                    'company_id': self.company_id.id,
                    # 'partner_id': self.partner_id.id if self.partner_id else None,
                    'journal_id': self.journal_id.id,
                    'line_ids': lines,
                    # 'voucher_id': voucher_id.id,
                    'payment_id': self.id
                })
                move_id.post()

            if voucher_id.installment_type == 'middle_payment':
                lines = [(0, 6, {
                    'name': _('Bank Account'),
                    'account_id': self.journal_id.default_credit_account_id.id,
                    'debit': 0.0,
                    'credit': self.currency_id.compute(round(self.amount, 2), self.company_id.currency_id),
                    # 'partner_id': self.partner_id.id if self.partner_id else None,
                    'currency_id': self.currency_id.id,
                    'amount_currency': round(self.amount, 2) * -1
                })]
                # maybe user select an account with analytic account *_* need check or make domain #TODO
                lines += [(0, 6, {
                    'name': _('Middle Account'),
                    'account_id': voucher_id.middle_payment_account.id,
                    'debit': self.currency_id.compute(round(self.amount, 2), self.company_id.currency_id),
                    'credit': 0.0,
                    # 'partner_id': self.partner_id.id if self.partner_id else None,
                    # 'analytic_account_id': line.account_analytic_id.id if line.account_analytic_id else None,
                    'currency_id': self.currency_id.id,
                    'amount_currency': round(self.amount, 2)
                })]

                move_id = self.env['account.move'].with_context(check_move_validity=False).create({
                    'ref': self.name,
                    'date': self.payment_date,
                    'company_id': self.company_id.id,
                    # 'partner_id': self.partner_id.id if self.partner_id else None,
                    'journal_id': self.journal_id.id,
                    'line_ids': lines,
                    # 'voucher_id': voucher_id.id,
                    'payment_id': self.id
                })
                move_id.post()

        elif voucher_id.installment_type == 'payable':
            self.post()

        elif voucher_id.pay_now == 'installments' and voucher_id.installment_type == 'pre_paid_expense':
            lines = [(0, 6, {
                'name': _('Bank Account'),
                'account_id': self.journal_id.default_credit_account_id.id,
                'debit': 0.0,
                'credit': self.currency_id.compute(round(self.amount, 2), self.company_id.currency_id),
                # 'partner_id': self.partner_id.id if self.partner_id else None,
                'currency_id': self.currency_id.id,
                'amount_currency': round(self.amount, 2) * -1
            })]

            move = self.env['account.move'].search([('id', '=', self._context.get('move_active_id', False))])
            #payable
            lines += [(0, 6, {
                    'name': _('Payable Account'),
                    'account_id': voucher_id.account_id.id if move.state == 'posted' else voucher_id.pre_paid_exp_account.id,
                    'debit': self.currency_id.compute(round(self.amount, 2), self.company_id.currency_id),
                    'credit': 0.0,
                    # 'partner_id': self.partner_id.id if self.partner_id else None,
                    # 'analytic_account_id': line.account_analytic_id.id if line.account_analytic_id else None,
                    'currency_id': self.currency_id.id,
                    'amount_currency': round(self.amount, 2)
                })]

            move_id = self.env['account.move'].with_context(check_move_validity=False).create({
                'ref': self.name,
                'date': self.payment_date,
                'company_id': self.company_id.id,
                # 'partner_id': self.partner_id.id if self.partner_id else None,
                'journal_id': self.journal_id.id,
                'line_ids': lines,
                # 'voucher_id': voucher_id.id,
                'payment_id': self.id
            })
            move_id.post()

        elif voucher_id.pay_now == 'installments' and  voucher_id.installment_type == 'middle_payment':
            lines = [(0, 6, {
                'name': _('Bank Account'),
                'account_id': self.journal_id.default_credit_account_id.id,
                'debit': 0.0,
                'credit': self.currency_id.compute(round(self.amount, 2), self.company_id.currency_id),
                #'partner_id': self.partner_id.id if self.partner_id else None,
                'currency_id': self.currency_id.id,
                'amount_currency': round(self.amount, 2) * -1
            })]
            #maybe user select an account with analytic account *_* need check or make domain #TODO
            lines += [(0, 6, {
                'name': _('Middle Account'),
                'account_id': voucher_id.middle_payment_account.id,
                'debit': self.currency_id.compute(round(self.amount, 2), self.company_id.currency_id),
                'credit': 0.0,
                #'partner_id': self.partner_id.id if self.partner_id else None,
                #'analytic_account_id': line.account_analytic_id.id if line.account_analytic_id else None,
                'currency_id': self.currency_id.id,
                'amount_currency': round(self.amount, 2)
            })]

            move_id = self.env['account.move'].with_context(check_move_validity=False).create({
                'ref': self.name,
                'date': self.payment_date,
                'company_id': self.company_id.id,
                #'partner_id': self.partner_id.id if self.partner_id else None,
                'journal_id': self.journal_id.id,
                'line_ids': lines,
                #'voucher_id': voucher_id.id,
                'payment_id':self.id
            })
            move_id.post()
            #for line in move_id.line_ids:

            #    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>||",line.move_id.state,line.move_id.id,line.name)



    def action_validate_invoice_payment(self):
        """
        override function to
        :return:
        """
        #in case user click on move payment button
        if self._context.get('voucher_active_id',False):
            voucher = self.env['account.voucher'].search([('id','=',self._context.get('voucher_active_id',False))])
            move = self.env['account.move'].search([('id','=',self._context.get('move_active_id',False))])
            move_amount =  move.line_ids[0].amount_currency if move.line_ids[0].amount_currency > 0 else move.amount if move.amount > 0 else move.amount * -1
            if self.amount != move_amount:
                raise UserError(_("You Must pay all amount not more or less than %s !!")%(move_amount))

            self.post_installment(voucher)

            #change payment state to done
            move.payment_state = 'done'

            #cheak if all voucher moves state is posted and payment complated
            voucher.check_installments_voucher_done(voucher.id)

        #in case user click on voucher Register payment to pay all voucher moves residual
        elif self._context.get('move_residual',False):
            voucher = self.env['account.voucher'].search([('id','=',self._context.get('voucher_id'))])

            if self.amount != self._context.get('residual_moves_amount',False):
                raise UserError(_("You Must pay all Residual Moves Amount not more or less than %s !!") % (self._context.get('residual_moves_amount',False)))

            #self.post()
            #send True as parameter means pay all residual amount

            pay_all_residual = True # more readable
            self.post_installment(voucher,pay_all_residual)

            for move in self.env['account.move'].search([('voucher_id','=',self._context.get('voucher_id')),('payment_state','=','draft')]):
                move.payment_state = 'done'

            #all amount is paid so no need to Button register payment to show up
            voucher.payment_complete = True

            # cheak if all voucher moves state is posted and payment complated
            voucher.check_installments_voucher_done(voucher.id)



        else :
            super(account_payment,self).action_validate_invoice_payment()


    @api.one
    @api.depends('voucher_ids')
    def _get_has_vouchers(self):
        self.has_vouchers = bool(self.voucher_ids)

    # add this field to solve problem in def _create_payment_entry in case of outstanding payments
    has_vouchers = fields.Boolean(compute="_get_has_vouchers", help="Technical field used for usability purposes")
    voucher_ids = fields.Many2many('account.voucher', 'account_voucher_payment_rel', 'payment_id', 'voucher_id', string="Vouchers", copy=False, readonly=True)
    # Money flows from the journal_id's default_debit_account_id or default_credit_account_id to the destination_account_id
    destination_account_id = fields.Many2one('account.account', compute='_compute_destination_account_id',
                                             readonly=True)
    payment_difference = fields.Monetary(compute='_compute_payment_difference', readonly=True)
    voucher_id = fields.Many2one('account.voucher',string='voucher')


    @api.model
    def default_get(self, fields):

        rec = super(account_payment, self).default_get(fields)
        if not 'voucher_ids' in rec:
            return rec
        #else :
        #    self.voucher_ids = [(4, self._context['active_id'], None)]
        #voucher_defaults = self.resolve_2many_commands('voucher_ids', rec.get('voucher_ids'))
        voucher_defaults = self.env['account.voucher'].search([('id','=',self._context.get('active_id'))])

        if voucher_defaults and len(voucher_defaults) == 1:
            payment_method = voucher_defaults.voucher_type == 'purchase' and \
                             self.env.ref('account.account_payment_method_manual_in') or \
                             self.env.ref('account.account_payment_method_manual_out')

            voucher = voucher_defaults
            rec['communication'] = voucher.number
            rec['currency_id'] = voucher.currency_id.id
            rec['payment_type'] = voucher.voucher_type == 'purchase' and 'outbound' or 'inbound'
            rec['partner_type'] = voucher.voucher_type == 'purchase' and 'supplier' or 'customer'
            rec['partner_id'] = voucher.partner_id.id
            rec['amount'] = voucher.residual
            rec['payment_method_id'] = payment_method.id

        return rec



    #v9: override _compute_destination_account_id in account.payment
    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id', 'voucher_ids')
    def _compute_destination_account_id(self):
        """
        Override _compute_destination_account_id in account.payment to calculate
        destination_account_id field in case if there are voucher_ids
        """
        if not self.voucher_ids:
            return super(account_payment, self)._compute_destination_account_id()
        else:
            return self._compute_voucher_destination_account_id()

    @api.one
    @api.depends('voucher_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_voucher_destination_account_id(self):
        if self.voucher_ids:
            self.destination_account_id = self.voucher_ids[0].account_id.id
        elif self.payment_type == 'transfer':
            if not self.company_id.transfer_account_id.id:
                raise UserError(_('Transfer account not defined on the company.'))
            self.destination_account_id = self.company_id.transfer_account_id.id
        elif self.partner_id:
            if self.partner_type == 'customer':
                self.destination_account_id = self.partner_id.property_account_receivable_id.id
            else:
                self.destination_account_id = self.partner_id.property_account_payable_id.id

    @api.one
    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id', 'voucher_ids')
    def _compute_payment_difference(self):
        """
        Override _compute_payment_difference in account.payment to calculate
        payment_difference field in case if there are voucher_ids
        """
        if len(self.voucher_ids) == 0:
            return super(account_payment, self)._compute_payment_difference()
        else:
            if self.voucher_ids[0].voucher_type in ['purchase']:
                self.payment_difference = self.amount - self._compute_total_voucher_amount()
            else:
                self.payment_difference = self._compute_total_voucher_amount() - self.amount


    @api.model
    def _compute_total_voucher_amount(self):
        """ Compute the sum of the residual of voucher, expressed in the payment currency """
        payment_currency = self.currency_id or self.journal_id.currency_id or self.journal_id.company_id.currency_id or self.env.user.company_id.currency_id

        total = 0
        for voucher in self.voucher_ids:
            if voucher.currency_id == payment_currency:
                total += voucher.residual_signed
            else:
                total += voucher.company_currency_id.with_context(date=self.payment_date).compute(
                    voucher.residual_company_signed, payment_currency)
        return abs(total)


    def _create_payment_entry(self, amount):
        """
        Override _create_payment_entry in account.payment to include voucher_ids
        modify This method by make the condition in  has_vouchers not in has_invoices
        """
        if self.has_vouchers == True:
            return self._create_voucher_payment_entry(amount)
        else:
            return super(account_payment, self)._create_payment_entry(amount)


    def _create_voucher_payment_entry(self, amount):
        """
        Create a journal entry corresponding to a payment, if the payment references voucher(s) they are reconciled.
            Return the journal entry
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        voucher_currency = False
        if self.voucher_ids and all([x.currency_id == self.voucher_ids[0].currency_id for x in self.voucher_ids]):
            # if all the vouchers selected share the same currency, record the paiement in that currency too
            voucher_currency = self.voucher_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id,
                                                          voucher_currency)

        move = self.env['account.move'].create(self._get_move_vals())

        # Write line corresponding to voucher payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.voucher_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml_dict.update({'partner_id': self.voucher_ids.partner_id.id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)

        # Reconcile with the vouchers
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(
                date=self.payment_date).compute_amount_fields(self.payment_difference, self.currency_id,
                                                              self.company_id.currency_id, voucher_currency)
            writeoff_line['name'] = _('Write-Off')
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit']:
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit']:
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo

        #Write counterpart lines
        if not self.currency_id.is_zero(self.amount):
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)

        #validate the payment
        move.post()

        #reconcile the invoice receivable/payable line(s) with the payment
        self.voucher_ids.register_payment(counterpart_aml)

        return move
    
    #TO DO Mathani: check if need it
    @api.multi
    def post1(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:

            if rec.state != 'draft':
                raise UserError(
                    _("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
                sequence_code)

            #rec.state = 'posted'
            rec.post()


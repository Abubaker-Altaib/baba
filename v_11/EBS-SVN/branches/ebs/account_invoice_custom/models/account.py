# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from dateutil.relativedelta import *
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError


class accountMoveLine(models.Model):
    _inherit = 'account.move.line'

    doc_no = fields.Integer(default = 0, string='doc')
    rate = fields.Float(default = 0, string='rate')
    dollar_rate = fields.Float(default = 0, string='dollar rate')

class accountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(selection_add=[('reversed', 'Reversed'),('cancel', 'Cancelled')], string='Status',
      required=True, readonly=True, copy=False, default='draft',
      help='All manually created new journal entries are usually in the status \'Unposted\', '
           'but you can set the option to skip that status on the related journal. '
           'In that case, they will behave as journal entries automatically created by the '
           'system on document validation (invoices, bank statements...) and will be created '
           'in \'Posted\' status.')
    invoice_id = fields.Many2one('account.invoice', string='Invoice')

    @api.multi
    def reverse(self):
        """
        Function change record state to 'reversed'.
        
        @return: write method of object
        """        
        return self.write({'state':'reversed'})

    @api.multi
    def reverse_moves(self, date=None, journal_id=None):
        """
        overwrite to update state of the two move to be reversed
        """
        date = date or fields.Date.today()
        reversed_moves = self.env['account.move']
        for ac_move in self:
            reversed_move = ac_move._reverse_move(date=date,
                                                  journal_id=journal_id)
            reversed_moves |= reversed_move
            #unreconcile all lines reversed
            aml = ac_move.line_ids.filtered(lambda x: x.account_id.reconcile or x.account_id.internal_type == 'liquidity')
            aml.remove_move_reconcile()
            #reconcile together the reconciliable (or the liquidity aml) and their newly created counterpart
            for account in list(set([x.account_id for x in aml])):
                to_rec = aml.filtered(lambda y: y.account_id == account)
                to_rec |= reversed_move.line_ids.filtered(lambda y: y.account_id == account)
                #reconciliation will be full, so speed up the computation by using skip_full_reconcile_check in the context
                to_rec.with_context(skip_full_reconcile_check=True).reconcile()
                to_rec.force_full_reconcile()
        if reversed_moves:
            reversed_moves._post_validate()
            reversed_moves.post()
            reversed_moves.reverse()
            ac_move.reverse()
            return [x.id for x in reversed_moves]
        return []


    # @api.multi
    # def cancel_ref_records(self):
    #     """
    #     Function that when reverse move, it updates the state of invoice, voucher, payment 
    #     which create this move  
    #     """
    #     for rec in self:
    #         if rec.payment_id:
    #             rec.payment_id.

    def action_reverse(self):
        """
        Reverse move and cancel every invoice and voucher connected to this move
        :return:
        """
        #TODO:The following code need ENHANCMENT :BY MUDATHIR
        moves = []
        for line in self.line_ids:
            if line.payment_id:
                line.payment_id.state = 'cancelled'

            if line.payment_id.move_line_ids:
                #reverse even vouchers moves
                for move_line in line.payment_id.move_line_ids:
                    moves.append(move_line.move_id.id)
                for m in self.env['account.move'].search([('id','in',moves)]):
                    m.reverse_moves(m.date, m.journal_id or False)
                    m.state = 'reverse'



            #voucher_id in account_voucher_ebs *_* what da HELL!!!!!!
            if line.payment_id.voucher_id:
                for line_id in line.payment_id.voucher_id.line_ids:
                    if line_id.budget_confirm_id:
                        line_id.budget_confirm_id.unlink()
                line.payment_id.voucher_id.state = 'cancel'
            # voucher_id in account_voucher_ebs *_* what da HELL!!!!!!

            if line.payment_id.invoice_id:
                for line_id in self.invoice_id.invoice_line_ids:
                    if line_id.budget_confirm_id:
                        line_id.budget_confirm_id.unlink()
                line.payment_id.invoice_id.state = 'cancel'

            if line.payment_id.invoice_ids:
                for invoice in line.payment_id.invoice_ids:
                    for line_id in invoice.invoice_line_ids:
                        line_id.budget_confirm_id.unlink()
                    invoice.state = 'cancel'
            break
        #self.state= 'reverse'
        reversed_moves = self.reverse_moves(self.date, self.journal_id or False)
        self.browse(reversed_moves[0]).state = 'reverse'
        self.state= 'reverse'




        for move in self.env['account.move'].search([('invoice_id', '=', self.invoice_id.id or -1)]):
            reversed_moves = move.reverse_moves(move.date, move.journal_id or False)
            self.browse(reversed_moves[0]).state = 'reverse'
            move.state = 'reverse'




    def post(self):
        """
        in case invoice is deffered revenue we must make invoice posted after all deferred moves become posted
        :return:
        """
        if self.invoice_id and self.invoice_id.revenue_type == 'month_revenue':
            if self.invoice_id.month_revenue_date > str(fields.datetime.now()):
                raise ValidationError(
                    _("Date Specified in invoice '%s' not come Yet!!") % (self.invoice_id.month_revenue_date))
            else:
                super(accountMove, self).post()
                self.invoice_id.state = 'posted'
                return


        else:
            super( accountMove,self).post()
            if self.invoice_id and self.invoice_id.revenue_type == 'deferred_revenue':
                is_all_move_invoice_posted =  self.env['account.move'].search([('invoice_id','=',self.invoice_id.id),('state','!=','posted')])
                if len(is_all_move_invoice_posted) == 0:
                    self.invoice_id.state = 'posted'


class accountPayment(models.Model):
    _inherit = 'account.payment'

    is_deferred = fields.Boolean(default = False,string='Is deferred')
    invoice_id = fields.Many2one('account.invoice', string='Invoice')

    journal_bank = fields.Selection(related = "journal_id.type")
    journal_balance = fields.Float(related = "journal_id.journal_balance")

    journal_bank_internal = fields.Selection(related = "destination_journal_id.type")
    journal_balance_internal = fields.Float(related = "destination_journal_id.journal_balance")
    invoice_ids = fields.Many2many('account.invoice',readonly=0, string='Invoices')
    account_id = fields.Many2one('account.account', string="Account")

    @api.multi
    def unlink(self):
        for rec in self:
            if len(rec.mapped('invoice_ids').filtered(lambda line:line.id)) > 0 or len(rec.mapped('invoice_id').filtered(lambda line:line.id)) > 0:
                raise UserError(_("You Can't delete Payment created from invoice"))
            return super(accountPayment, self).unlink()


    def action_validate_invoice_payment(self):
        if self.invoice_ids.revenue_type == 'pay_later':
            if self.amount >  self.invoice_ids.residual :
                raise  UserError(_("You Can't pay with amount more than amount residual "+str(self.invoice_ids.residual)))
            elif self.env['account.payment'].search([('invoice_id','=',self.invoice_ids.id)]).state != 'posted':
                raise UserError(
                    _("You must First make First payment posted  in payments"))
            # elif self.payment_date > fields.datetime.now():
            #     raise
            #     UserError(
            #         _("You can't pay in future date"))
            # elif self.payment_date < self.invoice_ids.date_invoice:
            #     raise
            #     UserError(
            #         _("You can't pay with date less than invoice date"))
            # Revenue Post
            """lines = [(0, 6, {
                'name': _('Bank Account'),
                'account_id': self.journal_id.default_credit_account_id.id,
                'debit': self.amount,
                'credit': 0.0,
                'partner_id': self.invoice_ids.partner_id.id,
                'payment_id': self.id
            })]

            lines += [(0, 6, {
                'name': _('Customer'),
                'account_id': self.account_id and self.account_id.id or self.invoice_ids.partner_id.property_account_receivable_id.id,
                'debit': 0,
                'credit': self.amount,
                'partner_id': self.invoice_ids.partner_id.id,
                'payment_id': self.id
            })]

            move_id = self.env['account.move'].with_context(check_move_validity=False).create({
                'ref': self.name,
                'date': fields.datetime.now(),
                'company_id': self.company_id.id,
                'partner_id': self.invoice_ids.partner_id.id,
                'journal_id': self.journal_id.id,
                'line_ids': lines,
                'invoice_id': self.invoice_ids.id
            })"""""
            #create standard payment
            super(accountPayment, self).action_validate_invoice_payment()
            self.invoice_ids.residual = self.invoice_ids.residual - self.amount
            if self.invoice_ids.residual == 0:
                self.invoice_ids.state = 'paid'

        else:
            super(accountPayment,self).action_validate_invoice_payment()
            if self.invoice_ids and self.invoice_ids.residual == 0:
                self.invoice_ids.state = 'paid'
    @api.multi
    def post(self):
        """
        Overide post function to create multiple moves from payment if invoice defereed
        :return:
        """


        #I changed the self to rec to avoid the problem of conforming more than one payment
        for rec in self :
            if rec.invoice_id.revenue_type == 'direct_revenue':
                account_invoice = rec.invoice_id

                date = datetime.strptime(account_invoice.date_invoice, '%Y-%m-%d')
                # self.installment_ids.unlink()

                lines = [(0, 6, {
                    'name': _('Bank Account'),
                    'account_id': rec.journal_id.default_credit_account_id.id,
                    'debit': rec.invoice_id.company_id.currency_id.compute(account_invoice.amount_total,rec.invoice_id.currency_id),
                    'credit': 0.0,
                    'partner_id': rec.partner_id.id,
                    'payment_id': rec.id,
                    'amount_currency':account_invoice.amount_total,
                    'currency_id':rec.invoice_id.currency_id.id
                })]
                for r in account_invoice.invoice_line_ids:
                    lines += [(0, 6, {
                        'name': _('Service Account'),
                        'account_id': r.account_id.id,
                        'debit':  0.0,
                        'credit':rec.invoice_id.company_id.currency_id.compute(r.price_subtotal,rec.invoice_id.currency_id),
                        'partner_id': rec.partner_id.id,
                        'payment_id': rec.id,
                        'analytic_account_id':r.account_analytic_id.id,
                        'amount_currency': r.price_subtotal * -1 ,
                        'currency_id': rec.invoice_id.currency_id.id
                    })]


                move_id = rec.env['account.move'].with_context(check_move_validity=False).create({
                    'ref': rec.name,
                    'date': fields.datetime.now(),
                    'company_id': rec.company_id.id,
                    'partner_id': rec.partner_id.id,
                    'journal_id': rec.journal_id.id,
                    'line_ids': lines,
                    'invoice_id':account_invoice.id,
                    'period_id':rec.period_id.id
                })

                move_id.post()

                rec.state = 'posted'

            elif rec.is_deferred == True:

                #account_invoice = self.env['account.invoice'].search([('payment_id','=',self.id)])
                account_invoice = rec.invoice_id

                date = datetime.strptime(account_invoice.date_invoice, '%Y-%m-%d')
                # self.installment_ids.unlink()

                lines = [(0, 6, {
                    'name': _('Bank Account'),
                    'account_id': rec.journal_id.default_credit_account_id.id,
                    'debit': account_invoice.amount_total ,
                    'credit': 0.0,
                    'partner_id': rec.partner_id.id,
                    'payment_id': rec.id
                })]

                lines += [(0, 6, {
                        'name': _('Middle Account'),
                        'account_id': account_invoice.middle_account.id,
                        'debit':  0.0,
                        'credit':rec.amount,
                        'partner_id': rec.partner_id.id,
                        'payment_id': rec.id,
                        #'analytic_account_id':line.account_analytic_id.id if line.account_analytic_id.id else False
                    })]

                move_id = rec.env['account.move'].with_context(check_move_validity=False).create({
                    'ref': rec.name,
                    'date': fields.datetime.now(),
                    'company_id': rec.company_id.id,
                    'partner_id': rec.partner_id.id,
                    'journal_id': rec.journal_id.id,
                    'line_ids': lines,
                    'period_id':rec.period_id.id,
                    'invoice_id':account_invoice.id
                })
                move_id.post()




                for x in range(account_invoice.installment_number):
                    new_date = date + relativedelta(months=(x-1)+1)

                    lines = [(0, 6, {
                        'name': _('Middle Account'),
                        'account_id': account_invoice.middle_account.id,
                        'debit':account_invoice.amount_total / account_invoice.installment_number,
                        'credit': 0.0,
                        'partner_id': rec.partner_id.id,
                        'payment_id':rec.id,
                    })]

                    for line in account_invoice.invoice_line_ids:
                        lines += [(0, 6, {
                            'name': _('Service Account'),
                            'account_id': line.account_id.id,
                            'debit': 0.0,
                            'credit': line.price_subtotal / account_invoice.installment_number,
                            'partner_id': rec.partner_id.id,
                            'payment_id': rec.id,
                            'analytic_account_id': line.account_analytic_id.id
                        })]

                    move_id = rec.env['account.move'].with_context(check_move_validity=False).create({
                        'ref': rec.name,
                        'date': new_date ,
                        'company_id': rec.company_id.id,
                        'partner_id': rec.partner_id.id,
                        'journal_id': rec.journal_id.id,
                        'line_ids': lines,
                        'period_id': rec.period_id.id,
                        'invoice_id':account_invoice.id
                    })

                    if str(new_date) <= str(fields.datetime.now()):
                        move_id.post()

                rec.state = 'posted'

            elif rec.invoice_id.revenue_type == 'month_revenue':

                super(accountPayment, rec).post()

                for line in self.move_line_ids:
                    line.date_maturity = rec.invoice_id.date_invoice
                for line in self.move_line_ids:
                    line.move_id.date = rec.invoice_id.date_invoice
                    break


                #raise ValidationError(_("Date Specified in invoice '%s' not come Yet!!")%(self.invoice_id.month_revenue_date))
                lines = [(0, 6, {
                    'name': _('Customer'),
                    'account_id': rec.account_id and rec.account_id.id or rec.partner_id.property_account_receivable_id.id,
                    'debit': rec.amount,
                    'credit': 0.0,
                    'partner_id': rec.partner_id.id,
                    'payment_id': rec.id
                })]

                for line in rec.invoice_id.invoice_line_ids:
                    lines += [(0, 6, {
                        'name': (line.product_id.name),
                        'account_id': line.account_id.id,
                        'debit': 0.0,
                        'credit': line.price_subtotal,
                        'partner_id': rec.partner_id.id,
                        'payment_id': rec.id,
                        'analytic_account_id': line.account_analytic_id.id
                    })]

                move_id = rec.env['account.move'].with_context(check_move_validity=False).create({
                    'ref': rec.name,
                    'date': rec.invoice_id.month_revenue_date,
                    'company_id': rec.company_id.id,
                    'partner_id': rec.partner_id.id,
                    'journal_id': rec.journal_id.id,
                    'line_ids': lines,
                    'period_id': rec.period_id.id,
                    'invoice_id': rec.invoice_id.id
                })

                #rec.invoice_id.state = 'posted'
            elif rec.invoice_id.revenue_type == 'pay_later':
                #super(accountPayment, rec).post()
                #raise ValidationError(_("Date Specified in invoice '%s' not come Yet!!")%(self.invoice_id.month_revenue_date))
                lines = [(0, 6, {
                    'name': _('Customer'),
                    'account_id': rec.account_id and rec.account_id.id or rec.partner_id.property_account_receivable_id.id,
                    'debit': rec.amount,
                    'credit': 0.0,
                    'partner_id': rec.partner_id.id,
                    'payment_id': rec.id
                })]

                for line in rec.invoice_id.invoice_line_ids:
                    lines += [(0, 6, {
                        'name': (line.product_id.name),
                        'account_id': line.account_id.id,
                        'debit': 0.0,
                        'credit': line.price_subtotal,
                        'partner_id': rec.partner_id.id,
                        'payment_id': rec.id,
                        'analytic_account_id': line.account_analytic_id.id
                    })]

                move_id = rec.env['account.move'].with_context(check_move_validity=False).create({
                    'ref': rec.name,
                    'date': fields.datetime.now(),
                    'company_id': rec.company_id.id,
                    'partner_id': rec.partner_id.id,
                    'journal_id': rec.journal_id.id,
                    'line_ids': lines,
                    'period_id': rec.period_id.id,
                    'invoice_id': rec.invoice_id.id
                })
                move_id.post()
                self.state = 'posted'

                # #Revenue Post
                # lines = [(0, 6, {
                #     'name': _('Bank Account'),
                #     'account_id': rec.journal_id.default_credit_account_id.id,
                #     'debit': rec.amount,
                #     'credit': 0.0,
                #     'partner_id': rec.partner_id.id,
                #     'payment_id': rec.id
                # })]
                #
                # lines += [(0, 6, {
                #     'name': _('Customer'),
                #     'account_id': rec.partner_id.property_account_receivable_id.id,
                #     'debit': 0,
                #     'credit':rec.amount,
                #     'partner_id': rec.partner_id.id,
                #     'payment_id': rec.id
                # })]
                #
                # move_id = rec.env['account.move'].with_context(check_move_validity=False).create({
                #     'ref': rec.name,
                #     'date': fields.datetime.now(),
                #     'company_id': rec.company_id.id,
                #     'partner_id': rec.partner_id.id,
                #     'journal_id': rec.journal_id.id,
                #     'line_ids': lines,
                #     'invoice_id': rec.invoice_id.id
                # })






            else:

                super(accountPayment, rec).post()
                # Check it later : By Mudathir
                if rec.payment_type == 'outbound' and rec.account_id:
                    ids = [line.id for line in rec.mapped('move_line_ids')]
                    move_change = rec.move_line_ids.search(
                        [('id', 'in', ids), ('account_id', '=', rec.partner_id.property_account_payable_id.id)])
                    move_change.move_id.state = 'draft'
                    move_change.account_id = rec.account_id
                    move_change.move_id.state = 'posted'

                elif rec.payment_type == 'inbound' and rec.account_id:
                    ids  = [line.id for line in rec.mapped('move_line_ids')]
                    move_change = rec.move_line_ids.search([('id','in',ids),('account_id','=',rec.partner_id.property_account_receivable_id.id)])
                    move_change.move_id.state = 'draft'
                    move_change.account_id = rec.account_id
                    move_change.move_id.state = 'posted'


# for security
class account_payment_method(models.Model):
    _inherit = 'account.payment.method'


class accountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    budget_confirm_id = fields.Many2one('account.budget.confirmation', 'Confirmation', select=2, ondelete="restrict")
    state = fields.Selection(
        [('complete', 'Waiting for Approve'), ('approve', 'Approved'), ('no_approve', 'Budget Not Approved'),
         ('cancel', 'Canceled')], 'State', required=False, readonly=True, default='complete')
    account_budget_required = fields.Boolean(related='account_id.budget_required')


class accountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_order = fields.Boolean(default=False, string='Sale Order')
    note = fields.Text(string='Note')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('revenue_confirm','Waiting for Head of Revenue Unit'),
        ('revenue_review','Waiting for Head of Financial Section\\Financial Manager'),
        ('open', 'Open'),
        ('wating_payments',' Waiting Payment'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
        ('no_approve','Waiting For Budget Approve'),
        ('no_approve2','Budget Not Approved'),
        ('approved', 'Waiting Head of Expenditure Unit'),
        ('approved2', 'Waiting Head of Financial Section'),
        ('approved3', 'Waiting Internal Auditor '),
        ('auditor_approved', 'Waiting Financial Manager '),
        ('payer', 'Payer') ,
        ('posted', 'Posted')
    ],string='Status', readonly=True, size=32, track_visibility='onchange',
        help=' * The \'Draft\' status is used when a user is enreq_darft Draft Request, req_complete Complete, req_budget_no_approve, req_confirm, req_cancelcoding a new and unconfirmed Voucher. \
                                    \n* The \'Waiting Head of Expenditure Unit\' status to make Ratification List Approve  \
                                    \n* The \'Waiting Head of Financial Section\' status to make Head of Financial Section Approve  \
                                    \n* The \'Waiting Internal Auditor\' status to make Internal Auditor to Approve or return it to Head of Financial Section  \
                                    \n* The \'Waiting Financial Manager\' status to make payment for Financial Manager   \
                                    \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                                    \n* The \'Cancelled\' status is used when user cancel voucher.')

    revenue_type = fields.Selection([
        ('direct_revenue','Direct Revenue'),
        ('deferred_revenue','Deferred Revenue'),
        ('month_revenue','Specific Month Revenue'),
        ('pay_later', 'Pay Later')],default='direct_revenue',required=1)
    installment_number = fields.Integer(required=0)
    middle_account = fields.Many2one('account.account')
    month_revenue_date = fields.Date()
    move_ids = fields.One2many('account.move','invoice_id',readonly=1, string='Moves')
    journal_id_invoice = fields.Many2one('account.journal', string='Journal')
    journal_bank = fields.Selection(related="journal_id_invoice.type")
    journal_balance = fields.Float(related="journal_id_invoice.journal_balance")
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=True,default=1,
                                        oldname="payment_method",
                                        help="Manual: Get paid by cash, check or any other method outside of Odoo.\n" \
                                             "Electronic: Get paid automatically through a payment acquirer by requesting a transaction on a card saved by the customer when buying or subscribing online (payment token).\n" \
                                             "Check: Pay bill by check and print it from Odoo.\n" \
                                             "Batch Deposit: Encase several customer checks at once by generating a batch deposit to submit to your bank. When encoding the bank statement in Odoo, you are suggested to reconcile the transaction with the batch deposit.To enable batch deposit,module account_batch_deposit must be installed.\n" \
                                             "SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit to your bank. To enable sepa credit transfer, module account_sepa must be installed ")
    payment_method_code = fields.Char(related='payment_method_id.code',
                                      help="Technical field used to adapt the interface to the payment type selected.",
                                      readonly=True)

    @api.multi
    def invoice_validate(self):
        """
        copy function from account budget
        @return: call super function
        """
        for invoice in self:
            date = invoice.date or invoice.date_invoice
            check=False
            for line in invoice.invoice_line_ids:
                if line.account_budget_required == True:
                    if line.account_analytic_id.budget:
                        budget_line_ids=self.env['crossovered.budget.lines'].search([('analytic_account_id','=',line.account_analytic_id.id),('date_from','<=',date),('date_to','>=',date),('crossovered_budget_id.state','=','validate')])
                        if not budget_line_ids:
                            raise UserError(_("This analytic account (%s) is Budget Required ,And it is not included in any budget *or* customer invoice date not in range of budget_line date")%line.account_analytic_id.name)
                        for budget_line in budget_line_ids:
                            #if line.account_id.id not in budget_line.general_budget_id.account_ids.ids:
                            if line.account_id.id != budget_line.general_budget_id.account_id.id:
                                continue
                            check=True

                            """if not :
                                raise UserError(_("In This date (%s) analytic account (%s) whice is Budget Required ,Does not have budget")% (date,line.account_analytic_id.name))
                                """
                        if not check:
                            raise UserError(_("This account (%s) is not included in any Budgetary Positions ,With analytic account (%s) whice is Budget Required *or* customer invoice date not in range of budget_line date")% (line.account_id.name,line.account_analytic_id.name))
        return super(accountInvoice, self).invoice_validate()


    def validate_input(self):
        self.action_invoice_open()

        if len(self.mapped('invoice_line_ids').filtered(lambda line:line.account_budget_required == True)) > 0:
            self.create_budget_confirmation_invoice()
            self.change_state()
        else:
            self.change_state()
            self.state = 'approved'

    def check_budget(self):
        """
        Function runs check_budget function in budget confirmation if state in confirm or unvalid
        :return:
        """
        if self.invoice_line_ids:
            for line in self.invoice_line_ids:
                if line.budget_confirm_id.state in ('waiting_valid','complete','unvalid') and line.account_budget_required == True:
                    line.budget_confirm_id.check_budget_invoice()
            self.change_state()
        else:
            raise ValidationError(_("You must enter at least one line in Bill Information!!!"))

    def change_state(self):
        """
        if all lines approve then vocher state will be budget_approved
        if all lines approve except one then state 'no_approve2'
        if all lines not approve state  'no_approve'
        :return:
        """

        # after creation of budget confirmation we change state of voucher depend on it
        # for line in self.line_ids:
        #    line.state = 'complete'
        #    break

        if self.invoice_line_ids:
            line_states = [line.state for line in self.invoice_line_ids]
            if 'approve' not in line_states:
                self.state = 'no_approve'
            elif 'approve' in line_states and (
                                'complete' in line_states or 'no_approve' in line_states or 'cancel' in line_states):
                self.state = 'no_approve2'
            else:
                self.state = 'approved'
                #for line in self.invoice_line_ids:
                #    #print(">>>>>>>>>>>>>>>>>>>>>>>>",line.budget_confirm_id.unlink())
                #    #line.budget_confirm_id.unlink()
            for line in self.mapped('invoice_line_ids').filtered(lambda line:line.account_budget_required == False):
                line.state = 'approve'


    @api.multi
    def create_budget_confirmation_invoice(self):
        """
        This Method for creating Budget Confirmation for each invoice Line with analytic account

        @return: boolean True it any confirmation created, or return False
        """
        confirmation_pool = self.env['account.budget.confirmation']
        currency_pool = self.env['res.currency']
        new_confirm_id = False
        flag = False
        for invoice in self:
            # v9: if invoice.invoice_type  in ('purchase','sale'):  super(account_invoice,self).compute_tax(cr, uid, [invoice.id], context=context)
            if invoice.journal_id.type == 'purchase':
                for invoice_line in invoice.invoice_line_ids:
                    if invoice_line.account_budget_required == True:
                        # v9: TEST ME if invoice_line.account_id and invoice_line.account_id.user_type_id.analytic_wk:
                        if invoice_line.account_id:
                            total_amount = invoice.company_id.currency_id.with_context(date=invoice.date).compute(
                                invoice_line.price_subtotal, invoice.currency_id)
                            amount = invoice.company_id.currency_id.with_context(date=invoice.date).compute(
                                invoice_line.price_subtotal,invoice.currency_id)
                            val = {
                                'reference': invoice.number,
                                'partner_id': invoice.partner_id.id,
                                'account_id': invoice_line.account_id.id,
                                'date': invoice.date_invoice,
                                'analytic_account_id': invoice_line.account_analytic_id and invoice_line.account_analytic_id.id,
                                'amount': total_amount or amount,
                                'residual_amount': total_amount or amount,
                                #'type': self._context.get('type', 'other'),
                                'type': 'other',
                                'note': invoice_line.name or '/',

                            }

                            if invoice_line.invoice_line_tax_ids:
                                val_amount = val.get('amount', 0)
                                net_amount = 0
                                total = 0
                                tax_amount = 0
                                tax_info = invoice_line.invoice_line_tax_ids.compute_all(invoice_line.price_unit, invoice.currency_id,
                                                                            invoice_line.quantity, invoice_line.product_id,
                                                                            invoice.partner_id)
                                total += tax_info.get('total_included', 0.0)
                                tax_amount += sum([t.get('amount', 0.0) for t in tax_info.get('taxes', False)])
                                net_amount = tax_amount + val_amount
                                val.update({'amount': net_amount or amount, })
                            new_confirm_id = False

                            if invoice_line.budget_confirm_id:
                                flag = True
                                # confirmation_pool.write([invoice_line.budget_confirm_id.id], val)
                                # new_confirm_id = invoice_line.budget_confirm_id.id
                            elif not invoice_line.budget_confirm_id:
                                flag = True
                                confirm = confirmation_pool.create(val)
                                new_confirm_id = int(confirm)
                                invoice_line.write({'budget_confirm_id': new_confirm_id})
                            # v11 condition is worng ???
                            # if new_confirm_id and not invoice.company_id.auto_budget:#v9: test me
                            if new_confirm_id and invoice.company_id.auto_budget:
                                confirmation_pool.browse(new_confirm_id).action_cancel_draft()
                                confirmation_pool.browse(new_confirm_id).budget_complete()
                                confirmation_pool.browse(new_confirm_id).check_budget_invoice()

        return flag

    def unlink_line_confirmation(self):
        if self.invoice_line_ids:
            for line in self.invoice_line_ids:
                if line.budget_confirm_id:
                    line.budget_confirm_id.budget_cancel()
                    confirm_id = line.budget_confirm_id.id
                    line.budget_confirm_id = False
                    self.env['account.budget.confirmation'].search([('id','=',confirm_id)]).unlink()
                line.state = 'complete'
        self.state = 'draft'
    def action_invoice_cancel(self):
        if self.revenue_type == 'deferred_revenue':
            main_payment = self.env['account.payment'].search([('invoice_id','=',self.id)])
            if main_payment.state == 'posted':
                sum_unposted = 0

                #for move_line in self.env['account.move.line'].search([('move_id.state','=','cancel'),('payment_id','=',main_payment.id)]):
                for move_line in self.env['account.move.line'].search(
                        [('move_id.state', '=', 'draft'), ('payment_id', '=', main_payment.id)]):
                    sum_unposted += move_line.debit
                    #move_line.move_id.state = 'draft'
                    move_line.move_id.state = 'cancel'

                bank_move_id = False
                debit_acc =False
                credit_acc =False
                line_f =False
                line_s = False
                line_all = []
                #*_* i think next code need optimization
                for move_line in self.env['account.move.line'].search([('payment_id','=',main_payment.id)],order="id"):
                    bank_move_id = move_line.move_id
                    for line in self.env['account.move.line'].search([('move_id','=',bank_move_id.id)]):
                        if line.debit !=0:
                            debit_acc = line.account_id.id
                            line_f = (0, 6, {
                                'name': line.name + _(' Reconcile'),
                                'account_id': line.account_id.id,
                                'debit': 0.0,
                                'credit': sum_unposted,
                                'partner_id': line.move_id.partner_id.id,
                                'payment_id': line.payment_id.id
                            })

                        else:
                            credit_acc = line.account_id.id
                            line_s = (0, 6, {
                                'name': line.name+_(' Reconcile'),
                                'account_id': line.account_id.id,
                                'debit': sum_unposted,
                                'credit': 0.0,
                                'partner_id': line.move_id.partner_id.id,
                                'payment_id': line.payment_id.id
                            })

                    line_all.append(line_f)
                    line_all.append(line_s)


                    move_id = self.env['account.move'].with_context(check_move_validity=False).create({
                        'ref': line.move_id.name + _(' Reconcile'),
                        'date': fields.datetime.now(),
                        'company_id': line.move_id.company_id.id,
                        'partner_id': line.move_id.partner_id.id,
                        'journal_id': line.move_id.journal_id.id,
                        'line_ids': line_all,
                        'state': 'posted'
                    })

                    break
                self.state = 'posted'
        elif self.revenue_type == 'month_revenue':
            main_payment = self.env['account.payment'].search([('invoice_id', '=', self.id)])
            if main_payment and main_payment.state == 'draft':
                main_payment.state = 'cancelled'
            #else:
            # SHow Error Message




    def action_invoice_open_custom(self):
        """
        run when revenue type = deferred_revenue' to create payment
        :return:
        """


        if self.revenue_type == 'deferred_revenue':
            payment = self.env['account.payment'].create({
                'amount': self.amount_total,
                'partner_id': self.partner_id.id or None,
                'partner_type': 'customer',
                'journal_id': self.journal_id.id,
                'payment_date': self.date_invoice,
                'payment_type': 'inbound',
                'payment_method_id': 1,
                'is_deferred':1,
                'invoice_id':self.id,
                'payment_method_id':self.payment_method_id.id,
                'period_id': self.period_id.id,
                'currency_id': self.currency_id.id
                #'voucher_id': self.id,

            })

            self.state = 'wating_payments'

        elif self.revenue_type == 'direct_revenue':

            payment = self.env['account.payment'].create({
                'amount': self.amount_total,
                'partner_id': self.partner_id.id or None,
                'partner_type': 'customer',
                'journal_id': self.journal_id_invoice.id,
                'payment_date': self.date_invoice,
                'payment_type': 'inbound',
                'payment_method_id': 1, #TODO : must be dynamic or make field required=False in python
                'invoice_id': self.id,
                #'state':'posted',
                'period_id':self.period_id.id,
                'payment_method_id': self.payment_method_id.id,
                'currency_id':self.currency_id.id
                # 'voucher_id': self.id,

            })
            payment.period_id = self.period_id.id


            payment.post()
            self.state = 'posted'

        elif self.revenue_type in ('month_revenue','pay_later'):
            payment = self.env['account.payment'].create({
                'amount': self.amount_total,
                'partner_id': self.partner_id.id or None,
                'partner_type': 'customer',
                'journal_id': self.journal_id.id,
                'payment_date': self.date_invoice,
                'payment_type': 'inbound',
                'payment_method_id': 1,
                'invoice_id': self.id,
                'payment_method_id': self.payment_method_id.id
                # 'voucher_id': self.id,

            })

            self.state = 'wating_payments'

            if self.revenue_type == 'pay_later':
                self.residual = self.amount_total





    @api.one
    @api.constrains('installment_number')
    def validate_installment_number(self):
        if self.revenue_type == 'deferred_revenue' and self.installment_number <= 0:
            raise ValidationError(_("Installment Number must be greater than ZERO!!"))

    @api.one
    @api.constrains('month_revenue_date')
    def validate_month_revenue_date(self):
        if self.revenue_type == 'month_revenue':
            if  self.month_revenue_date <= str(fields.datetime.now()):
                raise ValidationError(_("Month Revenue Date must be Greater than today"))




    def approve_expen_unit(self):
        self.state = 'approved2'
    def cancel_expen_unit(self):
        self.unlink_line_confirmation()
        self.state = 'draft'

    def approved3(self):
        self.state = 'approved3'
    def cancel_approved3(self):
        self.state = 'approved'

    def auditor_approved(self):
        self.state = 'auditor_approved'
    def cancel_auditor_approved(self):
        self.state = 'approved2'


    def financial_m_approved(self):
        self.state = 'open'
    def cancel_financial_m_approved(self):
        self.state = 'approved2'


    def set_draft(self):
        self.state = 'draft'

    # Customer Invoices Workflow Functions

    def button_revenue_confirm(self):
        if self.invoice_line_ids:
            self.write({'state':'revenue_confirm'})
        else :
            raise ValidationError(_("You must enter at least one invoice line "))

    def button_revenue_review(self):
        self.write({'state':'revenue_review'})

    def button_revenue_draft(self):
        self.write({'state':'draft'})

    def button_revenue_draft2(self):
        self.write({'state':'revenue_confirm'})


class AccountBudgetConfirmationInvoice(models.Model):
    """ Inherit to overwrite workflow mothods to reflect confirmation state in voucher line  """

    _inherit = "account.budget.confirmation"

    #v11 link budget confirmation with voucher line to reflect workflow in voucher line
    invoice_line_ids = fields.One2many('account.invoice.line','budget_confirm_id', string='Invoice Lines')

    @api.multi
    def check_budget_invoice(self):
        """
        This method check whether the budget line residual allow to validate this confirmation or not
        @return: boolean True if budget line residual more that confirm amount, or False
        """
        budget_line = []

        line_obj = self.env['crossovered.budget.lines']
        for confirmation in self:
            position = self.env['account.budget.post']._get_budget_position(confirmation.account_id.id)

            if not position:
                # self.budget_valid()
                raise UserError(_("Confirmation Has no Budget Position!"))
            else:
                budget_line = line_obj.search([('analytic_account_id', '=', confirmation.analytic_account_id.id),
                                               ('date_from', '<=', confirmation.date),
                                               ('date_to', '>=', confirmation.date),
                                               ('general_budget_id', '=', position.id),
                                               ('crossovered_budget_id.state', '=', 'validate')
                                               ])
            if budget_line:
                # FIXME: allow_budget_overdraw
                allow_budget_overdraw = budget_line.crossovered_budget_id.allow_budget_overdraw
                if not allow_budget_overdraw and confirmation.residual_amount > budget_line.residual:
                    self.budget_unvalid_invoice()
                elif confirmation.residual_amount <= budget_line.residual:
                    #    self.budget_valid()
                    if self.state == 'waiting_valid':
                        self.budget_valid_invoice()
                    else:
                        self.state = 'waiting_valid'
                else:
                    #    self.budget_valid()
                    if self.state == 'waiting_valid':
                        self.budget_valid_invoice()
                    else:
                        self.state = 'waiting_valid'
            elif confirmation.analytic_account_id.budget:
                # v9: test me
                raise ValidationError(_('This account has no budget!'))
        return True


    @api.multi
    def budget_valid_invoice(self):
        """
        overwrite to change vocher line state to approve
        """
        for conf in self:
            for line in conf.invoice_line_ids:
                line.write({'state': 'approve'})
        self.write({'state': 'valid', 'validating_user_id': self.env.user.id})
        # return super(AccountBudgetConfirmation, self).budget_valid()

    @api.multi
    def budget_unvalid_invoice(self):
        """
        overwrite to change vocher line state to no_approve
        """
        for conf in self:
            for line in conf.invoice_line_ids:
                line.write({'state': 'no_approve'})
        self.write({'state': 'unvalid'})
        # return super(AccountBudgetConfirmation, self).budget_unvalid()

    @api.multi
    def budget_cancel_invoice(self):
        """
        overwrite to change vocher line state to cancel
        """
        self.write({'state': 'cancel'})
        if self.line_id:
            raise ValidationError(_('This confirmation already have posted moves'))

        for conf in self:
            for line in conf.voucher_line_ids:
                line.write({'state': 'cancel'})

class res_currency(models.Model):
    """docstring for res_currency"""
    _inherit = "res.currency.rate"

    @api.constrains('rate')
    def check_rate(self):
        if self.rate < 0:
            raise UserError(_("rate must be positive"))

# for security

class resCompany(models.Model):
    _inherit = "res.company"

class resCurrency(models.Model):
    _inherit = "res.currency"

class accountAccount(models.Model):
    _inherit = "account.account"

class accountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

class hr_department(models.Model):
    _inherit = 'hr.department'

class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

class AccountTax(models.Model):
    _inherit = 'account.tax'

class AccountAccountType(models.Model):

    _inherit =  "account.account.type"

#must be inherited
#class account_approve(models.Model):
#    _name= 'account.approve'

class Payment_Token(models.Model):
    _inherit = 'payment.token'

class Payment_Tcon(models.Model):
    _inherit = 'payment.icon'

class Payment_Acquirer(models.Model):
    _inherit = 'payment.acquirer'

# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from dateutil.relativedelta import *
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError

class accountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(selection_add=[('cancel', 'Cancelled')])
    invoice_id = fields.Many2one('account.invoice')

class accountPayment(models.Model):
    _inherit = 'account.payment'

    is_deferred = fields.Boolean(default=False)
    invoice_id = fields.Many2one('account.invoice')



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

                date = datetime.strptime(account_invoice.date_due, '%Y-%m-%d')
                # self.installment_ids.unlink()

                lines = [(0, 6, {
                    'name': _('Bank Account'),
                    'account_id': rec.journal_id.default_credit_account_id.id,
                    'debit': account_invoice.amount_total,
                    'credit': 0.0,
                    'partner_id': rec.partner_id.id,
                    'payment_id': rec.id
                })]
                for r in account_invoice.invoice_line_ids:
                    lines += [(0, 6, {
                        'name': _('Service Account'),
                        'account_id': r.account_id.id,
                        'debit':  0.0,
                        'credit':r.price_subtotal,
                        'partner_id': rec.partner_id.id,
                        'payment_id': rec.id
                    })]

                move_id = rec.env['account.move'].with_context(check_move_validity=False).create({
                    'ref': rec.name,
                    'date': fields.datetime.now(),
                    'company_id': rec.company_id.id,
                    'partner_id': rec.partner_id.id,
                    'journal_id': rec.journal_id.id,
                    'line_ids': lines,
                    'state': 'posted',
                    'invoice_id':account_invoice.id
                })

                rec.state = 'posted'

            elif rec.is_deferred == True:

                #account_invoice = self.env['account.invoice'].search([('payment_id','=',self.id)])
                account_invoice = rec.invoice_id

                date = datetime.strptime(account_invoice.date_due, '%Y-%m-%d')
                # self.installment_ids.unlink()

                lines = [(0, 6, {
                    'name': _('Bank Account'),
                    'account_id': rec.journal_id.default_credit_account_id.id,
                    'debit': 0.0,
                    'credit': account_invoice.amount_total ,
                    'partner_id': rec.partner_id.id,
                    'payment_id': rec.id
                })]
                lines += [(0, 6, {
                    'name': _('Middle Account'),
                    'account_id': account_invoice.middle_account.id,
                    'debit': account_invoice.amount_total ,
                    'credit': 0.0,
                    'partner_id': rec.partner_id.id,
                    'payment_id': rec.id
                })]

                move_id = rec.env['account.move'].with_context(check_move_validity=False).create({
                    'ref': rec.name,
                    'date': fields.datetime.now(),
                    'company_id': rec.company_id.id,
                    'partner_id': rec.partner_id.id,
                    'journal_id': rec.journal_id.id,
                    'line_ids': lines,
                    'state':'posted',
                    'invoice_id':account_invoice.id
                })




                for x in range(account_invoice.installment_number):
                    new_date = date + relativedelta(months=x+1)

                    lines = [(0, 6, {
                        'name': _('Middle Account'),
                        'account_id': account_invoice.middle_account.id,
                        'debit':0.0,
                        'credit': account_invoice.amount_total / account_invoice.installment_number,
                        'partner_id': rec.partner_id.id,
                        'payment_id':rec.id
                    })]

                    lines += [(0, 6, {
                        'name': _('Service Account'),
                        'account_id': account_invoice.invoice_line_ids.account_id.id,
                        'debit': account_invoice.amount_total / account_invoice.installment_number,
                        'credit': 0.0,
                        'partner_id': rec.partner_id.id,
                        'payment_id': rec.id
                    })]

                    move_id = rec.env['account.move'].with_context(check_move_validity=False).create({
                        'ref': rec.name,
                        'date': new_date ,
                        'company_id': rec.company_id.id,
                        'partner_id': rec.partner_id.id,
                        'journal_id': rec.journal_id.id,
                        'line_ids': lines,
                        'state': str(new_date) <= str(fields.datetime.now()) and 'posted' or 'draft' ,
                        'invoice_id':account_invoice.id
                    })
                rec.state = 'posted'

            elif rec.invoice_id.revenue_type == 'month_revenue':
                if rec.invoice_id.month_revenue_date > str(fields.datetime.now()):
                    raise ValidationError(_("Date Specified in invoice '%s' not come Yet!!")%(self.invoice_id.month_revenue_date))
                else:
                    super(accountPayment,rec).post()
                    rec.invoice_id.state = 'posted'

            else:
                super(accountPayment,rec).post()



class accountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    budget_confirm_id = fields.Many2one('account.budget.confirmation', 'Confirmation', select=2, ondelete="restrict")
    state = fields.Selection(
        [('complete', 'Waiting for Approve'), ('approve', 'Approved'), ('no_approve', 'Budget Not Approved'),
         ('cancel', 'Canceled')], 'State', required=True, readonly=True, default='complete')

class accountInvoice(models.Model):
    _inherit = 'account.invoice'


    state = fields.Selection([
        ('draft', 'Draft'),
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
        ('month_revenue','Specific Month Revenue')],default='direct_revenue',required=1)
    installment_number = fields.Integer(required=1)
    middle_account = fields.Many2one('account.account')
    month_revenue_date = fields.Date()
    move_ids = fields.One2many('account.move','invoice_id',readonly=1)
    journal_id_invoice = fields.Many2one('account.journal', string='Journal')


    def validate_input(self):
        self.create_budget_confirmation_invoice()
        self.change_state()

        #self.state = 'approved'

    def check_budget(self):
        """
        Function runs check_budget function in budget confirmation if state in confirm or unvalid
        :return:
        """
        if self.invoice_line_ids:
            for line in self.invoice_line_ids:
                if line.budget_confirm_id.state in ('waiting_valid','complete','unvalid'):
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
                    # v9: TEST ME if invoice_line.account_id and invoice_line.account_id.user_type_id.analytic_wk:
                    if invoice_line.account_id:
                        total_amount = invoice.company_id.currency_id.with_context(date=invoice.date).compute(
                            invoice_line.price_subtotal, invoice.currency_id)
                        amount = invoice.company_id.currency_id.with_context(date=invoice.date).compute(
                            invoice_line.price_unit, invoice.currency_id)
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
                'payment_date': fields.datetime.now(),
                'payment_type': 'outbound',
                'payment_method_id': 1,
                'is_deferred':1,
                'invoice_id':self.id
                #'voucher_id': self.id,

            })

            self.state = 'wating_payments'

        elif self.revenue_type == 'direct_revenue':
            payment = self.env['account.payment'].create({
                'amount': self.amount_total,
                'partner_id': self.partner_id.id or None,
                'partner_type': 'customer',
                'journal_id': self.journal_id_invoice.id,
                'payment_date': fields.datetime.now(),
                'payment_type': 'outbound',
                'payment_method_id': 1,
                'invoice_id': self.id,
                'state':'posted',
                'period_id':self.period_id.id
                # 'voucher_id': self.id,

            })
            payment.period_id = self.period_id.id
            payment.post()
            self.state = 'posted'

        elif self.revenue_type == 'month_revenue':
            payment = self.env['account.payment'].create({
                'amount': self.amount_total,
                'partner_id': self.partner_id.id or None,
                'partner_type': 'customer',
                'journal_id': self.journal_id.id,
                'payment_date': fields.datetime.now(),
                'payment_type': 'outbound',
                'payment_method_id': 1,
                'invoice_id': self.id
                # 'voucher_id': self.id,

            })

            self.state = 'wating_payments'

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


class AccountBudgetConfirmationInvoice(models.Model):
    """ Inherit to overwrite workflow mothods to reflect confirmation state in voucher line  """

    _inherit = "account.budget.confirmation"

    #v11 link budget confirmation with voucher line to reflect workflow in voucher line
    invoice_line_ids = fields.One2many('account.invoice.line','budget_confirm_id','Invoice Lines')

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


        

# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import netsvc
from odoo.exceptions import Warning,UserError, ValidationError
from odoo import api, fields, models, _
from num2words import num2words


class account_approve(models.Model):
    _name= 'account.approve'

    name= fields.Char()
    employee_ids= fields.Many2many("hr.employee", "account_approve_rel_hr_employee", "account_id", "employee_id", required= True)
    min_amount= fields.Float()
    max_amount= fields.Float()
    company_id = fields.Many2one('res.company')


class company(models.Model):
    _inherit = 'res.company'

    account_approve_ids = fields.One2many('account.approve','company_id')


class AccountSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string="Company", required=True,
                                 default=lambda self: self.env.user.company_id)

    account_approve_ids = fields.One2many(related="company_id.account_approve_ids")




class AccountVoucher(models.Model):

    _inherit = 'account.voucher'

    company_id = fields.Many2one('res.company', 'Company',
        required=True, store=True,readonly=True, states={'draft': [('readonly', False)]},
        related='journal_id.company_id', default=lambda self: self._get_company())

    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('proforma', 'Pro-forma'),
        ('complete', 'Completed'),
        ('no_approve', 'Waiting For Budget Appove'),
        ('no_approve2', 'Budget Not Appoved'),
        ('budget_approved', 'Waiting for approve (Ratification List)'),
        ('approved', 'Waiting Head of Expenditure Unit'),
        ('approved2', 'Waiting Head of Financial Section'),
        ('approved3', 'Waiting Internal Auditor '),
        ('auditor_approved', 'Waiting Financial Manager '),
        ('posted', 'Waiting For Payment Complete'),
        ('done','Done')
    ], string='Status', readonly=True, size=32, track_visibility='onchange',
        help=' * The \'Draft\' status is used when a user is enreq_darft Draft Request, req_complete Complete, req_budget_no_approve, req_confirm, req_cancelcoding a new and unconfirmed Voucher. \
                                \n* The \'Pro-forma\' when voucher is in Pro-forma status,voucher does not have an voucher number. \
                                \n* The \'Waiting For Budget Appove\' when all budget confirmations related to this voucher didn\'t approve yet. \
                                \n* The \'Budget Not Appoved\' when at least one of budget confirmations related to this voucher didn\'t approve . \
                                \n* The \'Waiting for approve (Ratification List)\' status to make Ratification List Approve  \
                                \n* The \'Waiting Head of Expenditure Unit\' status to make Ratification List Approve  \
                                \n* The \'Waiting Head of Financial Section\' status to make Head of Financial Section Approve  \
                                \n* The \'Waiting Internal Auditor\' status to make Internal Auditor to Approve or return it to Head of Financial Section  \
                                \n* The \'Waiting Financial Manager\' status to make payment for Financial Manager   \
                                \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                                \n* The \'Cancelled\' status is used when user cancel voucher.')


    department_id =fields.Many2one('hr.department', 'Department')

    user_id=fields.Many2one('res.users', 'User',default=lambda self: self.env.user)

    payment_id = fields.Many2one('account.payment', readonly=1, string='Payment Link')
    payment_ids = fields.One2many('account.payment', 'voucher_id', readonly=1)
    amount_text = fields.Char(compute="_amount_to_text")
    payment_type= fields.Selection([('transfer','transfer'),('direct_payment','direct payment')])
    payment_purpose= fields.Char()
    move_ids= fields.One2many('account.move','voucher_id',string='Journal Entry')
    retf_approve = fields.Boolean(compute="_approve_retf")

    @api.one
    @api.depends('state')
    def _approve_retf(self):
        self.retf_approve = False
        if self.state == 'budget_approved':
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
            if employee:
                for line in self.env.user.company_id.account_approve_ids:
                    emp_list = [emp.id for emp in line.employee_ids]

                    if employee.id in emp_list:
                        if self.amount >= line.min_amount and self.amount <= line.max_amount:
                            self.retf_approve = True
                    emp_list = []



    @api.one
    @api.depends('line_ids.price_unit')
    def _amount_to_text(self):
        """
        to Write Total Amount as Text
        :return: string
        """
        self.amount_text = num2words( self.amount , lang = self._context.get('lang','ar')[0:2])




    @api.multi
    def proforma_voucher(self):
        # we comment next line beacause we want to create payment instead of journal
        # self.action_move_line_create()
        # new code

        bool = 1
        if self.payment_type == 'direct_payment':
            bool = 0
        payment = self.env['account.payment'].create({
            'amount': self.amount,
            'partner_id': self.partner_id.id or None,
            'partner_type': 'supplier',
            'journal_id': self.journal_id.id,
            'payment_date': fields.datetime.now(),
            'payment_type': 'outbound',
            'payment_method_id': 1,
            'from_purchase_receipts_f': bool,
            'voucher_id': self.id,

        })

        self.payment_id = payment.id
        if self.payment_type == 'transfer':
            self.payment_id.from_purchase_receipts_f = True

        self.state = 'posted'

    @api.model
    def default_get(self, fields):
        res = super(AccountVoucher, self).default_get(fields)
        user = self.env['res.users'].search([('id','=',self._uid)]).name
        emp = self.env['hr.employee'].search([('name', '=', user)])
        res.update({'department_id': emp.department_id.id})
        return res

    def check_budget(self):
        """
        Function runs check_budget function in budget confirmation if state in confirm or unvalid
        :return:
        """
        if self.line_ids:
            for line in self.line_ids:
                if line.budget_confirm_id.state in ('waiting_valid','complete','unvalid'):
                    line.budget_confirm_id.check_budget()
            self.change_state()
        else:
            raise ValidationError(_("You must enter at least one line in Bill Information!!!"))

    def cancel(self):
        """
        Function to cancel all budgets confirmation in lines
        :return:
        """
        if self.line_ids:
            for line in self.line_ids:
                if line.budget_confirm_id.state in ('complete','unvalid'):
                    line.budget_confirm_id.budget_cancel()
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

        if self.line_ids:
            line_states = [line.state for line in self.line_ids]
            if 'approve' not in line_states:
                self.state = 'no_approve'
            elif 'approve' in line_states and (
                                'complete' in line_states or 'no_approve' in line_states or 'cancel' in line_states):
                self.state = 'no_approve2'
            else:
                self.state = 'budget_approved'




   
    

    def confirm(self):
        #By Mudathir: for not to run create_budget_confirmation more than once
        #Must ask E.Mathani First to check if function must run every time when user click on confirm or not
        #How user can edit data if not approved , *_* , Run confirm again to check and change state or create another button to check
        #I Prefer first choice



        if self.line_ids:
            if self.state == 'draft':
                self.create_budget_confirmation()
            self.change_state()
        else:
            raise ValidationError(_("You must enter at least one line in Bill Information!!!"))

        if not self.number:
            name = self.journal_id.sequence_id.with_context(ir_sequence_date=self.date).next_by_id()
            self.number = name

    def unlink_line_confirmation(self):
        if self.line_ids:
            for line in self.line_ids:
                if line.budget_confirm_id:
                    line.budget_confirm_id.budget_cancel()
                    confirm_id = line.budget_confirm_id.id
                    line.budget_confirm_id = False
                    self.env['account.budget.confirmation'].search([('id','=',confirm_id)]).unlink()

    @api.multi
    def action_cancel_draft(self):
        super(AccountVoucher, self).action_cancel_draft()
        self.unlink_line_confirmation()


    def no_approve_draft(self):
        """
        Draft Buttom to change state to Draft
        :return: state
        """
        self.unlink_line_confirmation()
        self.state = 'draft'


    def no_approve2_draft(self):
        """
        Draft Buttom to change state to Draft
        :return: state
        """
        self.unlink_line_confirmation()
        self.state = 'draft'

    def approved_draft(self):
        """
        Draft Buttom to change state to Draft
        :return: state
        """
        self.unlink_line_confirmation()
        self.state = 'draft'


    def not_approve_cancel(self):
        """
        Cancel Button to change state based on current state
        :return: state
        """
        if self.state in ('no_approve','no_approve2','budget_approved'):
            self.state = 'cancel'
        elif self.state == 'approved2':
            self.state = 'approved'
        elif self.state == 'approved3':
            self.state = 'approved2'

    def not_approve2_cancel(self):

       self.state = 'cancel'

    def budget_approved_cancel(self):
        self.state = 'cancel'


    def not_approve2_back(self):
        self.state = 'approved'


    def not_approve3_back(self):
        self.state = 'approved2'



    def approved(self):
        """
        Change workflow state to approved
        :return: state
        """
        self.check_budget()
        self.state = 'approved'

    def approved2(self):
        """
        Change workflow state to approved2
        :return: state
        """
        self.state = 'approved2'

    def approved3(self):
        """
        Change workflow state to approved3
        :return: state
        """
        self.state = 'approved3'

    def auditor_approved(self):
        """
        Change workflow state auditor_approved
        :return: state
        """
        self.state = 'auditor_approved'


         


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

class AccountMove(models.Model):

    _inherit = 'account.move'

    voucher_id = fields.Many2one('account.voucher',string='Voucher')
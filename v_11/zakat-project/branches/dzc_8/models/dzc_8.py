# -*- coding: utf-8 -*-

import re
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, _


class dzc_8Channel(models.Model):
    _name = 'zakat.dzc8'
    _inherit = ['mail.thread']

    # @api.multi
    # @api.onchange('transport_company')
    # def company_destination(self):
    #     """
    #     Return Destination ids that match
    #     destination in transport company
    #     :return: lsit of ids
    #     """
    #     distination = []
    #     if self.transport_company:
    #         for state in self.transport_company.state_fees_ids:
    #             if state.distination_id.id not in distination:
    #                 distination.append(state.distination_id.id)
    #         return {'domain': {
    #             'distination_id': [('id', 'in', distination)],
    #         }}
    #     if not self.transport_company:
    #         return {'domain': {
    #             'distination_id': [('id', '=', False)],
    #         }}

    partner_id = fields.Many2one('res.partner', string="Iiban Alsabil", track_visibility='onchange')
    name = fields.Char(related="partner_id.name", string="Name")
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, ondelete='restrict')
    company_id = fields.Many2one("res.company", default=lambda self: self.env.user.company_id, string="Company",
                                 ondelete='cascade')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    code = fields.Char(string="Reference Number")
    claim = fields.Boolean(string="Claim Taken", default=False)
    date = fields.Date(string="Date", default=datetime.today())
    national_number = fields.Char(related="partner_id.national_number", string="National Number",
                                  track_visibility='onchange')
    phone = fields.Char(related="partner_id.phone", string="Phone Number", track_visibility='onchange')
    birth_date = fields.Date(related="partner_id.birth_date", string="Birth Date")
    social_status = fields.Selection([('married', 'Married'), ('single', 'Single'), ('widowed', 'Widowed'),
                                      ('abandoned', 'Abandoned')], string='Social Status')
    state_id = fields.Many2one('zakat.state', related="partner_id.zakat_state", string='State')
    local_state_id = fields.Many2one('zakat.local.state', related="partner_id.local_state_id", string='Local State')
    admin_unit = fields.Many2one('zakat.admin.unit', related="partner_id.admin_unit", string='Admin Unit')
    job = fields.Char(string="Job", related="partner_id.job")
    income_amount = fields.Monetary(string='Income Amount', currency_field='currency_id')
    reasons_arrival = fields.Char(string='Reasons for arrival')
    health_status = fields.Selection([('good', 'Good'), ('average', 'Average'), ('bad', 'Bad')], string="Health Status")
    come_from = fields.Selection([('hospital', 'Hospital'),
                                  ('university', 'University'),
                                  ('khalawi', 'Khalawi'),
                                  ('pension_procedures', 'Pension Procedures'),
                                  ('theft', 'Cases of Theft'),
                                  ('sanatoriums', 'Guest of Sanatoriums'),
                                  ('inmates', 'Prison Inmates'),
                                  ('other', 'Other/specific')])
    other = fields.Char(string="Others")
    transport_type = fields.Selection([('bus', 'Bus'), ('train', 'Train'), ('plane', 'Plane')])
    recommend = fields.Text(string="Recommendation")
    committee_decision = fields.Text(string="Committee Decision")
    manager_decision = fields.Text(string="Channel Director Decision")
    Transformer = fields.Char(string='Transfer To')
    apology_reason = fields.Char(string="Apology Reason")
    approve_type = fields.Selection(
        [('nathria', 'Nathria'),
         ('tickets', 'Traveling Tickets'),
         ('drugs', 'Drugs, Treatments And Tests')],
        string='Approve Type', track_visibility='onchange')
    approve_amount = fields.Monetary(string='Approved Amount', currency_field='currency_id')
    approve_date = fields.Date(string='Approve Date')
    state = fields.Selection([('draft', 'Draft'),
                              ('verify', 'Verified'),
                              ('approve', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Canceled')], string="Status", default='draft', track_visibility='onchange')
    attendant_id = fields.One2many('zakat.attendant', 'dzc_8_id', string='attendant name')
    date_of_arrival = fields.Date(string="Date of arrival")
    transport_company = fields.Many2one('dzc8.transport.company', string="Transport Company", ondelete="restrict")
    distination_id = fields.Many2one('dzc8.transport.state.fees', string="destination", ondelete="restrict")
    payment_id = fields.Many2one('dzc8.payment')
    note = fields.Text("Note")
    # Required Document Based on com_from
    # Hospital
    medical_report = fields.Boolean(string="Medical Report")
    hi_copy = fields.Boolean(string="A copy of the health insurance or social researcher study")
    initial_bill = fields.Boolean(string="Initial Bill")
    clinic_letter = fields.Boolean(string="Clinic letter")
    release_letter = fields.Boolean(string="Release Letter")
    prove = fields.Boolean(string="Prove it is from the states")
    khalwa_letter = fields.Boolean(string="Letter From Khalwa")
    identification = fields.Boolean(string="Copy of Identification")
    insurance = fields.Boolean(string="Health Insurance Card")
    police = fields.Boolean(string="A Police Report")
    documents = fields.Boolean(string="Copy of supporting documents")
    voucher_id = fields.Many2one('account.voucher')
    address_id = fields.Many2one('addresses','Address')
    @api.constrains('approve_amount')
    def _check_fees(self):
        if self.approve_type != 'tickets':
            if self.approve_amount <= 0.0:
                raise exceptions.ValidationError(_('Approve Amount Cannot Be Zero or Less.'))

    @api.constrains('date')
    def current_date(self):
        """
        Check If Date less than the current date and raise exception
        :raise: exception
        """
        today = datetime.strftime(datetime.today(), "%Y-%m-%d")
        if self.date < today or self.date > today:
            raise exceptions.ValidationError(_("Order Date Cannot be Before or After Today Date"))

    @api.multi
    def copy(self, default=None):
        """
        Prevent duplicate
        :raise: exceptions
        """
        raise exceptions.ValidationError(_("Record Could not Be Duplicated"))

    @api.multi
    def unlink(self):
        """
        Prevent unlink record if it state not in draft
        :return:
        """
        for record in self:
            if record.state != 'draft':
                raise exceptions.ValidationError(_("This Record Could not Be Removed it's not in draft state"))
            else:
                return super(dzc_8Channel, self).unlink()

    @api.multi
    def set_draft(self):
        """
        Change state to draft
        :return:
        """
        self.write({'state': 'draft'})

    @api.multi
    def verify_order(self):
        """
        Change state to Approve
        :return:
        """
        self.write({'state': 'verify'})

    @api.multi
    def approve_order(self):
        """
        TODO: check the description
        check approval type and change state to right state
        :return:
        """
        self.write({'state': 'approve'})

    @api.multi
    def done_order(self):
        """
        Change state to done
        :return:
        """
        if self.approve_type == 'tickets':
            self.write({'state': 'done', 'claim': True})

        if self.approve_type in ['nathria', 'drugs']:
            line = []
            if not self.company_id.property_ibanalsabil_account_id:
                raise exceptions.ValidationError(
                    _("Kindly Specify an Acount For Iban Alsabil in General Settings"))
            if not self.company_id.ibanalsabil_journal:
                raise exceptions.ValidationError(
                    _("Kindly Specify an Journal For Iban Alsabil in General Settings"))
            if not self.company_id.property_ibanalsabil_analytic_account_id:
                raise exceptions.ValidationError(
                    _("Kindly Specify an Analytic Acount For Iban Alsabil in General Settings"))

            zakat_account_id = self.company_id.property_ibanalsabil_account_id.id
            zakat_journal_id = self.company_id.ibanalsabil_journal.id
            analytic_account_id = self.company_id.property_ibanalsabil_analytic_account_id.id

            line += [(0, 6, {
                'name': _('Iban Alsabil Support'),
                'account_id': zakat_account_id,
                'account_analytic_id': analytic_account_id,
                'quantity': 1,
                'price_unit': self.approve_amount,
            })]

            voucher_id = self.env['account.voucher'].create(
                {
                    'name': _('Pay For') + ' ' + self.partner_id.name,
                    'journal_id': zakat_journal_id,
                    'pay_now': 'pay_later',
                    'reference': _('Ibn Alsabil Payment  Nathria'),
                    'voucher_type': 'purchase',
                    'company_id': self.env.user.company_id.id,
                    'line_ids': line,

                })
            self.voucher_id = voucher_id.id
            self.write({'state': 'done', 'claim': True})



    @api.multi
    def cancel_order(self):
        """
        TODO: check the description
        change state to canceled state
        :return:
        """
        self.write({'state': 'cancel'})

    @api.model
    def get_seq_to_view(self):
        """
        Get sequence in code filed in form view
        :return:
        """
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        """
        get the first, second, third and forth name in one place
        :param vals: fields values from view
        :return: dict
        """
        # set new sequence number in code for every new record
        vals['code'] = self.env['ir.sequence'].get(self._name) or '/'
        return super(dzc_8Channel, self).create(vals)

    @api.constrains('phone', 'national_number')
    def checks(self):
        """
        Desc:Check format Phones and ID Numbers
        :return:
        """
        # Regex pattern to check all chars are integers
        pattern = re.compile(r'^[0]\d{9,9}$')
        if self.phone != False:
            if not pattern.search(self.phone):
                raise exceptions.ValidationError(_('Phone 1 must be exactly 10 Numbers and Start with ZERO 0 .'))
        if self.national_number != False:
            if 11 < len(self.national_number) or 11 > len(self.national_number):
                raise exceptions.ValidationError(_('ID Number must be at least 11 Numbers.'))

    @api.constrains('attendant_id')
    def _check_member(self):
        count = 0
        print(self.attendant_id)
        if self.attendant_id:
            for record in self.attendant_id:
                count += 1
            if count > 9:
                raise exceptions.ValidationError(_("The Maximum attendant is 10"))

    @api.constrains('birth_date')
    def check_date(self):
        """
        To check date fields
        :return: raise exceptions
        """
        birth_date = datetime.strptime(self.birth_date, '%Y-%m-%d')
        now = datetime.now()
        # if self.date_of_arrival < self.date:
        #     raise exceptions.ValidationError(_("Date Of Arrivals Must Be With In The Current Date"))
        if birth_date.year >= now.year:
            raise exceptions.ValidationError(_('Birth Date Must Be Less Than Current Date'))


class Attendant(models.Model):
    _name = 'zakat.attendant'

    name = fields.Char(string='Name', required=True)
    # age = fields.Integer(string='Age')
    # relation = fields.Selection(
    #     [('father', 'Father'), ('mother', 'Mother'), ('son', 'Son'), ('brother', 'Brother/sister')],
    #     string="Relative Relation", required=True)
    dzc_8_id = fields.Many2one('zakat.dzc8')


class IbnAlsabilPayment(models.Model):
    _name = 'zakat.dzc8.payment'

    code = fields.Char(string="Refrance Number")
    name = fields.Char(string="Name")
    transport_company = fields.Many2one('dzc8.transport.company', string='Transport Company')
    order_date = fields.Date(string='Order Date')
    request = fields.Many2many('zakat.dzc8')
    state = fields.Selection([('draft', 'Draft'),
                              ('approve', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Canceled')], string="Status", default="draft")
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, ondelete='restrict')
    company_id = fields.Many2one("res.company", default=lambda self: self.env.user.company_id, string="Company",
                                 ondelete='cascade')
    company_currency_id = fields.Many2one('res.currency', string="Company Currency",
                                          default=lambda self: self.env.user.company_id.currency_id,
                                          help='Utility field to express amount currency')

    voucher_id = fields.Many2one('account.voucher')
    zakat_support = fields.Monetary('Support Amount', currency_field='company_currency_id', compute="get_zakat_support", store=True)

    @api.multi
    def copy(self, default=None):
        """
        Prevent duplicate
        :raise: exceptions
        """
        raise exceptions.ValidationError(_("Record Could not Be Duplicated"))

    @api.multi
    def unlink(self):
        """
        Prevent unlink record if it state not in draft
        :return:
        """
        for record in self:
            if record.state != 'draft':
                raise exceptions.ValidationError(_("This Record Could not Be Removed it's not in draft state"))
            else:
                return super(IbnAlsabilPayment, self).unlink()

    @api.depends('request')
    def get_zakat_support(self):
        """
        To Get The Total Cost Of Zakat and Financial Support
        :return:
        """
        amount = 0
        for order in self.request:
            if self._context.get('transport'):
                transport_fees = self.env['dzc8.transport.state.fees'].search([('id', '=', order.distination_id.id),
                                                                               ('transport_company_id', '=',
                                                                                self._context.get('transport'))])
                amount += transport_fees.transport_fees
            elif self.transport_company:
                transport_fees = self.env['dzc8.transport.state.fees'].search([('id', '=', order.distination_id.id),
                                                                               ('transport_company_id', '=',
                                                                                self.transport_company.id)])
                amount += transport_fees.transport_fees

        self.zakat_support = amount

    @api.model
    def get_seq_to_view(self):
        """
        Get sequence in code filed in form view
        :return:
        """
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        """
        get the first, second, third and forth name in one place
        :param vals: fields values from view
        :return: dict
        """
        # set new sequence number in code for every new record
        vals['code'] = self.env['ir.sequence'].get(self._name) or '/'
        vals['name'] = vals['code']
        return super(IbnAlsabilPayment, self).create(vals)

    @api.multi
    def set_draft(self):
        """
        Set State To Draft
        :return:
        """
        self.write({'state': 'draft'})

    @api.multi
    def approve_action(self):
        """
        Set State To Approve
        :return:
        """
        self.write({'state': 'approve'})

    @api.multi
    def done_action(self):
        """
        TODO: After Change state to done create a voucher
        :return: change state and create voucher
        """
        line = []
        zakat_account_id = self.transport_company.property_zakat_account_id.id
        zakat_journal_id = self.transport_company.zakat_journal.id
        analytic_account_id = self.transport_company.property_analytic_account_id.id

        line += [(0, 6, {
            'name': _('payment for Transport Company With name:') + ' ' + self.transport_company.name,
            'account_id': zakat_account_id,
            'account_analytic_id': analytic_account_id,
            'quantity': 1,
            'price_unit': self.zakat_support,
        })]

        voucher_id = self.env['account.voucher'].create(
            {
                'name': _('Pay For') + ' ' + self.transport_company.name,
                'journal_id': zakat_journal_id,
                'pay_now': 'pay_later',
                'reference': _('Ibn Alsabil Payment'),
                'voucher_type': 'purchase',
                'company_id': self.env.user.company_id.id,
                'line_ids': line,

            })
        self.voucher_id = voucher_id.id
        self.write({'state': 'done'})
        for order in self.request:
            order.write({'state': 'done', 'claim': True})


    @api.multi
    def cancel_action(self):
        """
        change state to cancel
        :return:
        """
        self.write({'state': 'cancel'})



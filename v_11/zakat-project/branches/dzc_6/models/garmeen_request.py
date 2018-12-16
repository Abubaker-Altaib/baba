# -*- coding: utf-8 -*-
# Copyright 2018, AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, exceptions, _
import re
from odoo.exceptions import ValidationError, AccessError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class dzc6GarmeenRequest(models.Model):
    _name = 'dzc_6.garm.request'

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, readonly=True,
                              ondelete='restrict')
    name = fields.Char(string="Reference", readonly=True)
    order_date = fields.Date(string="Date", default=datetime.today())
    faqeer_id = fields.Many2one('zakat.aplication.form', string="Garm")
    national_number = fields.Char(related="faqeer_id.national_number", store=True, string="National Number")
    garm_state_id = fields.Many2one(string='Garm State', related='faqeer_id.state_id', store=True)
    garm_local_state_id = fields.Many2one(string='Garm Local State', related='faqeer_id.local_state_id', store=True)
    phone = fields.Char(string="Phone Number", related='faqeer_id.phone', store=True, )
    admin_unit_id = fields.Many2one(string='Administrative Unit', related='faqeer_id.admin_unit_id', store=True, )
    village = fields.Char(string='Village', related='faqeer_id.village', store=True, )

    state_id = fields.Many2one('zakat.state', string='State')
    local_state_id = fields.Many2one('zakat.local.state', string='Local State')

    type = fields.Many2one('dzc_6.gorm.types', string="Type")
    type_transfere = fields.Boolean(related="type.t_to_state", store=True)

    is_legal = fields.Boolean(string='Legal')
    loan_date = fields.Date(string='Loan Date')
    pay_date = fields.Date(string='Pay Date')
    total_amount = fields.Float(string="Total Amount")
    final_total_amount = fields.Float(compute="final_total_compute", string="Final Total Amount")

    resident_certificate = fields.Boolean(string='Resident Certificate')
    igrar_document = fields.Boolean(string='Igrar Document')
    court_copy_decision = fields.Boolean(string='Court Copy Decision')

    commitee_date = fields.Date(string='Commitee Date')
    partner_ids = fields.One2many('partner.garm', 'request_id', string="Partner")

    searcher = fields.Text(string="Researcher")
    address_id = fields.Many2one('addresses','Address')
    commitee_decision = fields.Selection(
        [('approve', 'Approve'), ('apology', 'Apoplogy'), ('forward_to_state', 'Forward to State')])
    state_commitee_decision = fields.Selection(
        [('approve', 'Approve'), ('apology', 'Apoplogy')])
    state_commitee = fields.Text(string="State Commitee")
    # pay_to = fields.Selection([( 'creditors' , 'Creditors') , ('other', 'Other' )] , default="other")
    # pay_partner_id = fields.Many2one('res.partner' , string="Partner")
    committee = fields.Text(string="Commitee")

    almasarf = fields.Text(string="Almasarf")

    loan_type = fields.Selection([('rent', 'Rent'), ('treatment', 'Treatment'), ('nafaqa', 'Nafaqa'),
                                  ('iasha', 'Iasha'), ('guarantee', 'Guarantee'), ('commercial', 'Commercial'),
                                  ('agricultural', 'Agricultural'), ('deeia', 'Deeia')])

    has_assets = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Has Assets That replace loan?")

    court_name = fields.Char(string="Court Name")

    final_judgment_date = fields.Date(string="Final judgment Date")

    follower_name = fields.Char(string='Procedure Follower Name')
    follower_national_number = fields.Char(string='Follower National Number')
    follower_phone = fields.Char(string='Follower Phone')

    relation = fields.Many2one('garm.relation', string="Relation")

    state = fields.Selection([('draft', 'Draft'),
                              ('approve1', 'Committee Local State'), ('approve2', 'Committe State'),
                              ('complete', 'Complete'), ('done', 'Done'), ('cancel', 'Cancel')], string="Status",
                             default="draft")

 
    @api.multi
    def approve1_action(self):
        if self.is_legal != True:
            raise ValidationError(_('Sorry! This Loan is not legal'))

        if self.faqeer_id.case_study != True:
            raise ValidationError(_('Case study of this Garm is not done'))
        if self.faqeer_id.case_type != 'garm':
            raise ValidationError(_('Case study type of this beneficiary is not Garm'))
        if not self.partner_ids:
            raise ValidationError(_('Sorry! You cannot confirm request that has not creditors'))

        self.write({'state': 'approve1'})

    @api.multi
    def approve2_action(self):
        if self.is_legal != True:
            raise ValidationError(_('Sorry! This Loan is not legal'))

        if self.faqeer_id.case_study != True:
            raise ValidationError(_('Case study of this Garm is not done'))
        if self.faqeer_id.case_type != 'garm':
            raise ValidationError(_('Case study type of this beneficiary is not Garm'))
        if not self.partner_ids:
            raise ValidationError(_('Sorry! You cannot confirm request that has not creditors'))

        amount = self.env['dzc_6.gorm.types'].search([('name', '=', self.type.name)])
        
        if self.commitee_decision == 'forward_to_state':
            self.write({'state': 'approve2'})

        if self.commitee_decision == 'apology':
            self.write({'state': 'cancel'})
        
        if self.final_total_amount > amount.amount and self.commitee_decision != 'forward_to_state':
            raise ValidationError(_('You cannot Approve this order because Final Total amount is greater than amount of this type'))


        if self.commitee_decision == 'approve' and self.final_total_amount < amount.amount:
            plans = self.env['dzc_6.gorm.order.line'].search(
                ['&', ('type_id.id', '=', self.type.id), ('plan_id.state', '=', 'done'), '&',
                 ('plan_id.duration_from', '<=', self.order_date), ('plan_id.duration_to', '>=', self.order_date), '&',
                 ('plan_id.state_id.id', '=', self.state_id.id),
                 ('plan_id.local_state_id.id', '=', self.local_state_id.id)])
            for rec in plans:
                rec.no_of_orders += self.final_total_amount
                rec.executing_actual += 1
                if rec.planned > 0.0:
                    pers = (rec.executing_actual / 100)
                    rec.percentage = (pers / rec.planned)
            self.write({'state': 'done'})

    @api.multi
    def complete_action(self):
        if self.state_commitee_decision == 'apology':
            self.write({'state': 'cancel'})

        if self.state_commitee_decision == 'approve':
            self.write({'state': 'complete'})

    @api.multi
    def done_action(self):
        plans = self.env['dzc_6.gorm.order.line'].search(
            ['&', ('type_id.id', '=', self.type.id), ('plan_id.state', '=', 'done'), '&',
             ('plan_id.duration_from', '<=', self.order_date), ('plan_id.duration_to', '>=', self.order_date), '&',
             ('plan_id.state_id.id', '=', self.state_id.id),
             ('plan_id.local_state_id.id', '=', self.local_state_id.id)])
        for rec in plans:
            rec.no_of_orders += self.final_total_amount
            rec.executing_actual += 1
            if rec.planned > 0.0:
                pers = (rec.executing_actual / 100)
                rec.percentage = (pers / rec.planned)
        self.write({'state': 'done'})

    @api.multi
    def cancel_action(self):
        self.write({'state': 'cancel'})

    @api.multi
    def set_to_draft_action(self):
        self.write({'state': 'draft'})

    @api.multi
    def unlink(self):
        for record in self:
            if record.state not in ('draft'):
                raise UserError(_('Sorry! You cannot delete request not in Draft state.'))
        return models.Model.unlink(self)

    @api.constrains('total_amount')
    def total_amount_check(self):
        if self.total_amount <= 0.0:
            raise ValidationError(_('Total Amount Cannot be zero or negative'))

    @api.one
    @api.depends('partner_ids.remain_amount')
    def final_total_compute(self):
        for rec in self.partner_ids:
            self.final_total_amount += rec.remain_amount

   
    @api.constrains('follower_name')
    def check_Fname(self):
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.follower_name.replace(" ", "")):
            raise ValidationError(_('Follower name  must be Literal'))
        if self.follower_name and (len(self.follower_name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("Follower name must not be spaces"))
        if self.follower_name and (len(self.follower_name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("Follower name must not be spaces"))

    @api.constrains('follower_national_number', 'follower_phone')
    def checks(self):
        """
        Desc:Check format Phones and ID Numbers
        :return:
        """
        # Regex pattern to check all chars are integers
        pattern = re.compile(r'^[0]\d{9,9}$')
        if self.follower_phone != False:
            if not pattern.search(self.follower_phone):
                raise exceptions.ValidationError(_('Follower Phone must be exactly 10 Numbers and Start with ZERO 0 .'))
        if self.follower_national_number != False:
            if not re.match("^[0-9]*$", self.follower_national_number.replace(" ", "")):
                raise ValidationError(_('Follower National Number Field must be number'))
            if self.follower_national_number.replace(" ", "") != self.follower_national_number:
                raise ValidationError(_('Follower National Number Field must be number'))
            if 11 < len(self.follower_national_number) or 11 > len(self.follower_national_number):
                raise exceptions.ValidationError(_('Follower National Number must be at least 11 Numbers.'))

    @api.constrains('loan_date', 'pay_date')
    def loan_pay_check(self):
        if self.pay_date < self.loan_date:
            raise ValidationError(_('Pay Date must be after Loan date'))

    # @api.constrains('resident_certificate' , 'igrar_document' ,'court_copy_decision')
    # def garm_documents_check(self):
    # 	if not self.resident_certificate or not self.igrar_document or not self.court_copy_decision:
    # 		raise ValidationError(_('All Documents are required'))

    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('dzc6.garmeen.request.sequence') or '/'

        return super(dzc6GarmeenRequest, self).create(vals)


class PartnerGarm(models.Model):
    _name = 'partner.garm'

    partner_id = fields.Many2one('res.partner')
    p_name = fields.Char(related="partner_id.name")
    amount = fields.Float(string=" Amount")
    giveup_amount = fields.Float(string="Giveup Amount")
    remain_amount = fields.Float(compute="remain_compute", string="Remain Amount", store=True)
    request_id = fields.Many2one('dzc_6.garm.request')

    @api.one
    @api.depends('amount', 'giveup_amount')
    def remain_compute(self):
        for rec in self:
            rec.remain_amount = rec.amount - rec.giveup_amount

    @api.constrains('amount', 'giveup_amount')
    def amount_check(self):
        for rec in self:
            if rec.amount <= 0.0:
                raise ValidationError(_('Amount Cannot be zero or negative'))
            if rec.giveup_amount > rec.amount:
                raise ValidationError(_('Giveup amount cannot be greater than amount'))


class GarmRelation(models.Model):
    _name = 'garm.relation'

    name = fields.Char(string="Relation Name")

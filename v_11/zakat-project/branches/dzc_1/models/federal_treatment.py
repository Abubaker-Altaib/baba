# -*- coding: utf-8 -*-
import re
import calendar
import time
import hmac
import json
import hashlib
from datetime import datetime, timedelta, date
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.addons.zakat_base.models import API_integration


class FederalTreatmentRequest(models.Model):
    _name = 'zakat.federaltreatment.request'
    _order = 'create_date desc'

    code = fields.Char(string="Reference Number", copy=False)
    # date = fields.Date(string="Date", default=datetime.today(), copy=False)
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, ondelete='restrict')
    company_id = fields.Many2one("res.company", default=lambda self: self.env.user.company_id, string="Company",
                                 ondelete='cascade')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    name = fields.Char(related="partner_id.name", string="Patient Name", copy=False)
    partner_id = fields.Many2one('res.partner', string="Patient", ondelete="restrict")
    treatment_id = fields.Many2one('zkate.federaltreatment', string="Treatment Order By")
    type = fields.Selection([('it', 'Internal Treatment'),
                             ('at', 'Abroad Treatment'),
                             ('drugs', 'Drugs, Treatments And Tests')],
                            string="Type")
    birth_date = fields.Date(related="partner_id.birth_date", string="Birth Date")
    age = fields.Integer(string="Age", compute="_patient_age", store=True)
    gender = fields.Selection([("male", "Male"), ("female", "Female")], related="partner_id.gender", string="Gender")
    phone = fields.Char(related="partner_id.phone", string="Phone Number", track_visibility='onchange')
    national_number = fields.Char(related="partner_id.national_number", string="National Number",
                                  track_visibility='onchange')

    state_id = fields.Many2one('zakat.state', ondelete="restrict", related="partner_id.zakat_state", string='State')
    local_state_id = fields.Many2one('zakat.local.state', ondelete="restrict", related="partner_id.local_state_id",
                                     string='Local State')
    treatment_amount = fields.Monetary(currency_field='currency_id', string="Treatment Amount")
    follow_up_ref = fields.Char(string="Follow Up Ref", related="treatment_id.code")
    note = fields.Text(string="Note")
    state = fields.Selection([('draft', 'Draft'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')], default='draft', string="Status")
    address_id = fields.Many2one('addresses','Address')
    # study = fields.Boolean(string="A study by Zakat Committee")
    # # Related with internal Treatment Process
    # bill = fields.Boolean(string="Initial Bill")
    # medical = fields.Boolean(string="Medical Report")
    # payment = fields.Boolean(string="Payment status")
    # # f_zakat_approval = fields.Integer(string="Final Zakat Approval")
    # letter = fields.Boolean(string="Receiving Letter")
    # transformer = fields.Boolean(string="Transformer")
    # review = fields.Boolean(string="Review")
    # check = fields.Boolean(string="Receiving The check")
    ####################################################

    # Related with Abroad treatment Process
    # commission = fields.Boolean(string="Certificate Of Medical Commission For This Year")
    # abroad_cost = fields.Boolean(string="Cost Of State Treatment")
    # passport_co = fields.Boolean(string="Two Passport Copy")
    # tickets = fields.Boolean(string="Tickets")
    # visa = fields.Boolean(string="Visa")
    # conversion_replacement = fields.Boolean(string="Conversion Or Replacement Of At Least 50%")
    # conversion = fields.Boolean(string="Conversion")
    website_request_validate = fields.Boolean(string='Request Validate')
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments')

    # bnf_phone = fields.Char()

    @api.multi
    def check_lines(self):
        """
        Check If it Require an Attachment or not
        :raise: exception
        """
        if self.attachment_number == 0:
            raise ValidationError(_("Please Attach an File"))

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', self._name), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for treatment in self:
            treatment.attachment_number = attachment.get(treatment.id, 0)

    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', self._name), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': self._name, 'default_res_id': self.id}
        return res


    @api.one
    @api.depends('birth_date')
    def _patient_age(self):
        """
        get patient age from the given birth date
        :return: years
        """
        age = 0
        current = datetime.strftime(datetime.today(), '%Y-%m-%d')
        new = datetime.strptime(str(current), '%Y-%m-%d')
        if self.birth_date:
            birth = datetime.strptime(str(self.birth_date), '%Y-%m-%d')
            age = relativedelta.relativedelta(new, birth)
            self.age = int(age.years)

    @api.multi
    def action_draft(self):
        """
        Set State To Draft
        :return: change state to draft
        """
        self.write({'state': 'draft'})

    @api.multi
    def action_done(self):
        """
        Set State To Draft
        :return: change state to draft
        """
        treatment = self.env['zkate.federaltreatment'].create({
            'type': self.type,
            'partner_id': self.partner_id.id,
            'total_cost': self.treatment_amount,
            'study': self.study,
            'conversion': self.conversion,
            'conversion_replacement': self.conversion_replacement,
            'visa': self.visa,
            'passport_co': self.passport_co,
            'tickets': self.tickets,
            'abroad_cost': self.abroad_cost,
            'commission': self.commission,
            'check': self.check,
            'review': self.review,
            'transformer': self.transformer,
            'letter': self.letter,
            'payment': self.payment,
            'medical': self.medical,
            'bill': self.bill,
        })
        self.treatment_id = treatment.id
        # self.follow_up_ref = self.treatment_id.code
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        """
        Set State To Draft
        :return: change state to draft
        """
        self.write({'state': 'cancel'})

    # @api.constrains('note')
    # def check_note(self):
    #     """
    #     Check if note field if contain any non literal
    #     :raise: execption
    #     """
    #     if not re.match(
    #             "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
    #             self.note.replace(" ", "")):
    #         raise ValidationError(_('Note Field must be Literal'))

    @api.constrains('treatment_amount')
    def amount_field(self):
        """
        Check Amount Field if it have a vakue less than or equal zero
        :raise an exception
        """
        if self.treatment_amount <= 0:
            raise exceptions.ValidationError(_("Treatment Amount Field Cannot Be Zero or Less"))

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
        set sequence number for any new record created
        :param vals: fields values from view
        :return: dict
        """
        # set new sequence number in code for every new record
        vals['code'] = self.env['ir.sequence'].get(self._name) or '/'

        return super(FederalTreatmentRequest, self).create(vals)

    @api.multi
    def unlink(self):
        """
        Check If Record state not in Draft
        :raise exception
        """
        for record in self:
            if record.state != 'draft':
                raise exceptions.ValidationError(_("This Record Cannot be Removed if it not in Draft State"))
            if record.state == 'draft':
                return super(FederalTreatmentRequest, self).unlink()

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        default.update({'date': datetime.today()})
        return super(FederalTreatmentRequest, self).copy(default)


class FederalTreatment(models.Model):
    _name = 'zkate.federaltreatment'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    @api.multi
    @api.onchange('hospital_contract')
    def hospital_domain(self):
        """
        Return Hospitl if type = it adn pharmacy if type = durgs
        :return:
        """
        hospital_ids = []
        if self.hospital_contract == False:
            self.hospital_id = False
            for hospital in hospital_ids:
                self.hospital_id = hospital
                break
            return {'domain': {
                'hospital_id': [('id', '=', False)]}}
        if self.hospital_contract == 'c':
            if self._context.get('default_type') == 'it':
                for hospital in self.env['hospital.treatment'].search(
                        ['&', '&', ('Type', 'in', ['hospital', 'medical_center']), ('state', '=', 'approve'),
                         ('contract', '=', True)]):
                    hospital_ids.append(hospital.id)
            if self._context.get('default_type') == 'drugs':
                for hospital in self.env['hospital.treatment'].search(
                        ['&', ('state', '=', 'approve'), ('contract', '=', True)]):
                    hospital_ids.append(hospital.id)
            if self._context.get('default_type') == 'at':
                for hospital in self.env['hospital.treatment'].search(
                        ['&', '&', '&', ('Type', '=', 'hospital'), ('state', '=', 'approve'),
                         ('contract', '=', True), ('position', '=', 'ex')]):
                    hospital_ids.append(hospital.id)
            self.hospital_id = False
            for hospital in hospital_ids:
                self.hospital_id = hospital
                break
            return {'domain': {
                'hospital_id': [('id', 'in', hospital_ids)]}}
        if self.hospital_contract == 'n_c':
            for i in self.env['hospital.treatment'].search([('contract', '=', False)]):
                hospital_ids.append(i.id)
            for hospital in hospital_ids:
                self.hospital_id = hospital
                break
            return {'domain': {
                'hospital_id': [('id', 'in', hospital_ids)]}}

    partner_id = fields.Many2one('res.partner', string="Patient", ondelete="restrict")
    name = fields.Char(related="partner_id.name", string="Patient Name", copy=False)
    code = fields.Char(string="Reference Number", copy=False)
    date = fields.Date(string="Date", default=time.strftime('%Y-%m-%d'), copy=False)
    type = fields.Selection([('it', 'Internal Treatment'),
                             ('at', 'Abroad Treatment'),
                             ('drugs', 'Drugs, Treatments And Tests')],
                            string="Type")
    ratification_id = fields.Many2one('zakat.ratification', ondelete="restrict", string="Ratification")
    birth_date = fields.Date(related="partner_id.birth_date", string="Birth Date")
    age = fields.Integer(string="Age", compute="_patient_age", store=True)
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, readonly=True,
                              ondelete='restrict')
    company_id = fields.Many2one('res.company', string="Branch", default=lambda self: self.env.user.company_id,
                                 readonly=True, ondelete='restrict')
    hospital_contract = fields.Selection([('c', 'Contracted'),
                                          ('n_c', 'Not Contracted')], string="Hospital Contract")
    hospital_id = fields.Many2one('hospital.treatment', ondelete="restrict", string="Treatment Unit")
    gender = fields.Selection([("male", "Male"), ("female", "Female")], related="partner_id.gender", string="Gender")
    phone = fields.Char(related="partner_id.phone", string="Phone Number", track_visibility='onchange')
    national_number = fields.Char(related="partner_id.national_number", string="National Number",
                                  track_visibility='onchange')

    state_id = fields.Many2one('zakat.state', ondelete="restrict", related="partner_id.zakat_state", string='State')
    local_state_id = fields.Many2one('zakat.local.state', ondelete="restrict", related="partner_id.local_state_id",
                                     string='Local State')

    illness_sector_id = fields.Many2one('zakat.diagnostic.sectors', ondelete="restrict", string="Diagnostic Sector")
    illness_id = fields.Many2one('zakat.illness', string="Illness", ondelete="restrict")
    state = fields.Selection([('draft', 'Draft'),
                              ('w_unit', 'Waiting Unit Manager Approval'),
                              ('auditor', 'Waiting Auditor Approval'),
                              ('w_approval', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel'),
                              ], default='draft', string="Status")
    ex = fields.Boolean()
    study = fields.Boolean(string="A study by Zakat Committee")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    total_cost = fields.Float(string="Total Cost")
    # Related with internal Treatment Process
    bill = fields.Boolean(string="Initial Bill")
    medical = fields.Boolean(string="Medical Report")
    payment = fields.Boolean(string="Payment status")
    # f_zakat_approval = fields.Integer(string="Final Zakat Approval")
    letter = fields.Boolean(string="Receiving Letter")
    transformer = fields.Boolean(string="Transformer")
    review = fields.Boolean(string="Review")
    check = fields.Boolean(string="Receiving The check")
    surgery_date = fields.Date(string="Date of Surgery")
    claim = fields.Boolean(string="Claim Taken")
    ####################################################

    # Related with Abroad treatment Process
    zakat_support = fields.Monetary(string="Zakat Support", currency_field='currency_id')
    financial_support = fields.Monetary(string="Financial Support", currency_field='currency_id')
    passport_no = fields.Char(string="Passport No")
    transport_type = fields.Selection(
        [('air', 'Air'), ('land', 'Land'), ('sea', 'Sea'), ('authorization', 'Authorization')])
    commission = fields.Boolean(string="Certificate Of Medical Commission For This Year")
    abroad_cost = fields.Boolean(string="Cost Of State Treatment")
    passport_co = fields.Boolean(string="One Passport Copy")
    tickets = fields.Boolean(string="Tickets")
    visa = fields.Boolean(string="Visa")
    conversion_replacement = fields.Boolean(string="Conversion Or Replacement Of At Least 50%")
    conversion = fields.Boolean(string="Conversion")
    country = fields.Many2one('zakat.country', string="Country", ondelete="restrict")
    other_support = fields.Float(string="Other Support")

    # field to save the previous value of zakat & financial support
    zakat_approval = fields.Monetary(string="Zakat Support", currency_field='currency_id')
    financial_approval = fields.Monetary(string="Financial Support", currency_field='currency_id')
    voucher_id = fields.Many2one('account.voucher', ondelete="restrict")
    note = fields.Text(string="Note")
    insurance_support = fields.Monetary(string="Insurance Support", currency_field='currency_id')

    # fields needed to be filled from api call
    ncms_follow_id = fields.Char(string="Follow Number")
    # Api returend information
    patient_name = fields.Char(string="Patient Name")
    follow_id = fields.Char(string="Follow Number")
    follow_status = fields.Char(string="Follow Status")
    application_date = fields.Char(string="Application Date")
    classification_type = fields.Char(string="classification type")
    ncms_integration = fields.Boolean(related="company_id.ncms_integration")
    done_validation = fields.Boolean()
    e_first_name = fields.Char()
    e_second_name = fields.Char()
    e_third_name = fields.Char()
    e_forth_name = fields.Char()
    e_name = fields.Char()

    # Health insurace integration fields
    beneficiary_health_num = fields.Char(string="Beneficiary health number")

    valid_bnf = fields.Boolean(string="validation done")

    bnf_id = fields.Char(string="Beneficiary Number")
    bnf_name = fields.Char(string="Beneficiary Name")
    cst_name = fields.Char(string="Service Provider Name")
    sts = fields.Char(string="Status")
    health_ins_integration = fields.Boolean(related="company_id.health_ins_integration")
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments')

    # bnf_phone = fields.Char()

    @api.multi
    def check_lines(self):
        """
        Check If it Require an Attachment or not
        :raise: exception
        """
        if self.attachment_number == 0:
            raise ValidationError(_("Please Attach an File"))

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', self._name), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for treatment in self:
            treatment.attachment_number = attachment.get(treatment.id, 0)

    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', self._name), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': self._name, 'default_res_id': self.id}
        return res

    @api.constrains('e_second_name', 'e_third_name', 'e_forth_name')
    def fields_check(self):
        """
        Check if there is a White Space in field or number
        :raise exception
        """
        if self.type == 'at':
            if self.name_check(self.e_first_name):
                raise exceptions.ValidationError(_('English First name Must contain only ENGLISH letters'))
            if self.name_check(self.e_second_name):
                raise exceptions.ValidationError(_('Englis Second Name MUST contain only ENGLISH letters'))
            if self.name_check(self.e_third_name):
                raise exceptions.ValidationError(_('Englis Third Name MUST contain only ENGLISH letters'))
            if self.name_check(self.e_forth_name):
                raise exceptions.ValidationError(_('Englis Forth Name MUST contain only ENGLISH letters'))

    def name_check(self, name):
        if name[0] == ' ':
            return True
        for letter in name:
            if ord(letter) not in range(ord('a'), ord('z')) and ord(letter) not in range(ord('A'), ord('Z')):
                return True

    @api.multi
    def check_amount_ceiling(self):
        """
        To Check the total_cost range and set ( zakat and financial ) support
        :return: float
        """

        if self.state == 'draft':
            if 'approve' in self.env.context and self.env.context['approve']:

                # old_value = self.env['zkate.federaltreatment'].search([('id' ,'=', self.id)])
                # print("(((((((((((",old_value.total_cost ,"||||||||")
                # if old_value.total_cost != self.env.context['total']:

                #     print("3333333333333333333333" , "3333333" , self._context)
                #     raise exceptions.ValidationError(_("You have to click on compute button to get support amount"))

                if self.type != 'drugs':
                    if self.zakat_support == 0 or self.financial_support == 0:
                        raise ValidationError(_('You have to click on compute button to get support amount'))
                if self.type == 'drugs':
                    if self.zakat_support == 0:
                        raise ValidationError(_('You have to click on compute button to get support amount'))

        """
        Approve to auditor
        """
        if 'approve' in self.env.context and self.env.context['approve']:
            self.action_approve()
            # self.write({'total_change':False})

            if self.zakat_support <= 0:
                raise ValidationError(_('Zakat Support Field cannot be less than or Equal Zero'))

            if self.zakat_support > self.zakat_approval:
                raise exceptions.ValidationError(_("Sorry !! You Are Not Allowed to "
                                                   " Give a Value Greater Than The Specified Value"))

            if self.type != 'drugs':
                if self.financial_support <= 0:
                    raise ValidationError(_('Finanical Support Field cannot be less than or Equal Zero'))

                if self.financial_support > self.financial_approval:
                    raise exceptions.ValidationError(_("Sorry !! You Are Not Allowed to "
                                                       " Give a Value Greater Than The Specified Value"))

            if self.type == 'drugs':
                if self.zakat_support == 0:
                    raise exceptions.ValidationError(_("You have to click on compute button to get support amount"))
            if self.type in ['it', 'at']:
                if self.zakat_support == 0 or self.financial_support == 0:
                    raise exceptions.ValidationError(_("You have to click on compute button to get support amount"))

            if self.state == 'draft':
                if 'compute' in self.env.context and self.env.context['compute']:
                    pass
                else:
                    self.write({'state': 'auditor'})

        """
        Action Exception
        """
        if 'exception' in self.env.context and self.env.context['exception']:
            if 'exception' in self.env.context and self.env.context['exception']:
                self.ex = True
                if self.zakat_support <= 0:
                    raise ValidationError(_('Zakat Support Field cannot be less than or Equal Zero'))

                if not self.note:
                    raise exceptions.ValidationError(_("Please Explain The Reason of Exception In Note Page"))
                if self.type == 'drugs':
                    if self.zakat_support == 0 or 'support_change' in self.env.context:
                        raise exceptions.ValidationError(_("You have to click on compute button to get support amount"))
                if self.type in ['it', 'at']:
                    if self.financial_support <= 0:
                        raise ValidationError(_('Finanical Support Field cannot be less than or Equal Zero'))

                    if self.zakat_support == 0 or self.financial_support == 0 or 'support_change' in self.env.context:
                        raise exceptions.ValidationError(_("You have to click on compute button to get support amount"))

                self.write({'state': 'w_unit'})
            else:
                pass

        # if 'compute' in self.env.context and self.env.context['compute']:

        # self.write({'total_change':False})

        if self.total_cost <= (self.other_support + self.insurance_support):
            raise exceptions.ValidationError(_("Other Support Amount Must Be Less Than The Total Cost"))
        if self.financial_approval < self.financial_support or self.zakat_approval < self.zakat_support:
            self.zakat_support = 0
            self.financial_support = 0
        cost = self.total_cost - (self.other_support + self.insurance_support)
        appropriate_ceiling, max_ceiling, min_ceiling = self.ratification_id.get_appropriate_ceiling(cost)

        if cost < min_ceiling.From:
            raise exceptions.ValidationError(
                _("Zakat and Financial Support Cannot Be Computed Due The Fllowing reason \n"
                  "- Result f Other Support Amount and Total Cost Is Lower Than Celling"))

        exceed = False
        if not appropriate_ceiling:
            exceed = True
            appropriate_ceiling = max_ceiling

        if self.type == "drugs":
            zakat = cost * (appropriate_ceiling.zakat_pre / 100.0)
            if appropriate_ceiling.greater == 'yes' and exceed:
                zakat = appropriate_ceiling.To * (appropriate_ceiling.zakat_pre / 100.0)
                residual = cost - appropriate_ceiling.To
                delta = residual % appropriate_ceiling.In
                residual -= delta
                give = (residual / appropriate_ceiling.In) * appropriate_ceiling.give
                zakat += give

            if 'approve' in self.env.context and self.env.context['approve'] or 'exception' in self.env.context and \
                    self.env.context['exception']:
                self.zakat_approval = zakat

                if self.zakat_support > self.zakat_approval:
                    raise exceptions.ValidationError(
                        _("Sorry !! You Are Not Allowed to Give a Value Greater Than The Specified Value "))

            if 'compute' in self.env.context and self.env.context['compute']:
                self.zakat_support = zakat
                self.zakat_approval = zakat

                if self.zakat_support > self.zakat_approval:
                    raise exceptions.ValidationError(
                        _("Sorry !! You Are Not Allowed to Give a Value Greater Than The Specified Value "))

        if self.type == "it":
            if self.ratification_id.ratification_type.contribution == 'p':
                zakat = cost * (appropriate_ceiling.zakat_pre / 100.0)
                financial = cost * (appropriate_ceiling.financial_pre / 100.0)
                if appropriate_ceiling.greater == 'yes' and exceed:
                    zakat = appropriate_ceiling.To * (appropriate_ceiling.zakat_pre / 100.0)
                    financial = appropriate_ceiling.To * (appropriate_ceiling.financial_pre / 100.0)
                    residual = cost - appropriate_ceiling.To
                    delta = residual % appropriate_ceiling.In
                    residual -= delta
                    give = (residual / appropriate_ceiling.In) * appropriate_ceiling.give
                    zakat += (give / 2.0)
                    financial += (give / 2.0)

                if 'approve' in self.env.context and self.env.context['approve'] or 'exception' in self.env.context and \
                        self.env.context['exception']:
                    self.zakat_approval = zakat
                    self.financial_approval = financial

                    if self.financial_support > self.financial_approval:
                        raise exceptions.ValidationError(
                            _("Sorry !! You Are Not Allowed to Give a Value Greater Than The Specified Value "))

                    if self.zakat_support > self.zakat_approval:
                        raise exceptions.ValidationError(
                            _("Sorry !! You Are Not Allowed to Give a Value Greater Than The Specified Value "))

                if 'compute' in self.env.context and self.env.context['compute']:
                    self.zakat_support = zakat
                    self.financial_support = financial
                    self.zakat_approval = zakat
                    self.financial_approval = financial

                    if self.financial_support > self.financial_approval:
                        raise exceptions.ValidationError(
                            _("Sorry !! You Are Not Allowed to Give a Value Greater Than The Specified Value "))

                    if self.zakat_support > self.zakat_approval:
                        raise exceptions.ValidationError(
                            _("Sorry !! You Are Not Allowed to Give a Value Greater Than The Specified Value "))

            if self.ratification_id.ratification_type.contribution == 'fi':
                zakat = appropriate_ceiling.zakat_amount
                financial = appropriate_ceiling.financial_amount
                if appropriate_ceiling.greater == 'yes' and exceed:
                    residual = cost - appropriate_ceiling.To
                    delta = residual % appropriate_ceiling.In
                    residual -= delta
                    give = (residual / appropriate_ceiling.In) * appropriate_ceiling.give
                    zakat += (give / 2.0)
                    financial += (give / 2.0)

                if 'approve' in self.env.context and self.env.context['approve'] or 'exception' in self.env.context and \
                        self.env.context['exception']:

                    self.zakat_approval = zakat
                    self.financial_approval = financial

                    if self.financial_support > self.financial_approval:
                        raise exceptions.ValidationError(
                            _("Sorry !! You Are Not Allowed to Give a Value Greater Than The Specified Value "))

                    if self.zakat_support > self.zakat_approval:
                        raise exceptions.ValidationError(
                            _("Sorry !! You Are Not Allowed to Give a Value Greater Than The Specified Value "))

                if 'compute' in self.env.context and self.env.context['compute']:

                    self.zakat_support = zakat
                    self.financial_support = financial
                    self.zakat_approval = zakat
                    self.financial_approval = financial

                    if self.financial_support > self.financial_approval:
                        raise exceptions.ValidationError(
                            _("Sorry !! You Are Not Allowed to Give a Value Greater Than The Specified Value "))

                    if self.zakat_support > self.zakat_approval:
                        raise exceptions.ValidationError(
                            _("Sorry !! You Are Not Allowed to Give a Value Greater Than The Specified Value "))

        if self.type == "at":
            zakat = appropriate_ceiling.zakat_amount
            financial = appropriate_ceiling.financial_amount

            if 'approve' in self.env.context and self.env.context['approve'] or 'exception' in self.env.context and \
                    self.env.context['exception']:
                self.financial_approval = financial
                self.zakat_approval = zakat

                if self.financial_support > self.financial_approval:
                    raise exceptions.ValidationError(
                        _("Sorry !! You Are Not Allowed to Give a Value Greater Than The Specified Value "))

                if self.zakat_support > self.zakat_approval:
                    raise exceptions.ValidationError(
                        _("Sorry !! You Are Not Allowed to Give a Value Greater Than The Specified Value "))

            if 'compute' in self.env.context and self.env.context['compute']:
                self.zakat_support = zakat
                self.financial_support = financial
                self.financial_approval = financial
                self.zakat_approval = zakat

                if self.financial_support > self.financial_approval:
                    raise exceptions.ValidationError(
                        _("Sorry !! You Are Not Allowed to Give a Value Greater Than The Specified Value "))

                if self.zakat_support > self.zakat_approval:
                    raise exceptions.ValidationError(
                        _("Sorry !! You Are Not Allowed to Give a Value Greater Than The Specified Value "))

    @api.onchange('illness_sector_id')
    def _onchange_illness_sector_id(self):
        self.illness_id = False

    @api.multi
    def unlink(self):
        """
        Check If Record state not in Draft
        :raise exception
        """
        for record in self:
            if record.state != 'draft':
                raise exceptions.ValidationError(_("This Record Cannot be Removed if it not in Draft State"))
            if record.state == 'draft':
                return super(FederalTreatment, self).unlink()

    @api.constrains('total_cost', 'other_support', 'insurance_support')
    def amount_field(self):
        """
        Check Amount Field if it have a vakue less than or equal zero
        :raise an exception
        """
        if self.insurance_support < 0:
            raise exceptions.ValidationError(_("Insurance Amount Cannot Be Less Than Zero"))
        if self.total_cost <= 0:
            raise exceptions.ValidationError(_("Total Cost Field Cannot Be Zero or Less"))
        if self.other_support < 0:
            raise exceptions.ValidationError(_("Other Support Field Cannot Be Less Than Zero"))

    @api.multi
    def action_approve(self):
        """
        Check if user have other record with state done in the same range of ratification
        :return: change state
        """
        self.check_lines()
        if self.zakat_support <= 0:
            raise ValidationError(_('Zakat Support Field cannot be less than or Equal Zero'))
        if self.financial_support <= 0:
            raise ValidationError(_('Finanical Support Field cannot be less than or Equal Zero'))
        is_any = self.search([('ratification_id', '=', self.ratification_id.id)])
        if not is_any:
            return True

        range_years = int(self.ratification_id.year)
        range_months = int(self.ratification_id.months)

        date = self.get_date(self.date)
        start_date = self.monthdelta(self.addYears(date, range_years * -1), range_months * -1)
        end_date = self.monthdelta(self.addYears(date, range_years), range_months)

        date = date.date()
        start_date = start_date.date()
        end_date = end_date.date()

        is_any = self.search([('id', '!=', self.id), ('ratification_id', '=', self.ratification_id.id),
                              ('partner_id', '=', self.partner_id.id),
                              ('date', '>=', start_date), ('date', '<=', end_date),
                              ('state', 'in', ('w_unit', 'auditor', 'draft', 'w_approval', 'done'))])

        if is_any:
            raise exceptions.ValidationError(
                _('This Patient Have a Previous Treatment With This Reference No.' + self.code))

    @api.multi
    def action_draft(self):
        """
        Set State To Draft
        :return: change state to draft
        """
        self.write({'state': 'draft'})

    # @api.multi
    # def action_exception(self):
    #     """
    #     change state to w_unit
    #     :return: change state
    #     """
    #     if not self.note:
    #         raise exceptions.ValidationError(_("Please Explain The Reason of Exception In Note Page"))
    #     if self.type == 'drugs':
    #         if self.zakat_support == 0 or 'support_change' in self.env.context :
    #             raise exceptions.ValidationError(_("You have to click on compute button to get support amount"))
    #     if self.type in ['it', 'at']:

    #         if self.zakat_support == 0 or self.financial_support == 0 or 'support_change' in self.env.context :
    #             raise exceptions.ValidationError(_("You have to click on compute button to get support amount"))
    #     self.write({'state': 'w_unit'})

    @api.multi
    def w_unit_approval(self):
        """
        change state to w_approval
        :return:
        """
        cost = self.total_cost - self.other_support
        exception_cost = self.zakat_support + self.financial_support
        if exception_cost > cost:
            raise exceptions.ValidationError(_("Zakat & Financial Support Cannot Be Greater Than Total Cost"))

        self.write({'state': 'auditor'})

    @api.multi
    def auditor_approval(self):
        """
        change State To Approval
        :return:
        """

        self.write({'state': 'w_approval'})

    @api.multi
    def action_done(self):
        """
        Change State To Done
        :return:
        """
        if not self.surgery_date and self.type == 'it':
            raise exceptions.ValidationError(_("Please Enter The Surgery Date"))

        if self._context.get('default_type') == 'it':
            order_date = datetime.strptime(str(self.date), "%Y-%m-%d")
            surgery_date = datetime.strptime(str(self.surgery_date), '%Y-%m-%d')
            dif = relativedelta.relativedelta(surgery_date, order_date)
            if dif.years >= 1:
                raise exceptions.ValidationError(_('The Surgery Date Cannot Be After 1 Year From Order Date'))
            if self.surgery_date <= self.date:
                raise exceptions.ValidationError(_('The Surgery Date Cannot Be Before Order Date'))

        if self.type != 'at':
            self.write({'state': 'done'})
            if self.type == 'it':
                total_cost = self.zakat_support + self.financial_support
                hospital_cieling = self.env[('hospital.ceiling.subclass')].search(
                    [('hospital_id', '=', self.hospital_id.id), ('hospital_ceiling_id.state', '=', 'confirmed'),
                     '&', ('hospital_ceiling_id.start_date', '<=', self.surgery_date),
                     ('hospital_ceiling_id.end_date', '>=', self.surgery_date)])
                if hospital_cieling:
                    old_amount = hospital_cieling.taken_amount
                    total_cost = total_cost + old_amount
                    hospital_cieling.taken_amount = total_cost
            if self.type == 'drugs':
                total_cost = self.zakat_support
                hospital_cieling = self.env[('hospital.ceiling.subclass')].search(
                    [('hospital_id', '=', self.hospital_id.id), ('hospital_ceiling_id.state', '=', 'confirmed'),
                     '&', ('hospital_ceiling_id.start_date', '<=', self.date),
                     ('hospital_ceiling_id.end_date', '>=', self.date)])
                if hospital_cieling:
                    old_amount = hospital_cieling.taken_amount
                    total_cost = total_cost + old_amount
                    hospital_cieling.taken_amount = total_cost
        if self.type == 'at':
            line = []
            if self.done_validation == False:
                raise exceptions.ValidationError(_("Please Check The Follow Number"))
            ratification = self.ratification_id
            zakat_account_id = ratification.property_zakat_account_id.id
            financial_account_id = ratification.property_financial_account_id.id
            journal_id = ratification.zakat_journal.id

            if not zakat_account_id:
                raise exceptions.ValidationError(_("Kindly Specify an Acount For Zakat in Configuration/Ratification"
                                                   + "/Ratification List Accounting Page"))
            if self.type in ['it', 'at']:
                if not financial_account_id:
                    raise exceptions.ValidationError(
                        _("Kindly Specify an Acount For Financial in Configuration/Ratification"
                          + "/Ratification List Accounting Page"))
            if not journal_id:
                raise exceptions.ValidationError(
                    _("Kindly Specify an Journal For Zakat and Financial in Configuration/Ratification"
                      + "/Ratification List Accounting Page"))
            line += [(0, 6, {
                'name': _('Zakat Support'),
                'account_id': zakat_account_id,
                'quantity': 1,
                'price_unit': self.zakat_support,
            })]

            line += [(0, 6, {
                'name': _('Financial Support'),
                'account_id': financial_account_id,
                'quantity': 1,
                'price_unit': self.financial_support,
            })]

            month = datetime.today().month
            months = calendar.month_name[month]
            voucher_id = self.env['account.voucher'].create(
                {
                    'name': _('Pay For') + ' ' + self.partner_id.name,
                    'partner_id': self.partner_id.id,
                    'journal_id': journal_id,
                    'pay_now': 'pay_later',
                    'reference': _('Zakat & Financial Support'),
                    'voucher_type': 'purchase',
                    'company_id': self.env.user.company_id.id,
                    'line_ids': line,

                })
            self.voucher_id = voucher_id.id
            self.write({'state': 'done'})

    @api.multi
    def action_return(self):
        """
        Return To Previous State
        :return:
        """
        if self.ex == True:
            self.write({'state': 'w_unit'})
        elif self.ex == False:
            self.write({'state': 'draft'})

    @api.multi
    def action_cancel(self):
        """
        Set record state to cancel state
        :return:
        """
        self.write({'state': 'cancel'})

    @api.multi
    def action_call_ncms(self):
        """
        call ncms appi to check the follow id
        :return: related follow_id information
        """
        follow_id = self.ncms_follow_id
        key = 'NMC-v2-ServiceStatus-API'
        secret = key.encode('utf-8')
        sign = hmac.new(secret, follow_id.encode('utf-8'), hashlib.sha256).hexdigest()
        payload = {'follow_id': follow_id, 'token': sign, }
        # url to pass to the connection function
        url = "http://197.254.225.97/api/app/index.php/check/status"
        api = API_integration.APIIntegration()
        code = api.connection(url)
        if code == 200:
            response = api.set_payload(url, payload, sign)
            if response['response_code'] == '00':
                self.done_validation = True
                self.follow_id = self.ncms_follow_id
                self.patient_name = response['name']
                self.follow_status = response['service_status']
                self.classification_type = response['service_name']
            elif response['response_code'] == '103':
                raise exceptions.ValidationError(_("Please Check The Follow Number"))
            elif response['response_code'] == '101':
                raise exceptions.ValidationError(_("The Supplied Follow Number Does Not Exist"))
        elif code == False:
            raise exceptions.ValidationError(_("Please Check Your Internet Connection"))

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
        set sequence number for any new record created
        :param vals: fields values from view
        :return: dict
        """
        vals['code'] = self.env['ir.sequence'].sudo().get(self._name) or '/'
        if self.type == 'at':
            vals['e_name'] = vals.get('e_first_name', '') + ' ' + vals.get('e_second_name', '') + ' ' + vals.get(
                'e_third_name', '') + ' ' + vals.get('e_forth_name', '')
        return super(FederalTreatment, self).create(vals)

    def get_date(self, str):
        return datetime.strptime(str, "%Y-%m-%d")

    def addYears(self, d, years):
        try:
            # Return same day of the current year
            return d.replace(year=d.year + years)
        except ValueError:
            # If not same day, it will return other, i.e.  February 29 to March 1 etc.
            return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

    def monthdelta(self, date, delta):
        m, y = (date.month + delta) % 12, date.year + ((date.month) + delta - 1) // 12
        if not m: m = 12
        d = min(date.day, [31,
                           29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][
            m - 1])
        return date.replace(day=d, month=m, year=y)

    # @api.constrains('date')
    # def check_date(self):
    #     """
    #     Desc:Check date constrains if the is another record with current date period
    #     """
    #
    #     is_any = self.search([('ratification_id', '=', self.ratification_id.id)])
    #     if not is_any:
    #         return True
    #
    #     range_years = int(self.ratification_id.year)
    #     range_months = int(self.ratification_id.months)
    #
    #     date = self.get_date(self.date)
    #     start_date = self.monthdelta(self.addYears(date, range_years * -1), range_months * -1)
    #     end_date = self.monthdelta(self.addYears(date, range_years), range_months)
    #
    #     date = date.date()
    #     start_date = start_date.date()
    #     end_date = end_date.date()
    #
    #     is_any = self.search([('id', '!=', self.id), ('ratification_id', '=', self.ratification_id.id),
    #                           ('partner_id', '=', self.partner_id.id),
    #                           ('date', '>=', start_date), ('date', '<=', end_date),
    #                           ('state', 'in', ('w_unit', 'auditor', 'draft', 'w_approval', 'done'))])
    #
    #     if is_any:
    #         raise exceptions.ValidationError(
    #             _('This Patient Have a Previous Treatment With This Reference No.'+ self.code))

    @api.constrains('ncms_follow_id')
    def check_follow(self):
        """
        Check if follow id is write
        :return:
        """
        if self.ncms_follow_id:
            if not re.match("^[0-9]*$", self.ncms_follow_id.replace(" ", "")):
                raise ValidationError(_('Follow Number Field must be number'))

            if self.ncms_integration != False:
                if 10 < len(self.ncms_follow_id) or 10 > len(self.ncms_follow_id):
                    raise exceptions.ValidationError(_('Follow Number Must Be 10 Numbers.'))

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
                raise exceptions.ValidationError(_('Phone must be exactly 10 Numbers and Start with ZERO 0 .'))
        if self.national_number != False:
            if 11 < len(self.national_number) or 11 > len(self.national_number):
                raise exceptions.ValidationError(_('ID Number Must Be At least 11 Numbers.'))

    @api.one
    @api.depends('birth_date')
    def _patient_age(self):
        """
        get patient age from the given birth date
        :return: years
        """
        age = 0
        current = datetime.strptime(str(self.date), '%Y-%m-%d')
        if self.birth_date:
            birth = datetime.strptime(str(self.birth_date), '%Y-%m-%d')
            age = relativedelta.relativedelta(current, birth)
            self.age = int(age.years)

    @api.constrains('commission', 'abroad_cost', 'passport_co', 'tickets', 'visa', 'conversion',
                    'conversion_replacement', 'medical', 'bill', 'payment', 'letter', 'transformer', 'review', 'check')
    def check_federal_treatment_doc(self):
        """
        check if one of the required document is selected if not raise an exception
        :return: raise exception
        """
        if self.type == 'it':
            if not self.medical or not self.bill or not self.payment or not self.study:
                raise exceptions.ValidationError(_("You Must Select All Required Documents"))
        elif self.type == 'at':
            if not self.commission or not self.abroad_cost or not self.passport_co \
                    or not self.tickets or not self.visa or not self.conversion or not self.conversion_replacement:
                raise exceptions.ValidationError(_("You Must Select All Required Documents"))
        elif self.type == 'drugs':
            if not self.bill:
                raise exceptions.ValidationError(_("You Must Select All Required Documents"))

    """  passport validation (start with p followed by 8 digit)"""

    @api.constrains('passport_no')
    def validate_passport(self):
        if self.type == 'at':
            if self.passport_no and (len(self.passport_no.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Passport cannot contain spaces"))
            if self.passport_no and (len(self.passport_no.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Passport cannot contain spaces"))
            else:
                passport = self.passport_no
                if passport.isdigit():
                    if len(self.passport_no) != 9:
                        raise exceptions.ValidationError(_("Passport length must has 9 digits "))
                    else:
                        raise exceptions.ValidationError(_("Passport cannot contains special characters or leters"))
                    valid_patient_passport = self.env['zkate.federaltreatment'].search(
                        [('passport_no', '=', self.passport_no), ('id', '!=', self.id), ('name', '!=', self.name)])

                    if valid_patient_passport:
                        raise exceptions.ValidationError(_("This passport number already taken by other patient"))

    # @api.onchange('total_cost')
    # def change_cost(self):
    #     self.env.context = {'skip_change': True}
    #     self.check_amount_ceiling()
    #

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        default.update({'date': datetime.today()})
        return super(FederalTreatment, self).copy(default)

    def print_report(self):
        """
        pass the data i need to get the report
        :return: report action
        """
        if self.state != 'done':
            raise exceptions.ValidationError(_("You Cannot Get Guarantee Letter if state not in done"))
        data = self.id
        datas = {
            'ids': [],
            'model': 'zkate.federaltreatment',
            'treatment': data,

        }
        return self.env.ref('dzc_1.guarantee_letter_action').report_action(self, data=datas)

    def print_english_letter(self):
        if self.state != 'done':
            raise exceptions.ValidationError(_("You Cannot Get Guarantee Letter if state not in done"))
        data = self.id
        datas = {
            'ids': [],
            'model': 'zkate.federaltreatment',
            'treatment': data,
        }
        return self.env.ref('dzc_1.english_guarantee_letter_action').report_action(self, data=datas)

    def print_follow_form(self):
        """
        pass the data i need to get the report
        :return: report action
        """
        data = self.id
        datas = {
            'ids': [],
            'model': 'zkate.federaltreatment',
            'treatment': data,

        }
        return self.env.ref('dzc_1.follow_form_action').report_action(self, data=datas)

    def print_sergury_fees_report(self):
        """
        pass the data i need to get the report
        :return: report action
        """
        data = self.id
        datas = {
            'ids': [],
            'model': 'zkate.federaltreatment',
            'treatment': data,
        }
        return self.env.ref('dzc_1.print_sergury_fees_action').report_action(self, data=datas)

    def abroad_treatment(self):
        """
        pass the data i need to get the report
        :return: report action
        """
        data = self.id
        datas = {
            'ids': [],
            'model': 'zkate.federaltreatment',
            'treatment': data,

        }
        return self.env.ref('dzc_1.abroad_treatment_action').report_action(self, data=datas)

    ################################# Insurance health integration part ############

    @api.constrains('beneficiary_health_num')
    def bnf_num_constrains(self):
        if self.beneficiary_health_num:
            for b in self.beneficiary_health_num:
                if b.isalpha() and b != '-':
                    raise exceptions.ValidationError(_("Beneficiary Number can only contain digits and - dashes "))
            return True

    @api.multi
    def health_insurance_call(self):

        beneficiary_health_num = self.beneficiary_health_num

        service_user_id = '793'
        service_passowrd = '793'

        url = "http://196.29.166.236/YSINS_WCF_API/YSINS_API.svc/getBnfData/" + beneficiary_health_num + "/" + service_user_id + "/" + service_passowrd
        api = API_integration.APIIntegration()
        code = api.wcf_connection(url)
        import ast

        if code == 200:
            response = api.wcf_get(url)
            if "Err" in response:
                raise exceptions.ValidationError(_("Please Check Beneficiary number"))
            else:
                response = response.replace('[', '').replace(']', '')
                response = response.replace('{', '').replace('}', '')
                response = response.replace('\\', '')
                response = response.split(',')
                res = {x.split(':')[0]: x.split(':')[1] for x in response}

                self.valid_bnf = True

                self.bnf_id = self.beneficiary_health_num
                bnf_n = res["\"bnfName\""]

                self.bnf_name = bnf_n.replace('"', ' ')
                cst_n = res["\"cstName\""]

                self.cst_name = cst_n.replace('"', ' ')
                sts_n = res["\"sts\""].replace('"', ' ')

                sts = ""
                if sts_n == ' 1 ':
                    sts = "Active"

                else:
                    sts = "Inactive"

                self.sts = sts

                # self.bnf_phone = res[0][3]

        if code == False:
            raise exceptions.ValidationError(_("Please Check Your Internet Connection"))


class TreatmentPayment(models.Model):
    _name = 'zakat.treatmentpayment'

    name = fields.Char(string="Name")
    order_date = fields.Date(string="Order Date", default=datetime.today(), store=True, copy=False)
    code = fields.Char(string="Order Reference")
    hospital_id = fields.Many2one('hospital.treatment', string="Hospital", domain="[('state','=','approve')]",
                                  ondelete="restrict")
    zakat_support = fields.Float(string="Zakat Support", compute='get_zakat_financial_support', store=True)
    financial_support = fields.Float(string="Financial Support", compute='get_zakat_financial_support', store=True)
    federalTreatment_ids = fields.Many2many('zkate.federaltreatment')
    vouchers_ids = fields.One2many('account.voucher', 'treatment_payment_id', string="Vouchers", ondelete="restrict")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('review', 'Review'),
                              ('approve', 'Approve'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')], string="Status", default='draft')

    vouchers_count = fields.Integer(string='Vouchers', compute='_compute_vouchers_ids')
    company_id = fields.Many2one("res.company", default=lambda self: self.env.user.company_id, string="Company",
                                 ondelete='cascade')

    @api.constrains('hospital_id', 'federalTreatment_ids')
    def dont_create(self):
        t = self.env['zakat.treatmentpayment'].search(
            [('hospital_id', '=', self.hospital_id.id), ('federalTreatment_ids', '=', self.federalTreatment_ids.ids)])
        if t:
            raise ValidationError(_("This payment request is already exist"))

    @api.onchange('hospital_id')
    def _onchange_hospital_id(self):
        self.federalTreatment_ids = False

    @api.multi
    @api.depends('vouchers_ids')
    def _compute_vouchers_ids(self):
        for rec in self:
            rec.vouchers_count = len(rec.vouchers_ids)

    @api.constrains('federalTreatment_ids')
    def check_details(self):
        for rec in self:
            if not rec.federalTreatment_ids:
                raise ValidationError(_("At least one Patient should be added"))

    @api.multi
    def action_view_vouchers(self):
        action = self.env.ref('account_voucher.action_purchase_receipt').read()[0]

        vouchers_ids = self.mapped('vouchers_ids')
        if len(vouchers_ids) >= 1:
            action['domain'] = [('id', 'in', vouchers_ids.ids)]
        return action

    @api.multi
    def unlink(self):
        """
        Allow to  Delete if it in draft
        :return:
        """
        for payment in self:
            if payment.state != 'draft':
                raise exceptions.ValidationError(_("This Record Cannot be Removed if it not in Draft state"))
            if payment.state == 'draft':
                return super(TreatmentPayment, self).unlink()

    @api.multi
    def action_confirm(self):
        if not self.federalTreatment_ids:
            raise exceptions.ValidationError(_("You Have To Chose one Treatment Order at least"))
        self.write({'state': 'confirm'})

    @api.multi
    def action_review(self):
        self.write({'state': 'review'})

    @api.multi
    def action_approve(self):
        self.write({'state': 'approve'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

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
        set sequence number for any new record created
        :param vals: fields values from view
        :return: dict
        """
        # set new sequence number in code for every new record
        vals['code'] = self.env['ir.sequence'].get(self._name) or '/'
        vals['name'] = vals['code']

        if 'federalTreatment_ids' not in vals:
            raise ValidationError(_("At least one Patient should be added"))
        return super(TreatmentPayment, self).create(vals)

    @api.depends('federalTreatment_ids')
    def get_zakat_financial_support(self):
        """
        To Get The Total Cost Of Zakat and Financial Support
        :return:
        """
        zakat = 0
        financail = 0
        for teartment in self.federalTreatment_ids:
            zakat += teartment.zakat_support
            financail += teartment.financial_support
        self.zakat_support = zakat
        self.financial_support = financail

    @api.multi
    def action_done(self):
        """
        Change State To Done and Create Voucher with zakat and financial support
        totals
        :return:
        """
        zakat_cost = self.zakat_support
        financial_cost = self.financial_support
        line = []
        zakat_account_id = None
        financial_account_id = None
        journal_id = None

        line_dicts = {}
        for ratification in self.federalTreatment_ids:
            line_dicts[ratification.ratification_id] = line_dicts.get(ratification.ratification_id, [])
            line_dicts[ratification.ratification_id].append(ratification)

        for ratification_id in line_dicts:
            line = []
            tmep_zakat_cost = temp_financial_cost = 0.0
            for teartment in line_dicts[ratification_id]:
                teartment.claim = True
                zakat_account_id = teartment.ratification_id.property_zakat_account_id.id
                financial_account_id = teartment.ratification_id.property_financial_account_id.id
                journal_id = teartment.ratification_id.zakat_journal.id
                tmep_zakat_cost += teartment.zakat_support
                temp_financial_cost += teartment.financial_support

            line += [(0, 6, {
                'name': _('Zakat Support'),
                'account_id': zakat_account_id,
                'quantity': 1,
                'price_unit': tmep_zakat_cost,
            })]

            if ratification_id.ratification_list != 'dtt':
                line += [(0, 6, {
                    'name': _('Financial Support'),
                    'account_id': financial_account_id,
                    'quantity': 1,
                    'price_unit': temp_financial_cost,
                })]

            month = datetime.today().month
            months = calendar.month_name[month]
            voucher_id = self.env['account.voucher'].create(
                {
                    'name': ('Pay For') + self.hospital_id.name + ' For ' + months,
                    'journal_id': journal_id,
                    'pay_now': 'pay_later',
                    'reference': _('Pay For') + ' ' + self.hospital_id.name + ' For' + months,
                    'voucher_type': 'purchase',
                    'company_id': self.env.user.company_id.id,
                    'line_ids': line,
                    'treatment_payment_id': self.id,
                    'amount': tmep_zakat_cost + temp_financial_cost,
                })

        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        """
        Change state To Cancel
        :return:
        """
        self.write({'state': 'cancel'})

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        default.update({'date': datetime.today()})
        return super(TreatmentPayment, self).copy(default)


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    treatment_payment_id = fields.Many2one('zakat.treatmentpayment', "Treatment Payment")

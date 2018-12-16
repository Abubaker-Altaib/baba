# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api, exceptions, _
from datetime import datetime
from odoo.exceptions import ValidationError


class ZakatResPartner(models.Model):
    _inherit = 'res.partner'

    first_name = fields.Char()
    second_name = fields.Char()
    third_name = fields.Char()
    forth_name = fields.Char()
    code = fields.Char(string="Reference Number")
    national_number = fields.Char(string="National Number")
    nationality = fields.Selection([('sd', 'Sudanese'), ('other', 'Other')], string="Nationality", default='sd')
    # passport_char = fields.Char()
    passport = fields.Char(string="Passport No")
    date = fields.Date(default=datetime.today())
    zakat_state = fields.Many2one('zakat.state', string='State')
    sectors = fields.Many2one('zakat.sectors', string="Sectors")
    local_state_id = fields.Many2one('zakat.local.state', string='Local State')
    admin_unit = fields.Many2one('zakat.admin.unit', string='Administrative Unit')
    job = fields.Char(string="Job")
    job_type = fields.Selection([('pension', 'Pension'), ('non_pension', 'Not pension')])
    phone = fields.Char(string="Phone Number")
    birth_date = fields.Date(string='Date of Birth')
    # Fageer = fields.Boolean(default=False)
    # Ibn_Alsabil = fields.Boolean(default=False)
    # Garmeen = fields.Boolean(default=False)
    # Almsakeen = fields.Boolean(default=False)
    city = fields.Char()
    house_no = fields.Char()
    Village = fields.Char()
    gender = fields.Selection([("male", "Male"), ("female", "Female")], string="Gender")
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user.id,
                              ondelete='restrict')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    zakat_partner = fields.Boolean(default=False)
    zakat_committee = fields.Many2one('zakat.dzc1.committee')

    _sql_constraints = [
        ('unique_national_number', 'unique(national_number)', _("The National Number is Exists")),
        ('unique_passport', 'unique(passport)', _("Passport Number Is Exists"))
    ]

    @api.constrains('job')
    def check_name(self):
        # if self.city:
        #     if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.city.replace(" ","")):
        #         raise ValidationError(_('City name Should contain just Charactors or numbers and can not begin with white Space or special charactor'))
        #     if self.city and (len(self.city.replace(' ', '')) <= 0):
        #         raise exceptions.ValidationError(_("City name Should contain just Charactors or numbers and can not begin with white Space or special charactor"))
        # if self.Village:
        #     if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.Village.replace(" ","")):
        #         raise ValidationError(_('Village name Should contain just Charactors or numbers and can not begin with white Space or special charactor'))
        #     if self.Village and (len(self.Village.replace(' ', '')) <= 0):
        #         raise exceptions.ValidationError(_("Village name Should contain just Charactors or numbers and can not begin with white Space or special charactor"))
        if self.job:
            if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.job.replace(" ","")):
                raise ValidationError(_('job name Should contain just Charactors or numbers and can not begin with white Space or special charactor'))
            if self.job and (len(self.job.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("job name Should contain just Charactors or numbers and can not begin with white Space or special charactor"))


    def get_data(self):
        """
        TODO: Get Data For National Number API
        :return:
        """

    @api.constrains('first_name', 'second_name', 'third_name', 'forth_name', 'e_first_name', 'e_second_name',
                    'e_third_name', 'e_forth_name', 'passport_char', 'passport')
    def fields_check(self):
        """
        Check if there is a White Space in field or number
        :raise exception
        """
        if self.name_check(self.first_name):
            raise exceptions.ValidationError(_('First name Must be Literal'))
        if self.name_check(self.second_name):
            raise exceptions.ValidationError(_('Second Name MUST be Literal'))
        if self.name_check(self.third_name):
            raise exceptions.ValidationError(_('Third Name MUST be Literal'))
        if self.name_check(self.forth_name):
            raise exceptions.ValidationError(_('Forth Name MUST be Literal'))
        if self.nationality != 'sd':
            if 9 < len(self.passport) or 9 > len(self.passport):
                raise exceptions.ValidationError(_('Passport Number Must Be 8 number and Start with Letter'))
            if not re.match("^[0-9]*$", self.passport[-8:].replace(" ", "")):
                raise ValidationError(_('Passport Field must be number'))

    def name_check(self, name):
        for letter in name:
            if letter != ' ' and not letter.isalpha():
                return True

    @api.model
    def get_seq_to_view(self):
        """
        Get sequence in code filed in form view
        :return:
        """
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, values):
        if values.get('name', False) == False:
            for partner in self.env['res.partner'].search([('first_name', '=', values.get('first_name')),
                                                           ('second_name', '=', values.get('second_name')),
                                                           ('third_name', '=', values.get('third_name')),
                                                           ('forth_name', '=', values.get('forth_name'))]):
                raise exceptions.ValidationError(_('This Information Already Exists'))
        if values.get('name', False) == False:
            values['name'] = values.get('first_name', '') + ' ' + values.get('second_name', '') + ' ' \
                             + values.get('third_name', '') + ' ' + values.get('forth_name', '')
        
        # values['passport'] = values['passport_char']+''+values['passport']
        values['code'] = self.env['ir.sequence'].get(self._name) or '/'
        return super(ZakatResPartner, self).create(values)

    @api.multi
    def write(self, vals):
        """
        if name was change it reflect it in our tree and form view
        :param vals: field value
        :return: dict
        """
        if self._context.get('default_zakat_partner'):
            vals.update({'name': ''})
            if 'first_name' not in vals:
                vals.update({'first_name': self.first_name})
            if 'second_name' not in vals:
                vals.update({'second_name': self.second_name})
            if 'third_name' not in vals:
                vals.update({'third_name': self.third_name})
            if 'forth_name' not in vals:
                vals.update({'forth_name': self.forth_name})
            if 'name' in vals:
                vals['name'] = vals['first_name'] + ' ' + vals['second_name'] + ' ' + vals[
                    'third_name'] + ' ' + vals['forth_name']
        return super(ZakatResPartner, self).write(vals)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Desc : Function to make user search for partner based on name or national number
        :param name: (Text) what user want to search about
        :return:
        """
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(['|', ('name', operator, name), ('national_number', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.constrains('phone', 'national_number', 'birth_date', 'house_no')
    def checks(self):
        """
        Desc:Check format Phones and ID Numbers
        :return:
        """
        if 'default_zakat_partner' in self._context:
            pattern = re.compile(r'^[0]\d{9,9}$')
            if self.phone != False:
                if not pattern.search(self.phone):
                    raise exceptions.ValidationError(_('Phone must be exactly 10 Numbers and Start with ZERO 0 .'))
            if self.nationality == 'sd':
                if self.national_number != False:
                    if not re.match("^[0-9]*$", self.national_number.replace(" ", "")):
                        raise ValidationError(_('National Number Field must be number'))
                    if self.national_number.replace(" ", "") != self.national_number:
                        raise ValidationError(_('National Number Field must be number'))
                    if 11 < len(self.national_number) or 11 > len(self.national_number):
                        raise exceptions.ValidationError(_('ID Number must be at least 11 Numbers.'))
            values = self.env['zakat.family'].search([('national_number', '=', self.national_number)])
            for value in values:
                if len(value) > 0:
                    message = "This National Number is assigned for " + value.name + " and he is the " + value.relation + " of " + value.fageer_id.faqeer_id.name
                    raise exceptions.ValidationError(_(message))
            if self.birth_date != False:
                if self.birth_date > self.date:
                    raise exceptions.ValidationError(_('Birth Date MUST be before  today'))
            if self.house_no != False:
                if self.house_no.isdigit():
                    if int(self.house_no) <= 0:
                        raise exceptions.ValidationError(_('House Number can not be negative number '))
                else:
                    raise exceptions.ValidationError(_('House Number Can not be a Character'))


#####################################
#
# Account Voucher Modification
# Make account_id required False
#
######################################

class AccountVoucherCustom(models.Model):
    _inherit = 'account.voucher'

    journal_id = fields.Many2one(required=False)
    account_id = fields.Many2one(required=False)


class CompanyCustomizationClass(models.Model):
    _inherit = 'res.company'

    category = fields.Selection([('state_id', 'State'), ('local_state', 'Local State'), ('sector', 'Sector')],
                                string='Category')

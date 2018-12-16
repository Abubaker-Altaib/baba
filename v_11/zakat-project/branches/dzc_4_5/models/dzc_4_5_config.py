# -*- coding: utf-8 -*-

import re
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError


class dzc_4_5Places_of_worship(models.Model):
    _name = 'dzc_4_5.places.of.worship'

    name = fields.Char(string="Worship Name")
    type = fields.Selection([('khalwa', 'Khalwa'), ('masjid', 'Masjid'), ('place worship', 'Place Worship'),
                             ('place house', 'Place House')])
    date_of_establish = fields.Date(string="Date of Establish")
    state_id = fields.Many2one('zakat.state', string="State")
    local_state_id = fields.Many2one('zakat.local.state', string="Local State")
    supervisor = fields.Char(string='Supervisor')
    supervisor_national_number = fields.Char(string="Supervisor National Number")
    responsible = fields.Char(string='Responsible')
    responsible_national_number = fields.Char(string="Responsible National Number")
    support_type = fields.Selection([('emergency', 'Emergency'), ('periodic', 'Periodic')])
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user,
                              ondelete='restrict')
    pre_support = fields.Boolean(string="Has previous Support?", default=False)
    property_account_id = fields.Many2one('account.account', ondelete="restrict", string="Account",
                                          company_dependent=True)
    property_analytic_account_id = fields.Many2one('account.analytic.account', ondelete="restrict",
                                                   string="Analytic Account", company_dependent=True)
    property_journal_id = fields.Many2one('account.journal', ondelete="restrict", string="Journal",
                                          company_dependent=True)
    khalwa_size = fields.Selection([('small', 'Small'), ('large', 'Large')])
    khalwa_system = fields.Selection([('internal', 'Internal'), ('external', 'External')])
    no_shikh = fields.Integer(string="No Shikh")
    no_students = fields.Integer(string="No Students")
    owner = fields.Char(string='Kalwa Owner')

    @api.constrains('name')
    def check_name(self):
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('name Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))

    @api.constrains('supervisor')
    def check_supername(self):
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.supervisor.replace(" ", "")):
            raise ValidationError(_('supervisor Field must be Literal'))
        if self.supervisor and (len(self.supervisor.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("supervisor must not be spaces"))
        if self.supervisor and (len(self.supervisor.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("supervisor must not be spaces"))

    @api.constrains('responsible')
    def check_respons_name(self):
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.responsible.replace(" ", "")):
            raise ValidationError(_('responsible Field must be Literal'))
        if self.responsible and (len(self.responsible.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("responsible must not be spaces"))
        if self.responsible and (len(self.responsible.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("responsible must not be spaces"))

    @api.constrains('supervisor_national_number', 'responsible_national_number')
    def checks_Id_number(self):

        pattern = re.compile(r'^[0]\d{9,9}$')
        if self.supervisor_national_number != False:
            if 11 < len(self.supervisor_national_number) or 11 > len(self.supervisor_national_number):
                raise exceptions.ValidationError(_('ID Number must be at least 11 Numbers.'))
        if self.responsible_national_number != False:
            if 11 < len(self.responsible_national_number) or 11 > len(self.responsible_national_number):
                raise exceptions.ValidationError(_('ID Number must be at least 11 Numbers.'))

    @api.constrains('date_of_establish')
    def validate_date(self):
        if self.date_of_establish > str(datetime.today()):
            raise ValidationError(_("Date of Establish Must be previous date."))

    @api.constrains('no_shikh', 'no_students')
    def validate_nums(self):
        if self.type == 'khalwa':
            if self.no_shikh <= 0:
                raise ValidationError(_("No of shiekh must be greater than zero"))
            if self.no_students <= 0:
                raise ValidationError(_("No of students must be greater than zero"))


# DAWA Axis model
class DawaAxis(models.Model):
    _name = 'dawa.axis'
    name = fields.Char(string='Name')
    activitiy_ids = fields.One2many(comodel_name='dawa.axis.sub', inverse_name='dawa_axis_id', string='Activitis')
    journal_id = fields.Many2one('account.journal', string='Journal ID', company_dependent=True)
    property_account_id = fields.Many2one('account.account', string='Account ID', company_dependent=True)
    property_analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account",
                                                   company_dependent=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')

    @api.constrains('name', 'activitiy_ids')
    def check_name(self):
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('name Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
        if not self.activitiy_ids:
            raise ValidationError('Sorry! you must add atleast one Activity ')


class DawaAxisSub(models.Model):
    _name = 'dawa.axis.sub'
    dawa_axis_id = fields.Many2one('dawa.axis')
    name = fields.Char(string='Name')
    account = fields.Many2one('account.account', string='Account')

    @api.constrains('name')
    def check_name(self):
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('name Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        if self._context.get('axis_context', []):
            state_plan = self.env['dzc_4_5.dawa.activities.plan'].resolve_2many_commands('activities_ids',
                                                                                         self._context.get(
                                                                                             'axis_context', []))
            args.append(('id', 'not in',
                         [isinstance(d['activity_id'], tuple) and d['activity_id'][0] or d['activity_id']
                          for d in state_plan]))

        return super(DawaAxisSub, self).name_search(name, args=args, operator=operator, limit=limit)

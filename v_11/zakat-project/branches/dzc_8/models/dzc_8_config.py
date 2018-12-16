# -*- coding: utf-8 -*-

import re
from datetime import datetime
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError


# Transport state fees 
class TransportStateFees(models.Model):
    _name = 'dzc8.transport.state.fees'

    name = fields.Char(string="Name")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, ondelete='restrict')
    company_id = fields.Many2one("res.company", default=lambda self: self.env.user.company_id, string="Company",
                                 ondelete='cascade')
    transport_fees = fields.Monetary(string='Transport Fees', currency_field='currency_id')
    transport_company_id = fields.Many2one('dzc8.transport.company', ondelete="restrict")

    @api.constrains('name')
    def check_name(self):
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('Name Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("Name must not be Spaces"))

    @api.constrains('transport_fees')
    def _check_fees(self):
        if self.transport_fees <= 0.0:
            raise ValidationError(_('Sorry! Fees Cannot Be Zero or Less.'))


class TransportCompany(models.Model):
    _name = 'dzc8.transport.company'

    name = fields.Char(string='Company Name')
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, readonly=True,
                              ondelete='restrict')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    source_id = fields.Many2one('zakat.state', string="Source")
    state_fees_ids = fields.One2many('dzc8.transport.state.fees', 'transport_company_id',
                                     string="Destinations & Fees")
    property_zakat_account_id = fields.Many2one('account.account', ondelete="restrict", string="Zakat Account",
                                                company_dependent=True)
    property_analytic_account_id = fields.Many2one('account.analytic.account', ondelete="restrict",
                                                   string="Analytic Account",
                                                   company_dependent=True)
    zakat_journal = fields.Many2one('account.journal', ondelete="restrict", string="Zakat Journal",
                                    company_dependent=True)
    _sql_constraints = [
        ('unique_company', 'unique(name, company_id)', 'Sorry ! Transport Company name must be unique. ')]

    @api.model
    def create(self, vals):
        """
        :param vals: field value in view
        :raise: exception if state_fees_ids null
        """
        if 'state_fees_ids' not in vals:
            raise exceptions.ValidationError(_("Please Add one Destination at Least Cannot Be Empty"))
        return super(TransportCompany, self).create(vals)

    @api.constrains('name')
    def check_name(self):
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('Name Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("Name must not be Spaces"))

    @api.multi
    def unlink(self):
        """
        Prevent delete if record still reference in order of iban alsabil
        :raise exceptions
        """
        for record in self.env['zakat.dzc8'].search([]):
            if record.transport_company.id in self.ids:
                raise exceptions.ValidationError(_("Transport Company Could not Be Removed it Linked with an Order"))
            else:
                return super(TransportCompany, self).unlink()

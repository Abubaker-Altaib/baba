# -*- coding: utf-8 -*-

import re
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError


class dzc_7Maytr(models.Model):
    _name = 'dzc_7.maytr'

    name = fields.Char(string='Name', related='partner_id.name', store=True, )
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    partner_id = fields.Many2one('res.partner', string="Beneficiary Name")
    type = fields.Selection([('maytr', 'Maytr'), ('mujahid', 'Mujahid')], default="Mujahid")
    date_of_death = fields.Date(string="Date of Death")
    no_families = fields.Integer(string="No Families")
    national_number = fields.Char(string='National Number', related='partner_id.national_number', store=True, )
    state_id = fields.Many2one(string='State', related='partner_id.zakat_state', store=True, )

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        show only illness that is not selected
        :return: list of ids
        """
        if self._context.get('myter', []):
            illness_id = self.env['maytr.family.support'].resolve_2many_commands('lines_ids',
                                                                                 self._context.get('myter', []))
            args.append(('id', 'not in',
                         [isinstance(d['maytr_id'], tuple) and d['maytr_id'][0] or d['maytr_id']
                          for d in illness_id]))
        return super(dzc_7Maytr, self).name_search(name, args=args, operator=operator, limit=limit)

    _sql_constraints = [
        ('maytr_id_uniq', 'unique (partner_id)',
         'This Maytr already Exist !')
    ]

    @api.constrains('date_of_death')
    def validate_death_date(self):
        if self.type == 'maytr':
            if self.date_of_death > str(datetime.today()):
                raise ValidationError(_("Sorry! Death Date Cannot be Later Than today"))

    @api.constrains('no_families')
    def no_family_validate(self):
        if self.no_families < 0:
            raise ValidationError(_("Sorry! No of Families Cannot be negative"))

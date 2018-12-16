# -*- coding: utf-8 -*-
# Copyright 2018, AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models,api, exceptions,_
import re
from odoo.exceptions import ValidationError, AccessError 
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta

class dzc6GormTypes(models.Model):
    _name = 'dzc_6.gorm.types'

    name = fields.Char(string='Name')
    persentage = fields.Float(string="Persentage")
    t_to_state = fields.Boolean(string="Transferable to the State")
    amount = fields.Float(string="Amount")
   
    property_account_id = fields.Many2one('account.account', ondelete="restrict", string="Account", company_dependent=True)
    property_analytic_account_id = fields.Many2one('account.analytic.account', ondelete="restrict", string="Analytic Account",company_dependent=True)
    property_journal_id = fields.Many2one('account.journal', ondelete="restrict", string="Journal", company_dependent=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
    @api.constrains('name')
    def check_name(self):
        if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.name.replace(" ","")):
            raise ValidationError(_('name Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
   
    @api.constrains('amount' , 'persentage')
    def validate_amount(self):
        if self.t_to_state == True:
            if self.amount <= 0.0 :
                raise ValidationError(_("Amount Cannot be zero or Negative"))
        if self.persentage <= 0.0:
            raise ValidationError(_("Persentage Cannot be zero or Negative"))
        if self.persentage > 100.0:
            raise ValidationError(_("Persentage Cannot be greater than 100"))

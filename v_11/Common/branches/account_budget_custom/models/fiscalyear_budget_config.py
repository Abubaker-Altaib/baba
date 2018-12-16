import re
from odoo import api, fields, models, exceptions,_
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
import time


class AccountBudgetConfig(models.Model):
    _name = 'fiscalyear.budget.config'

    months = fields.Char(string="Months Number")
    name = fields.Char(string="Name")

    @api.constrains('months', 'name')
    def fields_check(self):
        if not re.match("^[0-9]*$", self.months.replace(" ", "")):
            raise ValidationError(_('Months field must be number'))
        if self.months.replace(" ", "") != self.months:
            raise ValidationError(_('Months field must be number'))
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('Budget name field must be literal'))
        if self.months == '0':
            raise exceptions.ValidationError(_("Months number cannot be zero"))
        if self.months:
            if int(self.months) > 12:
                raise exceptions.ValidationError(_("Months number cannot be More Than 12 Months"))




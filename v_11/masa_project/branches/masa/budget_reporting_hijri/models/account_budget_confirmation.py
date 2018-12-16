# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields
from odoo.addons.hijri_datepicker.models import date_log
from datetime import datetime

class AccountBudgeConfirmationt(models.Model):
    _inherit = "account.budget.confirmation"

    def gregorian_to_hijri(self,date):
        date = fields.Date.from_string(date)
        dec = date_log.gregorian_to_hijri(self,date)
        if dec:
        	return dec['year']+ '/' + dec['month'] +'/' +dec['day']
        return ""





# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api, models, fields
from odoo.addons.hijri_datepicker.models import date_log
from datetime import datetime

class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def gregorian_to_hijri(self,date):
        date = fields.Date.from_string(date)
        dec = date_log.gregorian_to_hijri(self,date)
        if dec:
        	return dec['year']+ '/' + dec['month'] +'/' +dec['day']
        return ""







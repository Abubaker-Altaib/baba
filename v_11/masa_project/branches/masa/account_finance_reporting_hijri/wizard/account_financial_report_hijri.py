# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.hijri_datepicker.models import date_log
from datetime import datetime
class AccountingReport(models.TransientModel):
    _inherit = ['accounting.report']


    date_option = fields.Selection([
        ('greg', 'Gregorian'),
        ('isl', 'Islamic'),
        ('both', 'Both'),],string='Date Option',default='greg',required=True,)

    def gregorian_to_hijri(self,date):
        date = fields.Date.from_string(date)
        dec = date_log.gregorian_to_hijri(self,date)
        return dec['year']+ '/' + dec['month'] +'/' +dec['day']

    def _print_report(self, data):
        data['form'].update(self.read(['date_option',])[0])
        return super(AccountingReport,self)._print_report(data)

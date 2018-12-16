# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import models, fields, api , _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError
from odoo.addons.hijri_datepicker.models import date_log
from datetime import datetime

class BudgetReportComparison(models.TransientModel):
    _inherit = 'budget.custom.report.comparison'
    #Used in wizard to choose date type in reports
    date_option = fields.Selection([
        ('greg', 'Gregorian'),
        ('isl', 'Islamic'),
        ('both', 'Both'),],string='Date Option',default='greg',required=True,)

    def print_report(self):
        data = {}

        data.update({'date_option': self.date_option})
        return super(BudgetReportComparison,self).print_report(data)

    def gregorian_to_hijri(self,date):
        date = fields.Date.from_string(date)
        dec = date_log.gregorian_to_hijri(self,date)
        return dec['year']+ '/' + dec['month'] +'/' +dec['day']

class BudgetReportComparison11(models.TransientModel):
    _inherit = 'budget.custom.report'


    def gregorian_to_hijri(self,date):
        """
        :param date: string off gregorian date
        :return: string off hijry date
        :rtype: string
        """
        date = fields.Date.from_string(date)
        dec = date_log.gregorian_to_hijri(self,date)
        return dec['year']+ '/' + dec['month'] +'/' +dec['day']
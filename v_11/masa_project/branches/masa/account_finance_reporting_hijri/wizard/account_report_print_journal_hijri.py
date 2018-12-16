# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import fields, models


class AccountPrintJournal(models.TransientModel):
    _inherit = "account.print.journal"
    _description = "Account Print Journal Hijri"

    date_option = fields.Selection([
        ('greg', 'Gregorian'),
        ('isl', 'Islamic'),
        ('both', 'Both'),],string='Date Option',default='greg',required=True,)

    def gregorian_to_hijri(self,date):
        date = fields.Date.from_string(date)
        dec = date_log.gregorian_to_hijri(self,date)
        return dec['year']+ '/' + dec['month'] +'/' +dec['day']

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'date_option': self.date_option})
        return self.env.ref('account_finance_reporting.action_report_journal_custom').with_context(landscape=True).report_action(self, data=data)

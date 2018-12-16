# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.addons.hijri_datepicker.models import date_log
from datetime import datetime

class AccountReportAccountStatement(models.TransientModel):
    _inherit = "account.report.account.statement"
    _description = "Account Statement Report Hijri"

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
        data['form'].update(self.read(['initial_balance', 'sortby', 'account_id', 'partner_id','date_option'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        records = self.env[data['model']].browse(data.get('ids', []))
    
        return  self.env.ref('account_finance_reporting.action_report_account_statement').report_action(records, data=data)

    
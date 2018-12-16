# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountReportanalyticStatement(models.TransientModel):
    _inherit = "account.common.account.report"
    _name = "account.report.analytic.statement"
    _description = "Analytic Account Statement Report"

    initial_balance = fields.Boolean(string='Include Initial Balances',
                                    help='If you selected date, this field allow you to add a row to display the amount of debit/credit/balance that precedes the filter you\'ve set.', default=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account' ,domain="[('type', '=', 'normal')]", required=True)
    sortby = fields.Selection([('sort_date', 'Date'), ('sort_journal_partner', 'Journal & Partner')], string='Sort by', required=True, default='sort_date')


    def _print_report(self, data):

        data = self.pre_print_report(data)
        data['form'].update(self.read(['initial_balance', 'sortby', 'analytic_account_id'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        records = self.env[data['model']].browse(data.get('ids', []))

        return self.env.ref('account_finance_reporting.action_report_analytic_statement').report_action(records, data=data)

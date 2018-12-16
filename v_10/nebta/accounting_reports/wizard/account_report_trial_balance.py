# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountBalanceReport(models.TransientModel):
    _inherit = "account.common.account.report"
    _name = 'account.balance.report'
    _description = 'Trial Balance Report'

    journal_ids = fields.Many2many('account.journal', 'account_balance_report_journal_rel', 'account_id', 'journal_id', string='Journals', required=True, default=[])
    company_id = fields.Many2one('res.company', string='Company', required=True,
default=lambda self: self.env['res.company']._company_default_get('account.account'))

    def _print_report(self, data):
        data = self.pre_print_report(data)
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].get_action(records, 'accounting_reports.report_trialbalance_custom', data=data)

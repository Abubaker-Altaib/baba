# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class AccountingReport(models.TransientModel):
    _inherit = ['accounting.report']


    _description = "Accounting Financial Reports"

    cash_flow_template = fields.Boolean(string="Cash Flow Statement")
    owner_equity = fields.Boolean(string="Change Owner Equity")
    income_activity = fields.Boolean(string="Income and activity")
    with_details = fields.Boolean(string="With Details")

    def _build_init_context(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        if data['form']['filter_cmp'] == 'filter_date':            
            result['date_to'] = (datetime.strptime(data['form']['date_from_cmp'], '%Y-%m-%d').date() - timedelta(days=1)).strftime('%Y-%m-%d')
            result['strict_range'] = True
        return result

    @api.multi
    def check_report(self):
        res = super(AccountingReport, self).check_report()
        data = {}
        data['form'] = self.read(['account_report_id', 'date_from_cmp', 'date_to_cmp', 'journal_ids', 'filter_cmp', 'target_move'])[0]
        for field in ['account_report_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]

        comparison_context = self._build_comparison_context(data)
        res['data']['form']['comparison_context'] = comparison_context

        init_context = self._build_init_context(data)
        res['data']['form']['init_context'] = init_context
        return res

    def _print_report(self, data):
        data['form'].update(self.read(['date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter', 'target_move', 'owner_equity', 'cash_flow_template', 'income_activity', 'with_details'])[0])
        return self.env.ref('account_finance_reporting.action_report_financial_custom').report_action(self, data=data, config=False)

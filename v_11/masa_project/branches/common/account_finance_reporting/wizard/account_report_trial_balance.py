# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountBalanceReport(models.TransientModel):
    _inherit = "account.common.account.report"
    _name = 'account.balance.report'
    _description = 'Trial Balance Report'

    level = fields.Integer(string ="level")

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update(self.read(['level'])[0])
        if  not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        records = self.env[data['model']].browse(data.get('ids', []))
        print ('self.env trial', self.env.ref('account_finance_reporting.action_report_trial_balance_custom'))
        return self.env.ref('account_finance_reporting.action_report_trial_balance_custom').report_action(records, data=data)

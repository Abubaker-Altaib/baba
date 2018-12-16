# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReportTrial(models.AbstractModel):
    _inherit = 'report.account.report_trialbalance'
  
    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        display_account = data['form'].get('display_account')
        parent_account_id = data['form'].get('parent_account_id',False)

        if parent_account_id:
            accounts = docs if self.model == 'account.account' else self.env['account.account'].search([('parent_id','=',parent_account_id[0])])
            if not accounts:
                raise UserError(_("this parent Account has not any chailds accounts, this report cannot be printed."))
        else:
            accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account)
        
        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'Accounts': account_res,
        }

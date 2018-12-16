# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


# ---------------------------------------------------------
# Account Financial Report
# ---------------------------------------------------------


class AccountFinancialReport(models.Model):
    _inherit = "account.financial.report"
    description = "Account Report"

#Use for cash flow
    returned_value = fields.Selection([
        ('debit', 'Debit'),
        ('credit', 'Credit'),
        ('balance', 'Balance')
        ], 'Returned Value', default='balance')
    detail_number = fields.Integer('Detail Number')
#Used fo owner equity
    colomn_order = fields.Selection([
        ('first', 'First'),
        ('second', 'Second'),
        ('third', 'Third'),
        ('fourth', 'Fourth')
        ], 'Colomn Order')











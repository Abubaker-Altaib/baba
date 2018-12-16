# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields

# ---------------------------------------------------------
# Account
# ---------------------------------------------------------

class AccountAccount(models.Model):

    _inherit = "account.account"
    description = "Account Report"


    cash_flow = fields.Boolean(string="Cash Flow Statement")
    returned_value = fields.Selection([
        ('debit', 'Debit'),
        ('credit', 'Credit'),
        ('balance', 'Balance')
        ], 'Returned Value', default='balance')

    cashflow_type = fields.Selection([
        ('operation', 'Operational Activities'),
        ('investment', 'Investment Activities'),
        ('financing', 'Financing Activities'),
    ],'Cash Flow Type' )


# ---------------------------------------------------------
# Company
# ---------------------------------------------------------

class ResCompany(models.Model):
    _inherit = "res.company"

    identical_chart_of_account = fields.Boolean(string="Identical Chart Of Accounts")

# ---------------------------------------------------------
# Account Financial Report
# ---------------------------------------------------------


class AccountFinancialReport(models.Model):
    _inherit = "account.financial.report"
    description = "Account Report"


    returned_value = fields.Selection([
        ('debit', 'Debit'),
        ('credit', 'Credit'),
        ('balance', 'Balance')
        ], 'Returned Value', default='balance')

    cash_flow = fields.Boolean(string="Cash Flow Statement")
    detail_number = fields.Integer('Detail Number')

    @api.multi
    def prepare_cash_flow(self):
	#search process

        
	operation_acc_list = self.env['account.account'].search([('cash_flow', '=', True), ('cashflow_type', '=', 'operation')])
        value_operation = dict(self.env['account.account']._fields['cashflow_type'].selection)['operation']
        account_report_operation = self.search([('name', '=like', value_operation)])
        print 'account_report_operation>>>>>>>>', account_report_operation
        list_oper_acc_ids = []
        for record in operation_acc_list:
            list_oper_acc_ids.append(record.id)
        print'>>>>list_oper_acc_ids', list_oper_acc_ids

        invest_acc_list = self.env['account.account'].search([('cash_flow', '=', True), ('cashflow_type', '=', 'investment')])
        value_investment = dict(self.env['account.account']._fields['cashflow_type'].selection)['investment']
        account_report_investment = self.search([('name', '=like', value_investment)])
        print'account_report_investment>>>>>>>>',account_report_investment
        list_invs_acc_ids = []
        for record in invest_acc_list:
            list_invs_acc_ids.append(record.id)
        print'>>>>list_invest_acc_ids>>>>>>>>', list_invs_acc_ids


        financing_acc_list = self.env['account.account'].search([('cash_flow', '=', True), ('cashflow_type', '=', 'financing')])
        value_financing = dict(self.env['account.account']._fields['cashflow_type'].selection)['financing']
        account_report_financing = self.search([('name', '=like', value_financing)])
        print 'ccount_report_financing', account_report_financing
        list_financing_acc_ids = []
        for record in financing_acc_list:
            list_financing_acc_ids.append(record.id)
        print'>>>>list_finance_acc_ids', list_financing_acc_ids

        

        account_report_operation.account_ids = self.env['account.account'].search ([('id', 'in', list_oper_acc_ids)])
        account_report_investment.account_ids = self.env['account.account'].search ([('id', 'in', list_invs_acc_ids)])
        account_report_financing.account_ids = self.env['account.account'].search ([('id', 'in', list_financing_acc_ids)])
        












# -*- coding: utf-8 -*-

import time
from odoo import api, models


class ReportTrialBalance(models.AbstractModel):
    _name = 'report.accounting_reports.report_trialbalance_custom'

    def _get_accounts(self, accounts, display_account, company_id):
        """ compute the balance, debit and credit for the provided accounts
            :Arguments:
                `accounts`: list of accounts record,
                `display_account`: it's used to display either all accounts or those accounts which balance is > 0
            :Returns a list of dictionary of Accounts with following key and value
                `name`: Account name,
                `code`: Account code,
                `credit`: total amount of credit,
                `debit`: total amount of debit,
                `balance`: total amount of balance,
        """

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"','')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)

        # compute the balance, debit and credit for the provided accounts
        identical_COA = self.env['res.company'].browse(self.env['res.company']._company_default_get('report.accounting_reports.report_trialbalance_custom')).id.identical_chart_of_account

        if  identical_COA == True:
                filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
                print 'identical True'
		request = ("SELECT MIN(account_id) AS id, a.code AS code, SUM(l.debit) AS debit, SUM(l.credit) AS credit, (SUM(l.debit) - SUM(l.credit)) AS balance" +\
		           " FROM account_move_line l " +\
		           " LEFT JOIN account_account a ON (l.account_id=a.id)" +\
		           " LEFT JOIN account_move m ON (l.move_id=m.id)" +\
		           " WHERE l.account_id IN %s " + filters + " GROUP BY a.code")

		print'>>>>>>>>>>>>>>>>>>>>>>>>',  accounts.ids
		params = (tuple(accounts.ids),) + tuple(where_params)
		self.env.cr.execute(request, params)
		for row in self.env.cr.dictfetchall():
		    account_result[row.pop('id')] = row
        else:
                print 'identical False'
		request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
		           " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
		params = (tuple(accounts.ids),) + tuple(where_params)
		self.env.cr.execute(request, params)
		for row in self.env.cr.dictfetchall():
		    account_result[row.pop('id')] = row


        account_res = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name
            if account.id in account_result.keys():
                res['debit'] = account_result[account.id].get('balance') if account_result[account.id].get('balance') > 0 else 0.0
                res['credit'] = account_result[account.id].get('balance') if account_result[account.id].get('balance') < 0 else 0.0
                res['balance'] = account_result[account.id].get('balance')
            if display_account == 'all':
                account_res.append(res)
            if display_account in ['movement', 'not_zero'] and not currency.is_zero(res['balance']):
                account_res.append(res)
        return account_res


    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        display_account = data['form'].get('display_account')
        company_id = data['form'].get('company_id')
        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account, company_id)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': account_res,
        }
        return self.env['report'].render('accounting_reports.report_trialbalance_custom', docargs)

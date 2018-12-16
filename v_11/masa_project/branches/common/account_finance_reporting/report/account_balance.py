# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportTrialBalance(models.AbstractModel):
    _name = 'report.account_finance_reporting.report_trialbalance_custom'

    def _get_accounts(self, accounts, display_account, level):
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
        init_account_result = {}
        # Prepare initial sql query base on selected parameters from wizard 
        init_tables, init_where_clause, init_where_params = self.env['account.move.line']._query_get()
        init_tables = init_tables.replace('"','')
        init_where_clause = init_where_clause.replace('("account_move_line"."date" >= %s)','("account_move_line"."date" < %s)')
        init_wheres = [""] 
        if init_where_clause.strip():
            init_wheres.append(init_where_clause.strip())
        init_filters = " AND ".join(init_wheres)                 
        # compute the initial balance for the provided accounts
        init_request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
        " FROM " + init_tables + ", account_account AS a WHERE a.id = account_id AND account_id IN %s " + init_filters + " GROUP BY account_id")

        init_params = (tuple(accounts.ids),) + tuple(init_where_params)
        self.env.cr.execute(init_request, init_params)
        for row in self.env.cr.dictfetchall():
            init_account_result[row.pop('id')] = row
                #~~~~~~~~~~~~~~~~~~~~~~~~~ End Of Initial Balance ~~~~~~~~~~~~~~~~~~~~~~
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
        request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
                   " FROM " + tables + ", account_account AS a WHERE a.id = account_id AND account_id IN %s " + filters + " GROUP BY account_id")

        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row
        account_res = []

        acc_by_level = self.env['account.account'].with_context({'show_parent_account':True}).search([('level','=',level)])
        for account in acc_by_level:
            sub_accounts = self.env['account.account'].with_context({'show_parent_account':True}).search([('id','child_of',[account.id])])            
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance', 'init_debit', 'init_credit', 'init_balance', 'total_debit', 'total_credit'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name
            for sub_acc in sub_accounts:
                if sub_acc.id in init_account_result :
                    res['init_debit'] += init_account_result[sub_acc.id].get('balance') if init_account_result[sub_acc.id].get('balance') > 0 else 0.0
                    res['init_credit'] += init_account_result[sub_acc.id].get('balance') if init_account_result[sub_acc.id].get('balance') < 0 else 0.0
                    res['init_balance'] += init_account_result[sub_acc.id].get('balance')
                
                if sub_acc.id in account_result:               
                    res['debit'] += account_result[sub_acc.id].get('balance') if account_result[sub_acc.id].get('balance') > 0 else 0.0
                    res['credit'] += account_result[sub_acc.id].get('balance') if account_result[sub_acc.id].get('balance') < 0 else 0.0
                    res['balance'] += account_result[sub_acc.id].get('balance')

            
                res['total_debit'] = res['init_debit'] + res['debit'] if res['init_debit'] + res['debit'] > 0 else 0.0
                res['total_credit'] = res['init_credit'] + res['credit'] if res['init_credit'] + res['credit'] < 0 else 0.0


            if display_account == 'all':
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
            
            if display_account == 'movement' and (not currency.is_zero(res['debit']) or not currency.is_zero(res['credit']) or not currency.is_zero(res['init_debit']) or not currency.is_zero(res['init_credit']) or not currency.is_zero(res['total_debit'])  or not currency.is_zero(res['total_credit'])) :
                account_res.append(res)
        return account_res


    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        display_account = data['form'].get('display_account')
        level = data['form'].get('level')
        accounts = docs if self.model == 'account.account' else self.env['account.account'].with_context({'show_parent_account':True}).search([])
        account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account, level)

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': account_res,
        }
# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportTrialBalance(models.AbstractModel):
    _name = 'report.account_finance_reporting.report_trialbalance_custom'

    def _get_accounts(self, accounts, display_account, level):
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
        init_account_result = {}
        # Prepare initial sql query base on selected parameters from wizard 
        init_tables, init_where_clause, init_where_params = self.env['account.move.line']._query_get()
        init_tables = init_tables.replace('"','')
        init_where_clause = init_where_clause.replace('("account_move_line"."date" >= %s)','("account_move_line"."date" < %s)')
        init_wheres = [""] 
        if init_where_clause.strip():
            init_wheres.append(init_where_clause.strip())
        init_filters = " AND ".join(init_wheres)                 
        # compute the initial balance for the provided accounts
        init_request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
        " FROM " + init_tables + ", account_account AS a WHERE a.id = account_id AND account_id IN %s " + init_filters + " GROUP BY account_id")

        init_params = (tuple(accounts.ids),) + tuple(init_where_params)
        self.env.cr.execute(init_request, init_params)
        for row in self.env.cr.dictfetchall():
            init_account_result[row.pop('id')] = row
                #~~~~~~~~~~~~~~~~~~~~~~~~~ End Of Initial Balance ~~~~~~~~~~~~~~~~~~~~~~
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
        request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
                   " FROM " + tables + ", account_account AS a WHERE a.id = account_id AND account_id IN %s " + filters + " GROUP BY account_id")

        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row
        account_res = []

        acc_by_level = self.env['account.account'].with_context({'show_parent_account':True}).search([('level','=',level)])
        for account in acc_by_level:
            sub_accounts = self.env['account.account'].with_context({'show_parent_account':True}).search([('id','child_of',[account.id])])            
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance', 'init_debit', 'init_credit', 'init_balance', 'total_debit', 'total_credit'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name
            for sub_acc in sub_accounts:
                if sub_acc.id in init_account_result :
                    res['init_debit'] += init_account_result[sub_acc.id].get('balance') if init_account_result[sub_acc.id].get('balance') > 0 else 0.0
                    res['init_credit'] += init_account_result[sub_acc.id].get('balance') if init_account_result[sub_acc.id].get('balance') < 0 else 0.0
                    res['init_balance'] += init_account_result[sub_acc.id].get('balance')
                
                if sub_acc.id in account_result:               
                    res['debit'] += account_result[sub_acc.id].get('balance') if account_result[sub_acc.id].get('balance') > 0 else 0.0
                    res['credit'] += account_result[sub_acc.id].get('balance') if account_result[sub_acc.id].get('balance') < 0 else 0.0
                    res['balance'] += account_result[sub_acc.id].get('balance')

            
                res['total_debit'] = res['init_debit'] + res['debit'] if res['init_debit'] + res['debit'] > 0 else 0.0
                res['total_credit'] = res['init_credit'] + res['credit'] if res['init_credit'] + res['credit'] < 0 else 0.0


            if display_account == 'all':
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
            
            if display_account == 'movement' and (not currency.is_zero(res['debit']) or not currency.is_zero(res['credit']) or not currency.is_zero(res['init_debit']) or not currency.is_zero(res['init_credit']) or not currency.is_zero(res['total_debit'])  or not currency.is_zero(res['total_credit'])) :
                account_res.append(res)
        return account_res


    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        display_account = data['form'].get('display_account')
        level = data['form'].get('level')
        accounts = docs if self.model == 'account.account' else self.env['account.account'].with_context({'show_parent_account':True}).search([])
        account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account, level)

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': account_res,
        }


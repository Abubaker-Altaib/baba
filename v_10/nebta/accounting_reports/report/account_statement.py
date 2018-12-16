# -*- coding: utf-8 -*-

import time
from odoo import api, models


class ReportAccountStatement(models.AbstractModel):
    _name = 'report.accounting_reports.report_account_statement'

    def get_initial_balance(self, init_balance, account_id):

        print 'account_id>>>>>>>>>>>>>>>>>>>>>', account_id[0]
        cr = self.env.cr
        MoveLine = self.env['account.move.line']

        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=self.env.context.get('date_from'), date_to=False, initial_bal=True)._query_get()
            print 'init_tables', init_tables
            print 'init_where_clause',init_where_clause
            print 'init_where_params', init_where_params
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            print 'init_filters', init_filters
                 
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            print 'filters', filters
            date_from = self.env.context.get('date_from')
            print 'date_from', date_from
            sql = ("""SELECT  COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as initial_balance\
                FROM account_move_line l\
                LEFT JOIN account_move m ON (l.move_id=m.id)\
		LEFT JOIN account_account a ON (l.account_id=a.id)\
                WHERE l.account_id = %s""" + filters + ' GROUP BY l.account_id')
            params = (account_id[0],) + tuple(init_where_params)
            print 'params>>>>>>>>>>>>>>>>', params
            cr.execute(sql, params)
            initial_balance = cr.fetchone()[0] or 0.0
           
            print 'initial_balance', initial_balance
            return initial_balance


    def _get_account_move_entry(self, accounts, init_balance, sortby, account_id):
        """
        :param:
                accounts: the recordset of accounts
                init_balance: boolean value of initial_balance
                sortby: sorting by date or partner and journal


        Returns a dictionary of accounts with following key and value {
                'code': account code,
                'name': account name,
                'debit': sum of total debit amount,
                'credit': sum of total credit amount,
                'balance': total balance,
                'amount_currency': sum of amount_currency,
                'move_lines': list of move line
        }
        """

        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = dict(map(lambda x: (x, []), accounts.ids))

        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines

        sql = ('''SELECT  l.date AS ldate, j.code AS journal, l.ref AS lref, l.name AS lname, m.name AS move_name, COALESCE(l.debit,0.0) AS debit, COALESCE(l.credit,0.0) AS credit, COALESCE(l.debit,0.0) - COALESCE(l.credit, 0.0) AS balance, p.name AS partner_name\
            FROM account_move_line l\
            JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            WHERE l.account_id = %s ''' + filters + ''' ORDER BY ''' + sql_sort)
        params = (account_id[0],) + tuple(where_params)
        cr.execute(sql, params)
        account_res = []
        account_res = cr.dictfetchall()
        self.sum_debit = 0.0
        self.sum_credit = 0.0
        self.account_sum = 0.0
        for l in account_res:
            
            l['credit'] = l['credit'] == 'None' and 0 or l['credit']
            l['debit'] = l['debit'] == 'None' and 0 or l['debit']
            self.sum_credit += l['credit']
            self.sum_debit += l['debit']
            self.account_sum += l['debit'] - l['credit']
            l['progress'] = self.account_sum
        ''''
        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)
        print 'move_lines>>>>>>>>>>>>', move_lines
        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
        '''
        print 'account_res >>>', account_res
        return account_res

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))

        init_balance = data['form'].get('initial_balance', True)
        sortby = data['form'].get('sortby', 'sort_date')
        #display_account = data['form']['display_account']
        account_id = data['form']['account_id']
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]

        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        accounts_res = self.with_context(data['form'].get('used_context',{}))._get_account_move_entry(accounts, init_balance, sortby, account_id)
        print 'accounts_res', accounts_res
        report_initial_balance = self.with_context(data['form'].get('used_context',{})).get_initial_balance(init_balance, account_id) or 0.0
        print 'report_initial_balance', report_initial_balance
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': accounts_res,
            'print_journal': codes,
            'get_initial_balance': report_initial_balance,

        }
        return self.env['report'].render('accounting_reports.report_account_statement', docargs)

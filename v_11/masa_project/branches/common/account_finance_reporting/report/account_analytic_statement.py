# -*- coding: utf-8 -*-

import time
from odoo import api, models


class ReportAnalyticStatement(models.AbstractModel):
    _name = 'report.account_finance_reporting.report_analytic_custom'

    def get_initial_balance(self, init_balance, analytic_account_id):

        cr = self.env.cr
        MoveLine = self.env['account.move.line']

        # Prepare initial sql query and Get the initial move lines
        if init_balance == True:
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=self.env.context.get('date_from'), date_to=False, initial_bal=True)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            date_from = self.env.context.get('date_from')
            sql = ("""SELECT  COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as initial_balance\
                FROM account_move_line l\
                LEFT JOIN account_move m ON (l.move_id=m.id)\
		LEFT JOIN account_analytic_account a ON (l.analytic_account_id=a.id)\
                WHERE l.analytic_account_id = %s""" + filters + ' GROUP BY l.analytic_account_id')
            params = (analytic_account_id[0],) + tuple(init_where_params)
            cr.execute(sql, params)
            result = cr.fetchone()
            if result is not None:
                initial_balance = result[0] or 0.0 
                print ('--------------------initial_balance', initial_balance)
                return initial_balance


    def _get_account_move_entry(self, accounts, init_balance, sortby, analytic_account_id,partner_id):
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
        if partner_id :
            tables, where_clause, where_params = MoveLine._query_get([('partner_id', '=',partner_id [0] )])
        else :

            tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines

        sql = ('''SELECT  l.date AS ldate, j.code AS journal,a.name As account, l.ref AS lref, l.name AS lname, m.name AS move_name, COALESCE(l.debit,0.0) AS debit, COALESCE(l.credit,0.0) AS credit, COALESCE(l.debit,0.0) - COALESCE(l.credit, 0.0) AS balance, p.name AS partner_name\
            FROM account_move_line l\
            JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            LEFT JOIN account_account a ON (l.account_id=a.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            WHERE l.analytic_account_id = %s ''' + filters + ''' ORDER BY ''' + sql_sort)
        params = (analytic_account_id[0],) + tuple(where_params)
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
        print('anaaaaaaaaaaaaaaaaaaaaalytic',account_res) 
        return account_res


    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        init_balance = data['form'].get('initial_balance', True)
        sortby = data['form'].get('sortby', 'sort_date')
        analytic_account_id = data['form']['analytic_account_id']
        partner_id = data['form']['partner_id']
        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        account_res = self.with_context(data['form'].get('used_context'))._get_account_move_entry(accounts, init_balance, sortby, analytic_account_id,partner_id)
        report_initial_balance = self.with_context(data['form'].get('used_context',{})).get_initial_balance(init_balance, analytic_account_id) or 0.0

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': account_res,
            'get_initial_balance': report_initial_balance,
        }



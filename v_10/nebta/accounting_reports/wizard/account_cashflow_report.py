# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime



class AccountingCashflow(models.TransientModel):

    _inherit = ['accounting.report']


    _description = "Accounting Cashflow Report"



    cash_flow_template = fields.Boolean(string="Cash Flow Statement")
    allow_summation = fields.Boolean(string="Allow Summation")
    with_details = fields.Boolean(string="With Details")
    owner_equity = fields.Boolean(string="Change Owner Equity")



    def _get_equity_initial_balance(self):
        
            cr = self.env.cr
	    MoveLine = self.env['account.move.line']
		#move_lines = dict(map(lambda x: (x, []), accounts.ids))
	    #rint '####################### in initial '
		# Prepare initial sql query and Get the initial move lines

            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=self.env['accounting.report'].browse(self._context.get('active_id'))[0].date_from, date_to=False)._query_get()

	    #print 'init_tables', init_tables
	    print 'init_where_clause',init_where_clause
	    #print 'init_where_params', init_where_params
	    init_wheres = [""]
	    #print '####################### ', self.env['accounting.report'].browse(self._context.get('active_id'))[0].account_report_id.cash_flow

	    if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
                print 'init_wheres', init_wheres
		init_filters = " AND ".join(init_wheres)
	        print 'init_filters', init_filters
		 
	    filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            date_from = self.env['accounting.report'].browse(self._context.get('active_id'))[0].date_from      
	    print 'filters', filters
            sql = ("""SELECT  COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as equity_initial_balance\
			FROM account_move_line l\
			LEFT JOIN account_move m ON (l.move_id=m.id)\
			LEFT JOIN account_account a ON (l.account_id=a.id)\
			JOIN account_journal j ON (l.journal_id=j.id)\
			LEFT JOIN account_account_type t ON (a.user_type_id=t.id)\
			WHERE t.name = %s and (l.date <= %s) """ + filters )
	    params = ('Equity',date_from) + tuple(init_where_params)
	    print '?????????????????????????', init_where_params
	    print '7777777777777777777777777', tuple(init_where_params)
	    print 'params*************************',params
	    cr.execute(sql, params)
	    equity_initial_balance = cr.dictfetchall()
	    for row in equity_initial_balance:
	        equity_initial_balance = row['equity_initial_balance']
                print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& equity_initial_balance', equity_initial_balance
	    return equity_initial_balance

    def _get_retained_profits_initial_balance(self):
        
            cr = self.env.cr
	    MoveLine = self.env['account.move.line']
		#move_lines = dict(map(lambda x: (x, []), accounts.ids))
	    #rint '####################### in initial '
		# Prepare initial sql query and Get the initial move lines

            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=self.env['accounting.report'].browse(self._context.get('active_id'))[0].date_from, date_to=False)._query_get()
            print '_query_get()', MoveLine._query_get()
	    #print 'init_tables', init_tables
	    print 'init_where_clause',init_where_clause
	    #print 'init_where_params', init_where_params
	    init_wheres = [""]
	    #print '####################### ', self.env['accounting.report'].browse(self._context.get('active_id'))[0].account_report_id.cash_flow

	    if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
                print 'init_wheres', init_wheres
		init_filters = " AND ".join(init_wheres)
	        print 'init_filters', init_filters
		 
	    filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            date_from = self.env['accounting.report'].browse(self._context.get('active_id'))[0].date_from            
	    print 'filters', filters
            sql = ("""SELECT  COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as equity_initial_balance\
			FROM account_move_line l\
			LEFT JOIN account_move m ON (l.move_id=m.id)\
			LEFT JOIN account_account a ON (l.account_id=a.id)\
			JOIN account_journal j ON (l.journal_id=j.id)\
			LEFT JOIN account_account_type t ON (a.user_type_id=t.id)\
			WHERE t.name = %s and (l.date <= %s)""" + filters )
	    params = ('Retained profits',date_from) + tuple(init_where_params)
	    print '?????????????????????????', init_where_params
	    print '7777777777777777777777777', tuple(init_where_params)
	    print 'params*************************',params
	    cr.execute(sql, params)
	    retained_profits_initial_balance = cr.dictfetchall()
	    for row in retained_profits_initial_balance:
	        retained_profits_initial_balance = row['equity_initial_balance']
                print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& retained_profits_initial_balance', retained_profits_initial_balance
	    return retained_profits_initial_balance



    @api.multi
    def check_report(self):
        print '?????????????????????wizard', self._context.get('active_ids', False)
        res = super(AccountingCashflow, self).check_report()
        data = {}
        data['form'] = self.read(['account_report_id', 'date_from_cmp', 'date_to_cmp', 'journal_ids', 'filter_cmp', 'target_move'])[0]
        for field in ['account_report_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        comparison_context = self._build_comparison_context(data)
        res['data']['form']['comparison_context'] = comparison_context
        return res

    def _print_report(self, data):

        data['form'].update(self.read(['date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter', 'target_move', 'cash_flow_template', 'allow_summation', 'with_details', 'owner_equity'])[0])

        return self.env['report'].get_action(self, 'accounting_reports.report_cashflow', data=data)

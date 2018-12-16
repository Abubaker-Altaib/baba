# -*- coding: utf-8 -*-

import time
from odoo import api, models, _, fields
from datetime import datetime, timedelta
from babel.dates import format_datetime, format_date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools.misc import formatLang


class ReportCashflow(models.AbstractModel):
    _name = 'report.accounting_reports.report_cashflow'

    def _compute_account_balance(self, accounts):


        """ compute the balance, debit and credit for the provided accounts
        """

        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        res = {}
        for account in accounts:
            res[account.id] = dict((fn, 0.0) for fn in mapping.keys())

        if accounts:
            tables, where_clause, where_params = self.env['account.move.line']._query_get()
            #print 'get_query', self.env['account.move.line']._query_get()
            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            #print '>>>>>>>>>>>> tables = ', tables
            #print '>>>>>>>>>>>> where_clause = ', where_clause
            #print '>>>>>>>>>>>> where_params = ', where_params
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                       " FROM " + tables + \
                       " WHERE account_id IN %s " \
                            + filters + \
                       " GROUP BY account_id"
            #print '>>>>>>>>>>>> request = ', request
            params = (tuple(accounts._ids),) + tuple(where_params)
            #print '>>>>>>>>>>>> params', params
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                res[row['id']] = row


        return res

    def _compute_report_balance(self, reports):
        '''returns a dictionary with key=the ID of a record and value=the credit, debit and balance amount
           computed for this record. If the record is of type :
               'accounts' : it's the sum of the linked accounts
               'account_type' : it's the sum of leaf accoutns with such an account_type
               'account_report' : it's the amount of the related report
               'sum' : it's the sum of the children of this record (aka a 'view' record)'''

        res = {}
        
        fields = ['credit', 'debit', 'balance']
        for report in reports:
            if report.id in res:
                continue
            
            res[report.id] = dict((fn, 0.0) for fn in fields)
            if report.type == 'accounts':
                # it's the sum of the linked accounts
                res[report.id]['account'] = self._compute_account_balance(report.account_ids)
                
                for value in res[report.id]['account'].values():

                   
                    for field in fields:
                       
                        if self.env['account.account'].search([('id', '=', value.get('id'))]).returned_value == 'credit':
                            res[report.id][field] += value.get('credit')
                        elif self.env['account.account'].search([('id', '=', value.get('id'))]).returned_value == 'debit':
                            res[report.id][field] += value.get('debit')
                        else: 
                            res[report.id][field] += value.get(field)
                        
            elif report.type == 'account_type':
                # it's the sum the leaf accounts with such an account type
                accounts = self.env['account.account'].search([('user_type_id', 'in', report.account_type_ids.ids)])
                res[report.id]['account'] = self._compute_account_balance(accounts)
                for value in res[report.id]['account'].values():
                    for field in fields:
                        res[report.id][field] += value.get(field)
            elif report.type == 'account_report' and report.account_report_id:
                # it's the amount of the linked report
                res2 = self._compute_report_balance(report.account_report_id)
                for key, value in res2.items():
                    for field in fields:
                        res[report.id][field] += value[field]
            elif report.type == 'sum':
                # it's the sum of the children of this account.report
                res2 = self._compute_report_balance(report.children_ids)
                for key, value in res2.items():
                    for field in fields:
                        res[report.id][field] += value[field]

        return res

#details
    def get_account_details_lines(self, data):
        
        lines = []
        account_report = self.env['account.financial.report'].search([('id', '=', data['account_report_id'][0])])
        child_reports = account_report._get_children_by_order()
        print 'details context', data.get('used_context')
        res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports)
        for report in child_reports:
	    if data['with_details'] == True and report.detail_number > 0:
	        accounts = self.env['account.account'].search([('user_type_id', 'in', report.account_type_ids.ids)])
		res[report.id]['account'] = self.with_context(data.get('used_context'))._compute_account_balance(accounts)
		details =[]
		for value in res[report.id]['account'].values():
		    details.append({
			'name': report.name,
			'balance': res[report.id]['balance'] * report.sign,
			'type': 'report',
			'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
			'detail_name': self.env['account.account'].browse(value.get('id')).name,
			'detail_balance': value.get('balance'),
			'detail_number' :report.detail_number,
		     })      
		lines.append(details)

        return lines

# Cash Flow Statement
    def get_initial_balance(self):
        '''Get enitial balance for bank and cash at the begining of the the selected period'''


        cr = self.env.cr
        MoveLine = self.env['account.move.line']

        # Prepare initial sql query and Get the initial move lines

        init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=self.env.context.get('date_from'), date_to=False, initial_bal=True)._query_get()     
        init_wheres = [""]
        if init_where_clause.strip():
	    init_wheres.append(init_where_clause.strip())
        init_filters = " AND ".join(init_wheres)	 
        filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
    
        sql = ("""SELECT  COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as initial_balance\
	    FROM account_move_line l\
	    LEFT JOIN account_move m ON (l.move_id=m.id)\
	    LEFT JOIN account_account a ON (l.account_id=a.id)\
	    LEFT JOIN account_account_type t ON (a.user_type_id=t.id)\
	    WHERE t.type = %s""" + filters)
        params = ('liquidity',) + tuple(init_where_params)

        cr.execute(sql, params)
        initial_balance = cr.fetchone()[0] or 0.0
   
        print 'initial_balance in cash flow', initial_balance
        return initial_balance

    def get_bagining_beriod_balance(self, data):
        lines = []
        vals = {}
        account_report = self.env['account.financial.report'].search([('id', '=', data['account_report_id'][0])])

        child_reports = account_report._get_children_by_order()
        res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports)


        if  data['owner_equity']:
            print 'ownerequitu ', data.get('comparison_context')
            comparison_res = self.with_context(data.get('comparison_context'))._compute_report_balance(child_reports)
            print 'comparison_res>>>>>>>>>>>>>>>>>>>', comparison_res
            for report_id, value in comparison_res.items():
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in comparison_res[report_id].get('account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']

        for report in child_reports:
            if data['owner_equity']:
        
                for account_type in report.account_type_ids:
                    print 'res[report.id]', res[report.id]

                    if account_type.name == 'Equity':                        
                        vals['balance_capital_cmp'] =res[report.id]['comp_bal'] * report.sign

                    elif account_type.name == 'Retained profits':
                        vals['balance_income_cmp'] = res[report.id]['comp_bal'] * report.sign
                    print 'vals', vals
  	lines.append(vals)
        #print '.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.', lines
        return lines


    def get_account_lines(self, data):



        lines = []
        account_report = self.env['account.financial.report'].search([('id', '=', data['account_report_id'][0])])

        child_reports = account_report._get_children_by_order()
        print 'lines context', data.get('used_context')
        res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports)
        if data['enable_filter']:
            print 'normal ', data.get('comparison_context')
            comparison_res = self.with_context(data.get('comparison_context'))._compute_report_balance(child_reports)

            print '>>>>>>>>>>>>>>>>>>comparison_res.items()', comparison_res.items()
            for report_id, value in comparison_res.items():
                print 'report_id////////', report_id
                print 'value////////////', value
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in comparison_res[report_id].get('account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']

        for report in child_reports:

            vals = {
                'name': report.name,
                'balance': res[report.id]['balance'] * report.sign,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type or False, #used to underline the financial report balances
            }

            
            if data['debit_credit']:
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']

            if data['enable_filter']:
                vals['balance_cmp'] = res[report.id]['comp_bal'] * report.sign

	    if data['with_details'] == True and report.detail_number > 0:
                vals['detail_number'] = report.detail_number

	    if data['owner_equity'] == True:
        
                for account_type in report.account_type_ids:
                    print 'res[report.id]', res[report.id]

                    if account_type.name == 'Equity':                        
		        vals['capital_balance'] =  res[report.id]['balance'] * report.sign 
		        vals['income_balance'] = 0.0


                    elif account_type.name == 'Retained profits':
		        vals['capital_balance'] = 0.0
		        vals['income_balance'] = res[report.id]['balance'] * report.sign 

                    print 'vals', vals

  	    lines.append(vals)
	   
            if report.display_detail == 'no_detail':
                #the rest of the loop is used to display the details of the financial report, so it's not needed here.
                continue

            if res[report.id].get('account'):
                sub_lines = []


                for account_id, value in res[report.id]['account'].items():
                    #if there are accounts to display, we add them to the lines with a level equals to their level in
                    #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
                    #financial reports for Assets, liabilities...)
                    flag = False
                    account = self.env['account.account'].browse(account_id)
                    if account.returned_value == 'debit':
		            vals = {
		                'name': account.code + ' ' + account.name,
		                'balance': value['debit'] * report.sign or 0.0,
		                'type': 'account',
		                'level': report.display_detail == 'detail_with_hierarchy' and 4,
		                'account_type': account.internal_type,
		            }
                    elif account.returned_value == 'credit':
                            vals = {
		                'name': account.code + ' ' + account.name,
		                'balance': value['credit'] * report.sign or 0.0,
		                'type': 'account',
		                'level': report.display_detail == 'detail_with_hierarchy' and 4,
		                'account_type': account.internal_type,
		            }
                    else:

                            vals = {
		                'name': account.code + ' ' + account.name,
		                'balance': value['balance'] * report.sign or 0.0,
		                'type': 'account',
		                'level': report.display_detail == 'detail_with_hierarchy' and 4,
		                'account_type': account.internal_type,
		            }
           

                    if data['debit_credit']:
                        vals['debit'] = value['debit']
                        vals['credit'] = value['credit']
                        if not account.company_id.currency_id.is_zero(vals['debit']) or not account.company_id.currency_id.is_zero(vals['credit']):
                            flag = True
                    if not account.company_id.currency_id.is_zero(vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        vals['balance_cmp'] = value['comp_bal'] * report.sign
                        vals['balance_capital_cmp'] =res[report.id]['comp_bal'] * report.sign
                        vals['balance_income_cmp'] =res[report.id]['comp_bal'] * report.sign
                        if not account.company_id.currency_id.is_zero(vals['balance_cmp']):
                            flag = True


                    if flag:
                        sub_lines.append(vals)
         
                lines += sorted(sub_lines, key=lambda sub_line: sub_line['name'])
        #print 'last lines', lines
        return lines

    @api.model
    def render_html(self, docids, data=None):

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        report_lines = self.get_account_lines(data.get('form'))
        report_detail_lines =self.get_account_details_lines(data.get('form'))
        report_begining_balance_lines = self.get_bagining_beriod_balance(data.get('form'))
        cashflow_initial_balance = self.with_context(data['form'].get('used_context',{})).get_initial_balance() or 0.0
        print 'cashflow_initial_balance', cashflow_initial_balance
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_account_lines': report_lines,
            'get_account_details_lines' : report_detail_lines,
            'get_bagining_beriod_balance':report_begining_balance_lines,
            'get_initial_balance': cashflow_initial_balance,
        }
        return self.env['report'].render('accounting_reports.report_cashflow', docargs)

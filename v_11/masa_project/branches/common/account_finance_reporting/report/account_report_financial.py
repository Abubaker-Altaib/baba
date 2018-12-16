# -*- coding: utf-8 -*-

import time
from odoo import api, models, _, fields
from odoo.exceptions import UserError


class ReportFinancial(models.AbstractModel):
    _name = 'report.account_finance_reporting.report_financial_custom'

    def _compute_account_balance(self, accounts, income_activity):
        """ compute the balance, debit and credit for the provided accounts
        """
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        res = {}
        result = {}
        for account in accounts:
            res[account.id] = dict.fromkeys(mapping, 0.0)
            if income_activity == True:
                res[account.id].update({'restricted_balance':  0.0,'unrestricted_balance':  0.0, 'awqaf_balance':  0.0})
        if accounts:
            tables, where_clause, where_params = self.env['account.move.line']._query_get()
            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                       " FROM " + tables + \
                       " WHERE account_id IN %s " \
                            + filters + \
                       " GROUP BY account_id"
            params = (tuple(accounts._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                if income_activity == True:
                    res[row['id']].update(row)
                else:
                    res[row['id']] = row
            # Used for income activity report, calculate balance accourding to analytic account cost type (reatricted, unreatricted, awqaf)
            ## query for calculating reatricted balance
            if income_activity == True:
                    restrec_res = {}
                    unrestrec_res = {}
                    awqaf_res = {}
                    activity_filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
                    restricted_request = "SELECT account_id as id, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as restricted_balance" + \
		               " FROM account_move_line l " +\
			       " LEFT JOIN account_account a ON (l.account_id=a.id)" +\
			       " LEFT JOIN account_move m ON (l.move_id=m.id)" +\
		               " LEFT JOIN account_analytic_account an ON (l.analytic_account_id=an.id)" +\
		               " WHERE l.account_id IN %s AND an.cost_type = %s" \
		                    + activity_filters + \
		               " GROUP BY account_id"
                    params = (tuple(accounts._ids),'restricted') + tuple(where_params)
                    self.env.cr.execute(restricted_request, params)
                    for re_row in self.env.cr.dictfetchall():
                       restrec_res[re_row['id']] = re_row             
                       if re_row['id'] in res.keys():
                           res[re_row['id']].update({'restricted_balance': restrec_res[re_row['id']].get('restricted_balance')})

		    ## query for calculating unreatricted balance
                    unrestricted_request = "SELECT account_id as id, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as unrestricted_balance" + \
		               " FROM account_move_line l " +\
			       " LEFT JOIN account_account a ON (l.account_id=a.id)" +\
			       " LEFT JOIN account_move m ON (l.move_id=m.id)" +\
		               " LEFT JOIN account_analytic_account an ON (l.analytic_account_id=an.id)" +\
		               " WHERE l.account_id IN %s AND an.cost_type = %s" \
		                    + activity_filters + \
		               " GROUP BY account_id"
                    params = (tuple(accounts._ids),'unrestricted') + tuple(where_params)
                    self.env.cr.execute(unrestricted_request, params)
                    for unre_row in self.env.cr.dictfetchall():
                       unrestrec_res[unre_row['id']] = unre_row
                       if unre_row['id'] in res.keys():
                           res[unre_row['id']].update({'unrestricted_balance': unrestrec_res[unre_row['id']].get('unrestricted_balance') or 0.0})
		          
		    ## query for calculating awqaf balance
                    awqaf_request = "SELECT account_id as id, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as awqaf_balance" + \
		               " FROM account_move_line l " +\
			       " LEFT JOIN account_account a ON (l.account_id=a.id)" +\
			       " LEFT JOIN account_move m ON (l.move_id=m.id)" +\
		               " LEFT JOIN account_analytic_account an ON (l.analytic_account_id=an.id)" +\
		               " WHERE l.account_id IN %s AND an.cost_type = %s" \
		                    + activity_filters + \
		               " GROUP BY account_id"
                    params = (tuple(accounts._ids),'awqaf') + tuple(where_params)
                    self.env.cr.execute(awqaf_request, params)
                    for awq_row in self.env.cr.dictfetchall():
                       awqaf_res[awq_row['id']] = awq_row
                       if awq_row['id'] in res.keys():
                           res[awq_row['id']].update({'awqaf_balance': awqaf_res[awq_row['id']].get('awqaf_balance') or 0.0})
                    result = res
            else:
                result = res
        return result

    def _compute_report_balance(self, reports, income_activity):
        '''returns a dictionary with key=the ID of a record and value=the credit, debit and balance amount
           computed for this record. If the record is of type :
               'accounts' : it's the sum of the linked accounts
               'account_type' : it's the sum of leaf accoutns with such an account_type
               'account_report' : it's the amount of the related report
               'sum' : it's the sum of the children of this record (aka a 'view' record)'''
        res = {}
        if income_activity == True:
            fields = ['credit', 'debit', 'balance', 'restricted_balance' ,'unrestricted_balance', 'awqaf_balance']
        else:
            fields = ['credit', 'debit', 'balance']
        for report in reports:
            if report.id in res:
                continue
            res[report.id] = dict((fn, 0.0) for fn in fields)
            if report.type == 'accounts':
                # it's the sum of the linked accounts
                res[report.id]['account'] = self._compute_account_balance(report.account_ids, income_activity)
                for value in res[report.id]['account'].values():
                    for field in fields:
                        res[report.id][field] += value.get(field)
            elif report.type == 'account_type':
                # it's the sum the leaf accounts with such an account type
                accounts = self.env['account.account'].search([('user_type_id', 'in', report.account_type_ids.ids)])
                res[report.id]['account'] = self._compute_account_balance(accounts, income_activity)

                for value in res[report.id]['account'].values():
                    for field in fields:
                        # Used to get the returned value for cash flow  
                        if report.returned_value == 'credit':
                           res[report.id][field] += value.get('credit')
                        elif report.returned_value == 'debit':
                            res[report.id][field] += value.get('debit')
                        else:
                            res[report.id][field] += value.get(field)
                        
                        #res[report.id][field] += value.get(field)
            elif report.type == 'account_report' and report.account_report_id:
                # it's the amount of the linked report
                res2 = self._compute_report_balance(report.account_report_id, income_activity)
                for key, value in res2.items():
                    for field in fields:
                        res[report.id][field] += value[field]
            elif report.type == 'sum':
                # it's the sum of the children of this account.report
                res2 = self._compute_report_balance(report.children_ids, income_activity)
                for key, value in res2.items():
                    sign = self.env['account.financial.report'].search([('id', '=', key)]).sign
                    for field in fields:
                        res[report.id][field] += value[field] * sign
        return res

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
        return initial_balance

    def get_initial_balance_cmp(self, data):
        '''Get enitial balance for bank and cash at the begining of the the selected period'''


        cr = self.env.cr
        MoveLine = self.env['account.move.line']

        # Prepare initial sql query and Get the initial move lines

        init_tables, init_where_clause, init_where_params = MoveLine.with_context(data.get('init_context'))._query_get()     
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
        initial_balance_cmp = cr.fetchone()[0] or 0.0
        return initial_balance_cmp
#details
    def get_account_details_lines(self, data):
        
        lines = []
        account_report = self.env['account.financial.report'].search([('id', '=', data['account_report_id'][0])])
        child_reports = account_report._get_children_by_order()
        #print 'details context', data.get('used_context')
        res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports, data['income_activity'])
        for report in child_reports:
            if data['with_details'] == True and report.detail_number > 0:
                accounts = self.env['account.account'].search([('user_type_id', 'in', report.account_type_ids.ids)])
                res[report.id]['account'] = self.with_context(data.get('used_context'))._compute_account_balance(accounts, data['income_activity'])
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
        print ('detail>>>>>>>>>>>>>>>>>>', lines)            
        return lines

    def get_account_lines(self, data):
        lines = []
        account_report = self.env['account.financial.report'].search([('id', '=', data['account_report_id'][0])])
        child_reports = account_report._get_children_by_order()
        res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports, data['income_activity'])
        if data['enable_filter']:
            comparison_res = self.with_context(data.get('comparison_context'))._compute_report_balance(child_reports, data['income_activity'])
            init_res = self.with_context(data.get('init_context'))._compute_report_balance(child_reports,  data['income_activity'])
            for report_id, value in comparison_res.items():
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in comparison_res[report_id].get('account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']
            for report_id, value in init_res.items():             
               
                res[report_id]['init_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in init_res[report_id].get('account').items():
                        report_acc[account_id]['init_bal'] = val['balance']

        for report in child_reports:
            vals = {
                'name': report.name,
                'balance': res[report.id]['balance'] * report.sign,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type or False, #used to underline the financial report balances
                'colomn_order':report.colomn_order,
            }
            if data['income_activity']:
                vals['restricted_balance'] = res[report.id]['restricted_balance'] * report.sign
                vals['unrestricted_balance'] = res[report.id]['unrestricted_balance'] * report.sign
                vals['awqaf_balance'] = res[report.id]['awqaf_balance'] * report.sign
               
            if data['debit_credit']:
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']

            if data['with_details'] == True and report.detail_number > 0:
                vals['detail_number'] = report.detail_number


            if data['enable_filter']:
                vals['balance_cmp'] = res[report.id]['comp_bal'] * report.sign

            if data['owner_equity']:
                vals['balance_cmp_init'] = res[report.id]['init_bal'] * report.sign
 
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
                    vals = {
                        'name': account.code + ' ' + account.name,
                        'balance': value['balance'] * report.sign or 0.0,
                        'type': 'account',
                        'level': report.display_detail == 'detail_with_hierarchy' and 4,
                        'account_type': account.internal_type,
                    }
		    
                    if data['income_activity']:
                        vals['restricted_balance'] =  value['restricted_balance'] * report.sign  or 0.0
                        vals['unrestricted_balance'] =  value['unrestricted_balance'] * report.sign  or 0.0
                        vals['awqaf_balance'] =  value['awqaf_balance'] * report.sign  or 0.0

                    if data['debit_credit']:
                        vals['debit'] = value['debit']
                        vals['credit'] = value['credit']
                        if not account.company_id.currency_id.is_zero(vals['debit']) or not account.company_id.currency_id.is_zero(vals['credit']):
                            flag = True
                    if not account.company_id.currency_id.is_zero(vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        vals['balance_cmp'] = value['comp_bal'] * report.sign
                        vals['balance_cmp_init'] = value['init_bal'] * report.sign
                        if not account.company_id.currency_id.is_zero(vals['balance_cmp']):
                            flag = True
                        if not account.company_id.currency_id.is_zero(vals['balance_cmp_init']):
                            flag = True
                    if flag:
                        sub_lines.append(vals)
                lines += sorted(sub_lines, key=lambda sub_line: sub_line['name'])
        print ('>>>>>>>>>>>>>>>>>>>>>>>>>>> lines', lines)
        return lines

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        report_detail_lines =self.get_account_details_lines(data.get('form'))
        cashflow_initial_balance = self.with_context(data['form'].get('used_context',{})).get_initial_balance() or 0.0
        cashflow_initial_balance_cmp = self.with_context(data['form'].get('init_context',{})).get_initial_balance_cmp(data.get('form')) or 0.0
        report_lines = self.get_account_lines(data.get('form'))
        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_account_lines': report_lines,
            'get_initial_balance': cashflow_initial_balance,
            'get_initial_balance_cmp': cashflow_initial_balance_cmp,
            'get_account_details_lines' : report_detail_lines,
        }

# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from datetime import datetime
from openerp.tools.translate import _
from report import report_sxw
from account_custom.common_report_header import common_report_header

class account_budget(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(account_budget, self).__init__(cr, uid, name, context=context)
        company = self.pool.get('res.users').browse(self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join((_('BUDGET REPORT'), company.name, company.currency_id.name))
        footer_date_time = self.formatLang(str(datetime.today()), date_time=True)
        self.localcontext.update({
            'report_name': _('Budget Report'),
            'budgets':self.get_budget,
            'budget_total':self._budget_total,
            'departments': self._get_department_budget,
            'company_detail':self._get_company_detail,
            'company_detail_total':self._get_company_detail_total
        })	
        self.context = context
        self.total = {'planned_amount':0.0, 'total_operation':0.0, 'confirm':0.0,
                      'balance':0.0, 'residual_balance':0.0, 'bal_amount':0.0}
        self.dept_total = {'planned_amount':0.0, 'total_operation':0.0, 'confirm':0.0,
                           'balance':0.0, 'residual_balance':0.0, 'bal_amount':0.0}

    def set_context(self, objects, data, ids, report_type=None):
        # Report Header
        form = data.get('form',{})        
        period_pool = self.pool.get('account.period')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        analytic_pool = self.pool.get('account.analytic.account')
        self.account_ids = 'account_ids' in form and form['account_ids']  or \
                            'chart_account_id' in form and [form['chart_account_id']] or []
        self.analytic_account_ids = 'analytic_account_ids' in form and form['analytic_account_ids']  or \
                                    'chart_analytic_account_id' in form and [form['chart_analytic_account_id']] or []	

        chart_analytic_account = self._get_chart_analytic_account_id_br(data)
        cost_center = self._get_analytic_accounts_br(data)
        cost_center = (cost_center and cost_center) or (chart_analytic_account and [chart_analytic_account] ) or False
        if not 	cost_center:	
        	cost_center_ids = analytic_pool.search(self.cr, self.uid, [('parent_id', '=', False)], context=self.context)
        	cost_center = analytic_pool.browse(self.cr, self.uid, cost_center_ids, context=self.context)

        # Functions Filters
        fiscalyear_id = form.get('fiscalyear_id', False) and [form.get('fiscalyear_id', False)] or []
        period_from = form.get('period_from', False)
        period_to = form.get('period_to', False)
        
        period_from_start = period_from and period_pool.browse(self.cr, self.uid, period_from, context=self.context).date_start or ''
        period_stop = period_to and period_pool.browse(self.cr, self.uid, period_to, context=self.context).date_stop or ''

        domain = []
        if fiscalyear_id:
            if chart_analytic_account and chart_analytic_account.type == 'consolidation':
                FY = fiscalyear_pool.browse(self.cr, self.uid, fiscalyear_id, context=self.context)[0]
                fiscalyear_id = fiscalyear_pool.search(self.cr, self.uid, [('date_start', '=', FY.date_start),('date_stop', '=', FY.date_stop)], context=self.context)
            domain = [('fiscalyear_id', 'in', fiscalyear_id)]
            if period_from_start and period_stop:
                domain += [('date_start', '>=', period_from_start), ('date_stop', '<=', period_stop)]
        self.period_ids = period_pool.search(self.cr, self.uid, domain, context=self.context, order='date_start')
        self.analytic_child_ids = self._get_children_and_consol(self.cr, self.uid, self.analytic_account_ids, 'account.analytic.account', self.context)
        self.account_child_ids = self._get_children_and_consol(self.cr, self.uid, self.account_ids, 'account.account', context=self.context)

        self.localcontext.update({
            'fiscalyear': self.get_fiscalyear_br(data),
            'start_period': self.get_start_period_br(data),
            'stop_period': self.get_end_period_br(data),
            'chart_account': self._get_chart_account_id_br(data),
            'accounts': self.account_child_ids,
            'analytic_accounts': self.analytic_child_ids,
            'periods': self.period_ids,
            'cost_center': cost_center,
            'accuracy': form.get('accuracy',1)
        })
        return super(account_budget, self).set_context(objects, data, ids, report_type=report_type)
	
# # # # # # #  '1' Cost Center Details  # # # # # # #
    def get_budget(self, form):
        budget_pool = self.pool.get('account.budget')
        self.cr.execute("SELECT distinct account_budget_id,acc.code,period_id FROM account_budget_lines INNER JOIN account_analytic_account acc \
                ON acc.id = analytic_account_id WHERE analytic_account_id IN %s AND period_id IN %s AND general_account_id IN %s \
                ORDER BY acc.code,period_id", (tuple(self.analytic_child_ids,), tuple(self.period_ids,), tuple(self.account_child_ids,),))

        res = self.cr.fetchall()
        budget_ids = [rec[0] for rec in res]
        return budget_pool.browse(self.cr, self.uid, budget_ids, context=self.context)

    def _budget_total(self, budget):
        budget_line_pool = self.pool.get('account.budget.lines')
    	total = {'planned_amount':0.0, 'total_operation':0.0, 
                 'confirm':0.0, 'balance':0.0, 'residual_balance':0.0}
        
    	for line in budget.account_budget_line:
    	    if line.general_account_id.id in self.account_child_ids:
        		total['planned_amount'] += line.planned_amount
        		total['total_operation'] += line.total_operation
        		total['confirm'] += 'confirm' in budget_line_pool._columns and line.confirm or 0.0
        		total['balance'] += line.balance
        		total['residual_balance'] += line.residual_balance
        return [total]

# # # # # # #  '2' Cost Center Total  # # # # # # #
    def _get_department_budget(self, form):
        res = []
        budget_line_pool = self.pool.get('account.budget.lines')
        analytic_pool = self.pool.get('account.analytic.account')
        analytic_ids = form.get('analytic_account_ids', [])
        for analytic_id in analytic_ids:
           child_ids = self._get_children_and_consol(self.cr, self.uid, [analytic_id], 'account.analytic.account', context=self.context)
           lines = budget_line_pool.search(self.cr, self.uid, [('account_budget_id.period_id', 'in', self.period_ids), ('account_budget_id.analytic_account_id', 'in', child_ids)], context=self.context)
           analytic_name = analytic_pool.browse(self.cr, self.uid, analytic_id, context=self.context).name
           budget = {'name':analytic_name, 'planned_amount':0.0, 'total_operation':0.0, 'confirm':0.0, 'balance':0.0, 'residual_balance':0.0}

           for line in budget_line_pool.browse(self.cr, self.uid, lines, context=self.context):
               budget['planned_amount'] += line.planned_amount
               budget['total_operation'] += line.total_operation
               budget['confirm'] += 'confirm' in budget_line_pool._columns and line.confirm or 0.0
               budget['balance'] += line.balance
               budget['residual_balance'] += line.residual_balance

           self.dept_total['planned_amount'] += budget['planned_amount']
           self.dept_total['total_operation'] += budget['total_operation']
           self.dept_total['confirm'] += budget['confirm']
           self.dept_total['balance'] += budget['balance']
           self.dept_total['residual_balance'] += budget['residual_balance']
           res.append(budget)

        res.append({
           'name': _('Total'),
           'planned_amount': self.dept_total['planned_amount'],
           'total_operation': self.dept_total['total_operation'],
           'confirm': self.dept_total['confirm'],
           'balance': self.dept_total['balance'],
           'residual_balance': self.dept_total['residual_balance']
        })
        return res

# # # # # # # '3' Company Details # # # # # # #
    def _sort_filter(self, cr, uid, ids, context={}):
    	cr.execute('SELECT distinct account_id,sequence,acc.code \
    		        FROM   account_budget_classification_rel INNER JOIN account_budget_classification ON classification_id = id \
    				        INNER JOIN account_budget_lines ON general_account_id = account_id INNER JOIN account_account acc ON acc.id = account_id \
    		        WHERE  account_id in %s\
    		        ORDER BY 	sequence,acc.code', (tuple(ids),))
        return [acct[0] for acct in cr.fetchall()]   

    def _get_company_detail(self, form, analytic_acc=False):
        res = []
        account_pool = self.pool.get('account.account')
        budget_line_pool = self.pool.get('account.budget.lines')        
        general_account = self._sort_filter(self.cr, self.uid, self.account_child_ids, self.context)
        budget_class = {'id':False, 'name':''}
        class_total = {'planned_amount':0.0, 'total_operation':0.0, 'confirm':0.0, 'balance':0.0, 'residual_balance':0.0}
        for account_obj in account_pool.browse(self.cr, self.uid, general_account, context=self.context):
           classification = account_obj.budget_classification and account_obj.budget_classification[0] or False
           if budget_class['id'] != classification.id:
                if budget_class['id'] != False:
                    res.append({'code':'*', 'name':budget_class['name'], 'planned_amount':class_total['planned_amount'], 'total_operation':class_total['total_operation'], 'confirm':class_total['confirm'], 'balance':class_total['balance'], 'residual_balance':class_total['residual_balance']})
                    class_total = {'planned_amount':0.0, 'total_operation':0.0, 'confirm':0.0, 'balance':0.0, 'residual_balance':0.0}
                budget_class['id'] = classification.id
    
           account_budget = {'code':account_obj.code, 'name':account_obj.name, 'planned_amount':0.0, 'total_operation':0.0, 'confirm':0.0, 'balance':0.0, 'residual_balance':0.0}
    
           lines = budget_line_pool.search(self.cr, self.uid, [('account_budget_id.period_id', 'in', self.period_ids), ('account_budget_id.analytic_account_id', 'in', self.analytic_child_ids), ('general_account_id', '=', account_obj.id)], context=self.context)
           if lines:
                for line in budget_line_pool.browse(self.cr, self.uid, lines, self.context):
                   account_budget['planned_amount'] += line.planned_amount
                   account_budget['total_operation'] += line.total_operation
                   account_budget['confirm'] += 'confirm' in budget_line_pool._columns and line.confirm or 0.0
                   account_budget['balance'] += line.balance
                   account_budget['residual_balance'] += line.residual_balance
                self.total['planned_amount'] += account_budget['planned_amount']
                self.total['total_operation'] += account_budget['total_operation']
                self.total['confirm'] += account_budget['confirm']
                self.total['balance'] += account_budget['balance']
                self.total['residual_balance'] += account_budget['residual_balance']
                
                class_total['planned_amount'] += account_budget['planned_amount']
                class_total['total_operation'] += account_budget['total_operation']
                class_total['confirm'] += account_budget['confirm']
                class_total['balance'] += account_budget['balance']
                class_total['residual_balance'] += account_budget['residual_balance']
                if res and res[len(res)-1]['code'] == account_budget['code'] and account_budget['code'] != '*':
                   res[len(res)-1]['planned_amount'] += account_budget['planned_amount']
                   res[len(res)-1]['total_operation'] += account_budget['total_operation']
                   res[len(res)-1]['confirm'] += account_budget['confirm']
                   res[len(res)-1]['balance'] += account_budget['balance']
                   res[len(res)-1]['residual_balance'] += account_budget['residual_balance']                
                else:
                    res.append(account_budget)
           elif not res or not(res[len(res)-1]['code'] == account_budget['code'] and account_budget['code'] != '*'):
               res.append(account_budget)
           budget_class['name'] = classification.name
        res.append({
            'code':'*',
            'name':budget_class['name'],
            'planned_amount':class_total['planned_amount'],
            'total_operation':class_total['total_operation'],
            'confirm':class_total['confirm'],
            'balance':class_total['balance'],
            'residual_balance':class_total['residual_balance']
        })
    
        res.append({
            'code': '*',
            'name': _('Total'),
            'planned_amount': self.total['planned_amount'],
            'total_operation': self.total['total_operation'],
            'confirm': self.total['confirm'],
            'balance': self.total['balance'],
            'residual_balance': self.total['residual_balance']
        })
        return res

# # # # # # # '3' Company Details - Just Total # # # # # # #
    def _get_company_detail_total(self, form, analytic_acc=False):
        res = []
        account_pool = self.pool.get('account.account')
        budget_line_pool = self.pool.get('account.budget.lines')
        budget_classificaiton_pool = self.pool.get('account.budget.classification')

        class_ids = budget_classificaiton_pool.search(self.cr, self.uid, [], context=self.context)
        class_objs = budget_classificaiton_pool.browse(self.cr, self.uid, class_ids, self.context)
        total_budget = {'name':'Total', 'planned_amount':0.0, 'total_operation':0.0, 'confirm':0.0, 'balance':0.0, 'residual_balance':0.0}
        for  class_obj in class_objs:
            account_budget = {'code':class_obj.code, 'name':class_obj.name, 'planned_amount':0.0, 'total_operation':0.0, 'confirm':0.0, 'balance':0.0, 'residual_balance':0.0}
            acc_ids = account_pool.search(self.cr, self.uid, [('id', 'in', self.account_child_ids), ('budget_classification', '=', class_obj.id)])
            lines = budget_line_pool.search(self.cr, self.uid, [('account_budget_id.period_id', 'in', self.period_ids), ('account_budget_id.analytic_account_id', 'in', self.analytic_child_ids), ('general_account_id', 'in', acc_ids)], context=self.context)
            line_obj = budget_line_pool.browse(self.cr, self.uid, lines, self.context)
            for line in line_obj:
                account_budget['planned_amount'] += line.planned_amount
                account_budget['total_operation'] += line.total_operation
                account_budget['confirm'] += 'confirm' in budget_line_pool._columns and line.confirm or 0.0
                account_budget['balance'] += line.balance
                account_budget['residual_balance'] += line.residual_balance
            res.append(account_budget)
    
            total_budget['planned_amount'] += account_budget['planned_amount']
            total_budget['total_operation'] += account_budget['total_operation']
            total_budget['confirm'] += account_budget['confirm']
            total_budget['balance'] += account_budget['balance']
            total_budget['residual_balance'] += account_budget['residual_balance']
        res.append(total_budget)
        return res

report_sxw.report_sxw('report.account.account.budget',  'account.report.budget', 'addons/account_budget_custom/report/account_report_budget.rml', parser=account_budget, header=False)

report_sxw.report_sxw('report.account.account.budget.company.report',  'account.report.budget', 'addons/account_budget_custom/report/account_report_budget_company_report.rml', parser=account_budget, header=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


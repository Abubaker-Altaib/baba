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

class account_compare_budget(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context={}):
        super(account_compare_budget, self).__init__(cr, uid, name, context=context)
        company = self.pool.get('res.users').browse(self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join((_('BUDGET REPORT'), company.name, company.currency_id.name))
        footer_date_time = self.formatLang(str(datetime.today()), date_time=True)
        self.localcontext.update({
                'report_name': _('Comparison Budget Report'),
                'company_detail': self._get_company_detail,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type={}):
        analytic_pool = self.pool.get('account.analytic.account')
        period_pool = self.pool.get('account.period')
        account_ids = 'account_ids' in data['form'] and data['form']['account_ids']  or \
                      'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
        analytic_account_ids = 'analytic_account_ids' in data['form'] and data['form']['analytic_account_ids']  or \
                               'chart_analytic_account_id' in data['form'] and [data['form']['chart_analytic_account_id']] or []
        chart_account = self._get_chart_account_id_br(data)
        chart_analytic_account = self._get_chart_analytic_account_id_br(data)
        first_fiscalyear = self._get_info(data, 'first_fiscalyear', 'account.fiscalyear')
        next_fiscalyear = self._get_info(data, 'second_fiscalyear', 'account.fiscalyear')
        start_period = self.get_start_period_br(data)
        stop_period = self.get_end_period_br(data)
        cost_center = self._get_analytic_accounts_br(data)
        cost_center = (cost_center and cost_center) or (chart_analytic_account and [chart_analytic_account]) or False
        if not 	cost_center:
            cost_center_ids = analytic_pool.search(self.cr, self.uid, [('parent_id', '=', False)], context=self.context)
            cost_center = analytic_pool.browse(self.cr, self.uid, cost_center_ids, context=self.context)
        periods = []
        analytic_accounts = []
        if (not(start_period) and not(stop_period) and first_fiscalyear):
            start_period = self.get_first_fiscalyear_period(first_fiscalyear)
            stop_period = self.get_last_fiscalyear_period(first_fiscalyear)

        domain = []
        if((start_period or stop_period) and first_fiscalyear):
            domain = [('date_start', '>=', start_period.date_start),
                      ('date_start', '<=', stop_period.date_start)]
        if chart_analytic_account and chart_analytic_account.type != 'consolidation':
            domain += [('company_id', '=', chart_account.company_id.id)]
        self.periods = period_pool.search(self.cr, self.uid, domain, context=self.context)
            
        self.accounts = self._get_children_and_consol(self.cr, self.uid, account_ids, 'account.account', context=self.context)
        self.analytic_accounts = analytic_pool.search(self.cr, self.uid, [('parent_id', 'child_of', analytic_account_ids)], context=self.context)
        self.localcontext.update({
                'fiscalyear': first_fiscalyear,
                'next_fiscalyear': next_fiscalyear,
                'start_period': start_period,
                'stop_period': stop_period,
                'chart_account': chart_account,
                'accounts': self.accounts,
                'analytic_accounts': self.analytic_accounts,
                'periods': self.periods,
                'cost_center': cost_center,
                'accuracy': data['form']['accuracy']
        })
        self.fiscalyear = first_fiscalyear
        self.next_fiscalyear = next_fiscalyear
        return super(account_compare_budget, self).set_context(objects, data, ids, report_type=report_type)

    def _sort_filter(self, cr, uid, ids, context={}):
        res = []
        cr.execute('SELECT distinct account_id,sequence,acc.code \
                    FROM account_budget_classification_rel \
                         INNER JOIN account_budget_classification ON classification_id = id \
                         INNER JOIN account_budget_lines ON general_account_id = account_id \
                         INNER JOIN account_account acc ON acc.id = account_id \
                    WHERE account_id in %s \
                    ORDER BY sequence,acc.code', (tuple(ids),))
        return [acct[0] for acct in cr.fetchall()]   


    def _get_company_detail(self, form, analytic_acc=False):
        res = []
        period_pool = self.pool.get('account.period')
        account_pool = self.pool.get('account.account')
        budget_line_pool = self.pool.get('account.budget.lines')
        fisc_budget_line_pool = self.pool.get('account.fiscalyear.budget.lines')
        account_chart = form.get('chart_account_id', [])
        analytic_chart = analytic_acc and analytic_acc or form.get('chart_analytic_account_id', [])
        period_from = form.get('period_from', False)
        period_to = form.get('period_to', False)
        self.total = {'planned_amount':0.0, 'next_planned_amount':0.0, 'balance':0.0}
        period_from_start = period_from and period_pool.browse(self.cr, self.uid, period_from,
                                                                                   context=self.context).date_start or ''
        period_stop = period_to and period_pool.browse(self.cr, self.uid, period_to,
                                                                              context=self.context).date_stop or ''
        current_periods = period_pool.search(self.cr, self.uid, [('fiscalyear_id', '=', self.fiscalyear.id)],
                                                                 context=self.context)
        next_periods = period_pool.search(self.cr, self.uid, [('fiscalyear_id', '=', self.next_fiscalyear.id)],
                                                              context=self.context)
        analytic_child_ids = self._get_children_and_consol(self.cr, self.uid, analytic_chart,
                                                         'account.analytic.account', self.context)
        account_child_ids = self._get_children_and_consol(self.cr, self.uid, account_chart,
                                                          'account.account', self.context)
        general_account = self._sort_filter(self.cr, self.uid, account_child_ids, context=self.context)
        budget_class = {'id':False, 'name':'', 'class':''}
        class_total = {'planned_amount':0.0, 'next_planned_amount':0.0, 'balance':0.0}
        
        for account in account_pool.browse(self.cr, self.uid, general_account, context=self.context):
            classification = account.budget_classification and account.budget_classification[0] or False
            if budget_class['id'] != classification.id:
                if budget_class['id'] != False:
                    res.append({'code':'*', 'class':budget_class['class'], 'name':budget_class['name'], 'balance': class_total['balance'],
                                'planned_amount':class_total['planned_amount'], 'next_planned_amount':class_total['next_planned_amount']})
                    class_total = {'planned_amount':0.0, 'next_planned_amount':0.0, 'balance':0.0}
                budget_class['id'] = classification.id
                
            account_budget = {'code':account.code, 'name':account.name, 'planned_amount':0.0, 'next_planned_amount':0.0, 'balance':0.0}
            current_lines = budget_line_pool.search(self.cr, self.uid, [('period_id', 'in', current_periods),
                                 ('analytic_account_id', 'in', analytic_child_ids),
                                 ('general_account_id', '=', account.id)], context=self.context)
            next_lines = fisc_budget_line_pool.search(self.cr, self.uid, [('fiscalyear_id', '=', self.next_fiscalyear.id),
                                 ('analytic_account_id', 'in', analytic_child_ids),
                                 ('general_account_id', '=', account.id)], context=self.context)
            bal_lines = budget_line_pool.search(self.cr, self.uid, [('period_id', 'in', self.periods),
                                 ('analytic_account_id', 'in', analytic_child_ids),
                                 ('general_account_id', '=', account.id)], context=self.context)
            if current_lines:
                for line in budget_line_pool.browse(self.cr, self.uid, current_lines, context=self.context):
                    account_budget['planned_amount'] += line.planned_amount
                    
                self.total['planned_amount'] += account_budget['planned_amount']
                class_total['planned_amount'] += account_budget['planned_amount']

                if res:
                    if res[len(res) - 1]['code'] == account_budget['code'] and account_budget['code'] != '*':
                        res[len(res) - 1]['planned_amount'] += account_budget['planned_amount']
            if next_lines:
                for line in fisc_budget_line_pool.browse(self.cr, self.uid, next_lines, context=self.context):
                    account_budget['next_planned_amount'] += line.planned_amount
                    
                self.total['next_planned_amount'] += account_budget['next_planned_amount']
                class_total['next_planned_amount'] += account_budget['next_planned_amount']
                
                if res:
                    if res[len(res) - 1]['code'] == account_budget['code'] and account_budget['code'] != '*':
                        res[len(res) - 1]['next_planned_amount'] += account_budget['next_planned_amount']
                        
            if bal_lines:
                for line in budget_line_pool.browse(self.cr, self.uid, bal_lines, context=self.context):
                    account_budget['balance'] += line.balance + line.confirm
                    
                self.total['balance'] += account_budget['balance']
                class_total['balance'] += account_budget['balance']
                
                if res:
                    if res[len(res) - 1]['code'] == account_budget['code'] and account_budget['code'] != '*':
                        res[len(res) - 1]['balance'] += account_budget['balance']
                        
            res.append(account_budget)
            budget_class['name'] = classification.name
            budget_class['class'] = classification.code
            
        res.append({
                    'code':'*',
                    'name':budget_class['name'],
                    'class':budget_class['class'] or 1,
                    'planned_amount':class_total['planned_amount'],
                    'next_planned_amount':class_total['next_planned_amount'],
                    'balance':class_total['balance'],
                    })
        
        res.append({
                    'code': '*',
                    'name': _('Total'),
                    'planned_amount': self.total['planned_amount'],
                    'next_planned_amount': self.total['next_planned_amount'],
                    'balance': self.total['balance'],
                    })
        return res

report_sxw.report_sxw('report.account.account.compare.budget', "account.report.compare.budget",
                      'addons/account_budget_custom/report/account_report_compare_budget.rml',
                      parser=account_compare_budget, header=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import time

class AccountReportBudgetWizard(osv.osv_memory):

    _name = "account.report.budget"

    _description = 'Budget Report'

    _columns = {                
        'chart_account_id': fields.many2one('account.account', 'Chart of Account', help='Select Charts of Accounts', required=True, domain = [('parent_id','=',False)]),
        
        'company_id': fields.related('chart_account_id', 'company_id', type='many2one', relation='res.company', string='Company', readonly=True),
        
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', help='Keep empty for all open fiscal year'),
        
        'filter': fields.selection([('filter_no', 'No Filters'), ('filter_period', 'Periods')], "Filter By", required=True),

        'period_from': fields.many2one('account.period', 'Start Period'),
        
        'period_to': fields.many2one('account.period', 'End Period'),

        'chart_analytic_account_id':fields.many2one('account.analytic.account', 'Chart of Cost Center', required=True, 
                                                    help='Select Charts of Cost Center', domain = [('parent_id','=',False)]),

        'account_ids': fields.many2many('account.account', 'account_budget_report_account_rel', 'budget_report_id',
                                        'account_id', 'Accounts'),

        'analytic_account_ids': fields.many2many('account.analytic.account', 'account_budget_report_analytic_rel', 
                                                 'budget_report_id', 'analytic_account_id', 'Cost Centers'),

        'report_type': fields.selection([('1','Cost Center Details'), ('2','Cost Center Total'), ('3','Company Details')],
                                        'Report Style', required=True),

        'type_selection': fields.selection([('detail', 'Detailed'), ('total', 'Total'),],
                                           'Report Type', required=True),

        'accuracy': fields.selection([(1, '1 SDG'), (1000, '1000 SDG'),(1000000, '1000,000 SDG')],
                                           'Amount Accuracy', required=True),
    }

    def _get_fiscalyear_id(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        fiscalyear = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now),
                                                                          ('company_id','=',company)], context=context, limit=1)
        return fiscalyear and fiscalyear[0] or False

    def _get_account(self, cr, uid, context=None):
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        account = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False),('company_id','=',company)],
                                                          context=context, limit=1)
        return account and account[0] or False

    def _get_analytic_account(self, cr, uid, context=None):
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        analytic_account = self.pool.get('account.analytic.account').search(cr, uid, [('parent_id', '=', False), ('company_id','=', company)], 
                                                                            context=context, limit=1)
        return analytic_account and analytic_account[0] or False

    _defaults = {
            'filter': 'filter_no',
            'chart_account_id': _get_account,
            'fiscalyear_id': _get_fiscalyear_id,
            'chart_analytic_account_id': _get_analytic_account,
            'report_type':'1',
            'type_selection': 'detail',
            'report_type': '3',
            'accuracy': 1,
    }
    
    def onchange_chart_account_id(self, cr, uid, ids, chart_account_id=False, context=None):
        chart_account = self.pool.get('account.account').browse(cr, uid, chart_account_id, context=context)
        return {'value': {'company_id': chart_account and chart_account.company_id.id or False}}

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear=False, context=None):
        return {'value': not fiscalyear and {'filter': 'filter_no', 'period_from': False, 'period_to': False} or {}}

    def onchange_report_type(self, cr, uid, ids, report_type):
        return {'value': report_type == '2' and {'account_ids':[]} or {} }
     
    def onchange_filter(self, cr, uid, ids, filter='filter_no', fiscalyear_id=False, context=None):
        res = {'value': {}}
        if filter == 'filter_no':
            res['value'] = {'period_from': False, 'period_to': False}
        if filter == 'filter_period' and fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.special = false
                               ORDER BY p.date_start ASC, p.special ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               AND p.special = false
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
            periods =  [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 1:
                start_period = periods[0]
                end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to': end_period}
        return res
    
    def print_report(self, cr, uid, ids, context=None):
        data ={'ids':ids,'form': self.read(cr, uid, ids, [])[0]}
        data['form'].update({'chart_account_id': data['form']['chart_account_id'] and data['form']['chart_account_id'][0],
                             'fiscalyear_id': data['form']['fiscalyear_id'] and data['form']['fiscalyear_id'][0],
                             'period_from': data['form']['period_from'] and data['form']['period_from'][0],
                             'period_to': data['form']['period_to'] and data['form']['period_to'][0],
                             'chart_analytic_account_id': data['form']['chart_analytic_account_id'] and data['form']['chart_analytic_account_id'][0],
                             'accuracy':data['form']['accuracy']})

        if data['form']['report_type'] == '3':
                 return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.budget.company.report', 'datas': data}
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.budget', 'datas': data}

AccountReportBudgetWizard()

# ---------------------------------------------------------
#  Budget Comparison Report
# ---------------------------------------------------------

class AccountReportCompareBudgetWizard(osv.osv_memory):

    _name = "account.report.compare.budget"
    
    _description = 'Budget Comparison Report'

    def _get_fiscalyear_id(self, cr, uid, context={}):
        now = time.strftime('%Y-%m-%d')
        user = self.pool.get('res.users').browse(cr,uid,uid,context)
        fiscalyear = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), 
                                                                          ('date_stop', '>', now),
                                                                          ('company_id','=',user.company_id.id)], 
                                                                          context=context, limit=1 )
        return fiscalyear and fiscalyear[0] or False

    def _get_account(self, cr, uid, context={}):        
        user = self.pool.get('res.users').browse(cr,uid,uid,context)
        accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False),
                                                                     ('company_id','=',user.company_id.id)],
                                                                     context=context, limit=1)
        return accounts and accounts[0] or False


    def _get_analytic_account(self, cr, uid, context={}):        
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        analytic_accounts = self.pool.get('account.analytic.account').search(cr, uid, [('parent_id', '=', False),
                                                                                       ('company_id','=',user.company_id.id)],
                                                                                       context=context, limit=1)
        return analytic_accounts and analytic_accounts[0] or False

    _columns = {
        'chart_account_id': fields.many2one('account.account', 'Chart of Account', help='Select Charts of Accounts', required=True, domain = [('parent_id','=',False)]),
        
        'chart_analytic_account_id': fields.many2one('account.analytic.account', 'Chart of Cost Center', 
                                                     help='Select Charts of Cost Centers', required=True,
                                                     domain = [('parent_id','=',False)] ),
                
        'first_fiscalyear': fields.many2one('account.fiscalyear', 'First Fiscal year',  required=True),

        'second_fiscalyear': fields.many2one('account.fiscalyear', 'Second Fiscal year'),

        'filter': fields.selection([('filter_no', 'No Filters'), ('filter_period', 'Periods')], 
                                   "Filter by", required=True),
        
        'period_from': fields.many2one('account.period', 'Start Period'),
        
        'period_to': fields.many2one('account.period', 'End Period'),
        
        'date_from': fields.date("Start Date"),
        
        'date_to': fields.date("End Date"),

        'analytic_account_ids': fields.many2many('account.analytic.account', 'account_common_analytic_account_rel', 
                                                 'budget_report_id', 'analytic_account_id', 'Cost Centers'),

        'type_selection': fields.selection([('detail', 'Detailed'), ('total', 'Total'),],'Report Type', required=True),

        'report_name': fields.selection([('compare', 'FiscalYear Budget Comparison Report'),
                                          ('summary', 'Suggested Budget Summary'),
                                          ('flow', 'Budget Cash Flow'),],
                                          'Report Name', required=True),

        'company_id': fields.many2one('res.company', 'Company', type='many2one'),
        
        'accuracy': fields.selection([(1, '1 SDG'), (1000, '1000 SDG'),(1000000, '1000,000 SDG')],
                                           'Amount Accuracy', required=True),
                                           
        'size':fields.selection([('A4', 'A4'), ('A3', 'A3')], 'Page Size', required=True),
                                           
        'landscape': fields.boolean('Landscape'),
    }

    _defaults = {
        'filter': 'filter_no',
        'first_fiscalyear': _get_fiscalyear_id,
        'second_fiscalyear': _get_fiscalyear_id,
        'chart_account_id': _get_account,
        'chart_analytic_account_id': _get_analytic_account,
        'type_selection': 'detail',
        'report_name': 'compare',
        'accuracy': 1,
        'size': 'A4',
        'landscape': True,
    }

    def onchange_filter(self, cr, uid, ids, filter='filter_no', fiscalyear_id=False, context=None):
        res = {'value': {}}
        if filter == 'filter_no':
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': False ,'date_to': False}
        if filter == 'filter_date':
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': time.strftime('%Y-01-01'), 'date_to': time.strftime('%Y-%m-%d')}
        if filter == 'filter_period' and fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.special = false
                               ORDER BY p.date_start ASC, p.special ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               AND p.special = false
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
            periods =  [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 1:
                start_period = periods[0]
                end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to': end_period, 'date_from': False, 'date_to': False}
        return res
    
    def onchange_chart_account_id(self, cr, uid, ids, chart_account_id=False, context={}):
        company = self.pool.get('account.account').browse(cr, uid, chart_account_id, context=context)
        return {'value': {'company_id': company and company.company_id.id or False}}

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear=False, context=None):
        res = {'value': {'fiscalyear_id':fiscalyear}}
        if not fiscalyear:
            res['value'].update({'filter': 'filter_no', 'period_from': False, 'period_to': False})
        return res
     
    def print_report(self, cr, uid, ids, context=None):
        data ={'form': self.read(cr, uid, ids, [])[0]}
        data['form'].update({'chart_account_id': data['form']['chart_account_id'] and data['form']['chart_account_id'][0],
                             'first_fiscalyear': data['form']['first_fiscalyear'] and data['form']['first_fiscalyear'][0],
                             'second_fiscalyear': data['form']['second_fiscalyear'] and data['form']['second_fiscalyear'][0],
                             'period_from': data['form']['period_from'] and data['form']['period_from'][0],
                             'period_to': data['form']['period_to'] and data['form']['period_to'][0],
                             'company_id': data['form']['company_id'] and data['form']['company_id'][0],
                             'chart_analytic_account_id': data['form']['chart_analytic_account_id'] and data['form']['chart_analytic_account_id'][0]})
        if data['form']['report_name'] == 'compare':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.compare.budget', 'datas': data}
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.compare.dept.budget', 'datas': data}

AccountReportCompareBudgetWizard()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

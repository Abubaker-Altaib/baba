#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import time
from datetime import datetime

class AccountReportBudgetWizard(osv.osv_memory):
    """
    Budget reporting options
    """
    _name = "account.report.budget"

    _description = 'Budget Report'

    _columns = {
        'chart_account_id': fields.many2one('account.account', 'Chart of Account', help='Select Charts of Accounts', required=True, domain = [('parent_id','=',False)]),
        'company_id': fields.related('chart_account_id', 'company_id', type='many2one', relation='res.company', string='Company', readonly=True),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', help='Keep empty for all open fiscal year'),
        'filter': fields.selection([('filter_no', 'No Filters'), ('filter_period', 'Periods'),('filter_date','Date')], "Filter By", required=True),
        'period_from': fields.many2one('account.period', 'Start Period'),
        'period_to': fields.many2one('account.period', 'End Period'),
        'date_from':fields.date("Start Date"),
        'date_to':fields.date("End Date"),
        'chart_analytic_account_id':fields.many2one('account.analytic.account', 'Chart of Cost Center', required=True, 
                                                    help='Select Charts of Cost Center', domain = [('parent_id','=',False)]),
        'account_ids': fields.many2many('account.account', 'account_budget_report_account_rel', 'budget_report_id',
                                        'account_id', 'Accounts'),
        'analytic_account_ids': fields.many2many('account.analytic.account', 'account_budget_report_analytic_rel', 
                                                 'budget_report_id', 'analytic_account_id', 'Cost Centers'),
        'report_type': fields.selection([('1','Cost Center Details'), ('2','Cost Center Total'), ('3','Company Details')],
                                        'Report Style', required=True),
        'type_selection': fields.selection([('detail', 'Detailed'),('consol', 'consol'),('unit', 'unit'), ('dept', 'dept'),('planned', 'planned'),('state', 'state'),('sub', 'sub')],
                                           'Report Type', required=True),
        'accuracy': fields.selection([(1, '1 SDG'), (1000, '1000 SDG'),(1000000, '1000,000 SDG')],
                                           'Amount Accuracy', required=True),
    }

    def _get_fiscalyear_id(self, cr, uid, context=None):
        """
        Method to return the current fiscal year in logged in user
        
        @return: int current fiscal year id or False
        """
        now = time.strftime('%Y-%m-%d')
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        fiscalyear = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now),
                                                                          ('company_id','=',company)], context=context, limit=1)
        return fiscalyear and fiscalyear[0] or False

    def _get_account(self, cr, uid, context=None):
        """
        Method to return the root account in logged in user
        
        @return: int root account id or False
        """
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        account = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False),('company_id','=',company)],
                                                          context=context, limit=1)
        return account and account[0] or False

    def _get_analytic_account(self, cr, uid, context=None):
        """
        Method to return the root analytic account in logged in user
        
        @return: int root analytic account id or False
        """
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
        """
        Method to set the selected chart of account company as company_id value in wizard
        
        @return: dictionary of company_id value
        """
        chart_account = self.pool.get('account.account').browse(cr, uid, chart_account_id, context=context)
        return {'value': {'company_id': chart_account and chart_account.company_id.id or False}}

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear=False, context=None):
        """
        Method to reset filter, period_from & period_to value in wizard
        
        @return: dictionary of fields values
        """
        return {'value': not fiscalyear and {'filter': 'filter_no', 'period_from': False, 'period_to': False} or {}}

    def onchange_report_type(self, cr, uid, ids, report_type):
        """
        Method to reset account_ids field value when the selected report_type is 'Cost Center Total'
        
        @return: dictionary of account_ids field value
        """
        return {'value': report_type == '2' and {'account_ids':[]} or {} }
     
    def onchange_filter(self, cr, uid, ids, filter='filter_no', fiscalyear_id=False, context=None):
        """
        Method to set filters defaults values when changing the filter type as:
        1. if filter_no: emptying period_from & period_to
        2. if filter_period: set the first period in the selected fiscal year in period_from field 
            and set the current period in the selected fiscal year in period_to field 
        
        @return: dictionary of fields values
        """
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
            res['value'] = {'period_from': start_period, 'period_to': end_period, 'date_from': False ,'date_to': False}
        return res
    
    def print_report(self, cr, uid, ids, context=None):
        """
        Method to send wizards fields value to the report
        
        @return: dictionary call the report service 
        """
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




# ---------------------------------------------------------
#  Budget Comparison Report
# ---------------------------------------------------------

class AccountReportCompareBudgetWizard(osv.osv_memory):
    """
    Budget analytic reporting options
    """
    _name = "account.report.compare.budget"
    
    _description = 'Budget Comparison Report'

    def _get_fiscalyear_id(self, cr, uid, context=None):
        """
        Method to return the current fiscal year in logged in user
        
        @return: int current fiscal year id or False
        """
        now = time.strftime('%Y-%m-%d')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        fiscalyear = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now),
                                                                          ('date_stop', '>', now),
                                                                          ('company_id','=',user.company_id.id)],
                                                                          context=context, limit=1 )
        return fiscalyear and fiscalyear[0] or False

    def _get_account(self, cr, uid, context=None):
        """
        Method to return the root account in logged in user
        
        @return: int root account id or False
        """
        user = self.pool.get('res.users').browse(cr,uid,uid,context)
        accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False),
                                                                     ('company_id','=',user.company_id.id)],
                                                                     context=context, limit=1)
        return accounts and accounts[0] or False

    def _get_analytic_account(self, cr, uid, context=None):
        """
        Method to return the root analytic account in logged in user
        
        @return: int root analytic account id or False
        """
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
        """
        Method to set filters defaults values when changing the filter type as:
        1. if filter_no: emptying date_from, date_to, period_from & period_to
        2. if filter_period:
            - Emptying date_from, date_to
            - Set the first period in the selected fiscal year in period_from field
            - Set the current period in the selected fiscal year in period_to field
        
        @return: dictionary of fields values
        """
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

    def onchange_chart_account_id(self, cr, uid, ids, chart_account_id=False, context=None):
        """
        Method to set the selected chart of account company as company_id value in wizard
        
        @return: dictionary of company_id value
        """
        company = self.pool.get('account.account').browse(cr, uid, chart_account_id, context=context)
        return {'value': {'company_id': company and company.company_id.id or False}}

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear=False, context=None):
        """
        Method to reset filter, period_from & period_to value in wizard
        
        @return: dictionary of fields values
        """
        res = {'value': {'fiscalyear_id':fiscalyear}}
        if not fiscalyear:
            res['value'].update({'filter': 'filter_no', 'period_from': False, 'period_to': False})
        return res
    
    def print_report(self, cr, uid, ids, context=None):
        """
        Method to send wizards fields value to the report
        
        @return: dictionary call the report service
        """
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




# ---------------------------------------------------------
#  Budget Comparison Report2
# ---------------------------------------------------------

class AccountReportCompareBudgetWizardCustom(osv.osv_memory):
    """
    Budget analytic reporting options
    """
    _name = "account.report.compare.budget.custom"
    
    _description = 'Budget Comparison Report Custom'

    def _get_fiscalyear_id(self, cr, uid, context=None):
        """
        Method to return the current fiscal year in logged in user
        
        @return: int current fiscal year id or False
        """
        now = time.strftime('%Y-%m-%d')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        fiscalyear = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), 
                                                                          ('date_stop', '>', now),
                                                                          ('company_id','=',user.company_id.id)], 
                                                                          context=context, limit=1 )
        return fiscalyear and fiscalyear[0] or False

    def _get_account(self, cr, uid, context=None):
        """
        Method to return the root account in logged in user
        
        @return: int root account id or False
        """
        user = self.pool.get('res.users').browse(cr,uid,uid,context)
        accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False),
                                                                     ('company_id','=',user.company_id.id)],
                                                                     context=context, limit=1)
        return accounts and accounts[0] or False

    def _get_analytic_account(self, cr, uid, context=None):
        """
        Method to return the root analytic account in logged in user
        
        @return: int root analytic account id or False
        """
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
        'filter': fields.selection([('filter_no', 'No Filters'), ('filter_date','Date'), ('filter_period', 'Periods')], 
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
        'num_year': fields.integer('Years Number'),
        'classification_ids': fields.many2many('account.budget.classification', 'account_common_classification_rel', 
                                                 'budget_report_id', 'classification_id', 'Classification', required=True),
    }

    _defaults = {
        'filter': 'filter_no',
        'first_fiscalyear': _get_fiscalyear_id,
        'chart_account_id': _get_account,
        'chart_analytic_account_id': _get_analytic_account,
        'type_selection': 'detail',
        'report_name': 'compare',
        'accuracy': 1,
        'size': 'A4',
        'landscape': True,
    }

    def onchange_filter(self, cr, uid, ids, filter='filter_no', fiscalyear_id=False, context=None):
        """
        Method to set filters defaults values when changing the filter type as:
        1. if filter_no: emptying date_from, date_to, period_from & period_to
        2. if filter_period: 
            - Emptying date_from, date_to
            - Set the first period in the selected fiscal year in period_from field 
            - Set the current period in the selected fiscal year in period_to field 
        
        @return: dictionary of fields values
        """
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

    def onchange_chart_account_id(self, cr, uid, ids, chart_account_id=False, context=None):
        """
        Method to set the selected chart of account company as company_id value in wizard
        
        @return: dictionary of company_id value
        """
        company = self.pool.get('account.account').browse(cr, uid, chart_account_id, context=context)
        return {'value': {'company_id': company and company.company_id.id or False}}

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear=False, context=None):
        """
        Method to reset filter, period_from & period_to value in wizard
        
        @return: dictionary of fields values
        """
        res = {'value': {'fiscalyear_id':fiscalyear}}
        if not fiscalyear:
            res['value'].update({'filter': 'filter_no', 'period_from': False, 'period_to': False})
        return res
    
    def print_report(self, cr, uid, ids, context=None):
        """
        Method to send wizards fields value to the report
        
        @return: dictionary call the report service 
        """
        data ={'form': self.read(cr, uid, ids, [])[0]}
        data['form'].update({'chart_account_id': data['form']['chart_account_id'] and data['form']['chart_account_id'][0],
                             'first_fiscalyear': data['form']['first_fiscalyear'] and data['form']['first_fiscalyear'][0],

                             'num_year': data['form']['num_year'],
                             'classification_ids': data['form']['classification_ids'] and data['form']['classification_ids'],

                             'period_from': data['form']['period_from'] and data['form']['period_from'][0],
                             'period_to': data['form']['period_to'] and data['form']['period_to'][0],
                             'company_id': data['form']['company_id'] and data['form']['company_id'][0],
                             'chart_analytic_account_id': data['form']['chart_analytic_account_id'] and data['form']['chart_analytic_account_id'][0]})
        
        if data['form']['report_name'] == 'compare':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.compare.budget.custom', 'datas': data}
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.compare.dept.budget', 'datas': data}


# ---------------------------------------------------------
#  Budget Comparison Report2
# ---------------------------------------------------------

class AccountReportBudgetQuarterWizard(osv.osv_memory):
    """
    Budget analytic reporting options
    """
    _name = "account.report.budget.quarter"
    
    _description = 'Budget Quarter Report'

    def _get_fiscalyear_id(self, cr, uid, context=None):
        """
        Method to return the current fiscal year in logged in user
        
        @return: int current fiscal year id or False
        """
        now = time.strftime('%Y-%m-%d')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        fiscalyear = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), 
                                                                          ('date_stop', '>', now),
                                                                          ('company_id','=',user.company_id.id)], 
                                                                          context=context, limit=1 )
        return fiscalyear and fiscalyear[0] or False

    def _get_account(self, cr, uid, context=None):
        """
        Method to return the root account in logged in user
        
        @return: int root account id or False
        """
        user = self.pool.get('res.users').browse(cr,uid,uid,context)
        accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False),
                                                                     ('company_id','=',user.company_id.id)],
                                                                     context=context, limit=1)
        return accounts and accounts[0] or False

    def _get_analytic_account(self, cr, uid, context=None):
        """
        Method to return the root analytic account in logged in user
        
        @return: int root analytic account id or False
        """
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
        'first_fiscalyear': fields.many2one('account.fiscalyear', 'Fiscal year',  required=True),
        'filter': fields.selection([('filter_no', 'No Filters'), ('filter_period', 'Quarters')], 
                                   "Filter by", required=True),
        'quarter': fields.selection([('first', 'First Quarter'), ('second', 'Second Quarter'), ('third', 'Third Quarter'), ('fourth', 'Fourth Quarter')], 
                                   "Quarter", required=True),
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
        'classification_ids': fields.many2many('account.budget.classification', 'account_quarter_classification_rel', 
                                                 'budget_report_id', 'classification_id', 'Classification', required=True),
    }

    _defaults = {
        'filter': 'filter_period',
        'first_fiscalyear': _get_fiscalyear_id,
        'chart_account_id': _get_account,
        'chart_analytic_account_id': _get_analytic_account,
        'type_selection': 'detail',
        'report_name': 'compare',
        'accuracy': 1,
        'size': 'A4',
        'landscape': True,
    }


    def onchange_filter(self, cr, uid, ids, filter='filter_no', fiscalyear_id=False, context=None):
        """
        Method to set filters defaults values when changing the filter type as:
        1. if filter_no: emptying date_from, date_to, period_from & period_to
        2. if filter_period: 
            - Emptying date_from, date_to
            - Set the first period in the selected fiscal year in period_from field 
            - Set the current period in the selected fiscal year in period_to field 
        
        @return: dictionary of fields values
        """
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


    def onchange_quarter(self, cr, uid, ids, quarter, first_fiscalyear, context=None):
        """

        """
        res = {'value': {}}
        fiscal_year_obj = self.pool.get('account.fiscalyear')
        period_obj = self.pool.get('account.period')
        year = fiscal_year_obj.browse(cr, uid, first_fiscalyear, context=context).name
        date_start = ""
        date_stop = ""
        start_month = 1
        last_end_day = 1
        extra = 2
        if quarter == 'first':
            start_month = 1
            last_end_day = 30
            extra += 3
        elif quarter == 'second':
            start_month = 1
            last_end_day = 30
            extra += 6
        elif quarter == 'third':
            start_month = 1
            last_end_day = 31
            extra += 9
        elif quarter == 'fourth':
            start_month = 10
            last_end_day = 31
        elif quarter == 'all':
            start_month = 1
            last_end_day = 31
            extra += 9
        date_start += str(start_month) + " 1 " + str(year)
        date_stop += str(start_month + extra) + " " + str(last_end_day) + " " + str(year)
        date_object = datetime.strptime(date_start, '%m %d %Y')
        date_object = datetime.strptime(date_stop, '%m %d %Y')
        fiscalyear_id = fiscal_year_obj.search(cr, uid, [('name', '=', year)],context=context, limit=1)
        period_from = period_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear_id),('date_start', '=', date_start)],context=context, limit=1)
        period_to = period_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear_id),('date_stop', '=', date_stop)],context=context, limit=1)
        return {'value': {'period_from': period_from, 'period_to': period_to}}
        #return True


    def onchange_chart_account_id(self, cr, uid, ids, chart_account_id=False, context=None):
        """
        Method to set the selected chart of account company as company_id value in wizard
        
        @return: dictionary of company_id value
        """
        company = self.pool.get('account.account').browse(cr, uid, chart_account_id, context=context)
        return {'value': {'company_id': company and company.company_id.id or False}}

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear=False, context=None):
        """
        Method to reset filter, period_from & period_to value in wizard
        
        @return: dictionary of fields values
        """
        res = {'value': {'fiscalyear_id':fiscalyear}}
        if not fiscalyear:
            res['value'].update({'filter': 'filter_no', 'period_from': False, 'period_to': False})
        return res
    
    def print_report(self, cr, uid, ids, context=None):
        """
        Method to send wizards fields value to the report
        
        @return: dictionary call the report service 
        """
        data ={'form': self.read(cr, uid, ids, [])[0]}
        data['form'].update({'chart_account_id': data['form']['chart_account_id'] and data['form']['chart_account_id'][0],
                             'first_fiscalyear': data['form']['first_fiscalyear'] and data['form']['first_fiscalyear'][0],
                             'quarter': data['form']['quarter'] and data['form']['quarter'],
                             'classification_ids': data['form']['classification_ids'] and data['form']['classification_ids'],
                             'period_from': data['form']['period_from'] and data['form']['period_from'][0],
                             'period_to': data['form']['period_to'] and data['form']['period_to'][0],
                             'company_id': data['form']['company_id'] and data['form']['company_id'][0],
                             'type_selection': data['form']['type_selection'],
                             'chart_analytic_account_id': data['form']['chart_analytic_account_id'] and data['form']['chart_analytic_account_id'][0]})
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.budget.quarter', 'datas': data}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

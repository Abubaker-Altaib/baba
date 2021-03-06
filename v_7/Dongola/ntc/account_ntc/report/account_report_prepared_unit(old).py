# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import itertools
from operator import itemgetter
from datetime import datetime
from openerp.tools.translate import _
from report import report_sxw
import mx
from account_custom.common_report_header import common_report_header

class account_prepared_unit(report_sxw.rml_parse, common_report_header):

    globals()['total_plan'] = 0
    globals()['total_operation'] = 0
    globals()['total_balance'] = 0
    globals()['total_residual_balance'] = 0
    globals()['total_previous_balance'] = 0
    def __init__(self, cr, uid, name, context=None):
        super(account_prepared_unit, self).__init__(cr, uid, name, context=context)
        company = self.pool.get('res.users').browse(self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join((_('BUDGET REPORT'), company.name, company.currency_id.name))
        footer_date_time = self.formatLang(str(datetime.today()), date_time=True)
        self.localcontext.update({
            'report_name': _('Budget Report'),
            'budgets':self.get_budget,
            'budgets_line':self.get_budget_line,
            'get_account_code': self._get_account_code,
            'budgets_line_view':self.get_budget_line_view,
            'budget_total':self._budget_total,
            'types':self._types,
            'departments': self._get_department_budget,
            'company_detail':self._get_company_detail,
            'company_detail_total':self._get_company_detail_total
        })	
        self.context = context
        self.total = {'planned_amount':0.0, 'total_operation':0.0, 'confirm':0.0,
                      'balance':0.0, 'previous_balance':0.0 , 'residual_balance':0.0, 'bal_amount':0.0}
        self.dept_total = {'planned_amount':0.0, 'total_operation':0.0, 'confirm':0.0,
                           'balance':0.0, 'previous_balance':0.0 , 'residual_balance':0.0, 'bal_amount':0.0}

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
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', False)
        
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
        #self.analytic_child_ids = self._get_children_and_consol(self.cr, self.uid, self.analytic_account_ids, 'account.analytic.account', self.context)
        #self.account_child_ids = self._get_children_and_consol(self.cr, self.uid, self.account_ids, 'account.account', context=self.context)

        self.localcontext.update({
            'fiscalyear': self.get_fiscalyear_br(data),
            'start_period': self.get_start_period_br(data),
            'stop_period': self.get_end_period_br(data),
            'chart_account': self._get_chart_account_id_br(data),
            #'accounts': self.account_child_ids,
           # 'analytic_accounts': self.analytic_child_ids,
            'periods': self.period_ids,
            'cost_center': cost_center,
            'accuracy': form.get('accuracy',1),
        })
        return super(account_prepared_unit, self).set_context(objects, data, ids, report_type=report_type)



    def _get_account_code(self, data):
        if data['closure']:
           return data['closure']

    def _get_children_and_consol_view(self, cr, uid, ids,code, context=None):
        # this function search for all the children and all consolidated children (recursively) of the given account ids
        
        ids2 = self.pool.get('account.account').search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        ids3 = []
        for rec in self.pool.get('account.account').browse(cr, uid, ids2, context=context):
            for child in rec.child_consol_ids:
                ids3.append(child.id)
        if ids3:
            ids3 = self._get_children_and_consol(cr, uid, ids3, context)
 
        return ids2 + ids3

    def _get_children_and_consol(self, cr, uid, ids,code, context=None):
        # this function search for all the children and all consolidated children (recursively) of the given account ids
        
        ids2 = self.pool.get('account.account').search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        ids3 = []
        for rec in self.pool.get('account.account').browse(cr, uid, ids2, context=context):
            for child in rec.child_consol_ids:
                ids3.append(child.id)
        if ids3:
            ids3 = self._get_children_and_consol(cr, uid, ids3, context)
        ids4 = self.pool.get('account.account').search(cr, uid, [('code', '=', code)], context=context)
        return ids2 + ids3 + ids4

    def _get_children_and_consol_analytic(self, cr, uid, ids, context=None):
        # this function search for all the children and (recursively) of the given analytic account ids
        if ids:
            ids2 = self.pool.get('account.analytic.account').search(cr, uid, [('parent_id', 'child_of', ids)], context=context)            
        return ids2

# # # # # # #  '1' Cost Center Details  # # # # # # #
    def get_budget(self, form):
        analytic_account_pool = self.pool.get('account.analytic.account')
        analytic_account_id=form['chart_analytic_account_id']
        name=analytic_account_pool.browse(self.cr, self.uid, analytic_account_id, context=self.context).name
        analytic_account_ids = self.pool.get('account.analytic.account').search(self.cr, self.uid, [('id', 'child_of', analytic_account_id)], context=self.context)
        analytic_account_ids=self._get_children_and_consol_analytic(self.cr, self.uid,analytic_account_ids)
        res=[]
        res.append({
            'name':name, 'child_ids': analytic_account_ids           })
        return res

    def _types(self,form,child_ids):

        budget_pool = self.pool.get('account.budget')
        move_line_pool = self.pool.get('account.move.line')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', False)
        fiscalyear_id = form.get('fiscalyear_id', False)
        fiscalyear_date_start = fiscalyear_pool.browse(self.cr, self.uid, fiscalyear_id, context=self.context).date_start
        budget = []
        types=[]
        budget_ids = budget_pool.search(self.cr, self.uid, [('analytic_account_id', 'in', child_ids)], context=self.context)
        #Use this code for none Accounting user

        company_id = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=self.context).company_id.id
        
        company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('id', 'child_of', company_id),('id', '!=', company_id)], context=self.context)
        if form['unit_type']:
           types.append(form['unit_type'])
        else:
           types=('locality','ministry')  
 
        for type in types:

            balance = 0
            planned = 0
            total_operation = 0
            relative=0
            ratio=0
            if type=='locality':
                type_c='loc_sub'
            else:
                type_c='other'
            company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('id', 'child_of', company_id),('id', '!=', company_id),('type', '=',type_c) ], context=self.context)

            lines=  self.pool.get('account.budget.lines').search(self.cr, self.uid, [('account_budget_id', 'in', budget_ids),('company_id', 'in', company_ids)], context=self.context)
            print budget_ids,type_c,company_ids,len(lines),"llllllllllllllllllllllooooooooo"
            for line in self.pool.get('account.budget.lines').browse(self.cr, self.uid, lines, context=self.context):
                planned+=line.planned_amount
                total_operation+=line.total_operation    
                move = move_line_pool.search(self.cr, self.uid, [('analytic_account_id', 'in', child_ids),('date','>=',date_from),('date','<=',date_to),('state','=','valid'),('company_id', 'in', company_ids)] ,context=self.context)
                bl = 0
                sign = line.general_account_id.user_type.report_type in ('income','liability') and -1 or 1
                for oo in move_line_pool.browse(self.cr, self.uid, move, context=self.context):
                    bl += oo.debit - oo.credit
                balance = sign*bl
                balance = abs(balance)
                date_from1 = mx.DateTime.Parser.DateTimeFromString(date_from)
                date_to1 = mx.DateTime.Parser.DateTimeFromString(date_to)
                month_from=date_from1.month
                month_to=date_to1.month
                rate=month_to-month_from+1
                relative=round(((planned+total_operation)/12)*rate,2)
                ratio=round((balance/relative)*100,2)
            budget.append({ 'name':type,
           'balance':balance,'planned':planned,'total_operation':total_operation,'relative':relative,'ratio':ratio})
            print"pppppppppppppppppppppppppppppppppp",budget
        return budget
   
    def get_budget_line_view(self, form, child_ids,type):
        budget_pool = self.pool.get('account.budget')
        move_line_pool = self.pool.get('account.move.line')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        dept_pool = self.pool.get('hr.department')
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', False)
        fiscalyear_id = form.get('fiscalyear_id', False)
        fiscalyear_date_start = fiscalyear_pool.browse(self.cr, self.uid, fiscalyear_id, context=self.context).date_start
        budgets = []
        
        budget_ids = budget_pool.search(self.cr, self.uid, [('analytic_account_id', 'in', child_ids)], context=self.context)
        buds = budget_pool.browse(self.cr, self.uid, budget_ids, context=self.context)
        #budget_ids = ','.join(map(str, budget_ids))
        ############################################
        
        companies=[]
        company_id = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=self.context).company_id.id
        if form['unit_type']:
            company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('id', 'child_of', company_id),('id', '!=', company_id),('type', '=',form['unit_type']) ], context=self.context)
        else:
            company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('id', 'child_of', company_id),('id', '!=', company_id),('type', '=',type)], context=self.context)
 
        for b in self.pool.get('res.company').browse(self.cr, self.uid, company_ids, context=self.context):
             
            planned_amount=0
            balance=0.0
            sub_company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('parent_id', '=', b.id) ], context=self.context)
            analytic_account_ids= self.pool.get('account.analytic.account').search(self.cr, self.uid, [('id', 'in', child_ids),('company_id', 'in', sub_company_ids)]) 
 
            if not analytic_account_ids:
               continue
            budget_id2s = budget_pool.search(self.cr, self.uid, [('analytic_account_id', 'in', analytic_account_ids)], context=self.context)
            total_operation=0.0
            analytic_account_ids = ','.join(map(str,  analytic_account_ids))
            for budget in self.pool.get('account.budget').browse(self.cr, self.uid, budget_id2s, context=self.context):
                for line in budget.account_budget_line:
                    planned_amount+=line.planned_amount
                    total_operation+=line.total_operation
            self.cr.execute("select (sum(debit)-sum(credit)) as bl\
                   from account_move_line  where analytic_account_id in (%s)  and date>= '%s' and date <= '%s'" % (analytic_account_ids,date_from,date_to)) 
            move=self.cr.fetchall() 
            bl = move[0][0]           
            if bl:
                balance = abs(bl)   
            date_from1 = mx.DateTime.Parser.DateTimeFromString(date_from)
            date_to1 = mx.DateTime.Parser.DateTimeFromString(date_to)
            month_from=date_from1.month
            month_to=date_to1.month
            rate=month_to-month_from+1
            relative=round(((planned_amount+total_operation)/12)*rate,2)
            if  relative==0:
                ratio=0
            else:
                ratio=round((balance/relative)*100,2) 
            companies.append({
            'name':b.name, 'planned':planned_amount,'relative':relative,'balance':balance,'ratio':ratio, })
        return companies


    def get_budget_line(self, form, child_ids,parent_id):
        budget_pool = self.pool.get('account.budget')
        move_line_pool = self.pool.get('account.move.line')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', False)
        fiscalyear_id = form.get('fiscalyear_id', False)
        fiscalyear_date_start = fiscalyear_pool.browse(self.cr, self.uid, fiscalyear_id, context=self.context).date_start
         
        budget_ids = budget_pool.search(self.cr, self.uid, [('analytic_account_id', 'in', child_ids)], context=self.context)
        budget_ids = ','.join(map(str, budget_ids))
         
        # get account childs of parent_id
        childs = self.pool.get('account.account').search(self.cr, self.uid, [('parent_id', '=', parent_id)], context=self.context)
 
        budget=[]
        child_ids = ','.join(map(str, child_ids))
        for acc in self.pool.get('account.account').browse(self.cr, self.uid,childs, context=self.context):
            planned_amount=0.0
            balance=0.0
            total_operation=0.0
            relative=0.0
            ratio=0.0                       
            consol_ids= self._get_children_and_consol(self.cr, self.uid,acc.id,acc.code)
 
            consol_ids = ','.join(map(str, consol_ids))
            self.cr.execute("select sum(planned_amount) as planned_amount ,sum(total_operation) as total_operation\
                      from account_budget_lines where account_budget_id in (%s)  and general_account_id in (%s) " % (budget_ids,consol_ids)) 
            amounts=self.cr.fetchall()     
            planned_amount= amounts[0][0] or 0.0
            total_operation=amounts[0][1] or 0.0           
            # get moves of consolidation accounts
            self.cr.execute("select (sum(debit)-sum(credit)) as bl\
                   from account_move_line  where analytic_account_id in (%s)  and account_id in (%s)  and date>= '%s' and date <= '%s'" % (child_ids,consol_ids,date_from,date_to)) 
            move=self.cr.fetchall() 
            bl = move[0][0]           
            if bl:
                balance = abs(bl)
            date_from1 = mx.DateTime.Parser.DateTimeFromString(date_from)
            date_to1 = mx.DateTime.Parser.DateTimeFromString(date_to)
            month_from=date_from1.month
            month_to=date_to1.month
            rate=month_to-month_from+1
            if planned_amount>0:
                relative=round(((planned_amount+total_operation)/12)*rate,2)
                ratio=round((balance/relative)*100,2)
            budget.append({
            'account_name':acc.name,            'account_code':acc.code,'account_id':acc.id,'balance':balance,'planned':planned_amount,'total_operation':total_operation,'relative':relative,'ratio':ratio})
        budget=filter(lambda acc: acc['planned']!=0,budget)
        return budget


    def _budget_total(self,form,child_ids):

        budget_pool = self.pool.get('account.budget')
        move_line_pool = self.pool.get('account.move.line')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', False)
        fiscalyear_id = form.get('fiscalyear_id', False)
        fiscalyear_date_start = fiscalyear_pool.browse(self.cr, self.uid, fiscalyear_id, context=self.context).date_start
        budget = []
         
        budget_ids = budget_pool.search(self.cr, self.uid, [('analytic_account_id', 'in', child_ids)], context=self.context)
        #Use this code for none Accounting user
 
        types=[]
        balance = 0
        planned = 0
        if form['unit_type']:
           types.append(form['unit_type'])
        else:
           types=('locality','ministry','other')  
        company_id = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=self.context).company_id.id
        if form['unit_type']:
            company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('id', 'child_of', company_id),('id', '!=', company_id),('type', 'in',types) ], context=self.context)
        else:
            company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('id', 'child_of', company_id),('id', '!=', company_id)], context=self.context)
        total_operation = 0
        relative=0
        ratio=0
        lines=  self.pool.get('account.budget.lines').search(self.cr, self.uid, [('account_budget_id', 'in', budget_ids),('company_id', 'in', company_ids)], context=self.context)
        for line in self.pool.get('account.budget.lines').browse(self.cr, self.uid, lines, context=self.context):
            planned+=line.planned_amount
            total_operation+=line.total_operation 
 
            move = move_line_pool.search(self.cr, self.uid, [('analytic_account_id', 'in', child_ids),('date','>=',date_from),('date','<=',date_to),('state','=','valid'),('company_id', 'in', company_ids)] ,context=self.context)
 
            bl = 0
            sign = line.general_account_id.user_type.report_type in ('income','liability') and -1 or 1
            for oo in move_line_pool.browse(self.cr, self.uid, move, context=self.context):
                bl += oo.debit - oo.credit
            balance = sign*bl
            balance = abs(balance)
            date_from1 = mx.DateTime.Parser.DateTimeFromString(date_from)
            date_to1 = mx.DateTime.Parser.DateTimeFromString(date_to)
            month_from=date_from1.month
            month_to=date_to1.month
            rate=month_to-month_from+1
            relative=round(((planned+total_operation)/12)*rate,2)
            ratio=round((balance/relative)*100,2)
 
        budget.append({
       'balance':balance,'planned':planned,'total_operation':total_operation,'relative':relative,'ratio':ratio})
   
        return budget

    

# # # # # # #  '2' Cost Center Total  # # # # # # #
    def _get_department_budget(self, form):
        res = []
        budget_line_pool = self.pool.get('account.budget.lines')      
        period_pool = self.pool.get('account.period')
        analytic_pool = self.pool.get('account.analytic.account')
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.li ne')
        analytic_ids = form.get('analytic_account_ids', [])
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', False)
        result = {}
        for analytic_id in analytic_ids:
            child_ids = self._get_children_and_consol(self.cr, self.uid, [analytic_id], 'account.analytic.account', context=self.context)
            lines = budget_line_pool.search(self.cr, self.uid, [('account_budget_id.period_id', 'in', self.period_ids), ('account_budget_id.analytic_account_id', 'in', child_ids)], context=self.context)
            analytic_name = analytic_pool.browse(self.cr, self.uid, analytic_id, context=self.context).name
            budget = {'name':analytic_name, 'planned_amount':0.0, 'total_operation':0.0, 'confirm':0.0, 'balance':0.0, 'residual_balance':0.0}
            balance = 0
            planned = 0
            residual_balance = 0
            for line in budget_line_pool.browse(self.cr, self.uid, lines, context=self.context):
                if date_from and date_to:
                    self.cr.execute("SELECT distinct COALESCE(CASE WHEN per.date_start > %s and per.date_stop < %s THEN l.planned_amount  WHEN %s BETWEEN per.date_start and per.date_stop and %s BETWEEN per.date_start and date_stop THEN (l.planned_amount*(CAST(%s as date)-CAST(%s AS date)+1))/(per.date_stop-per.date_start+1) WHEN %s BETWEEN per.date_start and per.date_stop THEN (l.planned_amount*(per.date_stop-%s+1))/(per.date_stop-per.date_start+1) WHEN %s BETWEEN per.date_start and per.date_stop THEN (l.planned_amount*(%s-per.date_start+1))/(per.date_stop-per.date_start+1) ELSE 0.0 END) as planned FROM account_budget_lines l LEFT JOIN account_budget b \
                ON (b.id = l.account_budget_id) LEFT JOIN account_period per ON (per.id = b.period_id) \
                where l.id=%s", (date_from,date_to,date_from,date_to,date_to,date_from,date_from,date_from,date_to,date_to,line.id))
                    res_plan = self.cr.dictfetchall()
                    for plan in res_plan: 
                        planned = plan['planned']
                    sign = line.general_account_id.user_type.report_type in ('income','liability') and -1 or 1
                    move = move_line_pool.search(self.cr, self.uid, [('analytic_account_id', 'in', child_ids),('date','>=',date_from),('date','<=',date_to),('account_id', '=', line.general_account_id.id),('state','=','valid')], context=self.context)
                    bl = 0
                    for oo in move_line_pool.browse(self.cr, self.uid, move, context=self.context):
                        bl += oo.debit - oo.credit
                    balance = sign*bl
                    residual_balance = planned + line.total_operation - balance
                else:
                    balance = line.balance
                    planned = line.planned_amount
                    residual_balance = line.residual_balance
                budget['planned_amount'] += planned
                budget['total_operation'] += line.total_operation
                budget['confirm'] += 'confirm' in budget_line_pool._columns and line.confirm or 0.0
                budget['balance'] += balance
                budget['residual_balance'] += residual_balance
            
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
                    ORDER BY     sequence,acc.code', (tuple(ids),))
        return [acct[0] for acct in cr.fetchall()]   

    def _get_company_detail(self, form, analytic_acc=False):
        res = []
        account_pool = self.pool.get('account.account')
        budget_line_pool = self.pool.get('account.budget.lines')
        move_line_pool = self.pool.get('account.move.line')     
        general_account = self._sort_filter(self.cr, self.uid, self.account_child_ids, self.context)
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', False)
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
            balance = 0
            planned = 0
            residual_balance = 0 
            if lines:
                for line in budget_line_pool.browse(self.cr, self.uid, lines, self.context):
                    if date_from and date_to:
                        self.cr.execute("SELECT distinct COALESCE(CASE WHEN per.date_start > %s and per.date_stop < %s THEN l.planned_amount  WHEN %s BETWEEN per.date_start and per.date_stop and %s BETWEEN per.date_start and date_stop THEN (l.planned_amount*(CAST(%s as date)-CAST(%s AS date)+1))/(per.date_stop-per.date_start+1) WHEN %s BETWEEN per.date_start and per.date_stop THEN (l.planned_amount*(per.date_stop-%s+1))/(per.date_stop-per.date_start+1) WHEN %s BETWEEN per.date_start and per.date_stop THEN (l.planned_amount*(%s-per.date_start+1))/(per.date_stop-per.date_start+1) ELSE 0.0 END) as planned FROM account_budget_lines l LEFT JOIN account_budget b \
                ON (b.id = l.account_budget_id) LEFT JOIN account_period per ON (per.id = b.period_id) \
                where l.id=%s", (date_from,date_to,date_from,date_to,date_to,date_from,date_from,date_from,date_to,date_to,line.id))
                        res_plan = self.cr.dictfetchall()
                        for plan in res_plan:
                            planned = plan['planned']
                        sign = line.general_account_id.user_type.report_type in ('income','liability') and -1 or 1
                        move = move_line_pool.search(self.cr, self.uid, [('analytic_account_id', 'in', self.analytic_child_ids),('date','>=',date_from),('date','<=',date_to),('account_id', '=', line.general_account_id.id),('state','=','valid')], context=self.context)
                        bl = 0
                        for oo in move_line_pool.browse(self.cr, self.uid, move, context=self.context):
                            bl += oo.debit - oo.credit
                        balance = sign*bl
                        residual_balance = planned + line.total_operation - balance
                    else:
                        balance = line.balance
                        planned = line.planned_amount
                        residual_balance = line.residual_balance
                    account_budget['planned_amount'] += planned
                    account_budget['total_operation'] += line.total_operation
                    account_budget['confirm'] += 'confirm' in budget_line_pool._columns and line.confirm or 0.0
                    account_budget['balance'] += balance
                    account_budget['residual_balance'] += residual_balance
                    
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
        move_line_pool = self.pool.get('account.move.line')     
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', False)
        class_ids = budget_classificaiton_pool.search(self.cr, self.uid, [], context=self.context)
        class_objs = budget_classificaiton_pool.browse(self.cr, self.uid, class_ids, self.context)
        total_budget = {'name':'Total', 'planned_amount':0.0, 'total_operation':0.0, 'confirm':0.0, 'balance':0.0, 'residual_balance':0.0}
        for  class_obj in class_objs:
            account_budget = {'code':class_obj.code, 'name':class_obj.name, 'planned_amount':0.0, 'total_operation':0.0, 'confirm':0.0, 'balance':0.0, 'residual_balance':0.0}
            acc_ids = account_pool.search(self.cr, self.uid, [('id', 'in', self.account_child_ids), ('budget_classification', '=', class_obj.id)])

            lines = budget_line_pool.search(self.cr, self.uid, [('account_budget_id.period_id', 'in', self.period_ids), ('account_budget_id.analytic_account_id', 'in', self.analytic_child_ids), ('general_account_id', 'in', acc_ids)], context=self.context)
            line_obj = budget_line_pool.browse(self.cr, self.uid, lines, self.context)
            balance = 0
            planned = 0
            residual_balance = 0
            for line in line_obj:
                if date_from and date_to:
                    self.cr.execute("SELECT distinct COALESCE(CASE WHEN per.date_start > %s and per.date_stop < %s THEN l.planned_amount  WHEN %s BETWEEN per.date_start and per.date_stop and %s BETWEEN per.date_start and date_stop THEN (l.planned_amount*(CAST(%s as date)-CAST(%s AS date)+1))/(per.date_stop-per.date_start+1) WHEN %s BETWEEN per.date_start and per.date_stop THEN (l.planned_amount*(per.date_stop-%s+1))/(per.date_stop-per.date_start+1) WHEN %s BETWEEN per.date_start and per.date_stop THEN (l.planned_amount*(%s-per.date_start+1))/(per.date_stop-per.date_start+1) ELSE 0.0 END) as planned FROM account_budget_lines l LEFT JOIN account_budget b \
                ON (b.id = l.account_budget_id) LEFT JOIN account_period per ON (per.id = b.period_id) \
                where l.id=%s", (date_from,date_to,date_from,date_to,date_to,date_from,date_from,date_from,date_to,date_to,line.id))
                    res_plan = self.cr.dictfetchall()
                    for plan in res_plan:
                        planned = plan['planned']
                    sign = line.general_account_id.user_type.report_type in ('income','liability') and -1 or 1
                    move = move_line_pool.search(self.cr, self.uid, [('analytic_account_id', 'in', self.analytic_child_ids),('date','>=',date_from),('date','<=',date_to),('account_id', '=', line.general_account_id.id),('state','=','valid')], context=self.context)
                    bl = 0
                    for oo in move_line_pool.browse(self.cr, self.uid, move, context=self.context):
                        bl += oo.debit - oo.credit
                    balance = sign*bl
                    residual_balance = planned + line.total_operation - balance
                else:
                    balance = line.balance
                    planned = line.planned_amount
                    residual_balance = line.residual_balance
                account_budget['planned_amount'] += planned
                account_budget['total_operation'] += line.total_operation
                account_budget['confirm'] += 'confirm' in budget_line_pool._columns and line.confirm or 0.0
                account_budget['balance'] += balance
                account_budget['residual_balance'] += residual_balance
            res.append(account_budget)
    
            total_budget['planned_amount'] += account_budget['planned_amount']
            total_budget['total_operation'] += account_budget['total_operation']
            total_budget['confirm'] += account_budget['confirm']
            total_budget['balance'] += account_budget['balance']
            total_budget['residual_balance'] += account_budget['residual_balance']
        res.append(total_budget)
        return res

report_sxw.report_sxw('report.account.prepared.unit',  'account.report.budget', 'addons/account_ntc/report/account_report_prepared_unit.rml', parser=account_prepared_unit , header='external')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


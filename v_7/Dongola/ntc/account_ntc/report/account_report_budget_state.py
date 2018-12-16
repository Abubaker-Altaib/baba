# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import itertools
from openerp.osv import fields, osv, orm
from operator import itemgetter
from datetime import datetime
from openerp.tools.translate import _
from report import report_sxw
import mx
from account_custom.common_report_header import common_report_header

class account_budget_state(report_sxw.rml_parse, common_report_header):

    globals()['total_plan'] = 0
    globals()['total_operation'] = 0
    globals()['total_balance'] = 0
    globals()['total_residual_balance'] = 0
    globals()['total_previous_balance'] = 0
    def __init__(self, cr, uid, name, context=None):
        super(account_budget_state, self).__init__(cr, uid, name, context=context)
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
        return super(account_budget_state, self).set_context(objects, data, ids, report_type=report_type)



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
        ids2=[]
      
        if ids:
            ids2 = self.pool.get('account.analytic.account').search(cr, uid, [('parent_id', 'child_of', ids)], context=context) 
        return ids2

# # # # # # #  '1' Cost Center Details  # # # # # # #
    def get_budget(self, form):
        types=[]
        if form['unit_type']:
           types.append(form['unit_type'])
        else:
           types=('locality','ministry','other') 
        company_id = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=self.context).company_id.id 
        c_type = self.pool.get('res.company').browse(self.cr, self.uid, company_id, context=self.context).type
        if c_type=='locality':
            company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('id', 'child_of', company_id),('id', '!=', company_id), ], context=self.context)
        else:
            company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('id', 'child_of', company_id),('id', '!=', company_id) ], context=self.context)
        
 
        analytic_account_pool = self.pool.get('account.analytic.account')
        analytic_account_id=form['chart_analytic_account_id']
        name=analytic_account_pool.browse(self.cr, self.uid, analytic_account_id, context=self.context).name
        analytic_account_ids = self.pool.get('account.analytic.account').search(self.cr, self.uid, [('id', 'child_of', analytic_account_id),('company_id', 'in', company_ids)], context=self.context)
        analytic_account_ids=self._get_children_and_consol_analytic(self.cr, self.uid,analytic_account_ids)
        res=[]
        res.append({
            'name':name, 'child_ids': analytic_account_ids           })
 
        return res
        
    def get_budget_line_view(self, form, child_ids):
        if not child_ids:
            raise osv.except_osv(_('Warning!'), _("There is no childs associated with this analytic account ")%(child_ids))
        budget_pool = self.pool.get('account.budget')
        move_line_pool = self.pool.get('account.move.line')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', False)
        fiscalyear_id = form.get('fiscalyear_id', False)
        fiscalyear_date_start = fiscalyear_pool.browse(self.cr, self.uid, fiscalyear_id, context=self.context).date_start
        budgets = []
        balance = 0
        planned = 0
        residual_balance = 0
        budget_ids = budget_pool.search(self.cr, self.uid, [('analytic_account_id', 'in', child_ids)], context=self.context)
        if not  budget_ids:
            raise orm.except_orm(_('Warning!'), _("There is no budgets  associated with these analytic accounts "))
        buds = budget_pool.browse(self.cr, self.uid, budget_ids, context=self.context)
        budget_ids = ','.join(map(str, budget_ids))
 
        self.cr.execute("select general_account_id as acc_id from account_budget_lines where account_budget_id in (%s) order by code " % (budget_ids,))
 
        account_ids =  self.cr.fetchall()



        acc_ids=[ac[0] for ac in account_ids]
        acc_ids = ','.join(map(str, acc_ids))
        self.cr.execute("select  distinct code from account_account where id in (%s) order by code  " % (acc_ids,))
        account_ids2 = self.cr.fetchall()
        account_ids2 = ','.join(map(str, account_ids2))
        self.cr.execute("select  distinct code from account_account where id in (%s) order by code  " % (acc_ids,))
        account_ids2 = self.cr.fetchall()
        accounts=[]
        parents=[]
        #parents_uniqe=[54499,54500]
        parents_uniqe = []
        budget=[]
        company_id = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=self.context).company_id.id
        child_ids = ','.join(map(str, child_ids))
        main_acc = []

        for code in account_ids2:
            account_consol_id = self.pool.get('account.account').search(self.cr, self.uid, [('code', 'in', code),('company_id','=',company_id)], context=self.context)
            if not  account_consol_id:
               raise osv.except_osv(_('Warning!'), _("This account  (%s) doesn't exist in this unit ,please add it !") % (code,))
            name =self.pool.get('account.account').browse(self.cr, self.uid, account_consol_id[0], context=self.context ).name  
            code =self.pool.get('account.account').browse(self.cr, self.uid, account_consol_id[0], context=self.context ).code 
            acc_id =self.pool.get('account.account').browse(self.cr, self.uid, account_consol_id[0], context=self.context ).id
            parent_id = self.pool.get('account.account').browse(self.cr, self.uid, account_consol_id[0], context=self.context ).parent_id.id
            if not parent_id in parents:
                parents.append(parent_id)   
        for parent in parents:
            if not parent in parents_uniqe:
                parents_uniqe.append(parent)
                #just get all main acc
                main_acc.append(parent)

        planned_amount=0


        #get all parents of main acc
        all_parent = []
        for ac in main_acc:
            #all_parent.append(ac)
            all_parent.append(self.pool.get('account.account').browse(self.cr, self.uid,
                                                            ac,
                                                            context=self.context).code)
            have_parent = True
            next_child = ac
            while(have_parent):
                wh_ac = self.pool.get('account.account').browse(self.cr, self.uid,
                                                            next_child,
                                                            context=self.context)
                if not wh_ac.parent_id.id:

                    have_parent = False
                else:
                    all_parent.append(wh_ac.parent_id.code)
                    next_child = wh_ac.parent_id.id
        # get rid of deplication in accounts_parents
        myset = set(all_parent)
        all_parent = list(myset)
        #sort accounts by
        all_parent = sorted(all_parent)


        all_parent_copy = all_parent
        all_parent = []
        #after sorted accounts by level of code then gets id
        for parent in all_parent_copy:
 
            all_parent.append(self.pool.get('account.account').search(self.cr, self.uid, [('code','=',parent),('company_id','=',company_id)], context=self.context )[0])
 
        #get rid of first accounts because we don't need main root account
        all_parent.pop(0)
        for acc in self.pool.get('account.account').browse(self.cr, self.uid, all_parent, context=self.context ):
            planned=0
            planned_amount_min=0
            planned_amount_loc=0
            planned_amount_out=0
            planned_loc=0
            planned_min=0
            balance=0.0
            total_operation=0.0
            total_operation_min=0.0
            total_operation_loc=0.0
            all_parents=self.pool.get('account.account').search(self.cr, self.uid, [('code', 'like', acc.code),('company_id','child_of',company_id)], context=self.context)

            all_parents = ','.join(map(str, all_parents))
            self.cr.execute("select id from account_account  where   parent_id in (%s) " % (all_parents)) 
            all_accounts=self.cr.fetchall()
 
            all_accounts=[ac[0] for ac in all_accounts]
            all_accounts = ','.join(map(str, all_accounts))
            if len(all_accounts) > 0:
                self.cr.execute("select sum(planned_amount) as planned_amount ,sum(total_operation) as total_operation\
                          from account_budget_lines where account_budget_id in (%s)  and general_account_id in (%s) " % (budget_ids,all_accounts))

                amounts=self.cr.fetchall()
                if amounts[0][1] :
                    total_operation=amounts[0][1]
                if amounts[0][0] :
                    planned_amount= amounts[0][0]
                # get planned for ministries
                mins_company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('id', 'child_of', company_id),('id', '!=', company_id),('type', '=','other') ], context=self.context)
                #mins_company_ids_subs= self.pool.get('res.company').search(self.cr, self.uid, [('parent_id', 'in', mins_company_ids) ], context=self.context)
                mins_company_ids_subs = ','.join(map(str, mins_company_ids)) 
                self.cr.execute("select sum(planned_amount) as planned_amount ,sum(total_operation) as total_operation\
                          from account_budget_lines where account_budget_id in (%s)  and general_account_id in (%s) and company_id in (%s) " % (budget_ids,all_accounts,mins_company_ids_subs))

                min_amounts=self.cr.fetchall()
                if min_amounts[0][1] :
                    total_operation_min=min_amounts[0][1]
                if min_amounts[0][0] :
                    planned_amount_min= min_amounts[0][0]
                # get planned for localities 
                loc_company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('id', 'child_of', company_id),('id', '!=', company_id),('type', '=','loc_sub') ], context=self.context)
                #loc_company_ids_subs= self.pool.get('res.company').search(self.cr, self.uid, [('parent_id', 'in', loc_company_ids) ], context=self.context)
                loc_company_ids_subs = ','.join(map(str, loc_company_ids)) 
                self.cr.execute("select sum(planned_amount) as planned_amount ,sum(total_operation) as total_operation\
                          from account_budget_lines where account_budget_id in (%s)  and general_account_id in (%s) and company_id in (%s) " % (budget_ids,all_accounts,loc_company_ids_subs))

                self.cr.execute("select sum(planned_amount) as planned_amount ,sum(total_operation) as total_operation\
                          from account_budget_lines where account_budget_id in (%s)  and general_account_id in (%s) and company_id in (%s) " % (budget_ids,all_accounts,loc_company_ids_subs))

                loc_amounts=self.cr.fetchall()
                if amounts[0][1] :
                    total_operation_loc=loc_amounts[0][1]
                if amounts[0][0] :
                    planned_amount_loc= loc_amounts[0][0]
                out_company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('id', 'child_of', company_id),('out_budget', '=', True)])
                out_company_ids = ','.join(map(str, out_company_ids)) 
                self.cr.execute("select sum(planned_amount) as planned_amount ,sum(total_operation) as total_operation\
                          from account_budget_lines where account_budget_id in (%s)  and general_account_id in (%s) and  company_id in (%s) " % (budget_ids,all_accounts,out_company_ids))

                out_amounts=self.cr.fetchall()
                if out_amounts[0][0] :
                    planned_amount_out= out_amounts[0][0]

                account_ids=self._get_children_and_consol(self.cr, self.uid,acc.id,acc.code)
                #c_type = self.pool.get('res.company').browse(self.cr, self.uid, company_id, context=self.context).type
                #if c_type=='main':
                 #   self.cr.execute("select id from account_account  where   parent_id in (%s) " % (all_parents)) 
                ids4 = ','.join(map(str, account_ids))

                self.cr.execute("select (sum(debit)-sum(credit)) as bl\
                       from account_move_line  where analytic_account_id in (%s)  and account_id in (%s)  and date>= '%s' and date <= '%s'" % (child_ids,ids4,date_from,date_to))
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
                if relative != 0:
                    ratio=round((balance/relative)*100,2)
                else:
                    ratio = 0
                #just to get white childs in report for main_accounts
                is_main=False
                if acc.id in main_acc:
                    is_main = True
                    if is_main == True:
                        childs = self.pool.get('account.account').search(self.cr, self.uid, [('parent_id','=',acc.id)],
                                                                            context=self.context)
                        for child in childs:
                            if child in main_acc:
                                is_main =False

                budget.append({
               'is_main':is_main, 'account_name':acc.name,            'account_code':acc.code,'account_id':acc.id,'balance':balance,'planned_out':planned_amount_out,'planned_min':planned_amount_min,'planned_loc':planned_amount_loc,'planned':planned_amount,'total_operation':total_operation,'total_operation_min':total_operation_min,'total_operation_loc':total_operation_loc,'relative':relative,'ratio':round(ratio,1)})

        return budget


    def get_budget_line(self, form, child_ids,parent_id,is_main):
        budget_pool = self.pool.get('account.budget')
        move_line_pool = self.pool.get('account.move.line')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', False)
        fiscalyear_id = form.get('fiscalyear_id', False)
        fiscalyear_date_start = fiscalyear_pool.browse(self.cr, self.uid, fiscalyear_id, context=self.context).date_start
        company_id = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=self.context).company_id.id
         
        budget_ids = budget_pool.search(self.cr, self.uid, [('analytic_account_id', 'in', child_ids)], context=self.context)
        budget_ids = ','.join(map(str, budget_ids))
         
        # get account childs of parent_id
        childs = self.pool.get('account.account').search(self.cr, self.uid, [('parent_id', '=', parent_id)], context=self.context)
 
        budget=[]

        if is_main:
            child_ids = ','.join(map(str, child_ids))
            for acc in self.pool.get('account.account').browse(self.cr, self.uid,childs, context=self.context):
                planned_amount=0.0
                planned_amount_min=0.0
                planned_amount_loc=0.0
                planned_amount_out=0.0
                balance=0.0
                total_operation=0.0
                total_operation_min=0.0
                total_operation_loc=0.0
                relative=0.0
                ratio=0.0
                consol_ids= self._get_children_and_consol(self.cr, self.uid,acc.id,acc.code)

                consol_ids = ','.join(map(str, consol_ids))
                self.cr.execute("select sum(planned_amount) as planned_amount ,sum(total_operation) as total_operation\
                          from account_budget_lines where account_budget_id in (%s)  and general_account_id in (%s) " % (budget_ids,consol_ids))
                amounts=self.cr.fetchall()
                planned_amount= amounts[0][0] or 0.0
                total_operation=amounts[0][1] or 0.0
                # get planned for ministries
                mins_company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('id', 'child_of', company_id),('id', '!=', company_id),('type', '=','other'),('out_budget', '=',False) ], context=self.context)
                #mins_company_ids_subs= self.pool.get('res.company').search(self.cr, self.uid, [('parent_id', 'in', mins_company_ids) ], context=self.context)
                mins_company_ids_subs = ','.join(map(str, mins_company_ids)) 
                self.cr.execute("select sum(planned_amount) as planned_amount ,sum(total_operation) as total_operation\
                          from account_budget_lines where account_budget_id in (%s)  and general_account_id in (%s) and company_id in (%s) " % (budget_ids,consol_ids,mins_company_ids_subs))

                min_amounts=self.cr.fetchall()
                if min_amounts[0][1] :
                    total_operation_min=min_amounts[0][1]
                if min_amounts[0][0] :
                    planned_amount_min= min_amounts[0][0]
                # get planned for localities 
                loc_company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('id', 'child_of', company_id),('id', '!=', company_id),('type', '=','loc_sub') ], context=self.context)
                #loc_company_ids_subs= self.pool.get('res.company').search(self.cr, self.uid, [('parent_id', 'in', loc_company_ids) ], context=self.context)
                loc_company_ids_subs = ','.join(map(str, loc_company_ids)) 
                self.cr.execute("select sum(planned_amount) as planned_amount ,sum(total_operation) as total_operation\
                          from account_budget_lines where account_budget_id in (%s)  and general_account_id in (%s) and company_id in (%s) " % (budget_ids,consol_ids,loc_company_ids_subs))

                loc_amounts=self.cr.fetchall()
                if amounts[0][1] :
                    total_operation_loc=loc_amounts[0][1]
                if amounts[0][0] :
                    planned_amount_loc= loc_amounts[0][0]
                # get planned for out budget 
                out_company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('id', 'child_of', company_id),('id', '!=', company_id),('out_budget', '=',True) ], context=self.context)
                #loc_company_ids_subs= self.pool.get('res.company').search(self.cr, self.uid, [('parent_id', 'in', loc_company_ids) ], context=self.context)
                out_company_ids = ','.join(map(str, out_company_ids)) 
                self.cr.execute("select sum(planned_amount) as planned_amount ,sum(total_operation) as total_operation\
                          from account_budget_lines where account_budget_id in (%s)  and general_account_id in (%s) and company_id in (%s) " % (budget_ids,consol_ids,out_company_ids))

                out_amounts=self.cr.fetchall()
                 
                if out_amounts[0][0] :
                    planned_amount_out= out_amounts[0][0]
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
                'account_name':acc.name,            'account_code':acc.code,'account_id':acc.id,'balance':balance,'planned':planned_amount,'planned_out':planned_amount_out,'planned_min':planned_amount_min,'planned_loc':planned_amount_loc,'total_operation':total_operation,'total_operation_loc':total_operation_loc,'total_operation_min':total_operation_min,'relative':relative,'ratio':round(ratio,1)})
            budget=filter(lambda acc: acc['planned']!=0,budget)
        else:
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>ELSE ",parent_id
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
 
        
        balance = 0
        planned = 0
 
        total_operation = 0
        relative=0
        ratio=0
        lines=  self.pool.get('account.budget.lines').search(self.cr, self.uid, [('account_budget_id', 'in', budget_ids)], context=self.context)
        for line in self.pool.get('account.budget.lines').browse(self.cr, self.uid, lines, context=self.context):
            planned+=line.planned_amount
            total_operation+=line.total_operation 
 
            move = move_line_pool.search(self.cr, self.uid, [('analytic_account_id', 'in', child_ids),('date','>=',date_from),('date','<=',date_to),('state','=','valid')] ,context=self.context)
 
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
        move_line_pool = self.pool.get('account.move.line')
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

report_sxw.report_sxw('report.account.budget.state',  'account.report.budget', 'addons/account_ntc/report/account_report_budget_state.rml', parser=account_budget_state , header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


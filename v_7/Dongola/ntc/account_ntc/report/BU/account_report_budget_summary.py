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

class account_budget_summary(report_sxw.rml_parse, common_report_header):

    globals()['total_plan'] = 0
    globals()['total_operation'] = 0
    globals()['total_balance'] = 0
    globals()['total_residual_balance'] = 0
    globals()['total_previous_balance'] = 0
    def __init__(self, cr, uid, name, context=None):
        super(account_budget_summary, self).__init__(cr, uid, name, context=context)
        company = self.pool.get('res.users').browse(self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join((_('BUDGET REPORT'), company.name, company.currency_id.name))
        footer_date_time = self.formatLang(str(datetime.today()), date_time=True)
        print ">>>>>>>>>>>>>>>>>>>ADASDASDASD Date From ",name, context
        self.localcontext.update({
            'report_name': _('Budget Report'),
            'budgets':self.get_budget,
            'budgets_line':self.get_budget_line,
            'get_account_code': self._get_account_code,
            'budgets_line_view':self.get_budget_line_view,
            'budgets_line_all' : self.budgets_line_all,
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


    def budgets_line_all(self, form, budget_id):
        n_list = []
        for line_budget in self.get_budget_line_view(form, budget_id):
            n_list.append(line_budget)
            for line_view in self.get_budget_line_custom(form, budget_id, line_budget['account_id']):
                n_list.append((line_view))
        for list in n_list:
            print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>LINEEEEEEE ",list['account_code']


        ##Sorting
        sort_on = "account_code"

        decorated = [(dict_[sort_on], dict_) for dict_ in n_list]

        decorated.sort()

        result = [dict_ for (key, dict_) in decorated]
        #to link childs with main parents
        new_dict = []
        for resr in result:

            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>RESULT ",resr['account_code'],resr['type']
        sub = []
        temp = False
        temp_sub = []
        for rest in result:
            if temp != False:
                temp.update({'lines': []})
            if rest['type'] == 'view':
                if len(temp_sub)>0:
                    temp.update({'lines':temp_sub})
                    temp_sub = []


                if temp == False:
                    temp = {}
                else:
                    new_dict.append(temp)

                temp = rest
            if rest['type'] == 'normal':
                temp_sub.append(rest)
        if len(temp_sub) > 0:
            temp.update({'lines': temp_sub})
            new_dict.append(temp)


        #for dic in new_dict:

        #    print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>LINEEEEEEE 1 ",dic['account_code'],dic['type']
        #    #if n.has_key('lines'):
        #    for line in dic['lines']:
        #        print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>LINEEEEEEE 2 ", line['account_code'], line['type']

        #print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>DICT ",new_dict
        return new_dict


        """mydict = []
        #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>ENTERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR"
        for line_budget in self.get_budget_line_view(form,budget_id):
            #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>LINE VIEW",line_budget
           #mydict.append(line_budget)
            lis = []
            for line_view in self.get_budget_line_custom(form,budget_id,line_budget['account_id']):

                lis.append(line_view)
            line_budget.update({'lines':lis})
            mydict.append((line_budget))
            #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Budget Line"
        #print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>final MYDICT",mydict
        integ = []
        print "mydict>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<",mydict
        for dic in mydict:
            print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MYDICT", dic['account_code']
            integ.append(dic['account_code'])
            for dic_line in dic['lines']:
                print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> >MYDICT", dic_line['account_code']

                integ.append(dic_line['account_code'])

        integers = integ
        #print " SORTED", sorted(integers, key=str)


            #print ">>>>>>>>>>>>>>>>>>>>>>>>>> ALL ROW DIC", dic
        return mydict"""

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
            'accuracy': form.get('accuracy',1),
        })
        return super(account_budget_summary, self).set_context(objects, data, ids, report_type=report_type)



    def _get_account_code(self, data):
        if data['closure']:
           return data['closure']


# # # # # # #  '1' Cost Center Details  # # # # # # #
    def get_budget(self, form):

        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Tuples ",tuple(self.analytic_child_ids,), tuple(self.period_ids,), tuple(self.account_child_ids,)
        budget_pool = self.pool.get('account.budget')
        self.cr.execute("SELECT distinct account_budget_id,acc.code,period_id FROM account_budget_lines INNER JOIN account_analytic_account acc \
                ON acc.id = analytic_account_id WHERE analytic_account_id IN %s AND period_id IN %s AND general_account_id IN %s \
                ORDER BY acc.code,period_id", (tuple(self.analytic_child_ids,), tuple(self.period_ids,), tuple(self.account_child_ids,),))

        res = self.cr.fetchall()
        budget_ids = [rec[0] for rec in res]

        return budget_pool.browse(self.cr, self.uid, budget_ids, context=self.context)
        
    def get_budget_line_view(self, form, budget_id):

        budget_pool = self.pool.get('account.budget')
        move_line_pool = self.pool.get('account.move.line')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', False)
        fiscalyear_id = form.get('fiscalyear_id', False)
        fiscalyear_date_start = fiscalyear_pool.browse(self.cr, self.uid, fiscalyear_id, context=self.context).date_start
        budget = []
        balance = 0
        planned = 0
        residual_balance = 0
        print ">>>>>>>>>>>>>>>>>>>>>>>>>BUDGET ID = ",budget_id
        bud = budget_pool.browse(self.cr, self.uid, budget_id, context=self.context)
        #Use this code for none Accounting user
        account_user = self.pool.get('res.users').has_group(self.cr, self.uid, 'account.group_account_user')
        if not account_user:
            user_account_ids = [line.general_account_id.id for line in bud.account_budget_line]
            analytic_account = self.pool.get('account.analytic.account').search(self.cr, self.uid, [('type', '=', 'normal')], context=self.context)
            temp_account_ids = []
            self.cr.execute("SELECT gid as group_id FROM res_groups_users_rel WHERE uid='%s'" % (str(self.uid),)) 
            #group_ids = list(cr.fetchall())
            user_group_ids = [x for x, in self.cr.fetchall()]
            for account in self.pool.get('account.account').browse(self.cr, self.uid, user_account_ids, context=self.context ):
                if set([group.id for group in account.group_ids]) & set(user_group_ids):
                    temp_account_ids.append(account.id)

        accounts = []
        parents = []
        parents_uniqe = []
        accounts_id = []
        for line in bud.account_budget_line:
            parent_id = line.general_account_id.parent_id.id
            parents.append(parent_id)
            accounts_id.append(line.general_account_id.id)

        #print ">>>>>>>>>>>>>>>Accounts ",accounts_id
        for parent in parents:
            if not parent in parents_uniqe:
                parents_uniqe.append(parent)
        i = 0

        #parents_uniqe = [47965, 48011, 48015, 48023, 48032]





        # get all accounts and get second root
        code = 0
        if form['type_rep'] == 'income':
            code = 1
        elif form['type_rep'] == 'cost':
            code = 2
        else:
            code = 3
        #parents_uniqe = self.pool.get('account.account').search(self.cr, self.uid, [('company_id','=',bud.company_id.id)],
        #                                               limit=2,context=self.context)
        root_id = self.pool.get('account.account').search(self.cr, self.uid, [('company_id','=',bud.company_id.id),('code','=',code)],
                                                       limit=2,context=self.context)
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<ROOT ID" ,root_id
        #parents_uniqe = self.pool.get('account.account').search(self.cr, self.uid, [('id','child_of',parents_uniqe[1]),('id','not in',accounts_id)],
        #                                               context=self.context)
        parents_uniqe = self.pool.get('account.account').search(self.cr, self.uid,
                                                                [('id', 'child_of', root_id),
                                                                 ('id', 'not in', accounts_id)],
                                                       context=self.context)


        #print ">>>>>>>>>>>>>>>>>>All Accounts ", parents_uniqe

        #main parent 47881 ('parent_id', 'child_of', 47881)

        for acc in self.pool.get('account.account').browse(self.cr, self.uid, parents_uniqe, context=self.context ):
            ids2 = self.pool.get('account.account').search(self.cr, self.uid, [('parent_id', 'child_of', acc.id)],order="id desc", context=self.context)
            planned=0
            balance=0.0
            total_operation=0.0
            #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>...........CHILD OF ACC ID",acc.id, " Ids2 ",ids2
            #To sum child to parent to get All Totals
            budget_lines = self.pool.get('account.budget.lines').search(self.cr, self.uid, [('account_budget_id','=',bud.id),('general_account_id.parent_id', 'child_of', acc.id)],context=self.context)
            for line in self.pool.get('account.budget.lines').browse(self.cr, self.uid,budget_lines):
                planned += line.planned_amount
                total_operation+=line.total_operation


            #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>budget_lines ",budget_lines

            #for line in bud.account_budget_line:
            #    if line.general_account_id.parent_id.id==acc.id:
            #        planned+=line.planned_amount
            #        total_operation+=line.total_operation
            #for plus in self.pool.get('account.account').browse(self.cr, self.uid, parents_uniqe, context=self.context ):


            move = move_line_pool.search(self.cr, self.uid, [('analytic_account_id', '=', bud.analytic_account_id.id),('date','>=',date_from),('date','<=',date_to),('account_id', 'in', ids2),('state','=','valid')], context=self.context)
 
            bl = 0
            sign = line.general_account_id.user_type.report_type in ('income','liability') and -1 or 1
            debit = 0
            credit = 0
            for oo in move_line_pool.browse(self.cr, self.uid, move, context=self.context):
                bl += oo.debit - oo.credit
                debit = oo.debit
                credit = oo.credit
            balance = sign * bl
            debit = sign * debit
            credit = sign * credit

            balance = abs(balance)
            debit = abs(debit)
            credit = abs(credit)

            date_from1 = mx.DateTime.Parser.DateTimeFromString(date_from)
            date_to1 = mx.DateTime.Parser.DateTimeFromString(date_to)
            month_from=date_from1.month
            month_to=date_to1.month
            rate=month_to-month_from+1
            relative=round(((planned+total_operation)/12)*rate,2)


            #Mudathir : To solve exception devided by ZERO *_*
            ratio = relative != 0 and round((balance / relative) * 100, 2) or 0





            #By Mudathir : Get Rid of any line we don't  need in report or simply all line numbers = 0
            (balance == 0 and ratio == 0 and planned == 0 and total_operation == 0) \
            or \
            budget.append({
                'account_name':acc.name,
                'account_code':acc.code,
                'account_id':acc.id,
                'balance':balance,
                'planned':planned,
                'total_operation':total_operation,
                'relative':relative,
                'ratio':ratio,
                'type':'view',
                'debit':debit,
                'credit':credit
            })


        return budget

    def get_budget_line_custom(self, form, budget_id, parent_id):
        globals()['total_plan'] = 0
        globals()['total_operation'] = 0
        globals()['total_balance'] = 0
        globals()['total_residual_balance'] = 0
        globals()['total_previous_balance'] = 0
        budget_pool = self.pool.get('account.budget')
        move_line_pool = self.pool.get('account.move.line')
        move_pool = self.pool.get('account.move')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', False)
        fiscalyear_id = form.get('fiscalyear_id', False)
        fiscalyear_date_start = fiscalyear_pool.browse(self.cr, self.uid, fiscalyear_id,
                                                       context=self.context).date_start
        budget = []
        balance = 0
        planned = 0
        residual_balance = 0
        bud = budget_pool.browse(self.cr, self.uid, budget_id, context=self.context)
        # Use this code for none Accounting user
        account_user = self.pool.get('res.users').has_group(self.cr, self.uid, 'account.group_account_user')
        if not account_user:
            user_account_ids = [line.general_account_id.id for line in bud.account_budget_line]

            analytic_account = self.pool.get('account.analytic.account').search(self.cr, self.uid,
                                                                                [('type', '=', 'normal')],
                                                                                context=self.context)
            temp_account_ids = []
            self.cr.execute("SELECT gid as group_id FROM res_groups_users_rel WHERE uid='%s'" % (str(self.uid),))
            # group_ids = list(cr.fetchall())
            user_group_ids = [x for x, in self.cr.fetchall()]

            for account in self.pool.get('account.account').browse(self.cr, self.uid, user_account_ids,
                                                                   context=self.context):
                if set([group.id for group in account.group_ids]) & set(user_group_ids):
                    temp_account_ids.append(account.id)
        for line in bud.account_budget_line:
            if line.general_account_id.parent_id.id == parent_id:
                # Check for non accounting user
                if not account_user and line.general_account_id.id not in temp_account_ids:
                    continue

                if date_from and date_to:
                    '''self.cr.execute("SELECT distinct COALESCE(CASE WHEN per.date_start > %s and per.date_stop < %s THEN l.planned_amount  WHEN %s BETWEEN per.date_start and per.date_stop and %s BETWEEN per.date_start and date_stop THEN (l.planned_amount*(CAST(%s as date)-CAST(%s AS date)+1))/(per.date_stop-per.date_start+1) WHEN %s BETWEEN per.date_start and per.date_stop THEN (l.planned_amount*(per.date_stop-%s+1))/(per.date_stop-per.date_start+1) WHEN %s BETWEEN per.date_start and per.date_stop THEN (l.planned_amount*(%s-per.date_start+1))/(per.date_stop-per.date_start+1) ELSE 0.0 END) as planned FROM account_budget_lines l LEFT JOIN account_budget b \
                    ON (b.id = l.account_budget_id) LEFT JOIN account_period per ON (per.id = b.period_id) \
                    where l.id=%s", (date_from,date_to,date_from,date_to,date_to,date_from,date_from,date_from,date_to,date_to,line.id))
                    res_plan = self.cr.dictfetchall()
                    for plan in res_plan:
                        planned = plan['planned']'''
                    # Use for plan amount in line
                    planned = line.planned_amount
                    sign = line.general_account_id.user_type.report_type in ('income', 'liability') and -1 or 1
                    mov = move_pool.search(self.cr, self.uid,
                                           [('company_id', '=', bud.company_id.id), ('state', '!=', 'reversed'),
                                            ('date', '>=', date_to), ('date', '<', date_from)])

                    previous_move_ids = move_line_pool.search(self.cr, self.uid,
                                                              [('analytic_account_id', '=', bud.analytic_account_id.id),
                                                               ('date', '>=', fiscalyear_date_start),
                                                               ('date', '<', date_from),
                                                               ('account_id', '=', line.general_account_id.id),
                                                               ('state', '=', 'valid')], context=self.context)
                    pre_balance = 0
                    for record in move_line_pool.browse(self.cr, self.uid, previous_move_ids, context=self.context):
                        pre_balance += record.debit - record.credit
                    previous_balance = abs(pre_balance)

                    move = move_line_pool.search(self.cr, self.uid,
                                                 [('analytic_account_id', '=', bud.analytic_account_id.id),
                                                  ('date', '>=', date_from), ('date', '<=', date_to),
                                                  ('account_id', '=', line.general_account_id.id),
                                                  ('state', '=', 'valid'), ], context=self.context)
                    bl = 0
                    debit = 0
                    credit = 0
                    for oo in move_line_pool.browse(self.cr, self.uid, move, context=self.context):
                        bl += oo.debit - oo.credit
                        debit = oo.debit
                        credit = oo.credit
                    balance = sign * bl
                    debit = sign * debit
                    credit = sign * credit
                    balance = abs(balance)
                    debit = abs(debit)
                    credit = abs(credit)

                    date_from1 = mx.DateTime.Parser.DateTimeFromString(date_from)
                    date_to1 = mx.DateTime.Parser.DateTimeFromString(date_to)
                    month_from = date_from1.month
                    month_to = date_to1.month
                    rate = month_to - month_from + 1
                    if planned > 0:
                        relative = round(((planned + total_operation) / 12) * rate, 2)
                        # else:
                        # relative=0
                    # ratio=0.0
                    # if relative>0 :
                    ratio = round((balance / relative) * 100, 2)
                else:
                    balance = line.balance
                    planned = line.planned_amount
                    balance = abs(balance)
                    residual_balance = line.residual_balance
                budget.append(
                    {'account_name': line.general_account_id.name, 'account_code': line.general_account_id.code,
                     'account_parent_id': line.general_account_id.parent_id.id,
                     'account_parent_name': line.general_account_id.parent_id.name,
                     'account_parent_code': line.general_account_id.parent_id.code,
                     'planned_amount': planned,
                     'total_operation': line.total_operation,
                     'balance': balance,
                     'previous_balance': previous_balance,
                     'ratio': ratio,
                     'relative': relative,
                     'type':'normal',
                     'debit':debit,
                     'creadit':credit})
                globals()['total_plan'] += planned
                globals()['total_operation'] += line.total_operation
                globals()['total_balance'] += balance
            # Used if Report type selection is total, so aggregate by parent account
            if form.get('type_selection', False) == 'total':
                aggregate_budget_temp = []
                aggregate_budget = []
                budget.sort(key=itemgetter("account_parent_code"))
                for key, group in itertools.groupby(budget, lambda item: item["account_parent_code"]):
                    aggregate_budget_temp.append([item for item in group])
                for record in aggregate_budget_temp:
                    aggregate_budget.append({'account_name': record[0]['account_parent_name'],
                                             'account_code': record[0]['account_parent_code'],
                                             'planned_amount': sum([item["planned_amount"] for item in record]),
                                             'total_operation': sum([item["total_operation"] for item in record]),
                                             'balance': sum([item["balance"] for item in record]),
                                             'previous_balance': sum([item["previous_balance"] for item in record]),
                                             'residual_balance': sum([item["residual_balance"] for item in record]), })
                budget = aggregate_budget
        return budget

    def get_budget_line(self, form, budget_id,parent_id):
        globals()['total_plan'] = 0
        globals()['total_operation'] = 0
        globals()['total_balance'] = 0
        globals()['total_residual_balance'] = 0
        globals()['total_previous_balance'] = 0
        budget_pool = self.pool.get('account.budget')
        move_line_pool = self.pool.get('account.move.line')
        move_pool = self.pool.get('account.move')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', False)
        fiscalyear_id = form.get('fiscalyear_id', False)
        fiscalyear_date_start = fiscalyear_pool.browse(self.cr, self.uid, fiscalyear_id, context=self.context).date_start
        budget = []
        balance = 0
        planned = 0
        residual_balance = 0
        bud = budget_pool.browse(self.cr, self.uid, budget_id, context=self.context)
        #Use this code for none Accounting user
        account_user = self.pool.get('res.users').has_group(self.cr, self.uid, 'account.group_account_user')
        if not account_user:
            user_account_ids = [line.general_account_id.id for line in bud.account_budget_line]
 
            analytic_account = self.pool.get('account.analytic.account').search(self.cr, self.uid, [('type', '=', 'normal')], context=self.context)
            temp_account_ids = []
            self.cr.execute("SELECT gid as group_id FROM res_groups_users_rel WHERE uid='%s'" % (str(self.uid),)) 
            #group_ids = list(cr.fetchall())
            user_group_ids = [x for x, in self.cr.fetchall()]

            for account in self.pool.get('account.account').browse(self.cr, self.uid, user_account_ids, context=self.context ):
                if set([group.id for group in account.group_ids]) & set(user_group_ids):
                    temp_account_ids.append(account.id)
        for line in bud.account_budget_line:
            if line.general_account_id.parent_id.id == parent_id:
                #Check for non accounting user
                if not account_user and line.general_account_id.id not in temp_account_ids:
                    continue
                    
                if date_from and date_to:
                    '''self.cr.execute("SELECT distinct COALESCE(CASE WHEN per.date_start > %s and per.date_stop < %s THEN l.planned_amount  WHEN %s BETWEEN per.date_start and per.date_stop and %s BETWEEN per.date_start and date_stop THEN (l.planned_amount*(CAST(%s as date)-CAST(%s AS date)+1))/(per.date_stop-per.date_start+1) WHEN %s BETWEEN per.date_start and per.date_stop THEN (l.planned_amount*(per.date_stop-%s+1))/(per.date_stop-per.date_start+1) WHEN %s BETWEEN per.date_start and per.date_stop THEN (l.planned_amount*(%s-per.date_start+1))/(per.date_stop-per.date_start+1) ELSE 0.0 END) as planned FROM account_budget_lines l LEFT JOIN account_budget b \
                    ON (b.id = l.account_budget_id) LEFT JOIN account_period per ON (per.id = b.period_id) \
                    where l.id=%s", (date_from,date_to,date_from,date_to,date_to,date_from,date_from,date_from,date_to,date_to,line.id))
                    res_plan = self.cr.dictfetchall()
                    for plan in res_plan:
                        planned = plan['planned']'''
                    #Use for plan amount in line
                    planned = line.planned_amount
                    sign = line.general_account_id.user_type.report_type in ('income','liability') and -1 or 1
                    mov = move_pool.search(self.cr, self.uid, [('company_id', '=', bud.company_id.id),('state','!=','reversed'),('date','>=',date_to),('date','<',date_from)])
 
                    previous_move_ids = move_line_pool.search(self.cr, self.uid, [('analytic_account_id', '=', bud.analytic_account_id.id),('date','>=',fiscalyear_date_start),('date','<',date_from),('account_id', '=', line.general_account_id.id),('state','=','valid')], context=self.context)
                    pre_balance = 0
                    for record in move_line_pool.browse(self.cr, self.uid, previous_move_ids, context=self.context):
                        pre_balance += record.debit - record.credit
                    previous_balance = abs(pre_balance)


                    move = move_line_pool.search(self.cr, self.uid, [('analytic_account_id', '=', bud.analytic_account_id.id),('date','>=',date_from),('date','<=',date_to),('account_id', '=', line.general_account_id.id),('state','=','valid'),], context=self.context)
                    bl = 0
                    for oo in move_line_pool.browse(self.cr, self.uid, move, context=self.context):
                        bl += oo.debit - oo.credit
                    balance = sign*bl
                    balance = abs(balance)
                    date_from1 = mx.DateTime.Parser.DateTimeFromString(date_from)
                    date_to1 = mx.DateTime.Parser.DateTimeFromString(date_to)
                    month_from=date_from1.month
                    month_to=date_to1.month
                    rate=month_to-month_from+1
                    if planned>0:
                        relative=round(((planned+total_operation)/12)*rate,2)
                    #else:
                       #relative=0
                    #ratio=0.0
                    #if relative>0 :
                    #ratio=round((balance/relative)*100,2)
                    ratio = relative != 0 and round((balance / relative) * 100, 2) or 0
                else:
                    balance = line.balance
                    planned = line.planned_amount
                    balance = abs(balance)
                    residual_balance = line.residual_balance
                budget.append({'accounts_name':line.general_account_id.name, 'account_code':line.general_account_id.code,
                'account_parent_id':line.general_account_id.parent_id.id,
                'account_parent_name':line.general_account_id.parent_id.name,
                'account_parent_code':line.general_account_id.parent_id.code,
                'planned_amount':planned,
                'total_operation':line.total_operation,
                'balance':balance,
                'previous_balance':previous_balance,
                'ratio':ratio,
                'relative':relative})
                globals()['total_plan'] += planned
                globals()['total_operation'] += line.total_operation
                globals()['total_balance'] += balance
            #Used if Report type selection is total, so aggregate by parent account
            if form.get('type_selection', False) == 'total':
                aggregate_budget_temp =[]
                aggregate_budget =[]
                budget.sort(key=itemgetter("account_parent_code"))
                for key, group in itertools.groupby(budget, lambda item: item["account_parent_code"]):
                    aggregate_budget_temp.append([item for item in group])
                for record in aggregate_budget_temp:
                    aggregate_budget.append({'accounts_name':record[0]['account_parent_name'],
                    'account_code':    record[0]['account_parent_code'],
                    'planned_amount':  sum([item["planned_amount"] for item in record]),
                    'total_operation': sum([item["total_operation"] for item in record]),
                    'balance':         sum([item["balance"] for item in record]),
                    'previous_balance':sum([item["previous_balance"] for item in record]),
                    'residual_balance':sum([item["residual_balance"] for item in record]),})
                budget= aggregate_budget
        return budget

    def _budget_total(self,form,budget_id):

        budget_pool = self.pool.get('account.budget')
        move_line_pool = self.pool.get('account.move.line')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', False)
        fiscalyear_id = form.get('fiscalyear_id', False)
        fiscalyear_date_start = fiscalyear_pool.browse(self.cr, self.uid, fiscalyear_id, context=self.context).date_start
        budget = []
        
        bud = budget_pool.browse(self.cr, self.uid, budget_id, context=self.context)
        #Use this code for none Accounting user
        account_user = self.pool.get('res.users').has_group(self.cr, self.uid, 'account.group_account_user')
        if not account_user:
            user_account_ids = [line.general_account_id.id for line in bud.account_budget_line]
 
            analytic_account = self.pool.get('account.analytic.account').search(self.cr, self.uid, [('type', '=', 'normal')], context=self.context)
            temp_account_ids = []
            self.cr.execute("SELECT gid as group_id FROM res_groups_users_rel WHERE uid='%s'" % (str(self.uid),)) 
            #group_ids = list(cr.fetchall())
            user_group_ids = [x for x, in self.cr.fetchall()]

            for account in self.pool.get('account.account').browse(self.cr, self.uid, user_account_ids, context=self.context ):
                if set([group.id for group in account.group_ids]) & set(user_group_ids):
                    temp_account_ids.append(account.id)
        balance = 0
        planned = 0
 
        total_operation = 0
        relative=0
        ratio=0
        for line in bud.account_budget_line:
            planned+=line.planned_amount
            total_operation+=line.total_operation 
 
            move = move_line_pool.search(self.cr, self.uid, [('analytic_account_id', '=', bud.analytic_account_id.id),('date','>=',date_from),('date','<=',date_to),('state','=','valid')] ,context=self.context)
 
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

report_sxw.report_sxw('report.account.budget.summary',  'account.report.budget', 'addons/account_ntc/report/account_report_budget_summary.rml', parser=account_budget_summary , header='external')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


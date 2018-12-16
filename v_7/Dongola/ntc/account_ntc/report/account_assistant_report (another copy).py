# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from account_custom.common_report_header import common_report_header as common_header
from account.report.common_report_header import common_report_header as custom_common_header

class account_assistant_report(report_sxw.rml_parse, common_header, custom_common_header):
    _name = 'account.assistant.report'

    def __init__(self, cr, uid, name, context=None):
        super(account_assistant_report, self).__init__(cr, uid, name, context=context)
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.date_lst = []
        self.date_lst_string = ''
        self.result_acc = []
        self.result_acc2 = []
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'liness': self.liness,
            'get_parent': self._get_parents,
            'get_parents': self._get_parentss,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'get_fiscalyear':self._get_fiscalyear,
            'get_filter': self._get_filter,
            'account_partners':self.account_partners,
            'get_filter_Trans': self._get_filter_Trans,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period ,
            'get_account': self._get_account,
            'get_account_name': self._get_account_name,
            'get_account_code': self._get_account_code,
            'get_account_sign': self._get_account_sign,
            'get_journal': self._get_journal,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
            'get_Translation': self._get_Translation,
            'get_display_account': self._get_display_account,
            'get_label_according_model': self._get_label_according_model,
            'get_multi_company': self._get_multi_company,
            'get_debit':self._get_debit,
            'get_credit':self._get_credit,
            'get_sortby_gl': self._get_sortby_gl,

        })
        self.cr = cr
        self.uid = uid
        self.context = context
        self.init_query = ''

    def set_context(self, objects, data, ids, report_type=None):
        obj_move = self.pool.get('account.move.line')
        self.target_move = data.get('form', {}).get('target_move', 'all') 
        self.fiscalyear = data['form'].get('fiscalyear_id', False)
        self.display_partner = data['form'].get('display_partner', 'non-zero_balance')
        self.acc_balances = data.get('form', {}).get('acc_balances', False)
        self.detail = data.get('form', {}).get('detail', False)
        self.credit = 0
        self.debit = 0
        ctx2 = data.get('form', {}).get('used_context', {}).copy()
        ctx2.update({'initial_bal': bool(data['form']['initial_balance'])})
        ctx2['type'] = 'balance'   # This type used in _QUERY_GET to defertiate form GENERAL STATEMENT REPORTS
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)       
        if data.get('form', {}).get('filter', '') == 'filter_no':
            periods = self.pool.get('account.period').search(self.cr, self.uid, [('fiscalyear_id', '=', ctx2.get('fiscalyear', 0))], order='date_start')
            ctx2.update({'period_from': periods and periods[0] or False})
            ctx2.update({'period_to': periods and periods[len(periods) - 1] or False})
        #ctx2.update({'fiscalyear': False}) # it arise error when there is no initial balance 
        if ctx2.get('initial_bal', False):
            self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)
        new_ids = ids
        if (data.get('model', {}) == 'ir.ui.menu'):
            self.chart_company = self.pool.get('account.account').browse(self.cr, self.uid, data['form']['chart_account_id']).company_id.id
            new_ids = 'account_ids' in data['form'] and data['form']['account_ids']  or 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        self.state_query = ""
        if self.target_move == 'posted':
            self.state_query = " AND am.state = 'posted' "
        return super(account_assistant_report, self).set_context(objects, data, new_ids, report_type=report_type)

    def _get_account(self, data):
        if data['model'] == 'account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['id']).company_id.name
        return super(account_assistant_report , self)._get_account(data)


    def _get_account_name(self, data):
        if data['account_ids']:
 
           res=[]
           account=data['account_ids'][0]
           name=self.pool.get('account.account').browse(self.cr, self.uid,account).name
           res={'account':name}
 
           return name

    def _get_account_code(self, data):
        if data['account_ids']:
           account=data['account_ids'][0]
           for account in self.pool.get('account.account').browse(self.cr, self.uid, [account], context=self.context):
               code=account.code
           line_ids = self.pool.get('unit.report.line').search(self.cr,self.uid, [ ('code', '=', code)], context=self.context)
           for line in self.pool.get('unit.report.line').browse(self.cr, self.uid, line_ids, context=self.context):
               closure=line.closure

    def _get_account_sign(self, data):
        if data['account_ids']:
           report_type=''
           account_id= self.pool.get('account.account.type').search(self.cr,self.uid, [('id', '=', data['account_ids'][0])],context=self.context)
           for acc in self.pool.get('account.account.type').browse(self.cr,self.uid, account_id,context=self.context):
                    report_type= acc.user_typr.report_type
                    sign =report_type in ('income','liability') and -1 or 1
        return sign


    def _get_children_and_consol(self, cr, uid, ids, context=None):
        # this function search for all the children and all consolidated children (recursively) of the given account ids
        
        ids2 = self.pool.get('account.account').search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        ids3 = []
        for rec in self.pool.get('account.account').browse(cr, uid, ids2, context=context):
            for child in rec.child_consol_ids:
                ids3.append(child.id)
        if ids3:
            ids3 = self._get_children_and_consol(cr, uid, ids3, context)
        return ids2 + ids3

    def lines(self, form, code,ids=[], done=None):
        def _process_child(accounts, disp_acc, parent):
                state_query = ""
                account_rec = [acct for acct in accounts if acct['id'] == parent][0]
                #acc = self.pool.get('account.account').search(self.cr,self.uid, [('id', '=',account_rec['id'])
               
 
                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'user_type': account_rec['user_type'],
                    'code': account_rec['code'],
                    'name': account_rec['name'],
                    'level': account_rec['level'],
                    'company_id': account_rec['company_id'],
                    'debit': account_rec['debit'],
                    'credit': account_rec['credit'],
                    'balance': account_rec['balance'],
                    'parent_id': account_rec['parent_id'],
                    'bal_type': '',
                    'sign': '',
                }
                
                self.sum_debit += account_rec['debit']
                self.sum_credit += account_rec['credit']

                if self.target_move == 'posted':
                    state_query = " AND am.state = 'posted' "
                if self.target_move == 'all':
                    state_query = " AND am.state != 'reversed' "
                #~~~~~~~~~~~~~~~~~~~~~~~~~ Initial Balance ~~~~~~~~~~~~~~~~~~~~~~
                
                if self.init_query:
                    self.cr.execute('SELECT (sum(COALESCE(debit,0)) -sum(COALESCE(credit,0)))  as init_balance FROM account_move_line l, account_move am WHERE l.move_id=am.id ' + state_query + ' AND account_id=' + str(res['id']) + ' AND ' + self.init_query + ' ')
                    
                    if account_rec['child_id']:
                        children_and_consolidated = self._get_children_and_consol(self.cr, self.uid, res['id'])
                        # self.cr.execute('SELECT (sum(debit) - sum(credit)) as init_balance  FROM account_move_line l, account_move am WHERE l.move_id=am.id AND am.state in %s AND l.account_id in %s  AND ' + self.init_query + ' '  ,(tuple(move_state),tuple(children_and_consolidated), ))

                        self.cr.execute('SELECT (sum(COALESCE(debit,0)) - sum(COALESCE(credit,0))) as init_balance  FROM account_move_line l, account_move am WHERE l.move_id=am.id ' + state_query + ' AND l.account_id in %s  AND ' + self.init_query + ' '  , (tuple(children_and_consolidated),))
                    res['init_balance'] = self.cr.fetchone()[0] or 0.0
                else: 
                    res['init_balance'] = 0.0

                #~~~~~~~~~~~~~~~~~~~~~~~~~ Initial Balance End ~~~~~~~~~~~~~~~~~~~~~~
                if form.get('all_accounts', False) or self.chart_company == account_rec['company_id'][0] :
                    if disp_acc == 'bal_movement':
                        if account_rec['type'] in ('view', 'consolidation') :
                            self.result_acc.append(res)
                    elif disp_acc == 'bal_solde':
                        if account_rec['level'] == 1 :
                            self.result_acc.append(res)
                    elif disp_acc == 'bal':
                        if form['initial_balance'] and (res['init_balance'] + res['balance']) != 0 : 
                            self.result_acc.append(res)
                        elif not form['initial_balance'] and res['balance'] != 0 :
                            self.result_acc.append(res)
                    else:
                            self.result_acc.append(res)
            
                if account_rec['child_id'] and self.detail != 'min':
                    for child in account_rec['child_id']:
                        _process_child(accounts, disp_acc, child)

        obj_account = self.pool.get('account.account')
        
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done = {}
        
        ctx = self.context.copy()
        ctx['journal_ids'] = form.get('journal_ids', False)
        ctx['fiscalyear'] = form.get('fiscalyear_id', False)
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form.get('period_from', False)
            ctx['period_to'] = form.get('period_to', False)
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form.get('date_from', False)
            ctx['date_to'] = form.get('date_to', False)
        ctx['state'] = form.get('target_move', False)
        if ctx['state']=='all':
            ctx['state'] = ('draft','compeleted','posted')
        ctx['type'] = 'balance'   # This type used in _QUERY_GET to defertiate form GENERAL STATEMENT REPORTS
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
    
        if child_ids:
            ids = child_ids
  
        accounts = obj_account.read(self.cr, self.uid, ids, ['id','type','user_type', 'code', 'name', 'debit', 'credit', 'balance', 'parent_id', 'level', 'child_id', 'company_id'], ctx)

        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                _process_child(accounts, form['display_account'], parent)
        if form['initial_balance']:
            for res in self.result_acc:
                self.credit += (res['init_balance'] + res['balance']) < 0 and res['type'] != 'view' and abs(res['init_balance'] + res['balance']) or 0
                self.debit += (res['init_balance'] + res['balance']) > 0 and res['type'] != 'view' and abs(res['init_balance'] + res['balance']) or 0
        else:
            for res in self.result_acc:
                self.credit += res['balance'] < 0 and res['type'] != 'view' and abs(res['balance']) or 0
                self.debit += res['balance'] > 0 and res['type'] != 'view' and abs(res['balance']) or 0
        types=[]
        #report_types=('income','liability')
        #types = self.pool.get('account.account.type').search(self.cr,self.uid, [('report_type', 'in',report_types )],context=self.context)
        self.cr.execute(" select id as type_id  from account_account_type where report_type in ('income','liability' )")
        query_type = self.cr.dictfetchall()
        types = [ x['type_id'] for x in query_type ]
        new_res=[]
        res1=[]
        res2=[]
        acc_id=0
        company_id = self.pool.get('account.account').browse(self.cr, self.uid,  form['account_ids'][0]).company_id.id
        account = self.pool.get('account.account').search(self.cr,self.uid, [('code', '=', code),('company_id', '=', company_id)],context=self.context)
        for acc in  self.pool.get('account.account').browse(self.cr,self.uid, account,context=self.context):
            acc_id=acc.id
        res1=filter(lambda acc: acc['parent_id'][0] ==acc_id and (acc['debit']!=0 or acc['credit']!=0 or acc['init_balance']!=0),self.result_acc)
        
        for item in res1:
            if item not in res2:
               res2.append(item)
        for it in res2:
            sign = it['user_type'][0] in types and -1 or 1
            if it['balance']!=0:
                it['balance']=sign*it['balance']
            if it['init_balance']!=0:
                it['init_balance']=sign*it['init_balance']
 
 
        return res2
 


    def liness(self, form, ids=[], done=None):
        def _process_child(accounts, disp_acc, parent):
                state_query = ""
                account_rec = [acct for acct in accounts if acct['id'] == parent][0]

                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'user_type': account_rec['user_type'],
                    'code': account_rec['code'],
                    'name': account_rec['name'],
                    'level': account_rec['level'],
                    'company_id': account_rec['company_id'],
                    'debit': account_rec['debit'],
                    'credit': account_rec['credit'],
                    'balance': account_rec['balance'],
                    'parent_id': account_rec['parent_id'],
                    'bal_type': '',
                }
                
                self.sum_debit += account_rec['debit']
                self.sum_credit += account_rec['credit']

                if self.target_move == 'posted':
                    state_query = " AND am.state = 'posted' "
                if self.target_move == 'all':
                    state_query = " AND am.state != 'reversed' "
                ctx['type'] = 'balance'   # This type used in _QUERY_GET to defertiate form GENERAL STATEMENT REPORTS

                #~~~~~~~~~~~~~~~~~~~~~~~~~ Initial Balance ~~~~~~~~~~~~~~~~~~~~~~
                
                if self.init_query:
                    self.cr.execute('SELECT (sum(COALESCE(debit,0)) -sum(COALESCE(credit,0)))  as init_balance FROM account_move_line l, account_move am WHERE l.move_id=am.id ' + state_query + ' AND account_id=' + str(res['id']) + ' AND ' + self.init_query + ' ')
                    
                    if account_rec['child_id']:
                        children_and_consolidated = self._get_children_and_consol(self.cr, self.uid, res['id'])
                        # self.cr.execute('SELECT (sum(debit) - sum(credit)) as init_balance  FROM account_move_line l, account_move am WHERE l.move_id=am.id AND am.state in %s AND l.account_id in %s  AND ' + self.init_query + ' '  ,(tuple(move_state),tuple(children_and_consolidated), ))

                        self.cr.execute('SELECT (sum(COALESCE(debit,0)) - sum(COALESCE(credit,0))) as init_balance  FROM account_move_line l, account_move am WHERE l.move_id=am.id ' + state_query + ' AND l.account_id in %s  AND ' + self.init_query + ' '  , (tuple(children_and_consolidated),))
                    res['init_balance'] = self.cr.fetchone()[0] or 0.0
                else:
                    res['init_balance'] = 0.0

                #~~~~~~~~~~~~~~~~~~~~~~~~~ Initial Balance End ~~~~~~~~~~~~~~~~~~~~~~
                if form.get('all_accounts', False) or self.chart_company == account_rec['company_id'][0] :
                    if disp_acc == 'bal_movement':
                        if account_rec['type'] in ('view', 'consolidation') :
                            self.result_acc2.append(res)
                    elif disp_acc == 'bal_solde':
                        if account_rec['level'] == 1 :
                            self.result_acc2.append(res)
                    elif disp_acc == 'bal':
                        if form['initial_balance'] and (res['init_balance'] + res['balance']) != 0 : 
                            self.result_acc.append(res)
                        elif not form['initial_balance'] and res['balance'] != 0 :
                            self.result_acc2.append(res)
                    else:
                            self.result_acc2.append(res)
            
                if account_rec['child_id'] and self.detail != 'min':
                    for child in account_rec['child_id']:
                        _process_child(accounts, disp_acc, child)

        obj_account = self.pool.get('account.account')
        
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done = {}
        
        ctx = self.context.copy()
        ctx['journal_ids'] = form.get('journal_ids', False)
        ctx['fiscalyear'] = form.get('fiscalyear_id', False)
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form.get('period_from', False)
            ctx['period_to'] = form.get('period_to', False)
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form.get('date_from', False)
            ctx['date_to'] = form.get('date_to', False)
        ctx['state'] = form.get('target_move', False)
        if ctx['state']=='all':
            ctx['state'] = ('draft','compeleted','posted')
        ctx['type'] = 'balance'   # This type used in _QUERY_GET to defertiate form GENERAL STATEMENT REPORTS
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
    
        if child_ids:
            ids = child_ids
  
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','user_type', 'code', 'name', 'debit', 'credit', 'balance', 'parent_id', 'level', 'child_id', 'company_id'], ctx)

        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                _process_child(accounts, form['display_account'], parent)
        if form['initial_balance']:
            for res in self.result_acc2:
                self.credit += (res['init_balance'] + res['balance']) < 0 and res['type'] != 'view' and abs(res['init_balance'] + res['balance']) or 0
                self.debit += (res['init_balance'] + res['balance']) > 0 and res['type'] != 'view' and abs(res['init_balance'] + res['balance']) or 0
        else:
            for res in self.result_acc2:
                self.credit += res['balance'] < 0 and res['type'] != 'view' and abs(res['balance']) or 0
                self.debit += res['balance'] > 0 and res['type'] != 'view' and abs(res['balance']) or 0


        if form['account_ids']:
            account=form['account_ids'][0]
            code=self.pool.get('account.account').browse(self.cr, self.uid,account).code
            self.result_acc2=filter(lambda acc: acc['code'] == code,self.result_acc2)

        res3=[]
        
        for item in self.result_acc2:
            if item not in res3:
               res3.append(item)
        
        return res3
 
 

    def _get_credit(self):
        return self.credit

    def _get_debit(self):
        return self.debit

    def _get_parents(self,data):
        if data['account_ids']:
           res=[]
           codes=[]
           
           parents = self.pool.get('account.account').search(self.cr,self.uid, [('parent_id', '=', data['account_ids'][0]),('id', '!=', data['account_ids'][0]),('detialed','!=','True'),('type','=','view')], context=self.context)
          
           for parent in self.pool.get('account.account').browse(self.cr, self.uid, parents, context=self.context):
               codes.append(parent.code) 
           acc=self.lines(data,0)
           res=filter(lambda acc: acc['code'] in codes and (acc['debit']!=0 or acc['credit']!=0 or acc['init_balance']!=0),self.result_acc)
           types=[]
          
           self.cr.execute(" select id as type_id  from account_account_type where report_type in ('income','liability' )")
           query_type = self.cr.dictfetchall()
           types = [ x['type_id'] for x in query_type ]
           for it in res:
              sign = it['user_type'][0] in types and -1 or 1
              if it['balance']!=0:
                it['balance']=sign*it['balance']
              if it['init_balance']!=0:
                it['init_balance']=sign*it['init_balance']
           return res

    def _get_parentss(self,data):
        if data['account_ids']:
           res=[]
           codes=[]
           parents = self.pool.get('account.account').search(self.cr,self.uid, [('parent_id', '=', data['account_ids'][0]),('id', '!=', data['account_ids'][0]),('detialed','=','True'),('type','!=','view')], context=self.context)

           for parent in self.pool.get('account.account').browse(self.cr, self.uid, parents, context=self.context):
               codes.append(parent.code) 
           acc=self.lines(data,0)
           res=filter(lambda acc: acc['code'] in codes and (acc['debit']!=0 or acc['credit']!=0 or acc['init_balance']!=0),self.result_acc)
           types=[]
           res1=[]
           for item in res:
               if item not in res1:
                   res1.append(item)
            
           types=[]
          
           self.cr.execute(" select id as type_id  from account_account_type where report_type in ('income','liability' )")
           query_type = self.cr.dictfetchall()
           types = [ x['type_id'] for x in query_type ]
           for it in res:
              sign = it['user_type'][0] in types and -1 or 1
              if it['balance']!=0:
                it['balance']=sign*it['balance']
              if it['init_balance']!=0:
                it['init_balance']=sign*it['init_balance']
           return res1

    def account_partners(self, code):
        #account2 = self.pool.get('account.account').search(self.cr,self.uid, [('code', '=', code)], context=self.context)
        #account =[x.id for x in  self.pool.get('account.account').browse(self.cr,self.uid,account2, context=self.context)][0] 
        account=0
        accounts=[]
        account1 = self.pool.get('account.account').search(self.cr,self.uid, [('code', '=', code)],context=self.context)
        for acc in  self.pool.get('account.account').browse(self.cr,self.uid, account1,context=self.context):
            accounts.append(acc.id)
        state_query=""
        if self.target_move == 'posted':
            state_query += " AND am.state = 'posted' "
        if self.target_move == 'all':
            state_query += " AND am.state != 'reversed' "


        full_account = []
        result_tmp = 0.0
        partner_query = ""
         
        # select balance from move rather then total debit and total credit
        if self.init_query:
            self.cr.execute(
                "SELECT COALESCE(id,0) id,name, sum(debit) as debit ,sum(credit) as credit, sum(sdebit) as sdebit ,sum(scredit) as scredit, min(init_bal) as init_bal " \
                "FROM   (SELECT p.id, l.move_id, p.name AS name, "\
                            "CASE WHEN sum(debit) > sum(credit) "\
                                "THEN sum(debit) - sum(credit) "\
                                "ELSE 0 "\
                            "END AS debit ,"\
                            "CASE WHEN sum(credit) > sum(debit) "\
                                "THEN sum(credit) - sum(debit) "\
                                "ELSE 0 "\
                            "END AS credit, " \
                            "CASE WHEN sum(debit) > sum(credit) " \
                                "THEN sum(debit) - sum(credit) " \
                                "ELSE 0 " \
                            "END AS sdebit, " \
                            "CASE WHEN sum(debit) < sum(credit) " \
                                "THEN sum(credit) - sum(debit) " \
                                "ELSE 0 " \
                            "END AS scredit, " \
                            "(SELECT COALESCE(sum(debit-credit), 0.0) " \
                            "FROM account_move_line AS l, account_move AS am " \
                            "WHERE l.partner_id = p.id AND am.id = l.move_id " + state_query + " AND account_id in  %s AND " + self.init_query + ") AS init_bal "\
                    "FROM account_move_line l LEFT JOIN res_partner p ON (l.partner_id=p.id) JOIN account_move am ON (am.id = l.move_id)" \
                    "WHERE l.account_id in %s " + state_query + " AND " + self.query + " " + partner_query + " " \
                    "GROUP BY l.move_id,p.id, p.name " \
                    ") as result "\
                "GROUP BY result.id, result.name  ORDER BY result.name ", (tuple(accounts), tuple(accounts),))
        else:
            self.cr.execute(
                "SELECT COALESCE(id,0) id,name, sum(debit) as debit ,sum(credit) as credit, sum(sdebit) as sdebit ,sum(scredit) as scredit, 0 as init_bal " \
                "FROM   (SELECT p.id, l.move_id, p.name AS name, "\
                            "CASE WHEN sum(debit) > sum(credit) "\
                                "THEN sum(debit) - sum(credit) "\
                                "ELSE 0 "\
                            "END AS debit ,"\
                            "CASE WHEN sum(credit) > sum(debit) "\
                                "THEN sum(credit) - sum(debit) "\
                                "ELSE 0 "\
                            "END AS credit, " \
                            "CASE WHEN sum(debit) > sum(credit) " \
                                "THEN sum(debit) - sum(credit) " \
                                "ELSE 0 " \
                            "END AS sdebit, " \
                            "CASE WHEN sum(debit) < sum(credit) " \
                                "THEN sum(credit) - sum(debit) " \
                                "ELSE 0 " \
                            "END AS scredit " \
                    "FROM account_move_line l LEFT JOIN res_partner p ON (l.partner_id=p.id) JOIN account_move am ON (am.id = l.move_id)" \
                    "WHERE l.account_id in %s " + state_query + " AND " + self.query + "  " + partner_query + " "  \
                    "GROUP BY l.move_id,p.id, p.name " \
                    ") as result "\
                "GROUP BY result.id, result.name ORDER BY result.name  ", (tuple(accounts),))

        res = self.cr.dictfetchall()

###############
        part_ids = [ r['id'] for r in res ]
        init_parts = ""
        if part_ids:
            init_parts = " AND l.partner_id not in %s " 
        if self.init_query:
            param = init_parts and  (tuple(accounts), tuple(part_ids),) or (tuple(accounts),)
            self.cr.execute(
                    "SELECT p.name , 0 as debit , 0 as credit , l.partner_id, COALESCE(sum(debit-credit), 0.0) AS init_bal \
                     FROM account_move_line AS l, account_move AS am , res_partner as p \
                     WHERE  p.id =l.partner_id and am.id = l.move_id " + state_query + " \
                            AND account_id in %s AND " + self.init_query + "  " + init_parts + " " + partner_query + " \
                     GROUP BY l.partner_id, p.name", param)
        
            init_part = self.cr.dictfetchall()
            
            res = res + init_part
################ 

        if self.display_partner == 'non-zero_balance':
            if not self.fiscalyear:
                for e in res:
                    e['init_bal'] = 0.0
            prec = self.pool.get('decimal.precision').precision_get(self.cr, self.uid, 'Account')
            full_account = [r for r in res if round(r['init_bal'], prec) != 0 or round( r['debit'], prec) != 0 or round(r['credit'], prec) != 0]
        else:
            full_account = [r for r in res]
 
        progress = {'init_bal':0.0, 'debit':0.0, 'credit':0.0, 'balance':0.0}
        for rec in full_account:
            #if not rec.get('name', False):
             #   rec.update({'name': _('Unknown Partner')})
            progress['init_bal'] = progress['init_bal'] + rec['init_bal']
            progress['debit'] = progress['debit'] + rec['debit']
            progress['credit'] = progress['credit'] + rec['credit']
            progress['balance'] = progress['balance'] + (rec['init_bal'] + rec['debit'] - rec['credit'])

        self.account_total = [progress]

        return full_account



    
        
report_sxw.report_sxw('report.account.assistant.report', 'account.account', 'addons/account_ntc/report/account_assistant_report.rml', parser=account_assistant_report , header=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

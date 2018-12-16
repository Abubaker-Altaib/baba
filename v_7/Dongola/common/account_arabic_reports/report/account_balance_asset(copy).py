# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from datetime import datetime  
from datetime import timedelta  
import time
from report import report_sxw
from account_custom.common_report_header import common_report_header as common_header
from account.report.common_report_header import common_report_header as custom_common_header

class account_balance_asset(report_sxw.rml_parse, common_header, custom_common_header):
    _name = 'report.account.account.all.balance'

    def __init__(self, cr, uid, name, context=None):
        super(account_balance_asset, self).__init__(cr, uid, name, context=context)
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.date_lst = []
        self.date_lst_string = ''
        self.result_acc = []
        self.result_acc2 = []
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'get_total': self._get_total,
            'sum_credit': self._sum_credit,
            'get_account_name': self._get_account_name,
            'get_fiscalyear':self._get_fiscalyear,
            'get_filter': self._get_filter,
            'get_filter_Trans': self._get_filter_Trans,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period ,
            'get_account': self._get_account,
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
        self.acc_balances = data.get('form', {}).get('acc_balances', False)
        self.detail = data.get('form', {}).get('detail', False)
        self.credit = 0
        self.debit = 0
        ctx2 = data.get('form', {}).get('used_context', {}).copy()
        ctx2.update({'initial_bal': bool(data['form']['initial_balance'])})
        
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

        return super(account_balance_asset, self).set_context(objects, data, new_ids, report_type=report_type)

    def _get_account(self, data):
        if data['model'] == 'account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['id']).company_id.name
        return super(account_balance , self)._get_account(data)

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

    def _get_account_name(self, data):
        if data['account_ids']:
 
           res=[]
           account=data['account_ids'][0]
           name=self.pool.get('account.account').browse(self.cr, self.uid,account).name
           res={'account':name}
 
           return name
 

    def lines(self, form, ids=[], done=None):
        def _process_child(accounts, disp_acc, parent):
                state_query = ""
                account_rec = [acct for acct in accounts if acct['id'] == parent][0]

                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'detialed': account_rec['detialed'],
                    'user_type': account_rec['user_type'],
                    'code': account_rec['code'],
                    'no_code': account_rec['no_code'],
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
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalperiod_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        if child_ids:
            ids = child_ids
  
        accounts = obj_account.read(self.cr, self.uid, ids, ['id','detialed','user_type','type', 'code','no_code', 'name', 'debit', 'credit', 'balance', 'parent_id', 'level', 'child_id', 'company_id'], ctx)

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
        self.result_acc=filter(lambda acc: acc['type'] == 'view' or   acc['detialed'] == True       ,self.result_acc)
        if ctx['fiscalyear']:
            f_code=fiscalyear_obj.browse(self.cr, self.uid,ctx['fiscalyear']).code
        else:
            date_from = datetime.strptime(ctx['date_from'], '%Y-%m-%d')
            f_code=date_from.year  
            fiscalyear_id = fiscalyear_obj.search(self.cr, self.uid, [ ('code', '=', f_code)])
            f_code=fiscalyear_obj.browse(self.cr, self.uid,fiscalyear_id[0]).code   
        fiscalyear_ids = fiscalyear_obj.search(self.cr, self.uid, [ ('code', '=', f_code)])
        period_ids = fiscalperiod_obj.search(self.cr, self.uid, [('fiscalyear_id', 'in', fiscalyear_ids)])
        init_period = fiscalperiod_obj.search(self.cr, self.uid, [('special', '=', True), ('fiscalyear_id', 'in', fiscalyear_ids)])      
        date_start = fiscalperiod_obj.browse(self.cr, self.uid, init_period[0], context=ctx).date_start
        l_debit=0.0
        l_credit =0.0
        init=0
        res2 = {     
                    'init': 0,
                }
        '''for acc in self.result_acc:

             self.cr.execute('SELECT (sum(COALESCE(debit,0)) - sum(COALESCE(credit,0))) as init  FROM account_move_line l, account_move am WHERE l.move_id=am.id  AND m.date=date_start AND l.account_id = %s , (acc['id'],))
             res2['init'] = self.cr.fetchone()[0] or 0.0
             acc['init_balance']=acc['init_balance']-res2['init']'''
          
        types=[]    
        self.cr.execute(" select id as type_id  from account_account_type where report_type in ('income','liability' )")
        query_type = self.cr.dictfetchall()
        types = [ x['type_id'] for x in query_type ]
        for it in self.result_acc:
          sign = it['user_type'][0] in types and -1 or 1
          if it['balance']!=0:
            it['balance']=sign*it['balance']
          if it['init_balance']!=0:
            it['init_balance']=sign*it['init_balance']

        return self.result_acc

    def lines2(self, form, ids=[], done=None):
        def _process_child(accounts, disp_acc, parent):
                print "------------------inside lines 2",form,"ids are",ids
                state_query = ""
                account_rec = [acct for acct in accounts if acct['id'] == parent][0]

                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'detialed': account_rec['detialed'],
                    'user_type': account_rec['user_type'],
                    'code': account_rec['code'],
                    'no_code': account_rec['no_code'],
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
                else:
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
                            self.result_acc2.append(res)
                    elif disp_acc == 'bal_solde':
                        if account_rec['level'] == 1 :
                            self.result_acc2.append(res)
                    elif disp_acc == 'bal':
                        if form['initial_balance'] and (res['init_balance'] + res['balance']) != 0 : 
                            self.result_acc2.append(res)
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
        ctx['type'] = 'balance'   # This type used in _QUERY_GET to defertiate form GENERAL STATEMENT REPORTS
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalperiod_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        if child_ids:
            ids = child_ids
  
        accounts = obj_account.read(self.cr, self.uid, ids, ['id','detialed','user_type','type', 'code','no_code', 'name', 'debit', 'credit', 'balance', 'parent_id', 'level', 'child_id', 'company_id'], ctx)

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
        self.result_acc2=filter(lambda acc: acc['type'] == 'view' or   acc['detialed'] == True       ,self.result_acc2)
        if ctx['fiscalyear']:
            f_code=fiscalyear_obj.browse(self.cr, self.uid,ctx['fiscalyear']).code
        else:
            date_from = datetime.strptime(ctx['date_from'], '%Y-%m-%d')
            f_code=date_from.year  
            fiscalyear_id = fiscalyear_obj.search(self.cr, self.uid, [ ('code', '=', f_code)])
            f_code=fiscalyear_obj.browse(self.cr, self.uid,fiscalyear_id[0]).code   
        fiscalyear_ids = fiscalyear_obj.search(self.cr, self.uid, [ ('code', '=', f_code)])
        period_ids = fiscalperiod_obj.search(self.cr, self.uid, [('fiscalyear_id', 'in', fiscalyear_ids)])
        init_period = fiscalperiod_obj.search(self.cr, self.uid, [('special', '=', True), ('fiscalyear_id', 'in', fiscalyear_ids)])      
        date_start = fiscalperiod_obj.browse(self.cr, self.uid, init_period[0], context=ctx).date_start
        l_debit=0.0
        l_credit =0.0
        init=0
        res2 = {     
                    'init': 0,
                }
        '''for acc in self.result_acc2:

             self.cr.execute('SELECT (sum(COALESCE(debit,0)) - sum(COALESCE(credit,0))) as init  FROM account_move_line l, account_move am WHERE l.move_id=am.id  AND m.date=date_start AND l.account_id = %s , (acc['id'],))
             res2['init'] = self.cr.fetchone()[0] or 0.0
             acc['init_balance']=acc['init_balance']-res2['init']'''
          
        types=[]    
        self.cr.execute(" select id as type_id  from account_account_type where report_type in ('income','liability' )")
        query_type = self.cr.dictfetchall()
        types = [ x['type_id'] for x in query_type ]
        for it in self.result_acc2:
          sign = it['user_type'][0] in types and -1 or 1
          if it['balance']!=0:
            it['balance']=sign*it['balance']
          if it['init_balance']!=0:
            it['init_balance']=sign*it['init_balance']

        return self.result_acc2

    def _get_credit(self):
        return self.credit

    def _get_debit(self):
        return self.debit

    def _get_total(self, form, ids=[]):
        ctx = self.context.copy()
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalperiod_obj = self.pool.get('account.period')
        obj_account = self.pool.get('account.account')
        res=[]
        account_ids=form['account_ids']
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, account_ids, ctx)
        self.chart_company = self.pool.get('account.account').browse(self.cr, self.uid, form['chart_account_id']).company_id.id
        company_ids= self.pool.get('res.company').search(self.cr, self.uid, [('id', 'child_of', self.chart_company)], context=self.context)
        date_from = form.get('date_from', False)
        date_to = form.get('date_to', False)

        if  form.get('fiscalyear_id', False):
            f_code=fiscalyear_obj.browse(self.cr, self.uid,form.get('fiscalyear_id', False)).code
        else:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            f_code=date_from.year  
 
               
        fiscalyear_ids = fiscalyear_obj.search(self.cr, self.uid, [ ('code', '=', f_code)])
        period_ids = fiscalperiod_obj.search(self.cr, self.uid, [('fiscalyear_id', 'in', fiscalyear_ids)])
        print f_code,fiscalyear_ids,period_ids,"55555555555555555555555555"

        res=[]
        init_period = fiscalperiod_obj.search(self.cr, self.uid, [('special', '=', True), ('fiscalyear_id', 'in', fiscalyear_ids)])      
        date_start = fiscalperiod_obj.browse(self.cr, self.uid, init_period[0], context=ctx).date_start


        
        print date_from,date_to,date_start,"?????????????????????????????"
 
        date_from2 = form.get('date_from', False)
        if date_from2==date_start:
            print "=============here 1"
            self.cr.execute('''select sum(COALESCE(debit,0)),sum(COALESCE(credit,0)) from account_move_line s join account_move m on m.id=s.move_id where m.state!='reversed' and  s.date >%s and s.date <= %s and s.company_id in %s  and s.account_id in %s''',(date_from,date_to,tuple(company_ids),tuple(child_ids)))     
     
            move=self.cr.fetchone()
     
     
            self.cr.execute('''select (sum(debit)-sum(credit)) as bl from account_move_line s join account_move m on m.id=s.move_id where m.state!='reversed' and  m.date<= %s and s.company_id in %s and s.account_id in %s''',(date_from,tuple(company_ids),tuple(child_ids)))  
            initial=self.cr.fetchone()
 

        else:
            print "=================here 2"
            self.cr.execute('''select sum(COALESCE(debit,0)),sum(COALESCE(credit,0)) from account_move_line s join account_move m on m.id=s.move_id where m.state!='reversed' and  m.date between %s and %s and s.company_id in %s  and s.account_id in %s''',(date_from,date_to,tuple(company_ids),tuple(child_ids)))     
     
            move=self.cr.fetchone()
     
     
            self.cr.execute('''select (sum(debit)-sum(credit)) as bl from account_move_line s join account_move m on m.id=s.move_id where m.state!='reversed' and  m.date < %s and s.company_id in %s and s.account_id in %s''',(date_from,tuple(company_ids),tuple(child_ids)))  
            initial=self.cr.fetchone()
 

        res.append( {
 
                    'debit': move[0],
                    'credit': move[1],
                    'balance': initial[0]+move[0]-move[1],
                    'init_balance': initial[0],
 

                })
 
        return res



    def _get_credit(self):
        return self.credit

    def _get_debit(self):
        return self.debit

report_sxw.report_sxw('report.account.account.balance.asset.arabic', 'account.account', 'addons/account_arabic_reports/report/account_balance_asset.rml', parser=account_balance_asset , header=True)


 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

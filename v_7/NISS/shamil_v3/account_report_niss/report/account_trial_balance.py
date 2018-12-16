# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from account_custom.common_report_header import common_report_header as common_header
from account.report.common_report_header import common_report_header as custom_common_header

class account_trial_balance(report_sxw.rml_parse, common_header, custom_common_header):

    _name = 'report.account.trial.balance'

    def set_context(self, objects, data, ids, report_type=None):
        obj_move = self.pool.get('account.move.line')
        self.account_ids = data['form']['account_ids']
        ctx = data['form'].get('used_context', {})
        #ctx.update({'chart_account_id':  data['form']['account_id'][0]})
        ctx.update({'state':  data['form']['target_move']})
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx)
        ctx2 = ctx.copy()
        ctx2.update({'initial_bal':  bool(data['form']['initial_balance'])})
        ctx2.update({'periods': []})
        if data['form']['initial_balance']:
            self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)

        return super(account_trial_balance, self).set_context(objects, data, ids, report_type=report_type)

    def __init__(self, cr, uid, name, context=None):
        super(account_trial_balance, self).__init__(cr, uid, name, context=context)
        self.init_balance = 0.0

        self.balance = 0.0
        self.sum_debit = 0.0
        self.sum_credit = 0.0
        self.init_currency_amount = 0.0
        self.tot_currency = 0.0
        self.account_sum = 0.0
        self.context = context
        self.localcontext.update({
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'balance':self._balance,
            'init_balance':self._init_balance,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_filter': self._get_filter,
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,
            'get_fiscalyear': self._get_fiscalyear,
            'display_currency':self._display_currency,
            'get_sortby': self._get_sortby,
            'get_target_move': self._get_target_move,
    })

    def _display_currency(self, data):
        return data['form']['currency_id'][1]


    def _display_initial_balance(self, data):
        return data['form']['initial_balance']

    def _get_sortby(self, data):
        return 'code'

    def lines(self,data):
        account_obj = self.pool.get('account.account')
        currency_obj = self.pool.get('res.currency')
        currency=currency_obj.browse(self.cr,self.uid,data['form']['currency_id'][0])
        query2=' 1=1 '
        if self.account_ids:
            #for account_id in self.account_ids:
            child_ids =  account_obj.search(self.cr, self.uid,[('parent_id','child_of',self.account_ids)])
            if len(child_ids) == 1: query2 += " and ac.id = " + str(self.account_ids[0])
            else: 
              query2 = " ac.id in " + str(tuple(child_ids))
            self.query += " and l.account_id = ac.id "
        if data['form']['target_move']=='posted':
            self.query += " and m.state = 'posted' "
        if data['form']['target_move']=='all':
            self.query += " and m.state <> 'draft' "
        if not currency.base:
            if data['form']['currency_id']:
               self.query += " and l.currency_id = '"+ str(data['form']['currency_id'][0]) + "'"
               if not data['form']['all_account']:
                   query2 += " and ac.currency_id = '"+ str(data['form']['currency_id'][0]) + "'" 
            self.cr.execute("SELECT ac.id as account,ac.name as name ,ac.code as code,\
                           (select SUM(COALESCE(l.amount_currency,0)) from  \
                             account_move_line l\
                             LEFT OUTER JOIN res_currency c ON l.currency_id = c.id \
                             INNER JOIN account_move m ON  l.move_id = m.id \
                             WHERE l.amount_currency > 0 AND " + self.query + " and l.account_id = ac.id) as  amount_debit,\
                             (select SUM(COALESCE(l.amount_currency,0)) from  \
                             account_move_line l\
                             LEFT OUTER JOIN res_currency c ON l.currency_id = c.id \
                             INNER JOIN account_move m ON  l.move_id = m.id \
                             WHERE l.amount_currency < 0 AND " + self.query + " and l.account_id = ac.id) as  amount_credit \
                             FROM   account_account ac \
                             where " + query2 + " \
                             ORDER BY ac.code" )

            res = self.cr.dictfetchall()
         
        if currency.base:
            self.cr.execute("SELECT ac.id as account,ac.name as name ,ac.code as code,\
                            (select SUM(COALESCE(l.debit,0)) from  \
                             account_move_line l\
                             INNER JOIN account_move m ON  l.move_id = m.id \
                             WHERE l.currency_id is null AND " + self.query + " and l.account_id = ac.id) as  amount_debit,\
                             (select SUM(COALESCE(l.credit,0)) from  \
                             account_move_line l\
                             INNER JOIN account_move m ON  l.move_id = m.id \
                             WHERE  l.currency_id is null AND  " + self.query + " and l.account_id = ac.id) as  amount_credit \
                             FROM   account_account ac \
                             where ac.currency_id is null AND " + query2 + " \
                             ORDER BY ac.code" )

            res = self.cr.dictfetchall()
        res1=[]
        for l in res:l.update({'credit':0.0 , 'debit' : 0.0,'init_bal':0.0}) 
        for l in res:
         
           if not l['amount_credit']: l['amount_credit']= 0
           if not l['amount_debit']: l['amount_debit']= 0
           if not currency.base:
              l['amount_credit']=-l['amount_credit']
           if data['form']['initial_balance']:
               if not currency.base:
                  self.cr.execute("SELECT  SUM(COALESCE(l.amount_currency,0)) as init_amount_currency \
                                 FROM   account_move_line l LEFT OUTER JOIN res_currency c ON l.currency_id = c.id \
                                        INNER JOIN account_move m ON  l.move_id = m.id \
                                        LEFT OUTER JOIN account_account ac ON l.account_id = ac.id \
                                WHERE ac.id=%s AND l.currency_id=%s  AND " + self.init_query + " \
                                " ,(l['account'],data['form']['currency_id'][0],))
                  l['init_bal']=self.cr.fetchone()[0] or 0.0
               if currency.base:
                  self.cr.execute("SELECT (sum(COALESCE(l.debit,0)) -sum(COALESCE(l.credit,0))) as init_amount_currency \
                                 FROM   account_move_line l  \
                                        INNER JOIN account_move m ON  l.move_id = m.id \
                                        LEFT OUTER JOIN account_account ac ON l.account_id = ac.id \
                                WHERE ac.id=%s AND l.currency_id is null AND " + self.init_query + " \
                                " ,(l['account'],))
                  l['init_bal']=self.cr.fetchone()[0] or 0.0
               self.sum_debit+=l['amount_debit']
               self.sum_credit+=l['amount_credit']
               self.balance +=l['amount_debit']-l['amount_credit']
               self.init_balance+=l['init_bal']
               if l['amount_credit'] != 0 or l['amount_debit']!=0 or l['init_bal']!=0:res1.append(l)

        return res1

    def _sum_debit(self):
        return self.sum_debit

    def _sum_credit(self):
        return self.sum_credit

    def _balance(self):
        return self.balance
    def _init_balance(self):
        return self.init_balance

report_sxw.report_sxw('report.account.trial.balance', 'account.account', 'addons/account_report_niss/report/account_report_trial_balance.rml', parser =  account_trial_balance, header='external')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

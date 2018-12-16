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

class account_statement(report_sxw.rml_parse, common_header, custom_common_header):

    _name = 'report.account.account.statement'

    def set_context(self, objects, data, ids, report_type=None):
        obj_move = self.pool.get('account.move.line')
        ctx = data['form'].get('used_context', {})
        ctx.update({'chart_account_id':  data['form']['account_id'][0]})
        ctx['type'] = 'balance'   # This type used in _QUERY_GET to defertiate form GENERAL STATEMENT REPORTS
        ctx.update({'state':  data['form']['target_move']})
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx)
        ctx2 = ctx.copy()
        ctx2.update({'initial_bal':  bool(data['form']['initial_balance'])})
        ctx2.update({'periods': []})
        if data['form']['initial_balance']:
            self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)
        self.type_selection = data['form']['type_selection']
        self.sort_selection = data['form']['sort_selection']
        self.reverse = data['form']['reverse']
        return super(account_statement, self).set_context(objects, data, ids, report_type=report_type)

    def __init__(self, cr, uid, name, context=None):
        super(account_statement, self).__init__(cr, uid, name, context=context)
        self.init_balance = 0.0
        self.sum_debit = 0.0
        self.sum_credit = 0.0
        self.account_sum = 0.0
        self.context = context
        self.localcontext.update({
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'balance':self._balance,
            'ibalance':self._ibalance,
            'get_account_name': self._get_account_name,
            'get_account_code': self._get_account_code,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_account_id': self._get_account_id,
            'get_account': self._get_account,
            'get_filter': self._get_filter,
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,
            'get_fiscalyear': self._get_fiscalyear,
            'display_currency':self._display_currency,
            'display_initial_balance':self._display_initial_balance,
            'get_sortby': self._get_sortby,
            'get_target_move': self._get_target_move,
    })


    def _get_account_name(self, data):
        if data['account_id']:
 
           res=[]
           account=data['account_id'][0]
           name=self.pool.get('account.account').browse(self.cr, self.uid,account).name
           res={'account':name}
 
           return name

    def _get_account_code(self, data):
        if data['account_id']:
           account=data['account_id'][0]
           for account in self.pool.get('account.account').browse(self.cr, self.uid, [account], context=self.context):
               code=account.code
           line_ids = self.pool.get('unit.report.line').search(self.cr,self.uid, [ ('code', '=', code)], context=self.context)
           for line in self.pool.get('unit.report.line').browse(self.cr, self.uid, line_ids, context=self.context):
               closure=line.closure
 
           return closure

    def _display_currency(self, data):
        return data['form']['amount_currency']


    def _display_initial_balance(self, data):
        return data['form']['initial_balance']


    def _get_sortby(self, data):
        if self.sort_selection == 'date':
            if self.type_selection == 'total':
                self.sort_selection = 'MIN(m.date), MIN(l.create_date)'
            else:
                self.sort_selection = 'date, l.create_date'
            return 'Date'
        elif self.sort_selection == 'ref':
            return 'Reference Number'
        return 'Date'

    def _get_account_id(self, data):
        return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['account_id'][0]).id

    def _sum_debit(self):
        return self.sum_debit

    def _sum_credit(self):
        return self.sum_credit

    def _balance(self):
        return self.account_sum

    def _ibalance(self):
        self.init_balance=0.0
        self.cr.execute('SELECT (sum(debit) - sum(credit)) as balance FROM account_move_line l WHERE ' + self.init_query)
        self.init_balance = self.cr.fetchone()[0] or 0.0
        return self.init_balance

    def lines(self,data):
       
        if self.reverse == False:
            self.query += " and m.state <> 'reversed' "
        if self.type_selection == 'total':
            self.cr.execute("SELECT COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0.0) AS debit, MIN(m.ref) AS ref,\
                                    MIN(m.name) AS move, MIN(m.date) AS date \
                             FROM   account_move_line l INNER JOIN account_move m ON  l.move_id = m.id \
                             WHERE " + self.query + "  GROUP BY l.move_id ORDER BY " + self.sort_selection)

        else:
             self.cr.execute("SELECT l.id, COALESCE(l.credit,0) as credit, COALESCE(l.debit,0) as debit, l.amount_currency|| ' ' ||c.symbol as currency,  l.name as label, m.ref, m.name as move, l.date,cc.name as name \
                             FROM   account_move_line l LEFT OUTER JOIN res_currency c ON l.currency_id = c.id \
                                    INNER JOIN account_move m ON  l.move_id = m.id \
                                    INNER JOIN account_account cc ON  l.account_id = cc.id \
                            WHERE " + self.query + " \
                            ORDER BY l." + self.sort_selection)

        res = self.cr.dictfetchall()
        if self.init_balance  and self.account_sum == 0.0:
            self.account_sum += self.init_balance
        
        for l in res:
            l['credit'] = l['credit'] == 'None' and 0 or l['credit']
            l['debit'] = l['debit'] == 'None' and 0 or l['debit']
            self.sum_credit += l['credit']
            self.sum_debit += l['debit']
            self.account_sum += l['debit'] - l['credit']
            l['progress'] = self.account_sum
        return res

report_sxw.report_sxw('report.account.account.statement.detailed', 'account.account', 'addons/account_arabic_reports/report/account_statement_detailed.rml', parser=account_statement, header=True)

report_sxw.report_sxw('report.account.account.statement.total', 'account.account', 'addons/account_arabic_reports/report/account_statement_total.rml', parser=account_statement, header=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

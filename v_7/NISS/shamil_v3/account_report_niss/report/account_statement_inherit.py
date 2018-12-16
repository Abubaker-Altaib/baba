# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from osv import fields, osv
from tools.translate import _
from report import report_sxw
from account_custom.common_report_header import common_report_header as common_header
from account.report.common_report_header import common_report_header as custom_common_header

class account_statement(report_sxw.rml_parse, common_header, custom_common_header):

    _name = 'report.account.statement.inherit'

    def set_context(self, objects, data, ids, report_type=None):
        account_obj = self.pool.get('account.account')
        currency_obj = self.pool.get('res.currency')
        obj_move = self.pool.get('account.move.line')
        ctx = data['form'].get('used_context', {})
        ctx.update({'chart_account_id':  data['form']['account_id'][0]})
        ctx.update({'state':  data['form']['target_move']})
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx)
        ctx2 = ctx.copy()
        ctx2.update({'initial_bal':  bool(data['form']['initial_balance'])})
        ctx2.update({'periods': []})
        if data['form']['initial_balance']:
            self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2) 
            partner_id = data['form']['partner_id']
            if partner_id:
                self.init_query += " and l.partner_id = %s"%(partner_id[0])

            analytic_account_id = data['form']['analytic_account_id']
            if analytic_account_id:
                self.init_query += " and l.analytic_account_id = %s"%(analytic_account_id[0])
            currency_id = data['form']['currency_id']
            if currency_id:
                self.currency_is_base = currency_obj.browse(self.cr, self.uid, currency_id[0]).base
                if self.currency_is_base:
                    self.init_query += " and l.currency_id IS NULL "
                else:
                    self.init_query += " and l.currency_id = %s"%(currency_id[0])
        account_selected= account_obj.browse(self.cr, self.uid, data['form']['account_id'][0],context=ctx2)
        #This lines if type is view and currency is selected
        if account_selected.type == 'view' and data['form']['currency_id'] and not self.currency_is_base:
            account_ids = account_obj.search(self.cr, self.uid, [('currency_id','=',data['form']['currency_id'][0] ), ('type','!=','view'), ('id', 'child_of', account_selected.id)], order='code')
            self.init_query += " and l.account_id in %s "%(str(tuple(account_ids)))
            self.query += " and l.account_id in %s "%(str(tuple(account_ids)))
        self.type_selection = data['form']['type_selection']
        self.sort_selection = data['form']['sort_selection']
        self.reverse = data['form']['reverse']
        return super(account_statement, self).set_context(objects, data, ids, report_type=report_type)

    def __init__(self, cr, uid, name, context=None):
        super(account_statement, self).__init__(cr, uid, name, context=context)
        self.init_query = ' 1<> 1'
        self.currency_is_base = False
        self.init_balance = 0.0
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
            'ibalance':self._ibalance,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_account_id': self._get_account_id,
            'get_account': self._get_account,
            'get_filter': self._get_filter,
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,
            'get_fiscalyear': self._get_fiscalyear,
            'display_currency':self._display_currency,
            'icurrency_amount':self._icurrency_amount,
            'sum_amount_curency': self._sum_amount_curency,
            'display_initial_balance':self._display_initial_balance,
            'get_sortby': self._get_sortby,
            'get_target_move': self._get_target_move,
            'reset': self._reset,
    })

    def _reset(self, data):
        self.sum_debit = 0.0
        self.sum_credit = 0.0
        self.tot_currency = 0.0
        self.account_sum = 0.0

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
        return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['account_id'][0]).name

    def _sum_debit(self):
        return self.sum_debit

    def _sum_credit(self):
        return self.sum_credit

    def _sum_amount_curency(self):
        if self.currency_is_base:
            return self.account_sum
        return self.tot_currency

    def _icurrency_amount(self):
        self.init_currency_amount = 0.0
        query = ""
        #IF the currency is base currnecy do query for all line that has no currency
        if self.currency_is_base:
            query = 'SELECT (sum(debit) - sum(credit)) as balance FROM account_move_line l WHERE ' + self.init_query
        else:
            query = 'SELECT (sum(amount_currency)) as amount_currency FROM account_move_line l WHERE ' + self.init_query
        self.cr.execute(query)
        self.init_currency_amount = self.cr.fetchone()[0] or 0.0
        return self.init_currency_amount

    def _balance(self):
        return self.account_sum

    def _ibalance(self):

        self.init_balance = 0.0
        self.cr.execute('SELECT (sum(debit) - sum(credit)) as balance FROM account_move_line l WHERE ' + self.init_query)
        self.init_balance = self.cr.fetchone()[0] or 0.0
        return self.init_balance

    def lines(self, data):
        currency_obj = self.pool.get('res.currency')
        if self.reverse == False:
            self.query += " and m.state <> 'reversed' "
        partner_id = data['form']['partner_id']
        if partner_id:
            self.query += " and l.partner_id = %s"%(partner_id[0])
        analytic_account_id = data['form']['analytic_account_id']
        if analytic_account_id:
            self.query += " and l.analytic_account_id = %s"%(analytic_account_id[0])
        currency_id = data['form']['currency_id']
        currency_is_base = False
        if currency_id:
            currency_is_base = currency_obj.browse(self.cr, self.uid, currency_id[0]).base
            if currency_is_base:
                self.query += " and l.currency_id IS NULL "
            else:
                self.query += " and l.currency_id = %s"%(currency_id[0])
        if self.type_selection == 'total':
            self.cr.execute("SELECT COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0.0) AS debit, MIN(m.ref) AS ref,\
                                    MIN(m.name) AS move, MIN(m.date) AS date \
                             FROM   account_move_line l INNER JOIN account_move m ON  l.move_id = m.id \
                             WHERE " + self.query + "  GROUP BY l.move_id ORDER BY " + self.sort_selection)

        else:
             self.cr.execute("SELECT l.id, COALESCE(l.amount_currency,0) as amount_currency, COALESCE(l.credit,0) as credit, COALESCE(l.debit,0) as debit, l.amount_currency|| ' ' ||c.symbol as currency,  l.name as label, m.ref, m.name as move, l.date , coalesce(p.name || ']' || p.code || '[',p.name) as partner_name,'P/' || l.permission as permission, \
  (select chk_seq from account_voucher v where v.move_id = m.id) AS chk_seq ,\
  (select substring(chk_seq ,length(chk_seq)-5, 6 )from account_voucher v where v.move_id = m.id) AS chk_seq1\
                             FROM   account_move_line l LEFT OUTER JOIN res_currency c ON l.currency_id = c.id \
                                    LEFT OUTER JOIN res_partner p ON l.partner_id = p.id \
                                    INNER JOIN account_move m ON  l.move_id = m.id \
                            WHERE " + self.query + " \
                            ORDER BY l." + self.sort_selection)

        res = self.cr.dictfetchall()
        if self.init_balance  and self.account_sum == 0.0 and not currency_is_base:
            self.account_sum += self.init_balance 
        elif currency_is_base:
            if data['form']['amount_currency']:
                self.account_sum += self.init_currency_amount
            else:
                self.account_sum += self.init_balance 

        if self.init_currency_amount  and self.tot_currency==0.0:
            self.tot_currency  += self.init_currency_amount
        for l in res:
            if data['form']['amount_currency'] ==1 and not currency_is_base:
                self.tot_currency +=l['amount_currency']
                l['progress_currency'] = self.tot_currency
                if l['amount_currency'] < 0:l['credit']=-l['amount_currency']
                if l['amount_currency'] > 0:l['debit']=l['amount_currency']
                self.sum_credit += l['credit']
                self.sum_debit += l['debit']
                self.account_sum += l['debit'] - l['credit']
                l['progress'] = self.tot_currency
            else:
                l['credit'] = l['credit'] == 'None' and 0 or l['credit']
                l['debit'] = l['debit'] == 'None' and 0 or l['debit']
                self.sum_credit += l['credit']
                self.sum_debit += l['debit']
                self.account_sum += l['debit'] - l['credit']
                l['progress'] = self.account_sum
        if data['form']['partner_id']:
            if not res and not self.init_balance:
               raise osv.except_osv(_('Warning'), _("this partner have balance equal zero "))
        return res

report_sxw.report_sxw('report.account.statement.detailed.inherit', 'account.account', 'addons/account_report_niss/report/account_statement_detailed_inherit.rml', parser=account_statement, header='external')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

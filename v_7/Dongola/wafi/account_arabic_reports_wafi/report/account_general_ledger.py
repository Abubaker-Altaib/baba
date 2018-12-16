# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from openerp.tools.translate import _
from account_custom.common_report_header import common_report_header as common_header
from account.report.common_report_header import common_report_header as custom_common_header

class general_ledger(report_sxw.rml_parse, common_header, custom_common_header):
    
    _name = 'report.account.general.ledger'

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        obj_move = self.pool.get('account.move.line')
        self.sortby = data['form'].get('sortby', 'sort_date')
        context = data['form'].get('used_context', {})
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=context)
        self.ctx2 = data['form'].get('used_context', {}).copy()
        self.ctx2.update({'initial_bal':  bool(data['form']['initial_balance'])})
        self.ctx2.update({'periods': []})
        self.init_balance = data['form']['initial_balance']
        if self.init_balance:
            self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=self.ctx2)
        self.display_account = data['form']['display_account']
        self.target_move = data['form'].get('target_move', 'all')
        ctx = self.context.copy()       
        ctx['fiscalyear_id'] = data['form']['fiscalyear_id']
        if data['form']['filter'] == 'filter_period':
            ctx['period_from'] = data['form']['period_from']
            ctx['period_to'] = data['form']['period_to']
        elif data['form']['filter'] == 'filter_date':
            ctx['date_from'] = data['form']['date_from']
            ctx['date_to'] = data['form']['date_to']
        ctx['state'] = data['form']['target_move']
        self.context.update(ctx)
        if (data['model'] == 'ir.ui.menu'):
            new_ids = data['form']['chart_account_id']
            
            objects = self.pool.get('account.account').browse(self.cr, self.uid, [new_ids])
        self.state_query = ""
        if self.target_move == 'posted':
            self.state_query = " AND m.state = 'posted' "
        return super(general_ledger, self).set_context(objects, data, new_ids, report_type=report_type)

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(general_ledger, self).__init__(cr, uid, name, context=context)
        self.cr = cr
        self.uid = uid
        self.query = ""
        self.tot_currency = 0.0
        self.period_sql = ""
        self.sold_accounts = {}
        self.sortby = 'sort_date'
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit_account': self._sum_debit_account,
            'sum_credit_account': self._sum_credit_account,
            'sum_balance_account': self._sum_balance_account,
            'sum_currency_amount_account': self._sum_currency_amount_account,
            'get_children_accounts': self.get_children_accounts,
            'get_fiscalyear': self.get_fiscalyear_br,
            'get_journal': self._get_journal,
            'get_account': self._get_account,
            'get_start_period': self.get_start_period_br,
            'get_end_period': self.get_end_period_br,
            'get_filter': self._get_filter,
            'get_filter_Trans': self._get_filter_Trans,
            'get_sortby_gl': self._get_sortby_gl,
            'get_start_date':self._get_date_from,
            'get_end_date':self._get_date_to,
            'get_target_move': self._get_target_move,
            'get_Translation': self._get_Translation,
            'get_display_account': self._get_display_account,
            'get_label_according_model': self._get_label_according_model,
            'get_multi_company': self._get_multi_company,
        })
        self.context = context

    def _sum_currency_amount_account(self, account):
        self.cr.execute('SELECT sum(l.amount_currency) AS tot_currency \
                FROM account_move_line l \
                WHERE l.account_id = %s AND %s' % (account.id, self.query))
        sum_currency = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            self.cr.execute('SELECT sum(l.amount_currency) AS tot_currency \
                            FROM account_move_line l \
                            WHERE l.account_id = %s AND %s ' % (account.id, self.init_query))
            sum_currency += self.cr.fetchone()[0] or 0.0
        return sum_currency

    def get_children_accounts(self, account):
        res = []
        currency_obj = self.pool.get('res.currency')
        ids_acc = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, account.id)
        currency = account.currency_id and account.currency_id or account.company_id.currency_id
        for child_account in self.pool.get('account.account').browse(self.cr, self.uid, ids_acc, context=self.context):
            sql = """
                SELECT count(id)
                FROM account_move_line AS l
                WHERE %s AND l.account_id = %%s
            """ % (self.query)
            self.cr.execute(sql, (child_account.id,))
            num_entry = self.cr.fetchone()[0] or 0
            sold_account = self._sum_balance_account(child_account)
            self.sold_accounts[child_account.id] = sold_account
            if self.display_account == 'movement':
                if child_account.type != 'view' and num_entry != 0:
                    res.append(child_account)
            elif self.display_account == 'not_zero':
                if child_account.type != 'view' and num_entry != 0:
                    if not currency_obj.is_zero(self.cr, self.uid, currency, sold_account):
                        res.append(child_account)
            else:
                res.append(child_account)
        if not res:
            return [account]
        return res
    def lines(self, account):
        res = {}
        """ Return all the account_move_line of account with their account code counterparts """
        move_state = ['draft', 'posted', 'completed']
        if self.target_move == 'posted':
            move_state = ['posted', '']
        # First compute all counterpart strings for every move_id where this account appear.
        # Currently, the counterpart info is used only in landscape mode
        self.cr.execute("   SELECT m1.move_id, \
                            array_to_string(ARRAY(SELECT DISTINCT a.code \
                                          FROM account_move_line m2 \
                                          LEFT JOIN account_account a ON (m2.account_id=a.id) \
                                          WHERE m2.move_id = m1.move_id \
                                          AND m2.account_id<>%s), ', ') AS counterpart \
                FROM (SELECT move_id \
                        FROM account_move_line l \
                        LEFT JOIN account_move m ON (m.id = l.move_id) \
                        WHERE " + self.query + " " + self.state_query + "  AND l.account_id = %s GROUP BY move_id) m1 ", (account.id, account.id))
        counterpart_res = self.cr.dictfetchall()
        counterpart_accounts = {}
        for i in counterpart_res:
            counterpart_accounts[i['move_id']] = i['counterpart']
        del counterpart_res

        # Then select all account_move_line of this account
        if self.sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'
        else:
            sql_sort = 'l.date, l.move_id'

        self.cr.execute("SELECT l.id AS lid, l.date AS ldate, j.code AS lcode, l.currency_id,l.amount_currency,l.ref AS lref, \
                            l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, l.period_id AS lperiod_id, \
                            l.partner_id AS lpartner_id, m.name AS move_name, m.id AS mmove_id,per.code as period_code, c.symbol AS currency_code, \
                            i.id AS invoice_id, i.type AS invoice_type, i.number AS invoice_number, p.name AS partner_name \
                        FROM account_move_line l \
                            JOIN account_move m on (l.move_id=m.id) \
                            LEFT JOIN res_currency c on (l.currency_id=c.id) \
                            LEFT JOIN res_partner p on (l.partner_id=p.id) \
                            LEFT JOIN account_invoice i on (m.id =i.move_id) \
                            LEFT JOIN account_period per on (per.id=l.period_id) \
                            JOIN account_journal j on (l.journal_id=j.id) \
                        WHERE " + self.query + " " + self.state_query + " AND l.account_id = %s ORDER by " + sql_sort, (account.id,))
        res_lines = self.cr.dictfetchall()
        res_init = []
        ############if res_lines and self.init_balance:
        if self.init_balance:
            res_init = {'lid':0, 'ldate':'', 'lcode':'', 'amount_currency':0, 'lref':'', 'lname': 'Initial Balance', 'lperiod_id':'', 
                    'lpartner_id':'', 'move_name': '', 'mmove_id':'', 'period_code':'', 'currency_code':'' , 'currency_id': None,
                    'invoice_id':'', 'invoice_type':'', 'invoice_number':'', 'partner_name':''}
            res_init.update(self.pool.get('account.account').read(self.cr, self.uid, account.id, ['debit','credit','balance'], context=self.ctx2))
            res = [res_init] + res_lines
        else:
            res = res_lines
        account_sum = 0.0
        for l in res:
            l['move'] = l['move_name'] != '/' and l['move_name'] or ('*' + str(l['mmove_id']))
            l['partner'] = l['partner_name'] or ''
            account_sum += l['debit'] - l['credit']
            l['progress'] = account_sum
            l['line_corresp'] = l['mmove_id'] == '' and ' ' or counterpart_accounts[l['mmove_id']]  # .replace(', ',',')
            # Modification of amount Currency
            if l['credit'] > 0:
                if l['amount_currency'] != None:
                    l['amount_currency'] = abs(l['amount_currency']) * -1
            if l['amount_currency'] != None:
                self.tot_currency = self.tot_currency + l['amount_currency']
        return res  #----------------- Lines() END

#--------------------------------------Sum_Debit--------------------
    def _sum_debit_account(self, account):
        if account.type == 'view':
            sum_debit = account.debit
        else:
            move_state = ['draft', 'posted', 'completed']
            if self.target_move == 'posted':
                move_state = ['posted', '']
            self.cr.execute('SELECT sum(debit) \
                    FROM account_move_line l \
                    JOIN account_move m ON (m.id = l.move_id) \
                    WHERE (l.account_id = %s) ' + self.state_query + ' \
                    AND ' + self.query + ' '
                    , (account.id,))
            sum_debit = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            childs = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, account.id)
            self.cr.execute('SELECT sum(debit) \
                    FROM account_move_line l \
                    JOIN account_move m ON (m.id = l.move_id) \
                    WHERE (l.account_id IN %s) ' + self.state_query + '\
                    AND ' + self.init_query + ' '
                    , (tuple(childs),))
            # Add initial balance to the result
            sum_debit += self.cr.fetchone()[0] or 0.0
        return sum_debit

#--------------------------------------Sum_Credit--------------------
    def _sum_credit_account(self, account):
        if account.type == 'view':
            sum_credit = account.credit
        else:
            move_state = ['draft', 'posted', 'completed']
            if self.target_move == 'posted':
                move_state = ['posted', '']
            self.cr.execute('SELECT sum(credit) \
                    FROM account_move_line l \
                    JOIN account_move m ON (m.id = l.move_id) \
                    WHERE (l.account_id = %s) ' + self.state_query + ' \
                    AND ' + self.query + ' '
                    , (account.id,))
            sum_credit = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            childs = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, account.id)
            self.cr.execute('SELECT sum(credit) \
                    FROM account_move_line l \
                    JOIN account_move m ON (m.id = l.move_id) \
                    WHERE (l.account_id IN %s) ' + self.state_query + ' \
                    AND ' + self.init_query + ' '
                    , (tuple(childs),))
            # Add initial balance to the result
            sum_credit += self.cr.fetchone()[0] or 0.0
        return sum_credit

#--------------------------------------Sum_Balance--------------------
    def _sum_balance_account(self, account):
        if account.type == 'view':
            sum_balance = account.balance
        else:
            move_state = ['draft', 'posted', 'completed']
            if self.target_move == 'posted':
                move_state = ['posted', '']
            self.cr.execute('SELECT (sum(debit) - sum(credit)) as tot_balance \
                    FROM account_move_line l \
                    JOIN account_move m ON (m.id = l.move_id) \
                    WHERE (l.account_id = %s) ' + self.state_query + ' \
                    AND ' + self.query + ' '
                    , (account.id,))
            sum_balance = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            childs = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, account.id)
            self.cr.execute('SELECT (sum(debit) - sum(credit)) as tot_balance \
                    FROM account_move_line l \
                    JOIN account_move m ON (m.id = l.move_id) \
                    WHERE (l.account_id IN %s) ' + self.state_query + ' \
                    AND ' + self.init_query + ' '
                    , (tuple(childs),))
            # Add initial balance to the result
            sum_balance += self.cr.fetchone()[0] or 0.0
        return sum_balance

    def _get_account(self, data):
        if data['model'] == 'account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, [data['form']['id']]).company_id.name
        return super(general_ledger , self)._get_account(data)



report_sxw.report_sxw('report.account.general.ledger.arabic.wafi', 'account.account', 'addons/account_arabic_reports/report/account_general_ledger.rml', parser=general_ledger, header=True)

report_sxw.report_sxw('report.account.general.ledger_landscape.arabic.wafi', 'account.account', 'addons/account_arabic_reports_wafi/report/account_general_ledger_landscape.rml', parser=general_ledger, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

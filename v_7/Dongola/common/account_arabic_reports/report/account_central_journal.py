# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time

from report import report_sxw
from common_report_header import common_report_header
#
# Use period and Journal for selection or resources
#
class journal_print(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(journal_print, self).__init__(cr, uid, name, context=context)
        self.period_ids = []
        self.journal_ids = []
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'get_filter': self._get_filter,
            'get_fiscalyear': self._get_fiscalyear,
            'get_account': self._get_account,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_sortby': self._get_sortby,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'display_currency':self._display_currency,
            'get_target_move': self._get_target_move,
        })

    def set_context(self, objects, data, ids, report_type=None):
        obj_move = self.pool.get('account.move.line')
        new_ids = ids
        self.query_get_clause = ''
        self.target_move = data['form'].get('target_move', 'all')
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'active_ids' in data['form'] and data['form']['active_ids'] or []
            self.query_get_clause = 'AND '
            self.query_get_clause += obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context', {}))
            objects = self.pool.get('account.journal.period').browse(self.cr, self.uid, new_ids)
        if new_ids:
            self.cr.execute('SELECT period_id, journal_id FROM account_journal_period WHERE id IN %s', (tuple(new_ids),))
            res = self.cr.fetchall()
            self.period_ids, self.journal_ids = zip(*res)
        
        self.state_query = ""
        if self.target_move == 'posted':
            self.state_query = " AND am.state = 'posted' "

        return super(journal_print, self).set_context(objects, data, ids, report_type=report_type)

    def lines(self, period_id, journal_id):
        move_state = ['draft', 'posted']
        if self.target_move == 'posted':
            move_state = ['posted']

        self.cr.execute('SELECT a.currency_id, a.code, a.name, c.symbol AS currency_code, l.currency_id, l.amount_currency, SUM(debit) AS debit, SUM(credit) AS credit  \
                        from account_move_line l  \
                        LEFT JOIN account_move am ON (l.move_id=am.id) \
                        LEFT JOIN account_account a ON (l.account_id=a.id) \
                        LEFT JOIN res_currency c on (l.currency_id=c.id) WHERE l.period_id=%s  ' + self.state_query + ' AND l.journal_id=%s ' + self.query_get_clause + ' GROUP BY a.id, a.code, a.name,l.amount_currency,c.symbol, a.currency_id,l.currency_id', (period_id, journal_id))
        return self.cr.dictfetchall()

    def _set_get_account_currency_code(self, account_id):
        self.cr.execute("SELECT c.symbol as code "\
                "FROM res_currency c,account_account as ac "\
                "WHERE ac.id = %s AND ac.currency_id = c.id" % (account_id))
        result = self.cr.fetchone()
        if result:
            self.account_currency = result[0]
        else:
            self.account_currency = False

    def _get_account(self, data):
        if data['model'] == 'account.journal.period':
            return self.pool.get('account.journal.period').browse(self.cr, self.uid, data['id']).company_id.name
        return super(journal_print, self)._get_account(data)

    def _get_fiscalyear(self, data):
        if data['model'] == 'account.journal.period':
            return self.pool.get('account.journal.period').browse(self.cr, self.uid, data['id']).fiscalyear_id.name
        return super(journal_print, self)._get_fiscalyear(data)

    def _display_currency(self, data):
        if data['model'] == 'account.journal.period':
            return True
        return data['form']['amount_currency']

report_sxw.report_sxw('report.account.central.journal.arabic', 'account.journal.period', 'addons/account_arabic_reports/report/account_central_journal.rml', parser=journal_print, header=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

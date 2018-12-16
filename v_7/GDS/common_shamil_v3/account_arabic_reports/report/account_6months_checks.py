# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from common_report_header import common_report_header
from report import report_sxw
from openerp.tools.translate import _
import mx
from mx import DateTime
import datetime 

class account_6months_checks(report_sxw.rml_parse, common_report_header):
    # _name='account.6months.checks.arabic'

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(account_6months_checks, self).__init__(cr, uid, name, context=context)
        self.sort_selection = 'date'
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'get_fiscalyear': self._get_fiscalyear,
            'get_sortby': self._get_sortby,

    })

    def set_context(self, objects, data, ids, report_type=None):
        obj_move = self.pool.get('account.move.line')
        self.query_get_clause = ''
        if (data['model'] == 'ir.ui.menu'):
            self.query_get_clause = 'AND '
            self.query_get_clause += obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context', {}))
            self.sort_selection = data['form'].get('sort_selection', 'date')
            self.state_query = " AND am.state = 'posted' "

        return super(account_6months_checks, self).set_context(objects, data, ids, report_type=report_type)

   

    def lines(self):
        obj_mline = self.pool.get('account.move.line')
        self.cr.execute('SELECT l.id FROM account_move_line l , account_move am WHERE l.move_id=am.id AND (l.account_id IN (SELECT id from account_account WHERE type = %s) ) AND l.credit > 0  AND l.statement_id is null AND l.ref like %s '' ORDER BY l.' + self.sort_selection + ', l.move_id', ('liquidity', '%/CHK/%/%',))
        ids = map(lambda x: x[0], self.cr.fetchall())
        for idz in obj_mline.browse(self.cr, self.uid, ids):
            date1 = str(datetime.date.today())
            now = mx.DateTime.Parser.DateTimeFromString(date1)
            nm = now.month
            dat = mx.DateTime.Parser.DateTimeFromString(idz.date)
            dn = dat.month
            lst = []
            rslt = nm - dn
            if (rslt >= 6):
                lst.append(idz.id)
            return obj_mline.browse(self.cr, self.uid, lst)
 


    def _get_fiscalyear(self, data):
        if data['model'] == 'account.journal.period':
            return self.pool.get('account.journal.period').browse(self.cr, self.uid, data['id']).fiscalyear_id.name
        return super(account_6months_checks, self)._get_fiscalyear(data)

    def _get_sortby(self, data):
        if self.sort_selection == 'date':
            return 'Date'
        elif self.sort_selection == 'ref':
            return 'Refrence'
        return 'Date'

report_sxw.report_sxw('report.account.6months.checks.arabic', 'account.move.line', 'addons/account_arabic_reports/report/account_6months_checks.rml', parser=account_6months_checks, header='custom landscape')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

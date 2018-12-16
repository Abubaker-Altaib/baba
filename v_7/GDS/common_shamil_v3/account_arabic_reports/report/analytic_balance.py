# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from account_custom.common_report_header import common_report_header

class account_analytic_balance(report_sxw.rml_parse, common_report_header):
    
    def __init__(self, cr, uid, name, context):
        super(account_analytic_balance, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_objects': self._get_objects,
            'lines_g': self._lines_g,
            'total': self._total,
        })
        self.acc_ids = []
        self.read_data = []
        self.empty_acc = False
        self.acc_data_dict = {}  # maintains a relation with an account with its successors.
        self.acc_sum_list = []  # maintains a list of all ids

    def get_children(self, ids, date1, date2):
        new_ids = self._get_children_and_consol(self.cr, self.uid, ids, 'account.analytic.account')
        self.ids = self.pool.get('account.analytic.account').search(self.cr, self.uid, [('type', '=', 'normal'), ('id', 'in', new_ids)])
        self.cr.execute("SELECT aa.id AS id, aa.name AS name, aa.code AS code, MIN(c.name) AS company, \
                            COALESCE(sum(aal.debit),0.0) AS debit, COALESCE(sum(aal.credit),0.0) AS credit \
                        FROM account_move_line AS aal INNER JOIN account_analytic_account AS aa \
                                ON aal.analytic_account_id=aa.id INNER JOIN res_company c \
                                ON c.id = aa.company_id \
                        WHERE  (aal.analytic_account_id IN %s)\
                            AND (aal.date>=%s) AND (aal.date<=%s) \
                        GROUP BY aa.id, aa.name, aa.code, aa.company_id \
                        ORDER BY aa.company_id,aa.code", (tuple(self.ids), date1, date2))
        read_data = self.cr.dictfetchall()

        for data in read_data:
            if (data['id'] not in self.acc_ids):
                inculde_empty = True
                if (not self.empty_acc) and data['debit'] - data['credit'] == 0.00:
                    inculde_empty = False
                if inculde_empty:
                    self.acc_ids.append(data['id'])
                    self.read_data.append(data)
        return True


    def _get_objects(self, empty_acc, date1, date2):
        if self.read_data:
            return self.read_data
        self.empty_acc = empty_acc
        self.read_data = []
        self.get_children(self.ids, date1, date2)        
        self.total_res = []
        self.cr.execute("SELECT COALESCE(sum(aal.debit),0.0) AS debit, COALESCE(sum(aal.credit),0.0) AS credit \
                        FROM account_move_line AS aal, account_analytic_account AS aa \
                        WHERE (aal.analytic_account_id=aa.id) \
                            AND (aal.analytic_account_id IN %s)\
                            AND (aal.date>=%s) AND (aal.date<=%s) ", (tuple(self.ids), date1, date2))
        self.total_res = self.cr.dictfetchall()
        return self.read_data

    def _lines_g(self, account_id, date1, date2):
        account_analytic_obj = self.pool.get('account.analytic.account')
        ids = account_analytic_obj.search(self.cr, self.uid, [('parent_id', 'child_of', [account_id])])
        self.cr.execute("SELECT aa.name AS name, aa.code AS code, \
                            COALESCE(sum(aal.debit),0.0) AS debit, COALESCE(sum(aal.credit),0.0) AS credit \
                        FROM account_move_line AS aal, account_account AS aa \
                        WHERE (aal.account_id=aa.id) \
                            AND (aal.analytic_account_id IN %s)\
                            AND (date>=%s) AND (date<=%s) \
                        GROUP BY aal.account_id, aa.name, aa.code ", (tuple(ids), date1, date2))

        res = self.cr.dictfetchall()
        return res

    def _total(self):
        return self.total_res
report_sxw.report_sxw('report.account.analytic.account.balance.arabic', 'account.analytic.account', 'addons/account_arabic_reports/report/analytic_balance.rml',
        parser=account_analytic_balance, header=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


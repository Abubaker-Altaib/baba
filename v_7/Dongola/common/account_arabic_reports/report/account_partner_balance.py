# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
import re
import copy

from openerp.tools.translate import _
from report import report_sxw
from common_report_header import common_report_header

class partner_balance(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(partner_balance, self).__init__(cr, uid, name, context=context)
        self.account_ids = []
        self.localcontext.update({
            'time': time,
            'get_fiscalyear': self._get_fiscalyear,
            'get_filter': self._get_filter,
            'get_filter_Trans': self._get_filter_Trans,
            'get_account': self._get_account,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_partners':self._get_partners,
            'get_target_move': self._get_target_move,
            'account_partners':self.account_partners,
            'get_accounts':self.get_accounts,
            'account_total':self._account_total,
            'account_has_partner':self._account_has_partner,
            'get_multi_company': self._get_multi_company,
        })

    def set_context(self, objects, data, ids, report_type=None):
        self.display_partner = data['form'].get('display_partner', 'non-zero_balance')
        obj_move = self.pool.get('account.move.line')

        self.result_selection = data['form'].get('result_selection')
        self.target_move = data['form'].get('target_move', 'all')
        self.account_ids = data['form'].get('acc_ids', [])
        self.partner_id = data['form'].get('partner_ids', [])
        self.fiscalyear = data['form'].get('fiscalyear_id', False)
        ctx2 = data['form'].get('used_context', {}).copy()
        ctx2.update({'initial_bal':True, 'periods':[]}) 
        ctx2['type'] = 'balance' 
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)    
        if data.get('form', {}).get('filter', '') == 'filter_no':
            periods = self.pool.get('account.period').search(self.cr, self.uid, [('fiscalyear_id', '=', ctx2.get('fiscalyear', 0))], order='date_start')
            ctx2.update({'period_from': periods and periods[0] or False})
            ctx2.update({'period_to': periods and periods[len(periods) - 1] or False})
        ctx2.update({'fiscalyear': False})
        self.init_query = ''
        first_period = self.pool.get('account.period').search(self.cr, self.uid, [], order='date_start', limit=1)
        if data['form'].get('fiscalyear_id', False) and first_period and ctx2.get('period_from') != first_period[0]:
            self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)
        self.account_total = 0.0
        self.account_has_partner = False
        if (self.result_selection == 'customer'):
            self.ACCOUNT_TYPE = ('receivable',)
        elif (self.result_selection == 'supplier'):
            self.ACCOUNT_TYPE = ('payable',)
        else:
            self.ACCOUNT_TYPE = ('payable', 'receivable')

        self.state_query = ""
        if self.target_move == 'posted':
            self.state_query = " AND am.state = 'posted' "
        return super(partner_balance, self).set_context(objects, data, ids, report_type=report_type)

#~~~~~~~~~~~~~~~~~~~ get_accounts Function ~~~~~~~~~
    def get_accounts(self, data):
        '''
        if self.init_query:
            self.cr.execute('SELECT 	(COALESCE(sum(debit),0) - COALESCE(sum(credit),0))  as init_balance, a.name, a.id FROM 	account_account a , account_move_line l  WHERE a.id = l.account_id AND account_id IN %s AND ' + self.init_query + ' GROUP BY a.id,a.name '  ,(tuple(data),))
            res = self.cr.dictfetchall()
        else:
            res = []

        account_with_init = [r['id'] for r in res]
        minus = [x for x in data if x not in account_with_init]
        a = self.pool.get('account.account').read(self.cr, self.uid, minus, ['name'] )
        '''
        a = self.pool.get('account.account').read(self.cr, self.uid, data, ['name', 'code'])
        for r in a:
            r['init_balance'] = 0.0
        # return (res + a)
        return a
      

    def _account_total(self):
        return self.account_total

    def _account_has_partner(self):
        return self.account_has_partner

#~~~~~~~~~~~~~~~~~~~ account_partners Function ~~~~~~~~~
    def account_partners(self, account, init):
        self.account_has_partner = False
        move_state = ['draft', 'posted', 'completed']
        if self.target_move == 'posted':
            move_state = ['posted']

        full_account = []
        result_tmp = 0.0
        partner_query = ""
        if self.partner_id:
            partner_query = len(self.partner_id) == 1 and " AND l.partner_id in (%s) " % (self.partner_id[0]) or " AND l.partner_id in %s " % (str(tuple(self.partner_id)))
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
                            "WHERE l.partner_id = p.id AND am.id = l.move_id " + self.state_query + " AND account_id = %s AND " + self.init_query + ") AS init_bal "\
                    "FROM account_move_line l LEFT JOIN res_partner p ON (l.partner_id=p.id) JOIN account_move am ON (am.id = l.move_id)" \
                    "WHERE l.account_id = %s " + self.state_query + " AND " + self.query + " " + partner_query + " " \
                    "GROUP BY l.move_id,p.id, p.name " \
                    ") as result "\
                "GROUP BY result.id, result.name  ORDER BY result.name ", (account, account,))
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
                    "WHERE l.account_id = %s " + self.state_query + " AND " + self.query + "  " + partner_query + " "  \
                    "GROUP BY l.move_id,p.id, p.name " \
                    ") as result "\
                "GROUP BY result.id, result.name ORDER BY result.name  ", (account,))

        res = self.cr.dictfetchall()

###############
        part_ids = [ r['id'] for r in res ]
        init_parts = ""
        if part_ids:
            init_parts = " AND l.partner_id not in %s " 
        if self.init_query:
            param = init_parts and  (account, tuple(part_ids),) or (account,)
            self.cr.execute(
                    "SELECT p.name , 0 as debit , 0 as credit , l.partner_id, COALESCE(sum(debit-credit), 0.0) AS init_bal \
                     FROM account_move_line AS l, account_move AS am , res_partner as p \
                     WHERE  p.id =l.partner_id and am.id = l.move_id " + self.state_query + " \
                            AND account_id = %s AND " + self.init_query + "  " + init_parts + " " + partner_query + " \
                     GROUP BY l.partner_id, p.name", param)
        
            init_part = self.cr.dictfetchall()
            
            res = res + init_part
################ 

        if self.display_partner == 'non-zero_balance':
            if not self.fiscalyear:
                for e in res:
                    e['init_bal'] = 0.0
            prec = self.pool.get('decimal.precision').precision_get(self.cr, self.uid, 'Account')
            full_account = [r for r in res if round(r['init_bal'] + r['debit'] - r['credit'], prec) != 0]
        else:
            full_account = [r for r in res]

        progress = {'init_bal':0.0, 'debit':0.0, 'credit':0.0, 'balance':0.0}
        for rec in full_account:
            if not rec.get('name', False):
                rec.update({'name': _('Unknown Partner')})
            progress['init_bal'] = progress['init_bal'] + rec['init_bal']
            progress['debit'] = progress['debit'] + rec['debit']
            progress['credit'] = progress['credit'] + rec['credit']
            progress['balance'] = progress['balance'] + (rec['init_bal'] + rec['debit'] - rec['credit'])

        self.account_total = [progress]
        if len(full_account) == 0:
            self.account_has_partner = True
        return full_account
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  

    def _get_partners(self):
        if self.result_selection == 'customer':
            return _('Receivable Accounts')
        elif self.result_selection == 'supplier':
            return _('Payable Accounts')
        elif self.result_selection == 'customer_supplier':
            return _('Receivable and Payable Accounts')
        return ''

report_sxw.report_sxw('report.account.partner.balance.arabic', 'res.partner', 'addons/account_arabic_reports/report/account_partner_balance.rml', parser=partner_balance, header="external")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

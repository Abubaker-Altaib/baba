# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import re
from report import report_sxw
from common_report_header import common_report_header

class cost_type_ledger(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(cost_type_ledger, self).__init__(cr, uid, name, context=context)
        self.init_bal_sum = 0.0
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit_cost_type': self._sum_debit_cost_type,
            'sum_credit_cost_type': self._sum_credit_cost_type,
            'get_currency': self._get_currency,
            'comma_me': self.comma_me,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_account': self._get_account,
            'get_filter': self._get_filter,
            'get_filter_Trans': self._get_filter_Trans,
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,
            'get_fiscalyear': self._get_fiscalyear,
            'get_journal': self._get_journal,
            'get_intial_balance':self._get_intial_balance,
            #'display_initial_balance':self._display_initial_balance,
            'display_currency':self._display_currency,
            'get_target_move': self._get_target_move,
            'get_init_array':self._get_init_array,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        obj_move = self.pool.get('account.move.line')
        obj_cost_type = self.pool.get('account.cost.type')
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context', {}))
        ctx2 = data['form'].get('used_context',{}).copy()
        #self.initial_balance = data['form'].get('initial_balance', True)
        self.cumulate_move = data['form'].get('cumulate_move', True)
       # if self.initial_balance:
            #ctx2.update({'initial_bal': True,'periods':[]})
            #self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)
        self.reconcil = data['form'].get('reconcil', True)
        #self.result_selection = data['form'].get('result_selection', 'customer')
        self.amount_currency = data['form'].get('amount_currency', False)
        self.target_move = data['form'].get('target_move', 'all')
        self.cost_type_id = data['form'].get('cost_type_ids',[])
        self.account_ids = data['form'].get('account_ids',[])
        
        self.init_array = []
        COST_TYPE_REQUEST = ''

        self.state_query = " AND am.state <> 'reversed' "
        if self.target_move == 'posted':
            self.state_query = " AND am.state = 'posted' "


        obj_account = self.pool.get('account.account')

        if (data['model'] == 'account.cost.type'):
            ## Si on imprime depuis les partenaires
            if ids:
                COST_TYPE_REQUEST =  "AND line.cost_type_id IN %s",(tuple(ids),)
       
        if not self.account_ids: 
            child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ctx2.get('chart_account_id',[]), ctx2)
            self.account_ids = obj_account.search(self.cr, self.uid, [('id','in',child_ids),('type','in',self.ACCOUNT_TYPE)])

        cost_type_to_use = []

        if self.cost_type_id:
            cost_type_to_use = self.cost_type_id
        else:
            #self.pool.get('res.partner').search(cr, uid, [()])
            self.cr.execute(
                "SELECT DISTINCT l.cost_type_id " \
                "FROM account_move_line AS l, account_account AS account, " \
                " account_move AS am " \
                "WHERE l.cost_type_id IS NOT NULL " \
                    "AND l.account_id = account.id " \
                    "AND am.id = l.move_id "+self.state_query+" "
                    "AND l.account_id IN %s " \
                    " " + COST_TYPE_REQUEST + " " \
                    "AND account.active ",
                (tuple(self.account_ids),))

            res = self.cr.dictfetchall()
            for res_line in res:
                cost_type_to_use.append(res_line['cost_type_id'])
        new_ids = cost_type_to_use

        self.cost_type_ids = new_ids
        objects = obj_cost_type.browse(self.cr, self.uid, new_ids)
        
        return super(cost_type_ledger, self).set_context(objects, data, new_ids, report_type)

    def comma_me(self, amount):
        if type(amount) is float:
            amount = str('%.2f'%amount)
        else:
            amount = str(amount)
        if (amount == '0'):
             return ' '
        orig = amount
        new = re.sub("^(-?\d+)(\d{3})", "\g<1>'\g<2>", amount)
        if orig == new:
            return new
        else:
            return self.comma_me(new)

    def lines(self, cost_type):
        full_account = []
        if self.reconcil:
            RECONCILE_TAG = " "
        else:
            RECONCILE_TAG = "AND l.reconcile_id IS NULL"
        
        if self.cumulate_move:
            print 'self.state_query',self.state_query
            self.cr.execute(
                "SELECT min(l.id) as id, min(l.date) as date , min(j.code) as code, min(acc.code) as a_code, min(acc.name) as a_name, min(l.ref) as ref, min(am.name) as move_name, min(l.name) as name,CASE WHEN sum(debit) > sum(credit) THEN sum(debit) - sum(credit) ELSE 0 END AS debit , CASE WHEN sum(credit) > sum(debit) THEN sum(credit) - sum(debit) ELSE 0 END AS credit, min(l.amount_currency) as amount_currency,min(l.currency_id) as currency_id, min(c.symbol) AS currency_code " \
                "FROM account_move_line l " \
                "LEFT JOIN account_journal j " \
                    "ON (l.journal_id = j.id) " \
                "LEFT JOIN account_account acc " \
                    "ON (l.account_id = acc.id) " \
                "LEFT JOIN res_currency c ON (l.currency_id=c.id)" \
                "LEFT JOIN account_move am ON (am.id=l.move_id)" \
                "WHERE l.cost_type_id = %s " \
                    "AND l.account_id IN %s AND " + self.query +" "+self.state_query+" " \
                    " " + RECONCILE_TAG + " "\
                    " group by l.move_id ORDER BY date ",
                    (cost_type.id, tuple(self.account_ids)))
        else:
            self.cr.execute(
                "SELECT l.id, l.date, j.code, acc.code as a_code, acc.name as a_name, l.ref, am.name as move_name, l.name, l.debit, l.credit, l.amount_currency,l.currency_id, c.symbol AS currency_code " \
                "FROM account_move_line l " \
                "LEFT JOIN account_journal j " \
                    "ON (l.journal_id = j.id) " \
                "LEFT JOIN account_account acc " \
                    "ON (l.account_id = acc.id) " \
                "LEFT JOIN res_currency c ON (l.currency_id=c.id)" \
                "LEFT JOIN account_move am ON (am.id=l.move_id)" \
                "WHERE l.cost_type_id = %s " \
                    "AND l.account_id IN %s AND " + self.query +" "+self.state_query+" " \
                    " " + RECONCILE_TAG + " "\
                    "ORDER BY l.date",
                    (cost_type.id, tuple(self.account_ids)))

        res = self.cr.dictfetchall()
        sum = 0.0
        #if self.initial_balance:
            #sum = self.init_bal_sum
        for r in res:
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            full_account.append(r)
        return full_account

    def _get_init_array(self):
        return self.init_array

    def _get_intial_balance(self, cost_type):
        self.init_array = []
        move_state = ['draft','posted','completed']
        if self.target_move == 'posted':
            move_state = ['posted']
        if self.reconcil:
            RECONCILE_TAG = " "
        else:
            RECONCILE_TAG = "AND l.reconcile_id IS NULL"
        self.cr.execute(
            "SELECT COALESCE(SUM(l.debit),0.0), COALESCE(SUM(l.credit),0.0), COALESCE(sum(debit-credit), 0.0) " \
            "FROM account_move_line AS l,  " \
            "account_move AS am "
            "WHERE l.cost_type_id = %s " \
            "AND am.id = l.move_id " +self.state_query+" "\
            "AND account_id IN %s" \
            " " + RECONCILE_TAG + " "\
            "AND " + self.init_query + "  ",
            (cost_type.id, tuple(self.account_ids)))
        res = self.cr.fetchall()
        self.init_bal_sum = res[0][2]
        self.init_array = res

    def _sum_debit_cost_type(self, cost_type):
        move_state = ['draft','posted','completed']
        if self.target_move == 'posted':
            move_state = ['posted']

        result_tmp = 0.0
        result_init = 0.0
        if self.reconcil:
            RECONCILE_TAG = " "
        else:
            RECONCILE_TAG = "AND reconcile_id IS NULL"
        



        if self.cumulate_move:
            self.cr.execute(
                    "select sum(debit) as debit from (SELECT  CASE WHEN sum(debit) > sum(credit) THEN sum(debit) - sum(credit) ELSE 0 END AS debit " \
                "FROM account_move_line AS l, " \
                "account_move AS am "
                "WHERE l.cost_type_id = %s " \
                    "AND am.id = l.move_id " +self.state_query+ " "\
                    "AND account_id IN %s" \
                    " " + RECONCILE_TAG + " " \
                    "AND " + self.query + "  group by l.move_id) as result",
                (cost_type.id,  tuple(self.account_ids),))
        else:
            self.cr.execute(
                "SELECT sum(debit) " \
                "FROM account_move_line AS l, " \
                "account_move AS am "
                "WHERE l.cost_type_id = %s " \
                    "AND am.id = l.move_id " +self.state_query+ " "\
                    "AND account_id IN %s" \
                    " " + RECONCILE_TAG + " " \
                    "AND " + self.query + " ",
                (cost_type.id,  tuple(self.account_ids),))

        contemp = self.cr.fetchone()
        if contemp != None:
            result_tmp = contemp[0] or 0.0
        else:
            result_tmp = result_tmp + 0.0

        return result_tmp  + result_init

    def _sum_credit_cost_type(self, cost_type):
        move_state = ['draft','posted','completed']
        if self.target_move == 'posted':
            move_state = ['posted']

        result_tmp = 0.0
        result_init = 0.0
        if self.reconcil:
            RECONCILE_TAG = " "
        else:
            RECONCILE_TAG = "AND reconcile_id IS NULL"
  



        if self.cumulate_move:
            self.cr.execute(
                    "select sum(credit) as credit from (SELECT  CASE WHEN sum(credit) > sum(debit) THEN sum(credit) - sum(debit) ELSE 0 END AS credit " \
                "FROM account_move_line AS l, " \
                "account_move AS am "
                "WHERE l.cost_type_id=%s " \
                    "AND am.id = l.move_id " +self.state_query+ " "\
                    "AND account_id IN %s" \
                    " " + RECONCILE_TAG + " " \
                    "AND " + self.query + "  group by l.move_id) as result",
                (cost_type.id, tuple(self.account_ids),))
        else:
            self.cr.execute(
                "SELECT sum(credit) " \
                "FROM account_move_line AS l, " \
                "account_move AS am "
                "WHERE l.cost_type_id=%s " \
                    "AND am.id = l.move_id " +self.state_query+ " "\
                    "AND account_id IN %s" \
                    " " + RECONCILE_TAG + " " \
                    "AND " + self.query + " ",
                (cost_type.id, tuple(self.account_ids),))   
        contemp = self.cr.fetchone()
        if contemp != None:
            result_tmp = contemp[0] or 0.0
        else:
            result_tmp = result_tmp + 0.0
        return result_tmp  + result_init

    

    def _sum_currency_amount_account(self, account, form):
        self._set_get_account_currency_code(account.id)
        self.cr.execute("SELECT sum(aml.amount_currency) FROM account_move_line as aml,res_currency as rc WHERE aml.currency_id = rc.id AND aml.account_id= %s ", (account.id,))
        total = self.cr.fetchone()
        if self.account_currency:
            return_field = str(total[0]) + self.account_currency
            return return_field
        else:
            currency_total = self.tot_currency = 0.0
            return currency_total

    #def _display_initial_balance(self, data):
        # if self.initial_balance:
            # return True
         #return False

    def _display_currency(self, data):
         if self.amount_currency:
             return True
         return False

report_sxw.report_sxw('report.account.cost.type.ledger', 'account.cost.type',
        'addons/account_cost_type/report/account_cost_type_ledger.rml',parser=cost_type_ledger,
        header='internal landscape')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

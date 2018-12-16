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
import copy

from tools.translate import _
from report import report_sxw
from common_report_header import common_report_header

class cost_type_balance(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        self.context = context
        super(cost_type_balance, self).__init__(cr, uid, name, context=context)
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
            #'get_partners':self._get_partners,
            'get_target_move': self._get_target_move,
            'account_cost_types':self.account_cost_types,
            'get_accounts':self.get_accounts,
            'account_total':self._account_total,
            #'account_has_partner':self._account_has_partner,
            'get_multi_company': self._get_multi_company,
        })

    def set_context(self, objects, data, ids, report_type=None):
        #self.display_partner = data['form'].get('display_partner', 'non-zero_balance')
        obj_move = self.pool.get('account.move.line')
        ctx2 = data.get('form',{}).get('used_context',{}).copy()
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=dict(ctx2.items()+ self.context.items()))
        #self.result_selection = data['form'].get('result_selection')
        self.target_move = data['form'].get('target_move', 'all')
        self.account_ids = data['form'].get('account_ids',[])
        self.cost_type_ids = data['form'].get('cost_type_ids',[])
        self.category_ids = data['form'].get('category_ids',[])      
        self.fiscalyear = data['form'].get('fiscalyear_id', False)
        ctx2 = data['form'].get('used_context',{}).copy()
        ctx2.update({'initial_bal':True,'periods':[]})
        
        if data.get('form',{}).get('filter','') == 'filter_no':
            periods = self.pool.get('account.period').search(self.cr, self.uid, [('fiscalyear_id','=',ctx2.get('fiscalyear',0))], order='date_start')
            ctx2.update({'period_from': periods and periods[0] or False})
            ctx2.update({'period_to': periods and periods[len(periods)-1] or False})
        ctx2.update({'fiscalyear': False})

        self.init_query = ''
        first_period = self.pool.get('account.period').search(self.cr, self.uid, [], order='date_start', limit=1)
        if data['form'].get('fiscalyear_id', False) and first_period and ctx2.get('period_from') != first_period[0]:
            self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)
        self.account_total = 0.0
        #self.account_has_partner = False

       
        self.state_query = " AND am.state <> 'reversed' "
        if self.target_move == 'posted':
            self.state_query = " AND am.state = 'posted' "
        return super(cost_type_balance, self).set_context(objects, data, ids, report_type=report_type)

#~~~~~~~~~~~~~~~~~~~ get_accounts Function ~~~~~~~~~
    def get_accounts(self,data):

        a = self.pool.get('account.account').read(self.cr, self.uid, data, ['name','code'] )
        for r in a:
            r['init_balance'] = 0.0

        return a
      

    def _account_total(self):
        return self.account_total




    def account_cost_types(self,account):
        #self.account_has_partner = False
        move_state = ['draft','posted','completed']
        if self.target_move == 'posted':
            move_state = ['posted']

        full_account = []
        result_tmp = 0.0

        print'self.cost_type_ids', self.cost_type_ids
        cost_type_query = " "
        cost_types = self.cost_type_ids
        print'cost_types',cost_types
        if cost_types:
            cost_type_query = len(cost_types) == 1 and " AND l.cost_type_id in (%s) " % (cost_types[0]) or " AND l.cost_type_id in %s " % (str(tuple(cost_types)))



        print 'cost_type_query',cost_type_query
        print 'self.state_query',self.state_query
        print ' self.query', self.query
               
        # select balance from move rather then total debit and total credit

        print 'account',account

        self.cr.execute(
                "SELECT COALESCE(id,0) id,name, sum(debit) as debit ,sum(credit) as credit, sum(sdebit) as sdebit ,sum(scredit) as scredit, 0 as init_bal " \
                "FROM   (SELECT t.id, l.move_id, t.name AS name, "\
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
                    "FROM account_move_line l LEFT JOIN account_cost_type t ON (l.cost_type_id=t.id) JOIN account_move am ON (am.id = l.move_id)" \
                    "WHERE l.account_id = %s "+ self.state_query+" AND " + self.query + "  "+ cost_type_query  + " "  \
                    "GROUP BY l.move_id,t.id, t.name " \
                    ") as result "\
                "GROUP BY result.id, result.name ORDER BY result.name  ",(account,))
        

        res = self.cr.dictfetchall()
        print'res',res

        part_ids = [ r['id'] for r in res ]


        full_account = [r for r in res]
        print 'full_account',full_account
        progress = {'init_bal':0.0, 'debit':0.0, 'credit':0.0, 'balance':0.0}
        for rec in full_account:
            #if not rec.get('name', False):
                #rec.update({'name': _('Unknown Partner')})
            #progress['init_bal'] = progress['init_bal']+rec['init_bal']
            progress['debit'] = progress['debit']+rec['debit']
            progress['credit'] = progress['credit']+rec['credit']
            progress['balance'] = progress['balance']+(rec['debit']-rec['credit'])

        self.account_total = [progress]
#        if len(full_account) == 0:
#            self.account_has_partner = True
        return full_account
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  


report_sxw.report_sxw('report.account.cost.type.balance', 'account.cost.type', 'addons/account_cost_type/report/account_cost_type_balance.rml',parser=cost_type_balance, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

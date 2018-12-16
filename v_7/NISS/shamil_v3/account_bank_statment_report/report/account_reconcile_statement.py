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
from datetime import datetime
from report import report_sxw
from account_custom.common_report_header import common_report_header



class account_statement(report_sxw.rml_parse, common_report_header):
    #_name = 'report.account.reconcile.statement2'

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(account_statement, self).__init__(cr, uid, name, context=context)
        self.sort_selection = 'date'
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
        })
        self.context = context

    
    '''def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        print"<<<<<<<<<<<<<<<<<<<<<<<<<",data
        if (data['model'] == 'ir.ui.menu'):

            objects = self.pool.get('account.bank.statement').browse(self.cr, self.uid, new_ids)

        return super(account_statement, self).set_context(objects, data, ids, report_type=report_type)'''


    def line_ids(self,  statement,type=''):  
        move_line_ids = [y.id for y in statement.move_line_ids]
        non_bank_moves = [x.id for x in statement.non_bank_moves]
        if type == 'non': #return ids of non bank moves
            return non_bank_moves
        elif type == 'period':#return ids of bank & non bank moves of the specified period
            ids = move_line_ids + non_bank_moves
            pre_date = self.pool.get('account.bank.statement')._pre_date(self.cr, self.uid, statement)
            d = statement.date     
            self.cr.execute("SELECT distinct l.id  FROM  account_move_line l  WHERE l.date <= %s \
                           and  l.date > %s and l.id in %s",(d.replace('/','-'), pre_date, tuple(ids)))
            res = [r[0] for r in self.cr.fetchall()]
            return res    
        elif type == 'cancel':#return ids of cancel 
            ids = move_line_ids + non_bank_moves
            pre_date = self.pool.get('account.bank.statement')._pre_date(self.cr, self.uid, statement)
            d = statement.date     
            self.cr.execute("SELECT distinct l.id  FROM  account_move_line l \
                              left join  account_move m on (l.move_id = m.id) \
                              WHERE l.date <= %s and  l.date > %s and l.id in %s and m.canceled_chk = True ",(d.replace('/','-'), pre_date, tuple(ids)))

            res = [r[0] for r in self.cr.fetchall()]
            return res   
        #return ids of bank & non bank moves
        return move_line_ids + non_bank_moves     

    ######### DEBIT ###########
    def _sum_debit(self, statement, type=''):
        lines = self.line_ids( statement,type)        
        if len(lines) < 1:
            return 0.0
        ctx = { 'company_id':statement.company_id.id, 'move_line_ids':lines}
        debit = statement.account_id and self.pool.get('account.account').read(self.cr, self.uid, statement.account_id.id, ['debit'], ctx)['debit'] or 0.0
        return debit



    ######### CREDIT ###########


    def _sum_credit(self, statement, type=''):
        lines = self.line_ids( statement,type)  
        if len(lines) < 1:
            return 0.0      
        ctx = { 'company_id':statement.company_id.id, 'move_line_ids':lines}#,'journal_ids':[journal_id]
        credit = statement.account_id and self.pool.get('account.account').read(self.cr, self.uid, statement.account_id.id, ['credit'], ctx)['credit'] or 0.0
        return credit

    ######### Print Move Lines ###########

    def lines(self, statement, type='', debit=False, credit=False):
        move_lines = self.line_ids( statement,type)   
        if len(move_lines) < 1:
            return {}
        line_query = len(move_lines) > 1 and " and l.id  IN %s " %(tuple(move_lines),) or " and l.id = %s " %(move_lines[0])
        amount_query = debit and  " and debit > 0 " or " and credit > 0 "
        self.cr.execute("SELECT distinct m.name as move, l.id, COALESCE(debit,0.0)as debit, COALESCE(credit,0.0) as credit, l.name as label ,l.ref as ref, l.date as date \
                         FROM  account_move_line l  \
                         left join  account_move m on (l.move_id = m.id) \
                         WHERE  l.account_id= %s " + line_query + amount_query + " ORDER BY l.date",( statement.journal_id.default_debit_account_id.id,))
        res = self.cr.dictfetchall() or {}
        return res

report_sxw.report_sxw('report.account.reconcile.statement.report.custom', 'account.bank.statement', 'account_bank_statment_report/report/account_reconcile_statement.rml', parser=account_statement, header=True)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

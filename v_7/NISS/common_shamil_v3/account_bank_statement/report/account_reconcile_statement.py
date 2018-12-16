# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import re
from openerp.osv import osv, orm
from openerp.tools.translate import _
from report import report_sxw
from account_custom.common_report_header import common_report_header

class account_statement(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(account_statement, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'report_sum':self.report_sum,
        })
        self.context = context

    def report_sum(self, statement):
        label = {'opening_balance':_('Last Journal Balance'),'balance_start':_('Last Bank Balance'),
                  'balance_end_real':_('Current Bank Balance'),'journal_balance':_('Current Journal Balance'),
                  'total_entry_encoding':_('Non-Journal Moves Total'),'balance_end':_('System Bank Balance'),
                  'line_ids.amount':_('Non-Bank Moves Total'),'non_bank_moves.debit':_('Unprecedented Revenue'),
                  'non_bank_moves.credit':_('Unprecedented Expense')}
        res = []
        stmt_pool = self.pool.get('account.bank.statement')
        statement_equation = statement.company_id.statement_equation
        statement_condition = statement.company_id.statement_condition
        if statement_equation and re.match(r'^[\.\+\-a-z_\*]*$', statement_equation):
            fields = filter(lambda x: len(x)>0,re.findall(r'(\(?[a-z_\.]*\)?)', statement_equation))
            fields.append(statement_condition)
            for f in fields:
                res.append((label.get(f,"unknown"), stmt_pool.calc_result(self.cr, self.uid, [statement.id], stmt_pool._name, f, context=self.context)))
        else:
            raise orm.except_orm(_('Error !'), _('You have unsupported characters in your equation! available character a-z,_,+,- and . '))
        return res

    def line_ids(self,  statement,type=''):
        stmt_pool = self.pool.get('account.bank.statement')
        if type == 'non': #return ids of non bank moves
            return [x.id for x in statement.non_bank_moves]
        elif type == 'period':#return ids of bank & non bank moves of the specified period
            ids = [x.id for x in statement.non_bank_moves] + [y.id for y in statement.move_line_ids]
            pre_date = stmt_pool._pre_date(self.cr, self.uid, statement)
            self.cr.execute("SELECT distinct l.id  FROM  account_move_line l  WHERE l.date <= %s \
                           and  l.date > %s and l.id in %s",(statement.date.replace('/','-'), pre_date, tuple(ids)))
            res = [r[0] for r in self.cr.fetchall()]
            return res
        #return ids of bank & non bank moves
        return [x.id for x in statement.non_bank_moves] + [y.id for y in statement.move_line_ids]

    ######### DEBIT ###########
    def _sum_debit(self, statement, type=''):
        account_obj = self.pool.get('account.account')
        lines = self.line_ids( statement,type)
        if len(lines) < 1:
            return 0.0
        ctx = { 'company_id':statement.company_id.id, 'move_line_ids':lines}#, 'journal_ids':[statement.journal_id.id]
        debit = statement.account_id and account_obj.read(self.cr, self.uid, statement.account_id.id, ['debit'], context=ctx)['debit'] or 0.0
        return debit


    ######### CREDIT ###########
    def _sum_credit(self, statement, type=''):
        account_obj = self.pool.get('account.account')
        lines = self.line_ids( statement,type)
        if len(lines) < 1:
            return 0.0      
        ctx = { 'company_id':statement.company_id.id, 'move_line_ids':lines}#,'journal_ids':[journal_id]
        credit = statement.account_id and account_obj.read(self.cr, self.uid, statement.account_id.id, ['credit'], context=ctx)['credit'] or 0.0
        return credit

    ######### Print Move Lines ###########
    def lines(self, statement, type='', debit=False, credit=False):
        move_lines = self.line_ids( statement,type)   
        if len(move_lines) < 1:
            return {}
        line_query = len(move_lines) > 1 and " and l.id  IN %s " %(tuple(move_lines),) or " and l.id = %s " %(move_lines[0])
        amount_query = debit and  " and debit > 0 " or " and credit > 0 "
        self.cr.execute("SELECT distinct l.id, COALESCE(debit,0.0)as debit, COALESCE(credit,0.0) as credit, l.name as label ,l.ref as ref, l.date as date,m.name as move \
                         FROM  account_move_line l  INNER JOIN account_move m ON m.id = l.move_id \
                         WHERE  l.account_id= %s " + line_query + amount_query + " ORDER BY l.date",( statement.journal_id.default_debit_account_id.id,))
        res = self.cr.dictfetchall() or {}
        return res

report_sxw.report_sxw('report.account.reconcile.statement.reportt', 'account.bank.statement', 'addons/account_bank_statement/report/account_reconcile_statement.rml', parser=account_statement, header=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

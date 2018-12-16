# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
import datetime
from report import report_sxw
from common_report_header import common_report_header


class account_statement(report_sxw.rml_parse, common_report_header):
    _name = 'report.account.reconcile.statement'
    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(account_statement, self).__init__(cr, uid, name, context=context)
        self.period_ids = []
        self.journal_ids = []
        self.ids_s = []
        self.sort_selection = 'date'
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'balance':self._balance,  ####
            'get_account': self._get_account,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,          
            'get_filter': self._get_filter,
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,
            'get_fiscalyear': self._get_fiscalyear,
            'display_currency':self._display_currency,            
            'display_closing_balance':self._display_closing_balance,  # # R ##
            'get_sortby': self._get_sortby,
            'get_target_move': self._get_target_move,        
            'get_debit':self._get_debit,
            'get_credit':self._get_credit,
        })
        self.context = context

    
    def set_context(self, objects, data, ids, report_type=None):   
        obj_move = self.pool.get('account.move.line')
        new_ids = ids
        self.credit = 0
        self.debit = 0
        self.query_get_clause = ''
        self.target_move = data['form'].get('target_move', 'all')
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context', {}))
        ctx2 = data['form'].get('used_context', {}).copy()
        ctx = self.context.copy()
        ctx['fiscalyear'] = data['form']['fiscalyear_id']
        if data['form']['filter'] == 'filter_period':
            ctx['period_from'] = data['form']['period_from']
            ctx['period_to'] = data['form']['period_to']
        elif data['form']['filter'] == 'filter_date':
            ctx['date_from'] = data['form']['date_from']
            ctx['date_to'] = data['form']['date_to']
        ctx['state'] = data['form']['target_move']
        self.context.update(ctx)

        if (data['model'] == 'ir.ui.menu'):
  
            objects = self.pool.get('account.bank.statement').browse(self.cr, self.uid, new_ids)
        self.state_query = ""
        if self.target_move == 'posted':
            self.state_query = " AND m.state = 'posted' "       
        if new_ids:
            
            self.cr.execute('SELECT period_id, journal_id FROM account_journal_period WHERE id IN %s', (tuple(new_ids),))
            res = self.cr.fetchall() 

            if res:
                self.period_ids, self.journal_ids = zip(*res)
            else:
                self.period_ids, self.journal_ids = [], []
        return super(account_statement, self).set_context(objects, data, ids, report_type=report_type)
    
    def _get_account_id(self, data):
        return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['account_id']).name

############################## DEBIT ###########
      
    def _sum_debit(self, period_id=False, journal_id=False):
        
        if not journal_id:
            journal_id = self.journal_ids
        else:
            journal_id = [journal_id]

        move_state = ['draft', 'posted', 'completed']
        if self.target_move == 'posted':
            move_state = ['posted', '']

        bank_statement = []

        self.cr.execute('select bs.id from account_bank_statement bs')
        account_bank_statement_obj = self.cr.fetchone()

        bank_statement.append(account_bank_statement_obj[0])
       

        account_bank_statement_object = self.pool.get('account.bank.statement').browse(self.cr, self.uid, bank_statement)[0]
        move_lines = [] 
        for line in account_bank_statement_object.move_line_ids:
            move_lines.append(line.id)
        self.cr.execute('select j.default_debit_account_id from account_bank_statement bs, account_journal j where bs.journal_id = j.id')
        journal_default_acc = self.cr.fetchone()
        
        if move_lines:
            self.cr.execute("SELECT COALESCE(SUM(debit),0.0)\
                             FROM  account_move_line l, account_move m \
                             WHERE " + self.query + " " + self.state_query + " AND l.move_id=m.id and l.id NOT IN %s and l.account_id= %s \
                             and statement_id is null", (tuple(move_lines), journal_default_acc,))


        sum_debit = self.cr.fetchone()[0] or 0.0

        return sum_debit


############################## CREDIT ###########

    def _sum_credit(self, period_id=False, journal_id=False):
        if not journal_id:
            journal_id = self.journal_ids
        else:
            journal_id = [journal_id]

        move_state = ['draft', 'posted', 'completed']
        if self.target_move == 'posted':
            move_state = ['posted', '']

        bank_statement = []

        self.cr.execute('select bs.id from account_bank_statement bs')
        account_bank_statement_obj = self.cr.fetchone()

        bank_statement.append(account_bank_statement_obj[0])
       

        account_bank_statement_object = self.pool.get('account.bank.statement').browse(self.cr, self.uid, bank_statement)[0]
        move_lines = [] 
        for line in account_bank_statement_object.move_line_ids:
            move_lines.append(line.id)
        self.cr.execute('select j.default_debit_account_id from account_bank_statement bs, account_journal j where bs.journal_id = j.id')
        journal_default_acc = self.cr.fetchone()
        
        if move_lines:
            self.cr.execute("SELECT COALESCE(SUM(credit),0.0)\
                             FROM  account_move_line l, account_move m \
                             WHERE " + self.query + " " + self.state_query + " AND l.move_id=m.id and l.id NOT IN %s and l.account_id= %s \
                             and statement_id is null", (tuple(move_lines), journal_default_acc,))


        sum_credit = self.cr.fetchone()[0] or 0.0
        return sum_credit


############################## BALANCE ###########

    def _balance(self, period_id=False, journal_id=False):
        if not journal_id:
            journal_id = self.journal_ids
        else:
            journal_id = [journal_id]

        move_state = ['draft', 'posted', 'completed']
        if self.target_move == 'posted':
            move_state = ['posted', '']

        bank_statement = []

        self.cr.execute('select bs.id from account_bank_statement bs')
        account_bank_statement_obj = self.cr.fetchone()

        bank_statement.append(account_bank_statement_obj[0])
       

        account_bank_statement_object = self.pool.get('account.bank.statement').browse(self.cr, self.uid, bank_statement)[0]
        move_lines = [] 
        for line in account_bank_statement_object.move_line_ids:
            move_lines.append(line.id)
        self.cr.execute('select j.default_debit_account_id from account_bank_statement bs, account_journal j where bs.journal_id = j.id')
        journal_default_acc = self.cr.fetchone()
        
        if move_lines:
            self.cr.execute("SELECT (sum(debit) - sum(credit)) as balance\
                             FROM  account_move_line l, account_move m \
                             WHERE " + self.query + " " + self.state_query + " AND l.move_id=m.id and l.id NOT IN %s and l.account_id= %s \
                             and statement_id is null", (tuple(move_lines), journal_default_acc,))

       
        balance = self.cr.fetchone()[0] or 0.0

        return balance
 

   
    ######### Print Move Lines ###########

    def lines(self, period_id, ids, journal_id=False):
        
        if not journal_id:
            journal_id = self.journal_ids
        else:
            journal_id = [journal_id]
        
        

        move_state = ['draft', 'posted', 'completed']
        if self.target_move == 'posted':
            move_state = ['posted', '']

        account_bank_statement_obj = self.pool.get('account.bank.statement').browse(self.cr, self.uid, ids)
        
        move_lines = [] 
        for line in account_bank_statement_obj.move_line_ids:
  
            move_lines.append(line.id)
        
        if move_lines:
            self.cr.execute("SELECT l.id, COALESCE(debit,0.0)as debit, COALESCE(credit,0.0) as credit, l.name as label ,l.ref as ref, l.date as date,\
                             l.move_id as move_id, m.name as move FROM  account_move_line l, account_move m \
                             WHERE " + self.query + " " + self.state_query + " AND l.move_id=m.id and l.id NOT IN %s and l.account_id= %s \
                             and statement_id is null ORDER BY l.date", (tuple(move_lines), account_bank_statement_obj.journal_id.default_debit_account_id.id,))
            res = self.cr.dictfetchall() or {} 

        else:
            self.cr.execute("SELECT l.id, COALESCE(debit,0.0)as debit, COALESCE(credit,0.0) as credit, l.name as label ,l.ref as ref, l.date as date,\
                             l.move_id as move_id, m.name as move FROM  account_move_line l, account_move m \
                             WHERE " + self.query + " " + self.state_query + " AND l.move_id=m.id  and l.account_id= %s \
                             and statement_id is null  ORDER BY l.date", (account_bank_statement_obj.journal_id.default_debit_account_id.id,))
            res = self.cr.dictfetchall() or {} 
       
  
   ####### move line balance #######
        
        account_sum = 0.0
     
        for l in res:
          
            account_balance = l['debit'] or 0.0 - l['credit'] or 0.0
          
            l['progress'] = account_balance 
            
        
        return res
#####################

    def _set_get_account_currency_code(self, account_id):
        self.cr.execute("SELECT c.symbol AS code "\
                "FROM res_currency c,account_account AS ac "\
                "WHERE ac.id = %s AND ac.currency_id = c.id" % (account_id))
        result = self.cr.fetchone()
        if result:
            self.account_currency = result[0]
        else:
            self.account_currency = False

    def _get_fiscalyear(self, data):
        if data['model'] == 'account.journal.period':
            return self.pool.get('account.journal.period').browse(self.cr, self.uid, data['id']).fiscalyear_id.name
        return super(account_statement, self)._get_fiscalyear(data)



    def _display_currency(self, data):
        if data['model'] == 'account.journal.period':
            return True
        return data['form']['amount_currency']


    def _display_closing_balance(self, data):  ######## R ########
        if data['model'] == 'account.bank.statement':
            return True
        return data['form']['close_balance']


    def _get_sortby(self, data):
        if self.sort_selection == 'date':
            return 'Date'
        elif self.sort_selection == 'ref':
            return 'Reference Number'
        return 'Date'
    def _get_credit(self):
        return self.credit

    def _get_debit(self):
        return self.debit

report_sxw.report_sxw('report.account.reconcile.statement', 'account.bank.statement', 'addons/account_arabic_reports/report/account_reconcile_statement.rml', parser=account_statement, header='custom landscape')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

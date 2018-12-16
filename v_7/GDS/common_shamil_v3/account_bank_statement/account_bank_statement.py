# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2013-2014 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import re
import time
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import date

#----------------------------------------------------------
#  Bank Statement (Inherit)
#----------------------------------------------------------
class account_bank_statement(osv.Model):

    _inherit = "account.bank.statement"

    _order = "date desc, id desc"

    def copy(self, cr, uid, ids, default={}, context=None):
        raise orm.except_orm(_('Warning!'), _('Bank Statement & Cash Register are not duplicatable. '))

    def _compute_balance_end_real(self, cr, uid, journal_id, context=None):
        """
        Calclate the last balance to bank statment for this journal_id

        @parm journal_id: journal id of new bank statement
        @return: dictionary {end_balance: end_balance or 0.0} 
        """
        res = False
        if context is None: context = {}
        if not context.get('date'):
            return super(account_bank_statement, self)._compute_balance_end_real(cr, uid, journal_id, context=context)
        if journal_id:
            cr.execute('SELECT balance_end_real \
                    FROM account_bank_statement \
                    WHERE journal_id = %s AND state = %s AND date < %s\
                    ORDER BY date DESC,id DESC LIMIT 1', (journal_id, 'confirm', context.get('statement_date')))
            res = cr.fetchone()
        return res and res[0] or 0.0

    def _end_balance(self, cr, uid, ids, name, attr, context=None):
        """
        Computing end balance as balance_start + debit of move_line_ids - credit of move_line_ids
        @param char name: functional field name,
        @param list attr: additional arguments,
        @return: dictionary {record_id: end_balance_value}
        """

        res = {}.fromkeys(ids, 0)
        for statement in self.browse(cr, uid, ids, context=context):
            if statement.journal_id.type == 'cash':
                res[statement.id] += statement.balance_start + sum([line.amount for line in statement.line_ids])
            else:
                statement_equation = statement.company_id.statement_equation
                if statement_equation and re.match(r'^[\.\+\-a-z_\*]*$', statement_equation):
                    res[statement.id] = self.calc_result(cr, uid, [statement.id], self._name, statement_equation, context=context)
                else:
                    raise orm.except_orm(_('Error !'), _('You have unsupported characters in your equation! available character a-z,_,+,- and . '))
        return res

    def _calc_balance(self, cr, uid, ids, name, attr, context=None):
        """
        Computing Last & Current Journal Balances
        :param char name: functional field name,
        :param list attr: additional arguments,
        :return: dictionary {record_id: {journal_balance:value,opening_balance:value}}
        """
        res = {}.fromkeys(ids, 0)
        for statement in self.browse(cr, uid, ids, context=context):
            context.update({'statement_date':statement.date})
            res[statement.id] = {
                    'balance_start':  statement.journal_id.type == 'cash' and sum([l.subtotal_opening for l in statement.details_ids]) or \
                    self._compute_balance_end_real( cr, uid, statement.journal_id.id, context=context),
                    'journal_balance': self._start_balance(cr, uid, statement.journal_id.id, statement.date, context=context),
                    'opening_balance': self._default_opening_balance(cr, uid, statement.journal_id.id, statement.date, context=context), }
        return res

    def calc_result(self, cr, uid, ids, model, statement_equation, context=None):
        """
        Iteration function calculate the result of received formula by getting the value of fields used in formula from received model
        @param char model: model which will read statement_equation fields from it
        @param char statement_equation: formula use to compute
        @return: float calculated result
        """
        fields = filter(lambda x: len(x) > 0, re.findall(r'([a-z_]*)', statement_equation))
        eq_vals = self.pool.get(model).read(cr, uid, ids, fields , context=context)
        res = 0
        for equation in filter(lambda x: len(x) > 0, re.findall(r'(-?\(?[a-z_\.]*\)?)', statement_equation)):
            sign = equation.startswith('-') and -1.0 or 1.0
            equation = equation.strip('-')
            f = equation.split('.')
            field_data = self.pool.get(model)._columns.get(f[0])
            if field_data and field_data._type in ('float', 'integer'):
                res += sum([v.get(equation, 0) * sign for v in eq_vals])
            elif field_data and field_data._type in ('one2many', 'many2many'):
                ids_list = []
                for v in eq_vals:
                    ids_list += v.get(f[0], [])
                res += self.calc_result(cr, uid, ids_list, field_data._obj, f[1], context=context) * sign
            else:
                raise orm.except_orm(_('Configuration Error!'),
                                     _('The field (%s) is not supported, maybe it\'s not exist or not one of these types (float, integer, one2many, many2many).') % (f[0],))
        return res

    def button_cancel(self, cr, uid, ids, context=None):
        """
        Call by 'Cancel' button, prevent reopening the statement if there is
        another bank statement used the current statement balance as opening balance
        If not change the statement state to draft

        @return: super write function to set state to draft
        """
        obj_account_move=self.pool.get('account.move')
        obj_account_move_line=self.pool.get('account.move.line')
        move_id=[]
        line_id=[]

        for st in self.browse(cr, uid, ids, context=context):
            journal=False
            date=st.date
            period=False
            cr.execute("select move_id from account_move_line where statement_id=1")
            line_id=obj_account_move_line.search(cr, uid, [('statement_id', '=', st.id)], limit=1, context=context)
            if line_id:
               for line in obj_account_move_line.browse(cr,uid,line_id,context=context):
                   move_id.append(line.move_id.id)
            if self.search(cr, uid, [('journal_id','=',st.journal_id.id),('date','>',st.date)], context=context):
                raise orm.except_orm(_('Error !'), _('You can\'t cancel this operation, another one depend on this already exist.'))
            if st.journal_id.type=='cash':
               obj_account_move.revert_move(cr, uid, move_id, journal, period, date, reconcile=True, context=context)
        return self.write(cr, uid, ids, {'state':'draft'}, context=context)

    def _start_balance(self, cr, uid, journal_id, statement_date, context=None):
        """
        Computing journal's account balance at statement date
        @param int journal_id: statement journal,
        @param date statement_date: statement date,
        @return: float which is the account balance in selected date
        """

        period_pool = self.pool.get('account.period')
        company_currency_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_id.id
        journal = journal_id and self.pool.get('account.journal').browse(cr, uid, journal_id, context=context) or False
        period_id = period_pool.search(cr, uid, [], order='date_start', limit=1, context=context)
        date = period_id and period_pool.read(cr, uid, period_id[0], ['date_start'], context=context)['date_start']
        account_id = journal and (journal.default_debit_account_id and journal.default_debit_account_id.id) or False
        currency_id = journal and journal.currency and journal.currency.id or False
        company_id = journal and journal.company_id and journal.company_id.id or False

        ctx = {'date_from': date, 'date_to': statement_date , 'state': 'posted', 'company_id':company_id}
        balance = account_id and self.pool.get('account.account').read(cr, uid, account_id, ['balance'], context=ctx)['balance'] or 0.0
        #recalculate journal balance

        if currency_id:
            if currency_id != company_currency_id:
               cr.execute('SELECT COALESCE(sum(l.amount_currency),0) as amount\
                        FROM account_move_line l\
                        LEFT JOIN account_move m on (m.id=l.move_id)\
                        WHERE l.currency_id = %s and m.state=%s and l.date <= %s and l.account_id=%s\
                        ', (currency_id,'posted',statement_date, account_id,))
               res = cr.fetchone()[0] or 0.0
        else :
               res = self.pool.get('res.currency').compute(cr, uid, company_currency_id, currency_id, balance, context=context)

        return round(res, 2) or 0.0

    def _default_opening_balance(self, cr, uid, journal_id, date, context=None):
        """
        Computing The opening balance of statement, which is the journal 
        balance of the last statement.

        @param int journal_id: statement journal,
        @return: float which is start balance of prev statement
        """
        stmt_ids = self.search(cr, uid, [('journal_id', '=', journal_id), ('date', '<', date)], order='date desc', limit=1, context=context)
        return stmt_ids and self.browse(cr, uid, stmt_ids[0], context=context).journal_balance or 0.0

    def onchange_journal_id(self, cr, uid, statement_id, journal_id, date, context=None):
        """
        Changing statement journal gonna change move_line_ids, non_bank_moves,
        journal_balance, balance start, starting details and opening_balance.

        @param int statement_id: statement which its journal has been changed,
        @param int journal_id: new journal,
        @return: dictionary conatins the new values of:
                move_line_ids: reconsiled move lines
                non_bank_moves: unreconciled move lines
                journal_balance: account balance at statement date
                opening_balance: end balance of prev reconsilation
        """
        box_line_pool = self.pool.get('account.cashbox.line')
        journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
        r = dict([(v.pieces, 0)  for v in journal.cashbox_line_ids])

        ctx = context and context.copy() or {}
        ctx.update({'journal_id':journal_id, 'date':date})
        val = super(account_bank_statement, self).onchange_journal_id(cr, uid, statement_id, journal_id, context=ctx).get('value', {})

        results = self.search(cr, uid, [('journal_id', '=', journal_id), ('state', '=', 'confirm'), ('date', '<', date)],
                              order="date DESC,id DESC", limit=1, context=context)
        line_ids = box_line_pool.search(cr, uid, [('bank_statement_id', '=', statement_id)], context=context)
        box_line_pool.unlink(cr, uid, line_ids, context=context)
        if results:
            cash_st = self.browse(cr, uid, results, context=context)[0]
            r.update(dict([(cash_line.pieces, cash_line.number_closing) for cash_line in cash_st.closing_details_ids]))
        details = [{'pieces':k, 'number_opening':r[k], 'subtotal_opening':k * r[k]} for k in sorted(r.iterkeys())]
        val.update({'move_line_ids': [],
                    'non_bank_moves': [],
                    'account_id': journal_id and self.pool.get('account.journal').browse(cr, uid, journal_id, context=ctx).default_debit_account_id.id,
                    'opening_details_ids': details,
                    'details_ids': details
                })

#        if journal_id:
#           opening_balance = self._default_opening_balance(cr, uid, journal_id, date, context=context)
#           journal_b = self._start_balance(cr, uid, journal_id, date, context=ctx)
#           val.update({
#                   'journal_balance': journal_b,
#                   'opening_balance':opening_balance,
#               })
        
        #return {'domain': account_domain,}

        return {'value': val}

    def onchange_date(self, cr, uid, statement_id, date, journal_id, company_id, context=None):
        """
        Changing statement date gonna change move_line_ids, non_bank_moves 
        and journal_balance.

        @param int/long statement_id: statement which its journal has been changed,
        @param date date: new statement date,
        @return: dictionary contain the new values of:
                move_line_ids: [] move lines
                non_bank_moves: unreconciled [] lines
                journal_balance: account balance at new date
        """
        ctx = context  and context.copy() or {}
        ctx.update({'date':date})
        res = super(account_bank_statement, self).onchange_date(cr, uid, statement_id, date, company_id, context=ctx)
        res['value'].update(self.onchange_journal_id(cr, uid, statement_id, journal_id, date, context=context).get('value', {}))
        #journal_b = self._start_balance(cr, uid, journal_id, date, context=ctx)
        res['value'].update({
                #'journal_balance': journal_b,
                'move_line_ids': [],
                'non_bank_moves': []
            })
        return res

    _columns = {
        'non_bank_moves': fields.many2many('account.move.line', 'account_bank_statement_line_move_r',
                                           'statement_id', 'non_bank_moves', 'Non-Bank Moves', readonly=True),
        'journal_balance': fields.function(_calc_balance, store=True, string='Current Journal Balance', readonly=True, 
                                            digits_compute=dp.get_precision('Account'), multi="calc"),
        'opening_balance': fields.function(_calc_balance, store=True, string='Last Journal Balance', readonly=True, 
                                            digits_compute=dp.get_precision('Account'), multi="calc"),
        'balance_start': fields.function(_calc_balance, store=True, string='Starting Balance', readonly=True, 
                                            digits_compute=dp.get_precision('Account'), multi="calc"),
        'note': fields.text('Note'),
        'balance_end': fields.function(_end_balance, store=True, string='Balance', digits_compute=dp.get_precision('Account'),
                                       help="Closing balance based on Starting Balance and Cash Transactions"),
    }

    _defaults = {
        'date': lambda * a: time.strftime('%Y-%m-%d'),
    }

    _sql_constraints = [('journal_date_uniq', 'unique(journal_id,date)', _("You can't open more than one statement in the same date!")),
                        ('date_check', 'check(date<=CURRENT_DATE)', _("You can't open statement in future date!"))
    ]

    def _check_statement_date(self, cr, uid, ids, context=None):
        """
        Constrain method to check if there exist other bank statement with date 
        greater than statement date  

        @return: boolean True or False
        """
        for statement in self.browse(cr, uid, ids, context=context):
            if self.search(cr, uid, [('state', '=', 'confirm'), ('journal_id', '=', statement.journal_id.id), ('date', '>', statement.date)], context=context):
                return False
        return True

    def _check_date(self, cr, uid, ids, context=None):
        for l in self.browse(cr, uid, ids, context=context):
            if l.journal_id.allow_date:
                if not time.strptime(l.date[:10],'%Y-%m-%d') >= time.strptime(l.period_id.date_start, '%Y-%m-%d') or not time.strptime(l.date[:10], '%Y-%m-%d') <= time.strptime(l.period_id.date_stop, '%Y-%m-%d'):
                    return False
        return True
    _constraints = [
        (_check_statement_date, 'There is a closed statement(s) with date after the date you select! \nkindly change your statement date or reopen closed statement(s) for more accurate calculations!', ['journal_id', 'date']),
        (_check_date, 'The date of your Statement is not in the defined period! You should change the date or remove this constraint from the journal.', ['date']),
    ]

    def _pre_date(self, cr, uid, statement, context=None):
        """
        Get very starting date of bank reconsilation to system starting date, 
        this function use in reconsilation report.

        @param obj statement: statement object which want to getn it pre_date
        @return: date or False
        """
        statement_date = time.strftime('%m/%d/%Y', time.strptime(statement.date, '%Y-%m-%d'))
        period_pool = self.pool.get('account.period')
        stmt_ids = self.search(cr, uid, [('journal_id', '=', statement.journal_id.id), ('date', '<', statement_date)], order='date desc', limit=1, context=context)
        if stmt_ids:
            return self.browse(cr, uid, stmt_ids[0], context=context).date
        period_id = period_pool.search(cr, uid, [], order='date_start', limit=1, context=context)
        return  period_id and period_pool.read(cr, uid, period_id[0], ['date_start'], context=context)['date_start'] or False

    def write(self, cr, uid, ids, vals, context=None):
        """
        Get all unreconsiled line and add them to statement non_bank_moves field
        and recalculate journal's account balance at statement date 

        @param vals: dictionary of all values use to create statement.
        @return: update statement record
        """
        if context is None:
            context = {}
        acc_mov_obj = self.pool.get('account.move.line')
        for statement in self.browse(cr, uid, ids, context=context):
            st_journal = vals.get('journal_id', False) and self.pool.get('account.journal').browse(cr, uid, vals['journal_id'], context=context) or statement.journal_id
            if st_journal.type == 'bank' and  statement.state == 'draft':
                l_ids = acc_mov_obj.search(cr, uid, [('date', '<=', statement.date), ('state', '=', 'valid'),
                                                     ('account_id', '=', st_journal.default_debit_account_id.id),
                                                     ('move_id.state', '=', 'posted')], context=context)
                if len(l_ids) > 0:
                    cr.execute("SELECT  l.id  FROM  account_move_line l left join account_bank_statement s on (s.id = l.statement_id) \
                                WHERE  l.id in %s and ((statement_id is not NULL and statement_id <> %s and s.date > %s) or statement_id is NULL)",
                                (tuple(l_ids), statement.id, statement.date))
                vals.update({'non_bank_moves': [(6, 0, [r[0] for r in cr.fetchall()])]})
#            start_balance = self._start_balance(cr, uid, st_journal.id, statement.date, context=context)
#            vals['journal_balance'] = start_balance
        return super(account_bank_statement, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        """
        Set statement number when create it
        :param dictionary vals: dictionary of all values use to create statement
        """
        vals.update({'name': self.pool.get('ir.sequence').get(cr, uid, 'account.bank.statement')})
        return super(account_bank_statement, self).create(cr, uid, vals, context=context)

#----------------------------------------------------------
#  Bank Statement Line(Inherit)
#----------------------------------------------------------
class account_bank_statement_line(osv.Model):

    _inherit = "account.bank.statement.line"

    def _calculate_balance( self , cr, uid, ids, name, arg=None, context={}):
        """
        Calculate the balance in account bank statement line.
        @param field_name: Name of the field
        @param arg: User defined argument
        @return:  Dictionary of values
        """
        res = {}
        for line in self.browse(cr, uid, ids):
            if line.statement_id.journal_id.type == 'cash':
                account_obj = self.pool.get('account.account')
                if line.partner_id:
                    context.update({'partner_ids':[line.partner_id.id]})

                res[line.id] = {'balance': account_obj.read(cr, uid, \
                                            [line.account_id.id], ['balance'], context)[0]['balance']}
        return res

    _columns = {
        'account_id': fields.many2one('account.account', 'Account', ),
        'balance': fields.function(_calculate_balance, method=True, type="float", string='Balance',multi='sums',
                   store = {
                    'account.bank.statement.line': (lambda self, cr, uid, ids, c={}: ids, ['account_id','partner_id'], 10),
                          }),
    }

    def _check_amount_balance(self, cr, uid, ids, context=None):
        """ 
        Constrain function to check the amount should be greater/less than balance
        @return Boolean True or False
        """
        for line in self.browse(cr, uid, ids, context=context):
            if line.statement_id.journal_id.type == 'cash':
                if line.account_id and line.account_id.check_type == 'credit' and line.amount<0 and line.amount<line.balance:
                    raise orm.except_orm(_('Warning!'), _('You can not withdraw more than due amount.'))
                if line.account_id and line.account_id.check_type == 'debit' and line.amount>0 and line.amount>line.balance:
                    raise orm.except_orm(_('Warning!'), _('You can not deposit more than treasury due amount.'))
        return True

    def _check_account_id(self, cr, uid, ids, context=None):
        """ 
        Constrain function to check the amount should be greater/less than balance
        @return Boolean True or False
        """
        for line in self.browse(cr, uid, ids, context=context):
            journal = line.statement_id.journal_id
            if journal.account_control_ids:
                account_ids = [account.id for account in journal.account_control_ids]
                if line.account_id.id not in  account_ids:
                    return False
        return True

    _constraints = [
        (_check_amount_balance, 
            'There is error in amount',
            ['Amount']),
        (_check_account_id, 
            'This account is not in journal Allowed Accounts.',
            ['Account'])]

    def onchange_account_id(self, cr, uid, ids,journal_id, context={}):
        """ 
        Onchange function tht return domain for the field account_id
        @return list contain domain for the field account_id
        """
        if isinstance(journal_id, list):
            journal_id = journal_id[0]
        journal = self.pool.get('account.journal').browse(cr,uid,journal_id)
        account_domain={'account_id':[('type', 'in', ('other','payable','receivable'))]}
        if journal.account_control_ids:
            account_ids = [account.id for account in journal.account_control_ids]
            account_domain['account_id'].append(('id','in',account_ids))
        return {'domain': account_domain,}

#----------------------------------------------------------
#  Cashbox Line (Inherit)
#----------------------------------------------------------
class account_cashbox_line(osv.Model):

    _inherit = 'account.cashbox.line'

    _sql_constraints = [('number_positive', 'CHECK (number_opening>=0.0 and number_closing>=0.0 and pieces>=0.0)',
                        _("Number of units for box opening/closing details and the unit of currency should be positive number!")),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

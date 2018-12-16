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

#----------------------------------------------------------
#  Bank Statement (Inherit)
#----------------------------------------------------------
class account_bank_statement(osv.Model):

    _inherit = "account.bank.statement"

    _order = "date desc, id desc"


    def _get_sum_entry_encoding(self, cr, uid, ids, name, arg, context=None):
        """
        Method to calculate encoding total of statements
        
        @param name: Names of fields.
        @param arg: User defined arguments
        @return: Dictionary of values.
        """
        res = {}
        for statement in self.browse(cr, uid, ids, context=context):
            res[statement.id] = sum((line.amount for line in statement.line_ids if line.line_type == "in_line"), 0.0) + sum((line.amount for line in statement.line_ids if line.line_type == "out_line"), 0.0)
        return res


    def copy(self, cr, uid, ids, default={}, context=None):
        """
        Inherit copy method to prevent coping any bank statements or cash box
        """
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
                    ORDER BY date DESC,id DESC LIMIT 1', (journal_id, 'confirm', context.get('date')))
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
                res[statement.id] = statement.balance_start
                for line in statement.line_ids:
                    line_amount = 0.0
                    if line.line_type == "in_line":
                        line_amount = line.amount 
                    elif line.line_type == "out_line":
                        line_amount = -(line.amount)
                    res[statement.id] += line_amount
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
            balance_start = 0.0
            if statement.journal_id.type == 'cash' :
                balance_start = sum([l.subtotal_opening for l in statement.details_ids])
            else:
                balance_start = self._compute_balance_end_real( cr, uid, statement.journal_id.id, context=context)
            res[statement.id] = {
                    'balance_start':  balance_start,
                    'journal_balance': self._start_balance(cr, uid,statement.id, statement.journal_id.id, statement.date, context=context),
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

        if fields[0] == 'amount':
            account_bank_statement_line = self.pool.get("account.bank.statement.line")
            for amount in eq_vals:
                value = amount["amount"]
                id = amount["id"]
                line = account_bank_statement_line.browse(cr,uid,id,context=context)
                if line.line_type and line.line_type == 'out_line':
                    res -= value
                else:
                    res += value
            return res

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

    def _start_balance(self, cr, uid, ids,journal_id, statement_date, context=None):
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

    def _get_details(self, cr, uid, journal, date, context=None):
        details = dict([(v.pieces, 0)  for v in journal.cashbox_line_ids])
        results = journal.with_last_closing_balance and self.search(cr, uid, [('journal_id', '=', journal.id), ('state', '=', 'confirm'), ('date', '<', date)],
                              order="date DESC,id DESC", limit=1, context=context)
        if results:
            cash_st = self.browse(cr, uid, results, context=context)[0]
            details.update(dict([(cash_line.pieces, cash_line.number_closing) for cash_line in cash_st.closing_details_ids]))
        return details
    
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
        journal = journal_id and self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)

        ctx = context and context.copy() or {}
        ctx.update({'journal_id':journal_id, 'date':date})
        val = super(account_bank_statement, self).onchange_journal_id(cr, uid, statement_id, journal_id, context=ctx).get('value', {})

        r = journal and self._get_details(cr, uid, journal, date, context=context) or {}
        details = [{'pieces':k, 'number_opening':r[k], 'subtotal_opening':k * r[k]} for k in sorted(r.iterkeys())]
        val.update({'move_line_ids': [],
                    'non_bank_moves': [],
                    'account_id': journal and  journal.default_debit_account_id.id or False,
                    'opening_details_ids': details,
                    'details_ids': details,
                    'with_last_closing_balance': journal and journal.with_last_closing_balance
                })
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

    def _get_statement(self, cr, uid, ids, context=None):
        """
        Method that maps record ids of a trigger model to ids of the corresponding records 
        in the source model (whose field values need to be recomputed).
        
        @param: list of statement line ids
        @return:  list of statement ids
        """
        result = {}
        for line in self.pool.get('account.bank.statement.line').browse(cr, uid, ids, context=context):
            result[line.statement_id.id] = True
        return result.keys()

    _columns = {
        'with_last_closing_balance': fields.boolean('Opening With Last Closing Balance'),
        'non_bank_moves': fields.many2many('account.move.line', 'account_bank_statement_line_move_r',
                                           'statement_id', 'non_bank_moves', 'Non-Bank Moves', readonly=True),
        'journal_balance': fields.function(_calc_balance, store=True, string='Current Journal Balance', readonly=True, 
                                            digits_compute=dp.get_precision('Account'), multi="calc"),
        'opening_balance': fields.function(_calc_balance, store=True, string='Last Journal Balance', readonly=True, 
                                            digits_compute=dp.get_precision('Account'), multi="calc"),
        'balance_start': fields.function(_calc_balance, store=True, string='Starting Balance', readonly=True, 
                                            digits_compute=dp.get_precision('Account'), multi="calc"),
        'note': fields.text('Note'),
        'balance_end': fields.function(_end_balance,
            store={
                'account.bank.statement': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'account.bank.statement.line': (_get_statement, ['amount'], 10),
            },
            string="Computed Balance", help='Balance as calculated based on Starting Balance and transaction lines'),

        'total_entry_encoding': fields.function(_get_sum_entry_encoding, string="Total Transactions",
            store={
                'account.bank.statement': (lambda self, cr, uid, ids, context=None: ids, ['line_ids', 'move_line_ids'], 10),
                'account.bank.statement.line': (_get_statement, ['amount'], 10),
            }),

    }

    _defaults = {
        'date': lambda * a: time.strftime('%Y-%m-%d'),
    }

    _sql_constraints = [('journal_date_uniq', 'unique(journal_id,date)', _("You can't open more than one statement in the same date!")),
                        ('date_check', 'check(date<=CURRENT_DATE)', _("You can't open statement in future date!"))
    ]

    def _check_statement_date(self, cr, uid, ids, context=None):
        """
        Constraint method to check if there exist other bank statement with date 
        greater than statement date  

        @return: boolean True or False
        """
        for statement in self.browse(cr, uid, ids, context=context):
            if self.search(cr, uid, [('state', '=', 'confirm'), ('journal_id', '=', statement.journal_id.id), ('date', '>', statement.date)], context=context):
                return False
        return True

    def _check_date(self, cr, uid, ids, context=None):
        """
        Constraint method to check whether the statement date is within the statement period

        @return: boolean True or False
        """
        for l in self.browse(cr, uid, ids, context=context):
            if l.journal_id.allow_date:
                if not time.strptime(l.date[:10],'%Y-%m-%d') >= time.strptime(l.period_id.date_start, '%Y-%m-%d') or not time.strptime(l.date[:10], '%Y-%m-%d') <= time.strptime(l.period_id.date_stop, '%Y-%m-%d'):
                    return False
        return True
    _constraints = [
        (_check_statement_date, 'There is a closed statement(s) with date after the date you select! \nkindly change your statement date or reopen closed statement(s) for more accurate calculations!', ['journal_id', 'date']),
        (_check_date, 'The date of your statement is not in the defined period! You should change the date or remove this constraint from the journal.', ['date']),
    ]

    def _pre_date(self, cr, uid, statement, context=None):
        """
        Get very starting date of bank reconsilation to system starting date, 
        this function use in reconsilation report.

        @param obj statement: statement object which want to getn it pre_date
        @return: date or False
        """
        period_pool = self.pool.get('account.period')
        stmt_ids = self.search(cr, uid, [('journal_id', '=', statement.journal_id.id), ('date', '<', statement.date)], order='date desc', limit=1, context=context)
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
            if vals.get('journal_id', False) and st_journal.with_last_closing_balance == True:
                r = self._get_details(cr, uid, st_journal, vals.get('date', statement.date), context=context)
                details = [(5,l.id) for l in statement.opening_details_ids]+[(0, False, {'pieces':k, 'number_opening':r[k], 'subtotal_opening':k * r[k]}) for k in sorted(r.iterkeys())]
                vals.update({
                        'opening_details_ids': details,
                        'details_ids': details,
                    })
            if st_journal.type == 'bank' and  statement.state == 'draft':
                l_ids = acc_mov_obj.search(cr, uid, [('date', '<=', statement.date), ('state', '=', 'valid'),
                                                     ('account_id', '=', st_journal.default_debit_account_id.id),
                                                     ('move_id.state', '=', 'posted')], context=context)
                if len(l_ids) > 0:
                    cr.execute("SELECT  l.id  FROM  account_move_line l left join account_bank_statement s on (s.id = l.statement_id) \
                                WHERE  l.id in %s and ((statement_id is not NULL and statement_id <> %s and s.date > %s) or statement_id is NULL)",
                                (tuple(l_ids), statement.id, statement.date))
                vals.update({'non_bank_moves': [(6, 0, [r[0] for r in cr.fetchall()])]})
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
    """
    Inherit statement line model to make account_id field not required
    """
    _inherit = "account.bank.statement.line"

    _columns = {
        'account_id': fields.many2one('account.account', 'Account'),
        'line_type': fields.selection([('out_line', 'Out'), ('in_line', 'In')], string='Line Type', required=True),
    }

    _defaults = {
        'line_type': 'in_line'
    }

    def _check_negative(self, cr, uid, ids, context=None):
        """ 
        Check the value of amount,
        if greater than zero or not.

        @return: Boolean of True or False
        """
        if self.search(cr, uid, [('id','in',ids),('amount','<=',0)], context):
            return False
        return True

    _constraints = [
        (_check_negative, _('The Amount Must Be Positive Value!'), ['amount'])
    ]

#----------------------------------------------------------
#  Cashbox Line (Inherit)
#----------------------------------------------------------
class account_cashbox_line(osv.Model):
    """
    Inherit cashbox line model to add constraint that prevents entering negative value in number_opening, number_closing & pieces fields
    """
    _inherit = 'account.cashbox.line'

    _sql_constraints = [('number_positive', 'CHECK (number_opening>=0.0 and number_closing>=0.0 and pieces>=0.0)',
                        _("Number of units for box opening/closing details and the unit of currency should be positive number!")),
    ]
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


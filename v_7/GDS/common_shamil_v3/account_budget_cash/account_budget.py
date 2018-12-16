# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp import netsvc
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import operator
from openerp.addons.account_budget_custom.account_budget import account_budget_lines as abl

fnct_residual_search = abl.fnct_residual_search
#---------------------------------------------------
# Account Budget
# --------------------------------------------------
class account_budget(osv.Model):

    _inherit = "account.budget"

    _columns = {

        'account_cash_budget_line': fields.one2many('account.budget.lines', 'account_budget_id', 'Budget Lines',
                                               readonly=True, states={'draft':[('readonly', False)]}),
    }

    def budget_done(self, cr, uid, ids, context={}):
        """
        This Method Transfer the residual_balance for each budget_line to the next periods budget_line
        Then close "done state" the budget & prevents any update on it.
        
        @return: boolean True
        """
        account_budget_lines = self.pool.get('account.budget.lines')
        period_pool = self.pool.get('account.period')
        budgets = self.browse(cr, uid, ids, context=context)
        for budget in budgets:
            next_period = period_pool.search(cr, uid,
                                            [('date_start', '>', budget.period_id.date_start),
                                             ('fiscalyear_id', '=', budget.period_id.fiscalyear_id.id)],
                                            context=context, limit=1)

            if next_period:
                to = {
                    'analytic_account' : budget.analytic_account_id.id,
                    'period_id' : next_period and next_period[0],
                    'company' : budget.analytic_account_id.company_id.id
                }
                for line in budget.account_budget_line:
                    to['account_id'] = line.general_account_id.id
                    if line.residual_balance > 0:
                        account_budget_lines.transfer(cr, uid, {'type':'close_transfer', 'budget_type':'plan', 'to':to,
                                                                'line_ids':[{'line_id':line, 'amount':line.residual_balance}]}, context=context)

                    if line.cash_residual_balance > 0:
                        account_budget_lines.transfer(cr, uid, {'type':'close_transfer', 'budget_type':'cash', 'to':to,
                                                                'line_ids':[{'line_id':line, 'amount':line.cash_residual_balance}]}, context=context)
                self.write(cr, uid, budget.id, {'state': 'done'}, context=context)
        return True

account_budget()

#---------------------------------------------------
# Account Budget Lines
# --------------------------------------------------
class account_budget_lines(osv.Model):
    """
    Account Budget Lines / Period's Budget Details
    One line of detail of the Period Budget representing planned amount 
    for special account in period Budget which it belong to
    """
    _inherit = "account.budget.lines"


    def transfer(self, cr, uid, vals={}, context=None):
        """
        This Method execute any increase or transfer operation.
                                
        @param dictionary vals: all operation values (type, budget_type, line_ids, to, reference),
        @return: dictionary (budget_line_id, history_ids
        """

        budget_type = vals.get('budget_type', 'plan')
        budget_history_pool = self.pool.get('account.budget.operation.history')
        budget_line_id , history_ids = super(account_budget_lines, self).transfer(cr, uid, vals, context=context)
        budget_history_pool.write(cr, uid, history_ids, {'type': budget_type}, context=context)

        return budget_line_id , history_ids

    def _total_operation(self, cr, uid, ids, field_name, arg=None, context=None):
        """
        This Method use to compute the tranfer, increase amount from the operation object.
        
        @param char field_name: functional field name,
        @param list arg: additional arguments,
        @return: dictionary, amount of total operation and cash total operation for each line
        """
        result = {}
        for id in ids:
            result[id] = {'total_operation': 0.0, 'cash_total_operation': 0.0}
            cr.execute("SELECT type,sum(COALESCE(amount,0))  \
                        FROM   (SELECT CASE WHEN  budget_line_id_from=%s \
                                        THEN -amount \
                                        ELSE amount \
                                    END AS amount, \
                                    CASE WHEN  type='plan' \
                                        THEN 'total_operation' \
                                        ELSE 'cash_total_operation' \
                                    END AS type \
                                FROM    account_budget_operation_history h \
                                where budget_line_id_from=%s or budget_line_id_to=%s) \
                                as result \
                        Group by type" % (id, id, id))

            result[id].update(dict(cr.fetchall()))
        return result

    def _residual_balance(self, cr, uid, ids, field_name, arg=None, context=None):
        """
        This Method use to compute the actual_balance & the residual_balance for each budget_line.
                    
        @param char field_name: functional field name,
        @param list arg: additional arguments,
        @return: dictionary of residual balance for each budget line
        """
        cr.execute('SELECT id,planned_amount+total_operation-balance,cash_total_operation-balance FROM account_budget_lines WHERE id IN (%s)' % (','.join(map(str, ids)),))
        return dict([(l[0], {'residual_balance':l[1], 'cash_residual_balance':l[2]}) for l in cr.fetchall()])


    def fnct_cash_residual_search(self, cr, uid, obj, name, domain=None, context=None):
        if context is None:
            context = {}
        if not domain:
            return []
        field, operator, value = domain[0]
        cr.execute('SELECT id FROM account_budget_lines \
                    WHERE cash_total_operation-balance ' + operator + str(value))
        res = cr.fetchall()
        return [('id', 'in', [r[0] for r in res])]

    def _get_operation_line_ids(self, cr, uid, ids, context=None):
        lines = self.pool.get('account.budget.operation.history').read(cr, uid, ids,
                                    ['budget_line_id_from', 'budget_line_id_to'], context=context)
        return reduce(operator.add, [[l['budget_line_id_from'] and l['budget_line_id_from'][0], l['budget_line_id_to'] and l['budget_line_id_to'][0]] for l in lines])

    _columns = {

        'total_operation': fields.function(_total_operation, method=True, digits_compute=dp.get_precision('Account'), string='in/de crease Amount',
                                           store={'account.budget.operation.history':
                                                                   (_get_operation_line_ids, ['budget_line_id_from', 'budget_line_id_to', 'type'], 10),
                                                 }, multi='operation'),

        'cash_total_operation': fields.function(_total_operation, method=True, digits_compute=dp.get_precision('Account'), string='In/De-crease Cash Amount',
                                                store={'account.budget.operation.history':
                                                                    (_get_operation_line_ids, ['budget_line_id_from', 'budget_line_id_to', 'type'], 10),
                                                      }, multi='operation'),

        'residual_balance': fields.function(_residual_balance, fnct_search=fnct_residual_search, method=True,
                                                    multi='residual', digits_compute=dp.get_precision('Account'), string='Residual Balance'),

        'cash_residual_balance': fields.function(_residual_balance, fnct_search=fnct_cash_residual_search, method=True,
                                                    multi='residual', digits_compute=dp.get_precision('Account'),
                                                    string='Cash Residual Balance'),

    }

    _defaults = {
        'cash_total_operation': 0.0,
    }
    #FIXME: budget_check when close budget
    _sql_constraints = [('cash_residual_check', 'CHECK ((cash_total_operation-balance)>=0)', _("Cash budget can't go overdrow!")),
                        ('budget_check', 'CHECK ((planned_amount+total_operation)>=cash_total_operation)', _("Cash budget can't be more than planned budget!")),

    ]


class budget_operation_history(osv.Model):

    _inherit = "account.budget.operation.history"

    _columns = {

        'type': fields.selection([('plan', 'Plan Budget'), ('cash', 'Cash Budget')], 'Budget Type' , readonly=True),
    }

    _defaults = {
        'type': 'plan',
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

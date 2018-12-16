# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2013-2014 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm

#----------------------------------------------------------
#  Bank Statement (Inherit)
#----------------------------------------------------------

class account_bank_statement(osv.Model):

    def _end_balance(self, cursor, user, ids, name, attr, context=None):
	"""
	Method to calculate the balance end rather than calculating it from
	the equation in the field statement_equation in  company object.
	
        @param name: char the name of the functional field to be calculated,        
        @param attr: other arguments,
        @return: dictionary of the field value to be updated
	
	"""

        res_currency_obj = self.pool.get('res.currency')
        res_users_obj = self.pool.get('res.users')
        res = {}

        company_currency_id = res_users_obj.browse(cursor, user, user,
                context=context).company_id.currency_id.id

        statements = self.browse(cursor, user, ids, context=context)
        if statements[0].currency.base:
            return super(account_bank_statement, self)._end_balance( cursor, user, ids, name, attr, context=context)
        for statement in statements:
            res[statement.id] = statement.balance_start
            currency_id = statement.currency.id
            for line in statement.move_line_ids:
                context.update({'date':line.date})
                if line.debit > 0 and not line.currency_id:
                    if line.account_id.id == \
                            statement.journal_id.default_debit_account_id.id and not line.currency_id:
                        res[statement.id] += res_currency_obj.compute(cursor,
                                user, company_currency_id, currency_id,
                                line.debit, context=context)
                else:
                    if line.account_id.id == \
                            statement.journal_id.default_credit_account_id.id and not line.currency_id:
                        res[statement.id] -= res_currency_obj.compute(cursor,
                                user, company_currency_id, currency_id,
                                line.credit, context=context)
                #edit end balance
                if line.currency_id:
                   res[statement.id]+=line.amount_currency

            #if statement.state in ('draft', 'open'):
            if statement.line_ids:
               for line in statement.line_ids:
                  res[statement.id] += line.amount
        for r in res:
            res[r] = round(res[r], 2)
        return res
    



    _columns = {

        'balance_end': fields.function(_end_balance, method=True, store=True, string='Balance', help="Closing balance based on Starting Balance and Cash Transactions"),
    }

    _inherit = "account.bank.statement"

#----------------------------------------------------------
#  Company (Inherit)
#----------------------------------------------------------

class res_company(osv.Model):	
    """
    Inherit company object to make required=False for the configuration field statement_equation
    """

    _inherit = "res.company"
    
    _columns = {

        'statement_equation': fields.char('Statement Equation', help="", size=128, required=False),
        
    }

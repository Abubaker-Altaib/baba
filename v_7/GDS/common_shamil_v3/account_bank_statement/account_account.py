# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2013-2014 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

#----------------------------------------------------------
#  Company (Inherit)
#----------------------------------------------------------
class res_company(osv.Model):

    _inherit = "res.company"
    
    _columns = {
        'statement_equation': fields.char('Statement Equation', size=128, required=True),
        
        'statement_condition': fields.char('Statement Condition', size=64, required=True),
    }
    
    _defaults = {
        'statement_equation': 'journal_balance-non_bank_moves.debit+non_bank_moves.credit+line_ids.amount',
        'statement_condition': 'balance_end_real',
    }

#----------------------------------------------------------
#  Account Config (Inherit)
#----------------------------------------------------------
class account_config_settings(osv.osv_memory):

    _inherit = 'account.config.settings'

    _columns = {
        'statement_equation':fields.related('company_id', 'statement_equation', type='char', string='Statement Equation', required=True,
                                        help="You can use +/- operators to build your equation. \nThe available field for use: \n1.balance_start: The last bank balance \n2.opening_balance: The last journal balance \n3.journal_balance: The current journal balance\n4.balance_end_real: The current bank balance \n5.non_bank_moves.debit: Revenues didn't deposit \n6.non_bank_moves.credit: Expenses didn't withdrow \n7.line_ids.amount: Bank moves didn't appear in journal"),
        
        'statement_condition':fields.related('company_id', 'statement_condition', type='char', string='Statement Condition', required=True,
                                        help="The available field for use: \n1.balance_start: The last bank balance \n2.opening_balance: The last journal balance \n3.journal_balance: The current journal balance\n4.balance_end_real: The current bank balance"),
    }

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        """
        Update dict. of values to set statement_equation & 
        statement_condition depend on company_id
        @param company_id: user company_id
        @return: dict. of new values
        """
        # update related fields
        values = super(account_config_settings,self).onchange_company_id(cr, uid, ids, company_id, context=context).get('value',{})
        
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            values.update({
                'statement_equation': company.statement_equation,
                'statement_condition': company.statement_condition,
            })
           
        return {'value': values}

#----------------------------------------------------------
#  Account account (Inherit)
#----------------------------------------------------------
class account_account(osv.Model):

    _inherit = 'account.account'

    _columns = {
            'check_type': fields.selection([('debit', 'Debit'), ('credit', 'Credit')], 'Check Type'),
               }



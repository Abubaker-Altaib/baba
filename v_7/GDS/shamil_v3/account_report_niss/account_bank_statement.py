# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2016 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class account_bank_statement(osv.osv):
    _inherit = 'account.bank.statement'

    def create_move_from_st_line(self, cr, uid, st_line_id, company_currency_id, st_line_number, context=None):
        """Overwrite this method to return False without create acount_move.

           :param int/long st_line_id: ID of the account.bank.statement.line to create the move from.
           :param int/long company_currency_id: ID of the res.currency of the company
           :param char st_line_number: will be used as the name of the generated account move
           :return: ID of the account.move created
        """

        if context is None:
            context = {}
        return False


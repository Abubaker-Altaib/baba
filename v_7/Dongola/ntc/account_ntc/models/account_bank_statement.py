# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2013-2014 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp.osv import fields, osv, orm
#from openerp.tools.translate import _

#----------------------------------------------------------
#  Bank Statement (Inherit)
#----------------------------------------------------------
class account_bank_statement(osv.Model):

    _inherit = "account.bank.statement"

    _columns = {
       'confirm_date': fields.datetime("Confirm On"),
       'state':fields.selection([('draft', 'New'),
                                 ('open', 'Open'),
                                 ('confirm', 'Confirm'), 
                                 ('closed', 'Closed')]),

         }

    def button_close_bank(self, cr, uid, ids, context=None):
        """
        Close bank statement button check statement balance before closing the statement
        change state to 'close' and set closing_date
        
        @return: update statement record
        """
        for st_id in ids:
            self.balance_check(cr, uid, st_id, context=context)
        return self.write(cr, uid, ids, {'state':'closed', 'closing_date': time.strftime("%Y-%m-%d %H:%M:%S")}, context=context)

    def button_confirm_bank(self, cr, uid, ids, context=None):
        """
        Confirm bank statement button check statement balance before closing the statement
        change state to 'confirm' and set confirm_date
        
        @return: update statement record
        """
        super(account_bank_statement, self).button_confirm_bank(cr, uid, ids, context)
        return self.write(cr, uid, ids, {'confirm_date': time.strftime("%Y-%m-%d %H:%M:%S")}, context=context)

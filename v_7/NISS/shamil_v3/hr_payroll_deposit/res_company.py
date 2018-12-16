 # -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2014-2015 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class res_company(osv.Model):

    _inherit = 'res.company'

    _columns = {
              'hr_deposit_account_id': fields.many2one('account.account', 'Deposit Account'),
              'hr_deposit_cash_account_id': fields.many2one('account.account', 'Deposit Cash Account'),
               }


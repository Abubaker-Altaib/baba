# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv
from datetime import datetime
import openerp.addons.decimal_precision as dp

class hr_loan_data(osv.osv): 
    _name = "hr.loan.data"

    _columns = {
            'name': fields.char('Notes', size=256),
            'loan_type': fields.char('loan type', size=64, select=True),
	    'partner_id' : fields.many2one('res.partner','Partner'),
            'amount': fields.float('Amount', digits_compute=dp.get_precision('Account')),
            'partner_name': fields.char('PrimaryName', size=64, select=True),
            'partner_code': fields.char('PrimaryID', size=64,select=True ),
            'transaction_time': fields.date('transactionTime', select=True),
	    'ready': fields.boolean('Ready for Import'),
            'state': fields.char('State', size=64, select=True),
    }

 



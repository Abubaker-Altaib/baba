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

class account_amanat_archive(osv.osv): 
    _name = "account.amanat.archive"

    _columns = {
            'name': fields.char('Notes', size=256),
	    'account_id' : fields.many2one('account.account','Account'),
	    'currency_id' : fields.many2one('res.currency','Currency'),
	    'partner_id' : fields.many2one('res.partner','Partner'),
	    'debit': fields.float('Debit', digits_compute=dp.get_precision('Account')),
            'credit': fields.float('Credit', digits_compute=dp.get_precision('Account')),
            'balance': fields.float('Balance', digits_compute=dp.get_precision('Account')),
            'partner_name': fields.char('PrimaryName', size=64, select=True),
            'partner_code': fields.char('PrimaryID', size=64,select=True ),
            'transaction_no': fields.char('txtDocumentID', size=64,),
            'transaction_time': fields.date('transactionTime', select=True),
	    'ready': fields.boolean('Ready for Import')
    }
    _defaults = {
	    'ready':False,
		}

account_amanat_archive()
 



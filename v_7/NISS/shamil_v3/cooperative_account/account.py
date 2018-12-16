# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.osv import osv,fields
from openerp import netsvc
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class account_account(osv.osv):
    _inherit = "account.account"
    _columns = {

        'co_operative' : fields.boolean('Cooperative?' , help="This Field determinate whether this account is a Cooperative or not"),
    }
    



class account_journal(osv.osv):
    _inherit = "account.journal"
    _columns = {

        'co_operative' : fields.boolean('Cooperative?' , help="This Field determinate whether this Journal is a Cooperative or not"),
    }

    
    
    

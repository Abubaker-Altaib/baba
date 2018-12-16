# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import fields, osv

# Define Occasion Account and Journal for each Company 

class occasion_journal(osv.Model):
    """inherits res.company to add feilds for the service's accounting configurations (Occasion journal and Occasion Account).
    """
    _inherit = 'res.company'
    _columns = {
                'occasion_jorunal_id': fields.many2one('account.journal','Occasion journal', required=True),
                'occasion_account_id': fields.many2one('account.account', 'Occasion Account', required=True),
                }


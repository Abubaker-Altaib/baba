# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv, fields

class purchase_journal(osv.osv):
    """
    To add clearance account and journal configration to company """

    _inherit = 'res.company'
    _columns = {
                'clearance_jorunal': fields.many2one('account.journal','Clearance journal'),
                'clearance_account': fields.many2one('account.account', 'Clearance Account'),
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

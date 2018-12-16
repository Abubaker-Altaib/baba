# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields

class occasion_journal(osv.Model):
    """
    To define Occasion Account and Journal for each Company """
    _inherit = 'res.company'
    _columns = {
                'occasion_jorunal_id': fields.many2one('account.journal','Occasion journal', required=True),
                'occasion_account_id': fields.many2one('account.account', 'Occasion Account', required=True),
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

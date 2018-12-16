# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv

class invoice(osv.osv):
    """
    To add contract id to account invoice """

    _inherit = 'account.invoice'
    _columns = {
                    'contract_id': fields.many2one('purchase.contract', 'Contract',),

                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


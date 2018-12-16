# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv

class account_voucher(osv.osv):
    """
    To add contract id to account voucher """
    _inherit = 'account.voucher'
    _columns = {
                    'contract_id': fields.many2one('purchase.contract', 'Contract',),

                }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

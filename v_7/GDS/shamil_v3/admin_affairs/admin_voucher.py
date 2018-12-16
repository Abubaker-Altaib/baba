# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
###############################################################################

from openerp.osv import fields, osv
import netsvc

class res_company(osv.Model):
    _inherit = "res.company"
    """Inherits res.company to add feild for accounting configuration for admin affairs
    """
    _columns = {
              
             'affairs_voucher_state': fields.char("affairs Voucher State", size=16),
    }
    def _check_affairs_voucher_state(self, cr, uid, ids, context=None):
        values = self.pool.get('account.voucher')._columns['state'].selection
        for company in self.browse(cr, uid, ids, context=context):
            if company.affairs_voucher_state not in dict(values).keys():
                return False
        return True

    _constraints = [
        (_check_affairs_voucher_state, 'Configuration error!\nThis state is not defined in voucher object', ['affairs_voucher_state']),
    ]






# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

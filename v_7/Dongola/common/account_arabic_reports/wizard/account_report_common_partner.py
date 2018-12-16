# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields

class account_common_partner_report(osv.osv_memory):
    """
    Inherit common partner wizard to choose which type of partner will be display when the report print
    """
    _inherit = "account.common.partner.report"

    _name = 'account.common.partner.report'

    _description = 'Account Common Partner Report'

    _columns = {
        'result_selection': fields.selection([('customer', 'Receivable Accounts'),
                                              ('supplier', 'Payable Accounts'),
                                              ('customer_supplier', 'Receivable and Payable Accounts')],
                                              "Partner's", required=True),
    }

    _defaults = {
        'result_selection': 'customer_supplier',
    }

    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data['form'].update(self.read(cr, uid, ids, ['result_selection'], context=context)[0])
        return data


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

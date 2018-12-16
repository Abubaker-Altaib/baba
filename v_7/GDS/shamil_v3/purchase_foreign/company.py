# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields

class purchase_journal(osv.osv):
    """
    To add accounts and journals to company to manage foreign purchase and letter of credit """

    _inherit = 'res.company'
    _columns = {
                'letter_of_credit_jorunal': fields.many2one('account.journal','Letter of Credit Journal'),
                'letter_of_credit_account': fields.many2one('account.account', 'Letter of Credit account'),
                'purchase_foreign_journal': fields.many2one('account.journal','Foreign Purchase Journal'),
                'purchase_foreign_account': fields.many2one('account.account', 'Foreign Purchase Account'),
                'name': fields.char('Name', size=256, required=True, translate=True, help='Name it to easily find a record'),
                }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

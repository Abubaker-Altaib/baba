# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import osv, fields

class purchase_journal(osv.osv):
    _inherit = 'res.company'
    _columns = {
                'transportation_jorunal': fields.many2one('account.journal','Transportation journal'),
                'transportation_account': fields.many2one('account.account', 'Transportation Account'),
                }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

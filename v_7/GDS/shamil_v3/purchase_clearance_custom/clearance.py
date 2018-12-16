# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from osv import osv, fields

class purchase_clearance(osv.osv):

    _inherit = "purchase.clearance"

    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed', 'Waiting for Dept Manager to Approve'),
    ('done', 'Done'),
    ('cancel', 'Cancel'),
    ]
   
    _columns = {
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, help="The state of the Clearance.", select=True),
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

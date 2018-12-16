# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
from tools.translate import _

# ----------------------------------------------------
# Stock Inventory (Inherit)
# ----------------------------------------------------

class stock_inventory(osv.osv):
    _inherit = "stock.inventory"
    _columns = {
        'state': fields.selection( (('draft', 'Draft'), ('cancel','Cancelled'), ('confirm','Confirmed'), ('approved', 'Approved'),('done', 'Done')), 'Status', readonly=True, select=True),
    }


class stock_inventory_line(osv.osv):
    _inherit = "stock.inventory.line"

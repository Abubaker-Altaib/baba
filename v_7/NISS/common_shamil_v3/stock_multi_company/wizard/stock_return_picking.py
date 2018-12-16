# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv,fields

class stock_return_picking_memory(osv.osv_memory):
    _inherit = "stock.return.picking.memory"

    def _check_product_qty(self, cr, uid, ids):
        for record in self.browse(cr, uid, ids):
            if record.quantity > record.move_id.product_qty:
                return False
            return True

    def _check_product_qty_positive(self, cr, uid, ids):
        for record in self.browse(cr, uid, ids):
            if record.quantity <= 0:
                return False
            return True

    _constraints = [
                 (_check_product_qty, 'The Quantity cannot be more than original quantity.',['quantity']),
                 (_check_product_qty_positive, 'The Quantity must be more than zero.',['quantity']),]

stock_return_picking_memory()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

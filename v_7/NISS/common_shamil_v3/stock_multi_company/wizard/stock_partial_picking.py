# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv,fields

# ----------------------------------------------------
# Product Product inherit
# ----------------------------------------------------

class stock_partial_picking_line(osv.TransientModel):

    _inherit = "stock.partial.picking.line"

    _columns = {
        'product_id' : fields.many2one('product.product', string="Product", required=True, ondelete='CASCADE', readonly=True,),
        'product_uom': fields.related('product_id', 'uom_id',type='many2one', relation='product.uom', string='Unit of Measure', readonly=True, ),     
    }  

    def _check_product_qty(self, cr, uid, ids):
        for record in self.browse(cr, uid, ids):
            if record.quantity > record.move_id.product_qty:
                return False
            return True

    _constraints = [
                 (_check_product_qty, 'The Quantity cannot be more than original quantity.',['quantity']),]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

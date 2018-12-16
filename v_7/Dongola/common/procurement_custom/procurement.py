# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class procurement_order(osv.Model):
    """
    Add constraints and exception messages to procurement """
    _inherit = "procurement.order"
    _columns = {
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM'), required=True, states={'draft':[('readonly',False)]}),
    }

    def action_confirm(self, cr, uid, ids, context=None):
        """ 
        Confirms procurement, create move and raise exception message if quantity
        is less than zero.
    
        @return: True
        """
        move_obj = self.pool.get('stock.move')
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.product_qty <= 0.00:
                raise osv.except_osv(_('Data Insufficient !'),
                    _('Please check the quantity in procurement order(s), it should not be 0 or less!'))
            if procurement.product_id.type in ('product', 'consu'):
                if not procurement.move_id:
                    source = procurement.location_id.id
                    if procurement.procure_method == 'make_to_order':
                        source = procurement.product_id.product_tmpl_id.property_stock_procurement.id
                    id = move_obj.create(cr, uid, {
                        'name': procurement.name,
                        'location_id': source,
                        'location_dest_id': procurement.location_id.id,
                        'product_id': procurement.product_id.id,
                        'product_qty': procurement.product_qty,
                        'product_uom': procurement.product_uom.id,
                        'date_expected': procurement.date_planned,
                        'state': 'draft',
                        #'company_id': procurement.company_id.id,
                        'auto_validate': True,
                    })
                    move_obj.action_confirm(cr, uid, [id], context=context)
                    self.write(cr, uid, [procurement.id], {'move_id': id, 'close_move': 1})
        self.write(cr, uid, ids, {'state': 'confirmed', 'message': ''})
        return True



class stock_warehouse_orderpoint(osv.Model):
    """
    Add minimum quantity and order point to warehouse"""

    _inherit = "stock.warehouse.orderpoint"
    _columns = {
        'product_minn_qty': fields.float('Min Quantity',
            help="When the virtual stock goes below the Min Quantity, OpenERP generates "\
            "a procurement to bring the virtual stock to the Max Quantity."),
        'product_min_qty': fields.float('Order Point', required=True),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

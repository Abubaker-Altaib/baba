# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import time

# ----------------------------------------------------
# Stock Inventory (Inherit)
# ----------------------------------------------------
class stock_inventory(osv.osv):
    _inherit = "stock.inventory"
    _columns = {
        'location_id': fields.many2one('stock.location', 'Location', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'inventory_line_id': fields.one2many('stock.inventory.line', 'inventory_id', 'Inventories', readonly=True, states={'draft': [('readonly', False)]}),
        'sequence': fields.char('Sequence', size=64, required=True,readonly=True, select=True),
        'user_id': fields.many2one('res.users', 'Responsible', required=True, readonly=True,),
        'creation_date': fields.datetime('Create Date', required=True, readonly=True,),
        'move_id': fields.many2one('account.move', 'Account move', readonly = True),
        'amount': fields.float('Amount Difference', digits_compute=dp.get_precision('account'), readonly = True),
        'note': fields.text('Notes', size = 256),
    }

    _defaults = {
        'sequence': '/',
        'user_id': lambda s, c, u, ctx: u,
        'creation_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        }
    _sql_constraints = [ 
            ('name_uniq', 'uniqu(name)', 'Name field must be unique !'),]

    def create(self, cr, user, vals, context=None):
        if ('sequence' not in vals) or (vals.get('sequence')=='/'):
            vals['sequence'] = self.pool.get('ir.sequence').get(cr, user, 'stock.inventory')
        new_id = super(stock_inventory, self).create(cr, user, vals, context)
        return new_id

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        sequence = self.pool.get('ir.sequence').get(cr, uid, 'stock.inventory')
        default = default.copy()
        default['sequence'] = sequence
        default['name'] = self.browse(cr, uid, id).name + ' (copy)' 
        default['user_id'] = uid
        default['creation_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        default['amount'] = 0.0
        default['move_ids'] = []
        return super(stock_inventory, self).copy(cr, uid, id, default, context)

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.state not in ['draft']:
                raise osv.except_osv(_('Error'), _('You cannot remove the inventory which is not in draft state!'))
        return super(stock_inventory, self).unlink(cr, uid, ids, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        """
        Inherit the method of confirmation to read the location_id from product 
        template instead of reading it from the product, and append the product 
        name in the dictionary of the values.
    
        @return: True
        """
        if context is None:
            context = {}
        # to perform the correct inventory corrections we need analyze stock location by
        # location, never recursively, so we use a special context
        product_context = dict(context, compute_child=False)

        location_obj = self.pool.get('stock.location')
        for inv in self.browse(cr, uid, ids, context=context):
            move_ids = []
            for line in inv.inventory_line_id:
                pid = line.product_id.id
                product_context.update(uom=line.product_uom.id, to_date=inv.date, date=inv.date, prodlot_id=line.prod_lot_id.id)
                amount = location_obj._product_get(cr, uid, line.location_id.id, [pid], product_context)[pid]

                change = line.product_qty - amount
                lot_id = line.prod_lot_id.id
                if change:
                    location_id = line.product_id.product_tmpl_id.property_stock_inventory.id
                    if not location_id:
                        raise osv.except_osv(_('Error'), _('Please add inventory location for the product %s.')%(line.product_id.name))
                    value = {
                        'name': 'INV:' + line.inventory_id.name + ':' + line.product_id.name,
                        'product_id': line.product_id.id,
                        'product_uom': line.product_uom.id,
                        'prodlot_id': lot_id,
                        'date': inv.date,
                    }
                    if change > 0:
                        value.update( {
                            'product_qty': change,
                            'location_id': location_id,
                            'location_dest_id': line.location_id.id,
                        })
                    else:
                        value.update( {
                            'product_qty': -change,
                            'location_id': line.location_id.id,
                            'location_dest_id': location_id,
                        })
                    move_ids.append(self._inventory_line_hook(cr, uid, line, value))
            message = _("Inventory %s is done.") %(inv.name)
            self.log(cr, uid, inv.id, message)
            self.write(cr, uid, [inv.id], {'state': 'confirm', 'move_ids': [(6, 0, move_ids)]})
            self.pool.get('stock.move').action_confirm(cr, uid, move_ids, context=context)
            amount = self.get_amount_difference(cr, uid, ids,context=context)
            self.write(cr, uid, [inv.id], {'amount':amount}, context=context)  
        return True

    def get_amount_difference(self, cr, uid, ids, context=None):
        for inv in self.browse(cr, uid, ids, context=context):
            amount = 0.0
            for move in inv.move_ids:
                if move.location_id.usage == 'internal':
                    amount -= (move.product_qty * move.product_id.standard_price )
                else:
                    amount += (move.product_qty * move.product_id.standard_price )
            self.write(cr, uid, [inv.id], {'amount':amount}, context=context)  
            return amount

stock_inventory()

class stock_inventory_line(osv.osv):
    _inherit = "stock.inventory.line"

    _columns = {
        'product_uom': fields.related('product_id','uom_id',type='many2one',relation='product.uom',string='Unit of Measure', store=True, readonly=True),
        'location_id': fields.related('inventory_id','location_id',type='many2one',relation='stock.location',string='Location', store=True, readonly=True),      
    }

    def _check_product_stock(self, cr, uid, ids, context=None):
        """ Checks whether product dublicated in the line.
        @return: True or False
        """
        for line in self.browse(cr, uid, ids, context=context):
            product_ids = self.search(cr,uid,[('product_id', '=',line.product_id.id),('inventory_id', '=',line.inventory_id.id)])
            if len(product_ids)>1:
                raise osv.except_osv(_('Error'), _('The product with name \n %s \n and code \n %s \n has been selected more than once.')%(line.product_id.name, line.product_id.default_code)) 
                return False
        return True

    def _check_positive_qty(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if line.product_qty < 0:
                return False
        return True

    _constraints = [      
        (_check_product_stock,'',['product_id']),
        (_check_positive_qty, 'Error! The product quantity can not be less than zero', ['product_qty'])]

stock_inventory_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

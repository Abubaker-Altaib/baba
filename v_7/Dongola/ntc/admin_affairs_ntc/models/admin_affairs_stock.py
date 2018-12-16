# coding: utf-8 
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp import tools
import netsvc
from openerp.tools.translate import _
from openerp.osv import osv, fields, orm
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class stock_picking(osv.Model):

    _inherit = "stock.picking"

    _columns = {
        'enrich_id': fields.many2one('payment.enrich', 'Payment Enrich'),
        'purpose': fields.char('Purpose'),
        'food_sup_in': fields.boolean('Food In'),
        'food_sup_out': fields.boolean('Food Out'),
        'state': fields.selection([
            #('draft', 'Draft'),
            #('sup','Supervisor Services'),
            #('complete', 'Complete'),
            #('cancel', 'Cancelled'),
            #('auto', 'Waiting Another Operation'),
            #('confirmed', 'Waiting Availability'),
            #('assigned', 'Ready to Transfer'),
            #('validated' , 'Waiting Approval'),
            #('done', 'Transferred'),
            ('draft', 'Draft'),
            ('complete', 'Waiting Department Manager'),
            ('sup','Supervisor Services'),
            ('validated' , 'Waiting General Department Manager'),
            ('auto', 'Waiting Another Operation'),
            ('in_progress', 'Purchase Order In Progress'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Waiting General HR Department Manager'),
            ('cancel', 'Cancelled'),
            ('approve_gm','Waiting Availability'),
            ('approve_ghrm','Ready to Deliver'),
            ('sign','Waiting Section Manager'),
            ('done', 'Delivered'),
            ], 'Status', readonly=True, select=True, track_visibility='onchange', help="""
            * Draft: not confirmed yet and will not be scheduled until confirmed\n
            * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
            * Waiting Availability: still waiting for the availability of products\n
            * Ready to Transfer: products reserved, simply waiting for confirmation.\n
            * Transferred: has been processed, can't be modified or cancelled anymore\n
            * Cancelled: has been cancelled, can't be confirmed anymore""" ),
    }

    #recived
    def sup(self, cr, uid, ids, context=None):
        stock = self.browse(cr, uid, ids[0], context=context)
        if not stock.move_lines:
            raise osv.except_osv(_('Error!'),_('You cannot process picking without stock moves.'))
        return self.write(cr, uid, ids, {'state': 'sup'})
    
    
    def create_enrich(self, cr, uid, ids, context=None):
        stock = self.browse(cr, uid, ids[0], context=context)
        total = 0
        for move in stock.move_lines:
            total_price = move.product_qty * move.price_unit
            total += total_price
            self.pool.get('stock.move').write(cr, uid, move.id, {'state': 'confirmed'})
        details = 'Enrich Line :'+stock.name and stock.name or ""
        self.pool.get('payment.enrich.lines').create(cr, uid, {'enrich_id':stock.enrich_id.id,'date':stock.date,
                                                'cost':total,'name':details,
                                                'department_id':stock.department_id.id},
                                                context=context)
        self.draft_force_assign(cr, uid, ids)
        return True 

    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'})
        
    def set_to_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}) 
    
    #deliver 
    def super_service(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        stock = self.browse(cr, uid, ids[0], context=context)
        qty = 0
        if not stock.move_lines:
            raise osv.except_osv(_('Error!'),_('You cannot process picking without stock moves.'))
        else:
            for move in stock.move_lines:
                loc = self.get_quantity_at_location(cr, uid, move.location_id.id, move.product_id.id)
                product = product_obj.browse(cr, uid, move.product_id.id)
                qty = move.product_qty
                if qty > loc:
                    raise osv.except_osv(_('Error!'),_('The required quantity is greater than the available.'))
                else:
                    self.action_assign(cr, uid, ids) 
        return True

    def get_quantity_at_location(self,cr,uid,locid,product):
        ls = ['stock_real','stock_virtual','stock_real_value','stock_virtual_value']
        move_avail = self.pool.get('stock.location')._product_value(cr,uid,[locid],ls,0,{'product_id':product})
        return move_avail[locid]['stock_real']
        
        
class stock_picking_in(osv.Model):

    _inherit = "stock.picking.in"
    _columns = {
        'enrich_id': fields.many2one('payment.enrich', 'Payment Enrich'),
        'purpose': fields.char('Purpose'),
        'food_sup_in': fields.boolean('Food'),
        'state': fields.selection(
            [('draft', 'Draft'),
            ('sup','Supervisor Services'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Ready to Receive'),
            ('done', 'Received'),
            ('cancel', 'Cancelled'),],
            'Status', readonly=True, select=True,
            help="""* Draft: not confirmed yet and will not be scheduled until confirmed\n
                 * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
                 * Waiting Availability: still waiting for the availability of products\n
                 * Ready to Receive: products reserved, simply waiting for confirmation.\n
                 * Received: has been processed, can't be modified or cancelled anymore\n
                 * Cancelled: has been cancelled, can't be confirmed anymore"""),
    }
    _defaults={
        'food_sup_in' :lambda self, cr, uid, c: c.get('food_sup_in', False),
    }
            
    def sup(self, cr, uid, ids, context=None):
        return self.pool.get('stock.picking').sup(cr, uid, ids, context=context)
        
    def create_enrich(self, cr, uid, ids, context=None):
        return self.pool.get('stock.picking').create_enrich(cr, uid, ids, context=context)
        
    def cancel(self, cr, uid, ids, context=None):
        return self.pool.get('stock.picking').cancel(cr, uid, ids, context=context)
        
    def set_to_draft(self, cr, uid, ids, context=None):
        return self.pool.get('stock.picking').set_to_draft(cr, uid, ids, context=context)
        
class stock_picking_out(osv.Model):

    _inherit = "stock.picking.out"
    _columns = {
        'food_sup_out': fields.boolean('Food'),
        'purpose': fields.char('Purpose'),
    }
    _defaults={
        'food_sup_out' : lambda self, cr, uid, c: c.get('food_sup_out', False),
    }

    def super_service(self, cr, uid, ids, context=None):
        return self.pool.get('stock.picking').super_service(cr, uid, ids, context=context)


class stock_move(osv.Model):

    _inherit = "stock.move"

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,
                            loc_dest_id=False, partner_id=False):
        """ On change of product id, if finds UoM, UoS, quantity and UoS quantity.
        @param prod_id: Changed Product id
        @param loc_id: Source location id
        @param loc_dest_id: Destination location id
        @param partner_id: Address id of partner
        @return: Dictionary of values
        """
        if not prod_id:
            return {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        lang = user and user.lang or False
        if partner_id:
            addr_rec = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if addr_rec:
                lang = addr_rec and addr_rec.lang or False
        ctx = {'lang': lang}

        product = self.pool.get('product.product').browse(cr, uid, [prod_id], context=ctx)[0]
        uos_id  = product.uos_id and product.uos_id.id or False
        result = {
            'name': product.partner_ref,
            'product_uom': product.uom_id.id,
            'product_uos': uos_id,
            'product_qty': 1.0,
            'qty': product.qty_available,
            'product_uos_qty' : self.pool.get('stock.move').onchange_quantity(cr, uid, ids, prod_id, 1.00, product.uom_id.id, uos_id)['value']['product_uos_qty'],
            'prodlot_id' : False,
        }
        if loc_id:
            result['location_id'] = loc_id
        if loc_dest_id:
            result['location_dest_id'] = loc_dest_id
        return {'value': result}


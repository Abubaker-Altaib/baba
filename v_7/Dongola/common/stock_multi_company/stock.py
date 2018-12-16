# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv,orm
from openerp.tools.translate import _
import tools
import netsvc
#----------------------------------------------------------
# Stock Location (Inherit)
#----------------------------------------------------------
class stock_location(osv.Model):
    _inherit = "stock.location"

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        """ 
        Changes the view dynamically

        @return: New arch of view.
        """
        if context is None:
            context = {}
        if view_type == 'tree':
            view_id = self.pool.get('ir.ui.view').search(cr,uid,[('name', '=', 'stock.location.tree2')])
            if context.get('product_id', ''):
                view_id = self.pool.get('ir.ui.view').search(cr, uid, [('name', '=', 'stock.location.tree')])
            view_id = view_id and view_id[0] or None  
        res = super(stock_location,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        return res

    def name_get(self, cr, uid, ids, context=None):
        """
        Inherit fuction to return name (not full hierarchical)       
        always return the full hierarchical name

        @return: list of tuple (id,name)
        """
        if not len(ids):
            return []
        res = [(r['id'], r['name']) for r in self.read(cr, uid, ids, ['name'], context)]
        return res

    _columns = {
        'user_id':  fields.many2many('res.users', 'users_loction', 'a_id', 'b_id', 'Location manager'),
    }

#----------------------------------------------------------
# ir_sequence (Inherit)
#----------------------------------------------------------
class ir_sequence(osv.Model):
    _inherit = "ir.sequence"
    def next_by_code(self, cr, uid, sequence_code, context=None):
        """
        Inherit function to add sequance number for objects.

        @param dict context: context dictionary may contain a
        ``force_company`` key with the ID of the company to
        use instead of the user's current company for the
        sequence selection. A matching sequence for that
        specific company will get higher priority. 
        @param sequence_code: current object

        @return: next sequance number
        """
        self.check_access_rights(cr, uid,'read')
        company_ids = self.pool.get('res.company').search(cr, uid, [], context=context) + [False]
        if sequence_code in['stock.picking.in','stock.picking.out','stock.picking.internal','stock.picking.quality','exchange.order']:
            company_ids = [self.pool.get('res.users').browse(cr, uid, uid).company_id.id ] + [False]
        ids = self.search(cr, uid, ['&',('code','=', sequence_code),('company_id','in',company_ids)])
        return self._next(cr, uid, ids, context)

#----------------------------------------------------------
# Stock Picking (Inherit)
#----------------------------------------------------------
class stock_picking(osv.Model):
    _inherit = "stock.picking"
    _columns = {
        'location_id': fields.related('move_lines', 'location_id', readonly=True, type='many2one', relation='stock.location', string='Location', store=True,  select=True),
        'location_dest_id': fields.related('move_lines', 'location_dest_id', readonly=True, type='many2one', relation='stock.location', store=True, string='Location Destination',  select=True),
        'user_id':fields.many2one('res.users', 'users',readonly=True),  
   
    }
    def _get_invoice_type(self, pick):
        """
        Inherit function to add new picking type(quality) when create invoice.

        @param pick: picking type
        @return: invoice type
        """
        src_usage = dest_usage = None
        inv_type = None
        if pick.invoice_state == '2binvoiced':
            if pick.move_lines:
                src_usage = pick.move_lines[0].location_id.usage
                dest_usage = pick.move_lines[0].location_dest_id.usage
            if pick.type == 'out' and dest_usage == 'supplier':
                inv_type = 'in_refund'
            elif pick.type == 'out' and dest_usage == 'customer':
                inv_type = 'out_invoice'
            elif pick.type == 'in' and src_usage == 'supplier':
                inv_type = 'in_invoice'
            elif pick.type == 'in' and src_usage == 'customer':
                inv_type = 'out_refund'
            elif pick.type == 'quality' and src_usage == 'supplier':
                inv_type = 'in_invoice'
            elif pick.type == 'quality' and src_usage == 'customer':
                inv_type = 'out_refund'
            else:
                inv_type = 'out_invoice'
        return inv_type
    def next_by_code(self, cr, uid, sequence_code,company_id, context=None):
        """
        @param company_id: company_id
        @param sequance_code: object

        @return: next sequance for current object
        """

        self.check_access_rights(cr, uid,'read')
        ids = self.pool.get('ir.sequence').search(cr, uid, ['&',('code','=', sequence_code),('company_id','in',[company_id])])
        return self.pool.get('ir.sequence')._next(cr, uid, ids, context)


    def action_done(self, cr, uid, ids, context=None):
        """
        Makes the move done and if all moves are done, it will finish the picking.

        @return:True
        """
        super(stock_picking, self).action_done(cr, uid, ids, context=None)
        moves=[]
        for pick in self.browse(cr, uid, ids, context=context):
            for move in pick.move_lines:
                if move.state=='cancel':
                    continue
                moves.append(move)
        self.pool.get('stock.move').create_chained_picking(cr, uid, moves, context)
        self.write(cr, uid, ids, {'user_id':uid})
        return True

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """
        Makes partial picking and moves done.

        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s'%(move.id), {})
                product_qty = partial_data.get('product_qty',0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom',False)
                product_price = partial_data.get('product_price',0.0)
                product_currency = partial_data.get('product_currency',False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

                    if product.id in product_avail:
                        product_avail[product.id] += qty
                    else:
                        product_avail[product.id] = product.qty_available

                    if qty > 0:
                        new_price = currency_obj.compute(cr, uid, product_currency,
                                move_currency_id, product_price)
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                product.uom_id.id)
                        if product.qty_available <= 0:
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context=context)[product.id]
                            new_std_price = ((amount_unit * product_avail[product.id])\
                                + (new_price * qty))/(product_avail[product.id] + qty)
                        # Write the field according to price type field
                        #product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})
                        cr.execute('UPDATE product_template SET standard_price=%s WHERE id=%s ', (new_std_price, product.product_tmpl_id.id,))
                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency})


            for move in too_few:
                product_qty = move_product_qty[move.id]
                if not new_picking:
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': sequence_obj.get(cr, uid, 'stock.picking.%s'%(pick.type)),
                                'move_lines' : [],
                                'state':'draft',
                            })
                if product_qty != 0:
                    defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty, #TODO: put correct uos_qty
                            'picking_id' : new_picking,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            'product_uom': product_uoms[move.id]
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)
                move_obj.write(cr, uid, [move.id],
                        {
                            'product_qty' : move.product_qty - partial_qty[move.id],
                            'product_uos_qty': move.product_qty - partial_qty[move.id], #TODO: put correct uos_qty
                            
                        })

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})
                move_obj.write(cr, uid, [move.id], defaults)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': product_qty, #TODO: put correct uos_qty
                    'product_uom': product_uoms[move.id]
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking])
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = new_picking
            else:
                self.action_move(cr, uid, [pick.id])
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}

        return res

# ----------------------------------------------------
# Move (Inherit)
# ----------------------------------------------------
class stock_move(osv.Model):

    _inherit = "stock.move"

    def create_chained_picking(self, cr, uid, moves, context=None):
        """
        Create chain picking.

        @param moves: List of ids
        @return: List of ids
        """
        res_obj = self.pool.get('res.company')
        location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        picking_obj = self.pool.get('stock.picking')
        new_moves = []
        if context is None:
            context = {}
        seq_obj = self.pool.get('ir.sequence')
        for picking, todo in self._chain_compute(cr, uid, moves, context=context).items():
            ptype = todo[0][1][5] and todo[0][1][5] or location_obj.picking_type_get(cr, uid, todo[0][0].location_dest_id, todo[0][1][0])
            if picking:
                # name of new picking according to its type
                company_is=todo[0][1][4] or res_obj._company_default_get(cr, uid, 'stock.company', context=context)
                new_pick_name = picking_obj.next_by_code(cr, uid, 'stock.picking.' + ptype,company_is)
                if not new_pick_name:
                    new_pick_name='/'
                pickid = self._create_chained_picking(cr, uid, new_pick_name, picking, ptype, todo, context=context)
                # Need to check name of old picking because it always considers picking as "OUT" when created from Sale Order
                old_ptype = location_obj.picking_type_get(cr, uid, picking.move_lines[0].location_id, picking.move_lines[0].location_dest_id)
                if old_ptype != picking.type:
                    old_pick_name = seq_obj.get(cr, uid, 'stock.picking.' + old_ptype)
                    picking_obj.write(cr, uid, [picking.id], {'name': old_pick_name, 'type': old_ptype}, context=context)
            else:
                pickid = False
            for move, (loc, dummy, delay, dummy, company_id, ptype, invoice_state) in todo:
                new_id = move_obj.copy(cr, uid, move.id, {
                    'location_id': move.location_dest_id.id,
                    'location_dest_id': loc.id,
                    'date_moved': time.strftime('%Y-%m-%d'),
                    'picking_id': pickid,
                    'state': 'waiting',
                    'company_id': company_id or res_obj._company_default_get(cr, uid, 'stock.company', context=context)  ,
                    'move_history_ids': [],
                    'date': (datetime.strptime(move.date, '%Y-%m-%d %H:%M:%S') + relativedelta(days=delay or 0)).strftime('%Y-%m-%d'),
                    'move_history_ids2': []}
                )
                move_obj.write(cr, uid, [move.id], {
                    'move_dest_id': new_id,
                    'move_history_ids': [(4, new_id)]
                })
                new_moves.append(self.browse(cr, uid, [new_id])[0])
            if pickid:
                wf_service.trg_validate(uid, 'stock.picking', pickid, 'button_confirm', cr)
                picking_obj.force_assign(cr, uid, [pickid])
        if new_moves:
            new_moves += self.create_chained_picking(cr, uid, new_moves, context)
        return new_moves

    def action_confirm(self, cr, uid, ids, context=None):
        """
        Confirms stock move.

        @return: List of ids.
        """
        self.write(cr, uid, ids, {'state': 'confirmed'})
        return []
    
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """
        Makes partial pickings and moves done.

        @param partial_datas: Dictionary containing details of partial picking
                          like partner_id, delivery_date, delivery
                          moves with product_id, product_qty, uom

        @return : List of ids
        """
        res = {}
        picking_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        wf_service = netsvc.LocalService("workflow")

        if context is None:
            context = {}

        complete, too_many, too_few = [], [], []
        move_product_qty = {}
        prodlot_ids = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ('done', 'cancel'):
                continue
            partial_data = partial_datas.get('move%s' % (move.id), False)
            assert partial_data, _('Missing partial picking data for move #%s') % (move.id)
            product_qty = partial_data.get('product_qty', 0.0)
            move_product_qty[move.id] = product_qty
            product_uom = partial_data.get('product_uom', False)
            product_price = partial_data.get('product_price', 0.0)
            product_currency = partial_data.get('product_currency', False)
            prodlot_ids[move.id] = partial_data.get('prodlot_id')
            if move.product_qty == product_qty:
                complete.append(move)
            elif move.product_qty > product_qty:
                too_few.append(move)
            else:
                too_many.append(move)

            # Average price computation
            if (move.picking_id.type == 'in') and (move.product_id.cost_method == 'average'):
                product = product_obj.browse(cr, uid, move.product_id.id)
                move_currency_id = move.company_id.currency_id.id
                qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
                if qty > 0:
                    new_price = currency_obj.compute(cr, uid, product_currency,
                            move_currency_id, product_price)
                    new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                            product.uom_id.id)
                    if product.qty_available <= 0:
                        new_std_price = new_price
                    else:
                        # Get the standard price
                        amount_unit = product.price_get('standard_price', context=context)[product.id]
                        new_std_price = ((amount_unit * product.qty_available)\
                            + (new_price * qty)) / (product.qty_available + qty)

                    #product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})
                    cr.execute('UPDATE product_template SET standard_price=%s WHERE id=%s ', (new_std_price, product.product_tmpl_id.id,))

                    # Record the values that were chosen in the wizard, so they can be
                    # used for inventory valuation if real-time valuation is enabled.
                    self.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency,
                                })

        for move in too_few:
            product_qty = move_product_qty[move.id]
            if product_qty != 0:
                defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty,
                            'picking_id' : move.picking_id.id,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            }
                prodlot_id = prodlot_ids[move.id]
                if prodlot_id:
                    defaults.update(prodlot_id=prodlot_id)
                new_move = self.copy(cr, uid, move.id, defaults)
                complete.append(self.browse(cr, uid, new_move))
            self.write(cr, uid, [move.id],
                    {
                        'product_qty' : move.product_qty - product_qty,
                        'product_uos_qty':move.product_qty - product_qty,
                    })


        for move in too_many:
            self.write(cr, uid, [move.id],
                    {
                        'product_qty': move.product_qty,
                        'product_uos_qty': move.product_qty,
                    })
            complete.append(move)

        for move in complete:
            if prodlot_ids.get(move.id):
                self.write(cr, uid, [move.id], {'prodlot_id': prodlot_ids.get(move.id)})
            self.action_done(cr, uid, [move.id], context=context)
            if  move.picking_id.id :
                # TOCHECK : Done picking if all moves are done
                cr.execute("""
                    SELECT move.id FROM stock_picking pick
                    RIGHT JOIN stock_move move ON move.picking_id = pick.id AND move.state = %s
                    WHERE pick.id = %s""",
                            ('done', move.picking_id.id))
                res = cr.fetchall()
                if len(res) == len(move.picking_id.move_lines):
                    picking_obj.action_move(cr, uid, [move.picking_id.id])
                    wf_service.trg_validate(uid, 'stock.picking', move.picking_id.id, 'button_done', cr)

        return [move.id for move in complete]

#----------------------------------------------------------
# Stock Warehouse (Inherit)
#----------------------------------------------------------
class stock_warehouse(osv.Model):
    _inherit = "stock.warehouse"
    _columns = { 
        'user_id':  fields.many2many('res.users', 'users_warehouse', 'a_id', 'b_id', 'Warehouse Managers'),
    }
#----------------------------------------------------------
# Stock Piching out (Inherit)
#----------------------------------------------------------


class stock_picking_out(osv.osv):
    _name = "stock.picking.out"
    _inherit = "stock.picking.in"
    _table = "stock_picking"
    _description = "Delivery Orders"
    _columns = { 
            'backorder_id': fields.many2one('stock.picking.out', 'Back Order of', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="If this shipment was split, then this field links to the shipment which contains the already processed part.", select=True),
        'state': fields.selection(
            [('draft', 'Draft'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Ready to Deliver'),
            ('done', 'Delivered'),
            ('cancel', 'Cancelled'),],
            'Status', readonly=True, select=True,
            help="""* Draft: not confirmed yet and will not be scheduled until confirmed\n
                 * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
                 * Waiting Availability: still waiting for the availability of products\n
                 * Ready to Deliver: products reserved, simply waiting for confirmation.\n
                 * Delivered: has been processed, can't be modified or cancelled anymore\n
                 * Cancelled: has been cancelled, can't be confirmed anymore"""),
        'user_id':  fields.many2many('res.users', 'users_warehouse', 'a_id', 'b_id', 'Warehouse Managers'),
    }
#----------------------------------------------------------
# Stock Piching in (Inherit)
#----------------------------------------------------------

class stock_picking_in(osv.osv):
    _name = "stock.picking.in"
    _inherit = "stock.picking.in"
    _table = "stock_picking"
    _description = "Incoming Shipments"
    _columns = { 
        'backorder_id': fields.many2one('stock.picking.in', 'Back Order of', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="If this shipment was split, then this field links to the shipment which contains the already processed part.", select=True),
        'state': fields.selection(
            [('draft', 'Draft'),
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

        'user_id':  fields.many2many('res.users', 'users_warehouse', 'a_id', 'b_id', 'Warehouse Managers'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

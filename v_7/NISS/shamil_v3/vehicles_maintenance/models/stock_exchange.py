# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
from tools.translate import _
from openerp import netsvc
import time
import openerp.addons.decimal_precision as dp


# ----------------------------------------------------
# Exchange Order inherit
# ----------------------------------------------------

class exchange_order(osv.Model):
    _inherit = 'exchange.order'

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('request_hq', 'Exchange Request From HQ'),
        ('confirmed_oc', 'Waiting Branch Manager Approval'),
        ('confirmed', 'Waiting Department Approval'),
        ('category_manager', 'Waiting for category manager'),
        ('approved', 'Approved'),
        ('approved_oc', 'Watiting Picking'),
        ('picking', 'Picking'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('wait_purchase', 'Waiting For Purchase Procedure'),
        ('goods_in_stock','Approve'),
    ]

    TYPE_SELECTION = [
        ('job','Related to maintenace job'),
        ('move','Movable'),
    ]

    _columns = {
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, select=True),
        'maintenance': fields.boolean('Maintenance'),
        'job_id': fields.many2one('maintenance.job', 'Maintenance Job'),
        'maintenance_department_id': fields.many2one('maintenance.department', 'Maintenance Department'),
        'maintenace_exchange_type': fields.selection(TYPE_SELECTION, 'Exchange Type'),
        'exchange_move_line': fields.one2many('exchange.move.fuel','exchange_id','Exchange Fuel Move Lines'),
        'mission_no': fields.char(string="mission no"),
        'mission_distance': fields.char(string="mission Distination"),
        'mission_leader': fields.char(string="mission team leader"),
        'mission_date': fields.date(string="Mission date" ),
        }

    _defaults = {
        'maintenance': False,
            }
    def _check_spaces_mission(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.mission_no:
                no=rec.mission_no.strip()
                if not no:
                    raise osv.except_osv(_('ValidateError'), _("mission Number must not be spaces"))
            if rec.mission_distance:
                dist=rec.mission_distance.strip()
                if not dist:
                    raise osv.except_osv(_('ValidateError'), _("mission Distination must not be spaces"))
            if rec.mission_leader:
                leader=rec.mission_leader.strip()
                if not leader:
                    raise osv.except_osv(_('ValidateError'), _("mission team leader must not be spaces"))
        return True

    def check_lines_order(self, cr, uid, ids, context=None):
        """ wf_service
        Changes order state to confirm.
        @return: True
        """
        for order in self.browse(cr, uid, ids, context=context):
            if not order.order_line:
                raise osv.except_osv(_('Error !'), _('You can not confirm the order without  order lines.'))
                
        return True

    def onchange_maintenance_department_id(self, cr, uid, ids, maintenance_department_id, context={}):
        """
        change department_id based on maintenance_department_id
        """
        vals = {'department_id': False, 'location_dest_id': False, 'location_id': False}
        domain = {}
        domain['department_id'] = domain['location_dest_id'] = domain['location_id'] = [('id','in',[])]
        if maintenance_department_id:
            maintenance_dep_rec = self.pool.get('maintenance.department').browse(cr, uid, maintenance_department_id, context)
            vals['department_id'] = maintenance_dep_rec.department_id and maintenance_dep_rec.department_id.id or False
            vals['location_dest_id'] = maintenance_dep_rec.stock_location_id and maintenance_dep_rec.stock_location_id.id or False
            vals['location_id'] = maintenance_dep_rec.location_dest_id and maintenance_dep_rec.location_dest_id.id or False
            
            domain['department_id'] = maintenance_dep_rec.department_id and [('id','in',[maintenance_dep_rec.department_id.id])] or [('id','in',[])]
            domain['location_dest_id'] = maintenance_dep_rec.stock_location_id and [('id','in',[maintenance_dep_rec.stock_location_id.id])] or [('id','in',[])]
            domain['location_id'] = maintenance_dep_rec.location_dest_id and [('id','in',[maintenance_dep_rec.location_dest_id.id])] or [('id','in',[])]
        
        return {'value':vals, 'domain':domain}

    def onchange_job_id(self, cr, uid, ids, job_id, context={}):
        """
        change department_id based on maintenance_department_id
        """
        exchange_line_obj = self.pool.get('exchange.order.line')
        vals = {'maintenance_department_id':False, 'department_id': False,'order_line': False}
        if ids :
            rec = self.browse(cr, uid, ids[0])
            lines_ids = [x.id for x in rec.order_line]
            '''if lines_ids:
                exchange_line_obj.unlink(cr, uid, lines_ids, context)'''
        
        if job_id:
            lines = []
            job_rec = self.pool.get('maintenance.job').browse(cr, uid, job_id, context)
            maintenance_department_id = job_rec.damage_line_id.department_id.id
            department_id = job_rec.damage_line_id.department_id.department_id.id
            vals['maintenance_department_id'] = maintenance_department_id
            vals['department_id'] = department_id
            for line in job_rec.spares_ids:
                onchange_vals = exchange_line_obj.product_id_change(cr, uid, [], line.product_id.id, line.quantity, False, date_order=False,
            name=False, price_unit=False, notes=False)
                lines_dict = {'product_id': line.product_id.id, 'product_qty': line.quantity,
                            'approved_qty': line.quantity,'name': onchange_vals['value']['name'], 
                            'price_unit': onchange_vals['value']['price_unit'], 
                            'product_uom': onchange_vals['value']['product_uom'],'state':'draft',
                }
                lines.append([0,False,lines_dict])
            vals['order_line'] = lines
        return {'value':vals}

    def onchange_maintenace_exchange_type(self, cr, uid, ids, maintenace_exchange_type, context={}):
        """
        """
        vals = {}
        if maintenace_exchange_type:
            if maintenace_exchange_type == 'move':
                vals = {'job_id':False}

        return {'value': vals}

    def _prepare_order_line_move(self, cr, uid, order, line, picking_id,product_qty ,context=None):
        """
        Prepare the dict of values to create the new stock move for a
        exchange order line. This method may be overridden to implement custom
        move generation (making sure to call super() to establish a clean extension chain).
        @param browse_record order: exchange.order record 
        @param browse_record line: exchange.order.line record 
        @param int picking_id: ID of stock  picking 
        @param product_qty : product qty(this is used for returning products including service)
        @return: dict of values to create() the stock move
        """

        if order.ttype =="other" and order.maintenance == True:
            return {
            'name': line.name[:250],
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'product_qty': product_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty':product_qty,
            'product_uos':  line.product_uom.id,
            'location_id': order.location_dest_id.id ,
            'location_dest_id': (order.maintenance_department_id and order.maintenance_department_id.location_dest_id.id) or False,
            #'location_dest_id': (order.location_id and order.location_id.id) or order.stock_journal_id.location_id.id,
            'exchange_line_id': line.id,
            'tracking_id': False,
            'state': 'draft',
            'note': line.notes,
            'price_unit': line.product_id.standard_price or 0.0,
            'move_type': 'one',
        }

        else:
            return super(exchange_order, self)._prepare_order_line_move(cr, uid, order, line, picking_id,product_qty ,context=None)

    def _prepare_order_picking(self, cr, uid, order, context=None):
        """
        Prepare the dict of values to create the new picking for a
        exchange order. This method may be overridden to implement custom
        picking generation (making sure to call super() to establish a clean extension chain).
        @param browse_record order: exchange.order.line record to invoice
        @return: dict of values to create() the picking
        """

        if order.ttype == 'other' and order.maintenance == True:
            return {
            'name': '/',
            'origin': order.name,
            'request': order.id,
            'date': order.date_order,
            'type': 'out',
            'state': 'draft',
            'exchange_id': order.id,
            'note': order.notes,
            'department_id':order.department_id.id,
            #'stock_journal_id':order.stock_journal_id and order.stock_journal_id.id,
            'invoice_state': 'none',
            'maintenance': True,
        }
        else:
            return super(exchange_order, self)._prepare_order_picking(cr, uid, order, context=None)

    def write(self,cr,uid, ids, vals, context=None):
        """
        override write to change state of job_id
        """
        exchange_line_obj = self.pool.get('exchange.order.line')
        exchange_move_line_obj = self.pool.get('exchange.move.fuel')
        for rec in self.browse(cr, uid, ids,context):
            if rec.maintenance:
                if 'maintenance_department_id' in vals:
                    onchange_vals = self.onchange_maintenance_department_id(cr, uid, [rec.id], vals['maintenance_department_id'])['value']
                    vals.update(onchange_vals)

                if 'order_line' in vals and rec.maintenance:
                    rec_line = []
                    domain = [('order_id','=',rec.id)]
                    for line in vals['order_line']:
                        if line[1] != False: rec_line.append(line[1])
                    if rec_line:
                        domain.append(('id','not in',rec_line))
                    unlink_line = exchange_line_obj.search(cr, uid, domain,context=context)
                    if unlink_line:
                        exchange_line_obj.unlink(cr, uid, unlink_line,context)
                if 'exchange_move_line' in vals and rec.maintenance:
                    rec_move_line = []
                    domain = [('exchange_id','=',rec.id)]
                    for line in vals['exchange_move_line']:
                        if line[1] != False: rec_move_line.append(line[1])
                    if rec_move_line:
                        domain.append(('id','not in',rec_move_line))
                    unlink_lines = exchange_move_line_obj.search(cr, uid, domain,context=context)
                    if unlink_lines:
                        exchange_move_line_obj.unlink(cr, uid, unlink_lines,context)
                
                if 'maintenace_exchange_type' in vals:
                    onchange_valss = self.onchange_maintenace_exchange_type(cr, uid, [rec.id], vals['maintenace_exchange_type'])['value']
                    vals.update(onchange_valss)


                super(exchange_order, self).write(cr, uid, [rec.id], vals, context)
                
                if 'state' in vals and vals['state'] == 'done' and rec.job_id:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'maintenance.job', rec.job_id.id, 'recieved', cr)
        
            else:
                super(exchange_order, self).write(cr, uid, ids, vals, context)
        return True

    def create(self, cr, uid, vals, context={}):
        """
        inherit to add constrain of order line
        @param vals :Dictionary of values
        @return : super of exchange_order_line
        """
        if context is None:
            context = {} 
        if 'maintenance' in vals and vals['maintenance'] == True:
            if 'maintenance_department_id' in vals:
                onchange_vals = self.onchange_maintenance_department_id(cr, uid, [], vals['maintenance_department_id'], context=context)['value']
                vals.update(onchange_vals)
        return super(exchange_order, self).create(cr, uid,  vals, context=context)

    def action_cancel_order(self, cr, uid, ids, context=None):
        """ 
        Workflow function Changes order state to cancel.
        @return: True
        """
        write_boolean = super(exchange_order, self).action_cancel_order(cr, uid, ids, context)
        for rec in self.browse(cr, uid, ids, context):
            if rec.maintenance and rec.job_id:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'maintenance.job', rec.job_id.id, 'cancel', cr)
        return write_boolean


    def _check_exchange_move_quantity(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):

            if rec.maintenance and rec.state == 'done' and rec.maintenace_exchange_type == 'move':
                exchange_move_line_obj = self.pool.get('exchange.move.fuel')
                for line in rec.order_line:
                    idss =  exchange_move_line_obj.search(cr, uid, [('exchange_line_id','=',line.id),
                        ('exchange_id','=',rec.id)])
                    qty = 0
                    if idss:
                        for x in exchange_move_line_obj.browse(cr, uid, idss):
                           qty += x.product_qty
                    if qty > (line.delivered_qty - line.returned_qty):
                        raise osv.except_osv(_(''), _("Total Quantity in Vehicle data For the spare %s is more than the spare's exchanged quantity ")%(line.product_id.name))

            

        return True

    _constraints = [
        (_check_exchange_move_quantity, _(''), []),
        (_check_spaces_mission, '', []),
    ]

# ----------------------------------------------------
# exchange_order_line
# ----------------------------------------------------
class exchange_order_line(osv.Model):

    _inherit = 'exchange.order.line'

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('request_hq', 'Exchange Request From HQ'),
        ('confirmed_oc', 'Waiting Branch Manager Approval'),
        ('confirmed', 'Waiting Department Approval'),
        ('category_manager', 'Waiting for category manager'),
        ('approved', 'Approved'),
        ('approved_oc', 'Watiting Picking'),
        ('picking', 'Picking'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ]

    _columns = {
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, select=True),
        'maintenance_spare_id': fields.many2one('maintenance.spare'),
        'returned_qty': fields.float('Returned Quantity'),
        }

    _defaults = {
        'returned_qty': 0.0,
    }


    def create(self, cr, uid, vals, context={}):
        """
        inherit to add constrain of order line
        @param vals :Dictionary of values
        @return : super of exchange_order_line
        """
        if context is None:
            context = {} 
        state = self.pool.get('exchange.order').browse(cr, uid, vals['order_id']).state
        context['maintenance'] = True
        return super(exchange_order_line, self).create(cr, uid,  vals, context=context)


#----------------------------------------------------------
# Stock Picking (Inherit)
#----------------------------------------------------------
class stock_picking(osv.Model):
    _inherit = "stock.picking"
    
    _columns = {
        'maintenance': fields.boolean('Maintenance'),
        'job_id': fields.many2one('maintenance.job', 'Maintenance Job'),
    }
    

    _defaults = {
        'maintenance': 0,
        'job_id': False,
    }


    def action_done(self, cr, uid, ids, context=None):
        """
        Method was overrided to cancel related job after spares recieved

        @return:True
        """

        super(stock_picking, self).action_done(cr, uid, ids, context=None)
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.type == 'in' and pick.maintenance and pick.job_id and pick.job_id.state == 'return':
                if pick.job_id.picking_id.state == 'done':
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'maintenance.job', pick.job_id.id, 'cancel', cr)

            if pick.type == 'in' and pick.maintenance and pick.exchange_id:
                exchange_obj = self.pool.get('exchange.order')
                exchange_line_obj = self.pool.get('exchange.order.line')
                stock_move_obj = self.pool.get('stock.move')
                exchange_line_ids = [move.exchange_line_id.id for move in pick.move_lines]
                if exchange_line_ids:
                    for line in exchange_line_obj.browse(cr, uid, exchange_line_ids):
                        move_ids = stock_move_obj.search(cr, uid, [('exchange_line_id','=',line.id),('state','=','done'),
                            ('type','=','in')])
                        if move_ids:
                            qty = 0.0
                            for move in stock_move_obj.browse(cr, uid, move_ids):
                                qty += move.product_qty * move.product_uom.factor

                        ## update returned quantity in exchange line with qty
                        exchange_line_obj.write(cr, uid, [line.id], {'returned_qty': qty})
                        ## update exchange order to check constarints related to returned_qty
                        exchange_obj.write(cr, uid, [line.order_id.id], {})




        return True

    

#----------------------------------------------------------
# Stock Piching in (Inherit)
#----------------------------------------------------------
class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    
    
    _columns = {
        'maintenance': fields.boolean('Maintenance'),
        'job_id': fields.many2one('maintenance.job', 'Maintenance Job'),
        'exchange_id': fields.many2one('exchange.order', 'Exchange Order', readonly = True,
            ondelete='set null', select=True),
    }

    _defaults = {
        'maintenance': 0,
        'job_id': False,
        'exchange_id': False,
    }


#----------------------------------------------------------
# Stock Piching out (Inherit)
#----------------------------------------------------------
class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    
    _columns = {
        'maintenance': fields.boolean('Maintenance'),
    }
    
    _defaults = {
        'maintenance': 0,
    }


#----------------------------------------------------------
# Stock Move
#----------------------------------------------------------
class stock_move(osv.osv):
    _inherit = "stock.move"

    _columns = {
        'maintenance': fields.boolean('Maintenance'),
    }

    def _default_location_destination(self, cr, uid, context=None):
        """ Gets default address of partner for destination location
        @return: Address id or False
        """
        mod_obj = self.pool.get('ir.model.data')
        picking_type = context.get('picking_type')
        location_id = False
        if context is None:
            context = {}
        if 'default_maintenance' in context and context['default_maintenance'] == True:
            return False
        else:
            return super(stock_move, self)._default_location_destination(cr, uid, context)

    def _default_location_source(self, cr, uid, context=None):
        """ Gets default address of partner for source location
        @return: Address id or False
        """
        mod_obj = self.pool.get('ir.model.data')
        picking_type = context.get('picking_type')
        location_id = False

        if context is None:
            context = {}

        if 'default_maintenance' in context and context['default_maintenance'] == True:
            return False
        else:
            return super(stock_move, self)._default_location_source(cr, uid, context)

    _defaults = {
        'maintenance': 0,
        'location_id': _default_location_source,
        'location_dest_id': _default_location_destination,
    }


# ----------------------------------------------------
# create_purchase_requestion inherit
# ----------------------------------------------------
class create_purchase_requestion(osv.osv_memory):
    """ 
    class to manage the wizard of creating the purchase requestion """

    _inherit = 'create.purchase.requestion'

    def create_purchase_requestion_maintenance(self, cr, uid, ids, context=None):
        #TODO change the state of the purchase requestion to quotes and let the wizard in specefic state
        """
        Button function to create purchase requestion from the
 
        @return: Purchase Requestion Id
        """        
        purchase_requestion_obj = self.pool.get('ireq.m')
        exchange = self.pool.get('exchange.order').browse(cr, uid, context['active_id'])
        requestion_lines_obj = self.pool.get('ireq.products')
        prod = self.pool.get('product.product')
        wf_service = netsvc.LocalService("workflow")
        if exchange.purchase_requestion_id:
                raise  osv.except_osv(_('Warning'), _('You allredy create a purchase requestion for this exchange order '))
        for wizard in self.browse(cr, uid, ids):
            for line in wizard.products_ids:
                context['uom'] = line.stock_exchange_line.product_uom.id
                context['location'] = exchange.location_dest_id.id
                product = self.pool.get('product.product').browse(cr, uid, line.product_id.id, context=context)
                if (product.qty_available - line.stock_exchange_line.product_qty) > product.mini_amount:
                      raise  osv.except_osv(_('Error'), _('You can not create a purchase requestion for the product %s, available quantity %s more than minimum amount %s')%(product.name,product.qty_available,product.mini_amount))

            requestion_id =  purchase_requestion_obj.create(cr, uid, {'company_id': exchange.company_id.id,
                                                                      'user': context['uid'],
                                                                      #'cat_id':exchange.category_id.id,
                                                                      'ir_ref': exchange.name, 
                                                                      'exchane_order_id':[(4, exchange.id)],
                                                                      'spare_order':True,
                                                                      'department_id':exchange.department_id.id,
                                                                      'state':'draft',
                                                                      'location_id': exchange.location_dest_id.id,})

            for wizard_lines in wizard.products_ids:
                product = prod.browse(cr, uid,wizard_lines.product_id.id)
                requestion_lines_obj.create(cr, uid, {'pr_rq_id':requestion_id,
                                                      'product_id': wizard_lines.product_id.id,
                                                      'name': product.name,
                                                      'product_qty': wizard_lines.product_qty,
                                                      'product_uom': product.uom_po_id.id, 
                                                      'desc': wizard_lines.description,})
         
        exchange.write({'purchase_requestion_id':requestion_id,'state' : 'wait_purchase'})
        exchange.job_id.write({'purchase_requestion_id':requestion_id}) 
        #wf_service.trg_validate(uid, 'ireq.m', requestion_id, 'draft_confirm', cr)
        return requestion_id


# ----------------------------------------------------
# exchange_partial_picking inherit
# ----------------------------------------------------
class exchange_partial_picking(osv.osv_memory):
    _inherit = "exchange.partial.picking"

    def do_partial(self, cr, uid, ids, context=None):
        """ 
        Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, partner_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        wf_service = netsvc.LocalService("workflow")
        super_return = super(exchange_partial_picking, self).do_partial(cr, uid, ids, context=None)
        maintenance_spare_obj = self.pool.get('maintenance.spare')
        line_obj = self.pool.get('exchange.order.line')
        exchange_order_obj = self.pool.get('exchange.order')

        for rec in self.browse(cr, uid, ids):
            lines = []
            spare_lines = []
            if rec.exchange_id.maintenance:
                if rec.exchange_id.picking_ids:
                    for line in rec.move_ids:
                        if rec.exchange_id.job_id:
                            if line.move_id.maintenance_spare_id:
                                maintenance_spare_obj.write(cr, uid, [line.move_id.maintenance_spare_id.id], 
                                    {'recieved_quantity':line.quantity})
                            else:
                                spare_lines.append({'product_id':line.product_id.id ,'quantity': line.move_id.product_qty, 
                                    'recieved_quantity':line.quantity, 'job_id': rec.exchange_id.job_id.id})
                    for line_order in rec.exchange_id.order_line:
                        line_obj.write(cr, uid, [line_order.id], {'state' :'picking'})
                        if line_order.approved_qty - line_order.delivered_qty != 0:
                            lines_dict = {'product_id': line_order.product_id.id, 'product_qty': line_order.approved_qty - line_order.delivered_qty,
                              'approved_qty': line_order.approved_qty - line_order.delivered_qty, 'name': line_order.name,
                              'price_unit': line_order.price_unit,
                              'product_uom': line_order.product_uom.id, 'state': 'draft',
                              #'maintenance_spare_id': line.id,
                              }
                            lines.append([0, False, lines_dict])

                    exchange_order_obj.write(cr, uid, [rec.exchange_id.id], {})
                    if lines:
                        new_id = exchange_order_obj.create(
                            cr, uid, {'ttype': 'other', 'maintenance': True,
                                      'maintenance_department_id': rec.exchange_id.maintenance_department_id.id,
                                      'location_id': rec.exchange_id.maintenance_department_id.location_dest_id.id,
                                      'location_dest_id': rec.exchange_id.maintenance_department_id.stock_location_id.id,
                                      'department_id': rec.exchange_id.maintenance_department_id.department_id.id,
                                      'order_line': lines})
                        wf_service.trg_validate(uid, 'exchange.order', new_id, 'exchange_cancel', cr)
                        exchange_order_obj.write(cr, uid, [new_id], {'job_id':rec.exchange_id.job_id.id})
                    for picking in rec.exchange_id.picking_ids:
                        wf_service.trg_validate(uid, 'stock.picking', picking.id, 'button_confirm', cr)
                        picking.force_assign()
                        wf_service.trg_validate(uid, 'stock.picking', picking.id, 'button_done', cr)

                    ##### when add new spare line from the exchange record 
                    ### in this case we should create maintenace spare line in job record
                    if spare_lines:
                        for spare_line in spare_lines:
                            line_id = self.pool.get('maintenance.spare').create(cr, uid, spare_line)
                            exchange_line_ids = line_obj.search(cr, uid, [('order_id','=',rec.exchange_id.id),
                                ('product_id','=',spare_line['product_id'])])
                            if exchange_line_ids:
                                line_obj.write(cr, uid, [exchange_line_ids[0]],{'maintenance_spare_id':line_id})


        return super_return

# ----------------------------------------------------
# Stock Inventory (Inherit)
# ----------------------------------------------------
class stock_inventory(osv.osv):
    _inherit = "stock.inventory"
    _columns = {
        'maintenance': fields.boolean('Maintenance'),
    }

    _defaults = {
        'maintenance': False,
        }



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
            if not inv.inventory_line_id:
                raise  osv.except_osv(_('Warning'), _('You can not confirm record without products'))  
        return super(stock_inventory, self).action_confirm(cr, uid, ids, context)

    def write(self, cr, uid, ids, vals, context={}):
        """
        """
        if 'inventory_line_id' in vals :
            unlink_ids = [ x[1] for x in vals['inventory_line_id'] if x[0] == 2  ]
            if unlink_ids:
                self.pool.get('stock.inventory.line').unlink(cr, uid, unlink_ids, context)
        return super(stock_inventory, self).write(cr, uid, ids, vals, context)


# ----------------------------------------------------
# stock_inventory_line inherit
# ----------------------------------------------------
class stock_inventory_line(osv.osv):
    _inherit = "stock.inventory.line"

    _columns = {
        'maintenance': fields.boolean('Maintenance'),      
    }

    _defaults = {
        'maintenance': False,
        }

    def on_change_maintenance_product_id(self, cr, uid, ids, location_id, product, uom=False, to_date=False):
        """ Changes UoM and name if product_id changes.
        @param location_id: Location id
        @param product: Changed product_id
        @param uom: UoM product
        @return:  Dictionary of changed values
        """
        if not product:
            return {'value': {'product_qty': 0.0, 'product_uom': False, 'prod_lot_id': False}}
        obj_product = self.pool.get('product.product').browse(cr, uid, product)
        uom = uom or obj_product.uom_id.id
        amount = self.pool.get('stock.location')._product_get(cr, uid, location_id, [product], {'uom': uom, 'to_date': to_date, 'compute_child': False})[product]
        result = {'product_qty': amount, 'product_uom': uom, 'prod_lot_id': False}
        return {'value': result}


   

#----------------------------------------------------------
# Exchange Move Fuel
#----------------------------------------------------------
class stock_picking_fuel(osv.osv):
    _name = "exchange.move.fuel"

    _columns = {
        'exchange_id': fields.many2one('exchange.order', 'Exchange', ondelete="cascade"),
        'name': fields.related('exchange_id', 'name', string='Process Referance', type="char"),
        'product_id': fields.many2one('product.product', 'Spare'),
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle'),
        'exchange_line_id': fields.many2one('exchange.order.line', 'Exchange Line'),
        #'location_id': fields.many2one('stock.location', 'Location',),
        #'location_dest_id': fields.many2one('stock.location', 'Dest. Location'),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
    }


    def onchange_product(self,cr , uid, ids, product_id, exchange_id, context={}):
        """
        """
        vals = {'exchange_line_id': False}
        if product_id and exchange_id:
            exchange_line = self.pool.get('exchange.order.line').search(cr, uid, [('order_id','=',exchange_id), 
                ('product_id','=',product_id)])
            if exchange_line:
                vals = {'exchange_line_id': exchange_line[0]}
        return {'value': vals}



    def create(self, cr, uid, vals, context={}):
        """
        overwrite create method to change related vehicle fieldsvals['product_qty_before']
        @return: super method
        """
        product_id = vals['product_id']
        #vals['product_uom'] = self.onchange_product(cr, uid, [],product_id )['value']['product_uom']

        return super(stock_picking_fuel, self).create(cr, uid, vals, context)


    def write(self, cr, uid, ids, vals, context={}):
        """
        overwrite write method to change related vehicle fields
        @return: super method
        """
        for rec in self.browse(cr, uid, ids, context):
            
            product_id = 'product_id' in vals and vals['product_id'] or rec.product_id.id
            #vals['product_uom'] = self.onchange_product(cr, uid, [],product_id )['value']['product_uom']

        return super(stock_picking_fuel, self).write(cr, uid, ids, vals, context)

    
    def _check_unique(self, cr, uid, ids, context=None):
        """
        """
        for rec in self.browse(cr, uid, ids, context=context):
            idss = self.search(cr, uid, [('vehicle_id','=',rec.vehicle_id.id),('product_id','=',rec.product_id.id),
             ('exchange_id','=',rec.exchange_id.id),('id','!=',rec.id)])
            if idss :
                raise osv.except_osv(_(''), _("Vehicle and Spare should be unique "))

        return True



    def _check_quantity(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.product_qty <= 0:
                raise osv.except_osv(_(''), _("Quantity should be more than Zero "))

        return True



    _constraints = [
        (_check_unique, _(''), []),
        (_check_quantity, _(''), []),
        #(_check_location, _(''), ['location_id','location_dest_id']),
    ]


#----------------------------------------------------------
# product_product (Inherit)
#----------------------------------------------------------


class product_product(osv.Model):

    _inherit = "product.product"


    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        ids = []
        if 'exchange_move' in context and context['exchange_move'] != False:
            idss = []
            exchange_obj = self.pool.get('exchange.order')
            exchange_line_obj = self.pool.get('exchange.order.line')

            if 'exchange_line' in context and context['exchange_line'] != False:
                exchange_line_ids = [x[1] for x in context['exchange_line']]
                for line in exchange_line_obj.browse(cr, uid, exchange_line_ids):
                    if line.delivered_qty - line.returned_qty > 0.0:
                        idss.append(line.product_id.id)
                

            args.append(('id', 'in', idss))

        return super(product_product, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)



#----------------------------------------------------------
# fleet_vehicle (Inherit)
#----------------------------------------------------------

class fleet_vehicle(osv.Model):
    _inherit = "fleet.vehicle"
    _columns = {
        'maintenance_move_spare_ids': fields.one2many('exchange.move.fuel', 'vehicle_id', string="Movable Spares"),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
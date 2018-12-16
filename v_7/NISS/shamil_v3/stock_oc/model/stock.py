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


#----------------------------------------------------------
# Stock inventory  (Inherit)
#----------------------------------------------------------
class stock_inventory(osv.osv):
    _inherit = "stock.inventory"

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
                     ]
    _columns = {
           'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),

    }
    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,
    }


# ----------------------------------------------------
# Exchange Order inherit
# ----------------------------------------------------

class exchange_order(osv.Model):
    _inherit = 'exchange.order'

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
    ]

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

    def check_oc_to_hq(self, cr, uid, ids,name, args, context=None):
        """ wf_service
        Changes order state to confirm.
        @return: True
        """
        res = {}
        for order in self.browse(cr, uid, ids, context=context): 
            if order.ttype == 'other' and order.executing_stock == 'hq' and order.executing_agency not in ['admin','tech','arms'] and order.state == 'request_hq': 
                res[order.id] = True
            elif order.ttype == 'other' and order.executing_agency in ['admin','tech','arms'] and order.state == 'draft':
                    res[order.id] = True
            else:
                res[order.id] = False
        return res

    def check_oc_to_hq_app(self, cr, uid, ids,name, args, context=None):
        """ wf_service
        Changes order state to confirm.
        @return: True
        """
        res = {}
        for order in self.browse(cr, uid, ids, context=context): 
            if order.ttype == 'other' and order.executing_agency in ['admin','tech','arms'] and order.state == 'approved': 
                res[order.id] = True
            elif order.ttype == 'other' and order.executing_agency in ['admin','tech','arms'] and order.state == 'approved':
                res[order.id] = True
            else:
                res[order.id] = False
        return res

    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),
        'executing_stock':fields.selection([('company_stock','My Company Stock'),
                                            ('hq','HQ Stock')], 'Executing Stock', select=True),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, select=True),
        'is_oc_hq': fields.function(check_oc_to_hq, type="boolean", string="HQ Request"),
        'is_oc_hq_app': fields.function(check_oc_to_hq_app, type="boolean", string="HQ Request App"),
        'recieved_location_id': fields.many2one('stock.location', 'Recipient Location'),
        }

    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,
        'executing_stock' : 'company_stock',
            }

    def _prepare_order_picking(self, cr, uid, order, context=None):
        """
        Prepare the dict of values to create the new picking for a
        exchange order. This method may be overridden to implement custom
        picking generation (making sure to call super() to establish a clean extension chain).
        @param browse_record order: exchange.order.line record to invoice
        @return: dict of values to create() the picking
        """
        vals = super(exchange_order, self)._prepare_order_picking(cr, uid, order, context=context)
        vals['executing_stock'] = order.executing_stock
        vals['executing_agency'] = order.executing_agency
        return vals

    def action_request_order(self, cr, uid, ids, context=None):
        """ wf_service
        Changes order state to confirm.
        @return: True
        """
        for order in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, ids, {'executing_stock': False})
            if not order.order_line:
                raise osv.except_osv(_('Error !'), _('You can not order without order lines.'))  
            x = 0
            
            for line in order.order_line:
                if line.product_id.asset==True:
                    x+=1
            
            if x>0 and order.custody==False:
                self.write(cr, uid, ids, {'custody':'True'})

            self.changes_state(cr, uid, ids, {'state': 'confirmed_oc'},context=context)
        return True

    def check_request_hq(self, cr, uid, ids, context=None):
        """
        Condition Workflow function.
        @return: boolean 
        """
        for order in self.browse(cr, uid, ids, context=context):
            if order.ttype == "other" and order.executing_stock == 'hq':
                return True
        return False

    def action_process_oc(self, cr, uid, ids, context={}):
        """
        action process for OC
        """

        return self.action_process(cr, uid, ids, context=context)

    def action_approve_order_oc(self, cr, uid, ids, context=None):
        """ 
        Changes order state to approved.
        @return: True
        """
        self.changes_state(cr, uid, ids,{'state': 'approved_oc'},context=context)
        self.write(cr, uid, ids, {'date_approve': time.strftime('%Y-%m-%d')})
        return True

    def check_location_dest_id(self, cr, uid, ids, context={}):
        """Method that checks if the enterd persentage is less than zero it raise .
           @return: Boolean True or False
        """

        for order in self.browse(cr, uid, ids):
            if order.ttype == 'other':
                if order.state == 'approved' and not order.location_dest_id:
                    raise osv.except_osv(_('Error'), _('Please select Location'))
        return True

    _constraints = [
       (check_location_dest_id, '', []),       
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
        }

#----------------------------------------------------------
# Stock Picking (Inherit)
#----------------------------------------------------------
class stock_picking(osv.Model):
    _inherit = "stock.picking"

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
                     ]
    
    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),
        'executing_stock': fields.related('exchange_id','executing_stock',type="selection",string="Executing Stock",store=True),
    }
    

    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,
    }


    def action_done(self, cr, uid, ids, context=None):
        """
        Makes the move done and if all moves are done, it will finish the picking.

        @return:True
        """
        super(stock_picking, self).action_done(cr, uid, ids, context=None)
        moves=[]
        stock_move_obj = self.pool.get('stock.move')
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.type == 'out' and pick.executing_agency not in ('admin','tech','arms') and pick.executing_stock == 'hq':
                stock_dict = self._prepare_internal_picking(cr, uid, pick, context=context)
                pick_id = self.create(cr, uid, stock_dict, context=context)
                for move in pick.move_lines:
                    lines_dict = self._prepare_internal_picking_line_move(cr, uid, move, pick_id, context=context)
                    stock_move_obj.create(cr, uid, lines_dict, context=context)
        return True

    def _prepare_internal_picking_line_move(self, cr, uid, line, picking_id ,context=None):
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
        return {
            'name': line.name[:250],
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'product_qty': line.product_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': line.product_qty,
            'product_uos':  line.product_uom.id,
            'location_id': line.picking_id.location_dest_id.id ,
            #'location_dest_id': (order.location_id and order.location_id.id) or order.stock_journal_id.location_id.id,
            'location_dest_id': line.picking_id.exchange_id.recieved_location_id.id,
            'exchange_line_id': False,
            'tracking_id': False,
            'state': 'draft',
            #'note': line.notes,
            'price_unit': line.price_unit or 0.0,
            'move_type': 'one',
        }

    def _prepare_internal_picking(self, cr, uid, pick, context=None):
        """
        Prepare the dict of values to create the new picking for a
        exchange order. This method may be overridden to implement custom
        picking generation (making sure to call super() to establish a clean extension chain).
        @param browse_record order: exchange.order.line record to invoice
        @return: dict of values to create() the picking
        """
        return {
            'name': '/',
            'origin': pick.name,
            'location_id': pick.location_dest_id.id,
            'request': False,
            'date': False,
            'type': 'internal',
            'state': 'draft',
            'exchange_id': False,
            'note': pick.note,
            'department_id':False,
            #'stock_journal_id':pick.stock_journal_id and order.stock_journal_id.id,
            'stock_journal_id': False,
            'invoice_state': 'none',
            'move_type': 'one',
            'executing_agency': pick.executing_agency,
        }

    

#----------------------------------------------------------
# Stock Piching in (Inherit)
#----------------------------------------------------------
class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
                     ]
    
    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),

    }

    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,
    }


    def create(self, cr, user, vals, context=None):
        """
        Override create to call create of stock.picking
        """
        picking_obj = self.pool.get('stock.picking')
        seq_obj_name =  self._name
        vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        new_id = picking_obj.create(cr, user, vals, context)
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        """
        Override write to call write of stock.picking
        """
        picking_obj = self.pool.get('stock.picking')
        write_boolean = picking_obj.write(cr, uid, ids, vals, context)
        return write_boolean

#----------------------------------------------------------
# Stock Piching out (Inherit)
#----------------------------------------------------------
class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
                     ]
    
    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),
        'executing_stock': fields.related('exchange_id','executing_stock',type="selection",string="Executing Stock" ,store=True),
    }
    
    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,
    }

    def create(self, cr, user, vals, context=None):
        """
        Override create to call create of stock.picking
        """
        picking_obj = self.pool.get('stock.picking')
        seq_obj_name =  self._name
        vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        new_id = picking_obj.create(cr, user, vals, context)
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        """
        Override write to call write of stock.picking
        """
        picking_obj = self.pool.get('stock.picking')
        write_boolean = picking_obj.write(cr, uid, ids, vals, context)
        return write_boolean


# ----------------------------------------------------
# Product category inherit
# ----------------------------------------------------
class product_category(osv.osv):
    _inherit = "product.category"

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
                     ]
    
    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'executing_agency', select=True , help='Select Department Which this user belongs to it'),

    }

    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,
    }



#----------------------------------------------------------
# stock_journal (Inherit)
#----------------------------------------------------------
class stock_journal(osv.Model):
    _inherit = 'stock.journal'

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
                     ]
    

    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', select=True,help='Department Which this request will executed it'),
    }

    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,
    }

#----------------------------------------------------------
# stock_location (Inherit)
#----------------------------------------------------------
class stock_location(osv.Model):
    _inherit = 'stock.location'

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
        ('oc', 'Operation Corporation'),
                     ]
    

    _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', select=True,help='Department Which this request will executed it'),
    }

    _defaults = {
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,
    }
    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

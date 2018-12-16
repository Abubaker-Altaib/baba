# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import pytz
from openerp import SUPERUSER_ID
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv.orm import browse_record, browse_null
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools.float_utils import float_compare
from openerp.tools.safe_eval import safe_eval as eval

#-------------------------
#Inherit ireq_m
#-------------------------

class ireq_m(osv.osv):

    _inherit = "ireq.m"

    STATE_SELECTION = [
         ('draft', 'Draft Request'),
         ('wait_invoice','Wait invoice'),
         ('wait_accountant','Wait accountant'),
         ('wait_workshop','Wait workshop'),
         ('purchase_officer','Purchase Officer'),
         ('wait_purchase','wait purchase and supply'),
         ('purchase_done','Purchase Done'),
         ('spare_cancel','Cancelled'),

         ('in_progress','In Progress'),
         ('completed','Completed'),
         ('closed','Closed'),
         ('in_progress_quote','In Progress Quote'),
         ('wait_confirmed','Wait Confirmed'),
         ('completed_quote','Completed Quote'),
         ('closed_quote','Closed Quote'),
         ('in_progress_fin_request','In Progress Financial Request'),
         ('completed_fin_request','Completed Financial Request'),
         ('closed_fin_request','Closed Financial Request'),
         ('done','Done'),
         ('cancel', 'Cancelled')]

    _columns = {
            'state': fields.selection(STATE_SELECTION, 'Status', readonly=True, select=True),
            'spare_order': fields.boolean('order for spare purchase'),
            'q_ids':fields.one2many('pur.quote', 'pq_ir_ref' ,'Quotes',readonly=True, states={'in_progress_quote':[('readonly',False)],'wait_invoice':[('readonly',False)]}),
            'location_id': fields.many2one('stock.location', 'Location',domain=[('usage','<>','view')]),
            'hq': fields.boolean("HQ"),
            'picking_id':fields.many2one('stock.picking', 'Stock picking'),
            'purchase_id':fields.many2one('purchase.order', 'Purchase order'),
            }

    def _default_hq(self,cr,uid,context=None):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        if user.company_id.hq:
            hq = True
        else:
            hq = False
        return hq

    _defaults ={
    'hq':_default_hq,
    'spare_order' : False,
        }

    def create(self, cr, user, vals, context=None):
        """ 
        Override to edit the name field by a new sequence. 
 
        @return: new object id 
        """
        if 'spare_order' in vals and vals['spare_order'] == True:
            seq = self.pool.get('ir.sequence').next_by_code(cr, user, 'spare.purchase.order')
            vals['name'] = seq
            if not seq:
                raise  osv.except_osv(_('Warning'), _('No sequence defined!\nPleas contact administartor to configue sequence with code \'spare.purchase.order\'') )
        return super(ireq_m, self).create(cr, user, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        """ 
        Ovrride to add constain on deleting the records. 

        @return: super unlink method
        """
        if context is None:
            context = {}
        if [ir for ir in self.browse(cr, uid, ids, context=context) if ir.state not in ['draft'] and ir.spare_order]:
            raise osv.except_osv(_('Invalid action !'), _('You cannot remove spare purchase order that is not in draft state !'))
        return super(ireq_m, self).unlink(cr, uid, ids, context=context)

    def spare_cancel(self,cr,uid,ids,context=None):
        """ 
        Workflow function changes order state to spare_cancel.

        @return: True 
        """

        exchange = self.pool.get('exchange.order')
        wf_service = netsvc.LocalService("workflow")
        for rec in self.browse(cr , uid ,ids):
            exchange_ref = rec.ir_ref
            exchange_id = exchange.search(cr , uid , [('name' , '=' , exchange_ref)])
            for exchange_record in exchange.browse(cr ,uid , exchange_id):
                wf_service.trg_validate(uid, 'exchange.order', exchange_record.id, 'exchange_cancel', cr)
            
        return self.write(cr, uid, ids, {'state':'spare_cancel'}, context=context)

    def wait_invoice(self,cr,uid,ids,context=None):
        """ 
        Workflow function changes order state to wait_invoice.

        @return: True 
        """
        if [ir for ir in self.browse(cr, uid, ids) if ir.pro_ids ]:
            self.write(cr, uid, ids, {'state':'wait_invoice'}, context=context)
        else:
            raise osv.except_osv( _('No Products !'), _('Please make sure you fill the products ..'))
        for req in self.browse(cr, uid, ids):
            for line in req.pro_ids:
                if line.product_qty == 0.0:
                    raise osv.except_osv( _('Zero Products quantity !'), _('Please make sure you fill the products quantity..'))
        return True

    def check_spare_invoice(self, cr ,uid ,ids , context=None):
        
        
        """ 
        Check That there is one quote Approved
        """
                
        for rec in self.browse(cr , uid ,ids):
            approved=False
            for quote in rec.q_ids:
                if quote.state == 'done':
                    approved=True
            if not approved:
               raise osv.except_osv( _('No approved Invoice!'), _('There is No Invoice approved.'))
               return False
        
        return True

    def check_invoice_complete(self, cr ,uid ,ids , context=None):
        
        
        """ 
        Check That all quote in confirmed or cancel state
        """
                
        for rec in self.browse(cr , uid ,ids) :
            if not rec.q_ids:
                raise osv.except_osv( _('No Invoice!'), _('There is no Invoices.'))
                return False
            confirm=False
            for quote in rec.q_ids:
                if quote.state in ('confirmed','done'):
                    confirm=True
                if quote.state == 'draft':
                   raise osv.except_osv(_('Warning!'),_('There is a Invoice still in Draft state.'))
                   return False
                if not confirm:
                    raise osv.except_osv(_('Warning!'),_('Not Confirmed Invoice!'))

        
        return True

    def create_spare_purchase_order(self,cr, uid, ids, context=None):
        """
        Creates purchase order or stock picking from quotation which is in done state 
        and then change the workflow state to purchase_officer.

        @return: Boolean True
        """
        print"================================================"
        picking_obj = self.pool.get('stock.picking')
        stock_move = self.pool.get('stock.move')
        purchase_obj = self.pool.get('purchase.order')
        rec=self.browse(cr, uid, ids)[0]
        qoute_ids = [qoute.id for qoute in rec.q_ids if qoute.state == 'done']
        if not rec.hq:
            if[ir for ir in self.browse(cr, uid, ids) if purchase_obj.search(cr, uid, [('ir_id','=',ir.id)])]:
                raise osv.except_osv(_('Purchase Order(s) Exsits !'), _('The Purchase Order(s) from this purchase requesition was alreadry created..\n Please .. Check Purchase Orders List ..'))
            else:
                purchase_id = self.pool.get('pur.quote').make_purchase_order(cr, uid, qoute_ids)
                print">>>>>>>>>>>>>>>>>>>>>>>>purchase_id",purchase_id
                purchase_obj.write(cr, uid, purchase_id, {'location_id':rec.location_id.id}, context=context)
            self.write(cr, uid, ids, {'state':'wait_purchase','purchase_id':purchase_id[0]}, context=context)                 
        else:
            quote=self.pool.get('pur.quote').browse(cr, uid, qoute_ids)[0]
            pick_id = picking_obj.create(cr, uid , {
                             'type': 'in',
                             'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
                             'origin': rec.name,
                             'date': rec.ir_date,
                             'executing_agency': rec.executing_agency,
                             'partner_id': quote.supplier_id.id,
                             'state': 'draft',
                             'department_id':rec.department_id.id,
                             'move_lines' : [],
                             'maintenance':True,
                            })
            print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>pick_id",pick_id
            for pro in quote.pq_pro_ids:
                move_id = stock_move.create(cr, uid, {
                    'name':pro.name,
                    'picking_id': pick_id,
                    'product_id': pro.product_id.id,
                    'product_qty': pro.product_qty,
                    'product_uos_qty': pro.product_id.uom_id.id,
                    'product_uos': pro.product_id.uom_id.id,
                    'product_uom': pro.product_id.uom_id.id,
                    'location_id': quote.supplier_id.property_stock_supplier.id,
                    'location_dest_id': rec.location_id.id,
                    'price_unit': pro.price_unit,
                    'state': 'draft',
                    'type':'in',   
                            }) 
            self.write(cr, uid, ids, {'picking_id':pick_id}, context=context)
            self.write(cr, uid, ids, {'state':'purchase_officer'}, context=context)
            print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>move_id",move_id
        return True

    def spare_purchase_order_done(self,cr, uid, ids, context=None):
        """
        make picking_id state to received.

        @return: Boolean True
        """
        exchange = self.pool.get('exchange.order')
        wf_service = netsvc.LocalService("workflow")
        for rec in self.browse(cr, uid, ids):
            if rec.hq and rec.picking_id:
                wf_service.trg_validate(uid, 'stock.picking', rec.picking_id.id, 'button_confirm', cr)
                wf_service.trg_validate(uid, 'stock.picking', rec.picking_id.id, 'button_done', cr)

                exchange_ref = rec.ir_ref
                exchange_id = exchange.search(cr , uid , [('name' , '=' , exchange_ref)])
                for exchange_record in exchange.browse(cr ,uid , exchange_id):
                    if exchange_record.state == 'wait_purchase' :
                        exchange.write(cr , uid , exchange_id , {'state' : 'goods_in_stock' })
        return self.write(cr, uid, ids, {'state':'purchase_done'}, context=context)



class qoute(osv.osv):
    _inherit = 'pur.quote'


    def create(self, cr, uid, vals, context=None):
        """ 
        Override to editing the name field by a new sequence.

        @return super create() method 
        """
        seq_obj = self.pool.get('ir.sequence')
        user_obj = self.pool.get('res.users')
        seq=False
        if vals.get('name', False) in ['/', False]:
            #Get the company only from user
            company_id = user_obj.browse(cr, uid, uid).company_id.id 
            ids = seq_obj.search(cr, uid, ['&',('code','=','spare.pur.quote'),('company_id','in',[company_id,False])])
            seq=seq_obj._next(cr, uid, ids, context)
            vals['name']=seq
            if not seq:
                raise  osv.except_osv(_('Warning'), _('No sequence defined!\nPleas contact administartor to configue sequence with code \'spare.pur.quote\' For Your company') )
        return super(qoute, self).create(cr, uid, vals, context=context)

    def spare_set_draft(self, cr, uid, ids, context=None): 
        """ 
        Changes order state to Draft.

        @return: True
        """
        for quote in self.browse(cr,uid,ids):
            rec_state = quote.pq_ir_ref.state
        if rec_state not in ["wait_workshop","purchase_officer","wait_purchase","purchase_done"] :
            if not len(ids):
                return False
            self.write(cr, uid, ids, {'state':'draft'}, context=context)
            wf_service = netsvc.LocalService("workflow")
            for s_id in ids:
                # Deleting the existing instance of workflow for PO
                wf_service.trg_delete(uid, 'pur.quote', s_id, cr)            
                wf_service.trg_create(uid, 'pur.quote', s_id, cr)
        else :
             raise osv.except_osv(_("Error"), _("You Can't Reset Quote After Approved The Winner Quote"))
        
        return True

    def quote_approved(self, cr, uid, ids,context=None): 
        """ 
        Workflow function changes quotation state to done, cancel all other quotations of the requisition
        and change the requisition state to wait_confirmed.

        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        internal_obj = self.pool.get('ireq.m')
        internal_products = self.pool.get('ireq.products')
        quote_obj = self.pool.get('pur.quote')
         
        for quote in self.browse(cr, uid, ids):
            self.write(cr, uid, ids, {'state':'done'})
            # For updating the internal requestion products prices
            for product in quote.pq_pro_ids:
                if product.req_product:
                    internal_products_ids = product.req_product.id
                else: 
                    internal_products_ids = internal_products.search(cr, uid, [('pr_rq_id', '=', quote.pq_ir_ref.id), ('product_id', '=', product.product_id.id)])
                internal_products_ids = internal_products.search(cr, uid, [('pr_rq_id', '=', quote.pq_ir_ref.id), ('product_id', '=', product.product_id.id)])
                internal_products.write(cr, uid, internal_products_ids, {'price_unit': product.price_unit })
            # For cancel all other quotes except this one                 
            quote_ids = quote_obj.search(cr, uid, [('pq_ir_ref', '=', quote.pq_ir_ref.id)])
            for created_quote in quote_ids:
                current_quote = quote_obj.browse(cr, uid, created_quote)
                if current_quote.id != quote.id:
                    quote_obj.write(cr, uid, created_quote, {'state':'cancel'})
            if quote.pq_ir_ref.hq:
                internal_obj.write(cr, uid, quote.pq_ir_ref.id, {'state':'wait_workshop'})
                wf_service.trg_validate(uid, 'ireq.m', quote.pq_ir_ref.id, 'to_workshop', cr) 
        return True

# ----------------------------------------------------
# Stock picking (Inherit)
# ----------------------------------------------------
class stock_picking(osv.Model):
    _inherit = "stock.picking"
    
    def action_done(self, cr, uid, ids, context=None):
        """
        Changes spare purchase order to done when done stock.picking(oc workflow)

        @return: True
        """
        internal_ids=[]
        internal_obj = self.pool.get('ireq.m')
        wf_service = netsvc.LocalService("workflow")
        exchange = self.pool.get('exchange.order')
        for pick in self.browse(cr, uid, ids, context=context):
            #CASE 1: Done the Spare Purchase Order(ireq.m) when done his picking from purchase ,OC Process
            if pick.purchase_id and pick.purchase_id.ir_id and not pick.purchase_id.ir_id.hq:
                wf_service.trg_validate(uid, 'ireq.m', pick.purchase_id.ir_id.id, 'purchase_done', cr)
            if pick.maintenance and pick.type == 'in':
                #CASE 2: Done the Spare Purchase Order(ireq.m) when done his picking ,HQ Process
                internal_ids = internal_obj.search(cr, uid, [('picking_id', '=', pick.id),('spare_order','=',True)])
                if internal_ids:
                    for ireq in internal_ids:
                        wf_service.trg_validate(uid, 'ireq.m', ireq, 'purchase_done', cr)
                #CASE 3: Done the Spare Purchase Order(ireq.m) when done his partial picking ,HQ Process
                picks_ids = self.search(cr, uid, [('backorder_id', '=', pick.id),('maintenance','=',True),('type','=','in')])
                if picks_ids:
                    ireq_ids = internal_obj.search(cr, uid, [('picking_id', 'in', picks_ids),('spare_order','=',True)])
                    for partial in internal_obj.browse(cr ,uid , ireq_ids):
                        exchange_ref = partial.ir_ref
                        exchange_id = exchange.search(cr , uid , [('name' , '=' , exchange_ref)])
                        for exchange_record in exchange.browse(cr ,uid , exchange_id):
                            if exchange_record.state == 'wait_purchase' :
                                exchange.write(cr , uid , exchange_id , {'state' : 'goods_in_stock' })
                        wf_service.trg_validate(uid, 'ireq.m', partial.id, 'purchase_done_partial', cr) 
        return super(stock_picking, self).action_done(cr, uid, ids, context=context)

# ----------------------------------------------------
# create partial picking (Inherit)
# ----------------------------------------------------
class create_partial_picking(osv.osv_memory):
    _inherit = 'create.partial.picking'

    def create_partial_picking(self, cr, uid, ids, context=None):
        """
        Inherit to Add maintenance = True in picking
        to show it in maintenance picking in view
        """
        if context == None:
            context = {}
        order_obj = self.pool.get('purchase.order')
        order_line_obj = self.pool.get('purchase.order.line')
        partial_move_obj = self.pool.get('create.partial.move')
        picking_obj = self.pool.get('stock.picking')
        stock_move = self.pool.get('stock.move')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        for order in self.browse(cr,uid,ids):
            if order.order_id.ir_id and order.order_id.ir_id.spare_order:
                if not order.order_id.partner_id.property_stock_supplier:
                    raise osv.except_osv(_('No location !'), _("Please add 'supplier location' in the supplier"))
                if not order.products_ids:
                    raise osv.except_osv(('No Products !'), ("You can not Create Picking Without Products"))
                if order.order_id.purchase_type == 'foreign' :
                    if order.order_id.clearance_ids not in []:
                       for clearnace in order.order_id.clearance_ids:
                            if clearnace.state not in ['done','cancel']:
                                raise osv.except_osv(_('not complete process!'), _(' you have clearance that not complete yet..'))         
                picking_data = {
                            'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
                            'purchase_id' : order.order_id.id,
                            'origin': order.order_id.name,
                            'date': time.strftime('%Y-%m-%d'),
                            'department_id' : order.order_id.department_id.id,
                            'partner_id': order.order_id.partner_id.id,
                            'invoice_state':'none',
                            'type': 'in',
                            'company_id': order.order_id.company_id.id,
                            'move_lines' : [],
                            'maintenance':True,
                                  }
                picking_id = picking_obj.create(cr, uid, picking_data)
                todo_moves = []
                all_the_new_quantity = 0.0
                wf_service = netsvc.LocalService("workflow")
                for move_line in order.products_ids:
                    new_qty = move_line.desired_qty
                    all_the_new_quantity += new_qty
                    
                    if not move_line.product_id:
                        continue
                    if move_line.product_id.type in ('product', 'consu'):
                        move_data = {
                            'name': move_line.product_id.name or '',
                            'product_id': move_line.product_id.id,
                            'product_qty':  move_line.desired_qty,
                            'product_uos_qty': move_line.desired_qty,
                            'product_uom': move_line.product_id.product_tmpl_id.uom_id.id,
                            'product_uos': move_line.product_id.product_tmpl_id.uos_id.id,
                            'date': time.strftime('%Y-%m-%d'),
                            'date_expected': time.strftime('%Y-%m-%d'),
                            'location_id': order.order_id.partner_id.property_stock_supplier.id,
                            'location_dest_id': order.order_id.location_id.id,
                            'picking_id': picking_id,
                            'partner_id': order.order_id.partner_id.id,
                            'state': 'draft',
                            'type':'in',
                            'company_id': order.order_id.company_id.id,
                            'purchase_line_id' : move_line.order_product_id.id,
                            'price_unit': move_line.price_unit
                              }
                        move_id = stock_move.create(cr,uid,move_data)
                        todo_moves.append(move_id)
                                          
                stock_move.action_confirm(cr, uid, todo_moves)
                stock_move.force_assign(cr, uid, todo_moves)
                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
                self.update_quantities(cr,uid,ids,picking_id,context)
            else:
                super(create_partial_picking, self).create_partial_picking(cr, uid, ids, context=context)
        return True



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

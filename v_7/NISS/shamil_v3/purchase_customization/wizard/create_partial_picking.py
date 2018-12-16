# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

# how can we use the existing things to make the changes of the code 
from openerp.osv import fields, osv
import time
import netsvc
from tools.translate import _

class create_partial_picking(osv.osv_memory):
    _description='Create Partial Picking'
    _name = 'create.partial.picking'
    _columns = {
                'order_id': fields.many2one('purchase.order', 'Purchase Order', readonly=True),
                'current_date': fields.date('Current Date', readonly=True),
                'products_ids':fields.one2many('create.partial.move', 'wizard_id' , 'Products'),                
                }
    
    _defaults = {
                'order_id':lambda cr,uid,ids,context:context['active_id'],
                'current_date': lambda *a: time.strftime('%Y-%m-%d'),
                }
    
    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}

        order_obj = self.pool.get('purchase.order')
        res ={}
        order_ids = context.get('active_ids', [])
        if not order_ids:
            return res

        result = []
        for req in order_obj.browse(cr, uid, order_ids, context=context):

            for product in req.order_line:
                if product.all_quantity_picking:
                    continue
                result.append(self.__create_partial_purchase_order_line(product))
        res.update({'products_ids': result,})
        if 'current_date' in fields:
            res.update({'order_id' : req.id ,'current_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return res


    def __create_partial_purchase_order_line(self, product):
        product_memory = {
            'product_id' : product.product_id.id,
            'product_qty':product.product_qty,
            'price_unit' : product.price_unit,
            'price_unit_total' : (product.product_qty * product.price_unit),
            'picking_qty': product.picking_quantity,
            'remain_qty' : (product.product_qty - product.picking_quantity) ,
            'desired_qty' : (product.product_qty - product.picking_quantity) ,
            'order_product_id' : product.id,
        }
        return product_memory
    
    
    def update_quantities(self,cr,uid,ids,picking_id,context=None):
            order_obj = self.pool.get('purchase.order')
            order_line_obj = self.pool.get('purchase.order.line')
            requisition_ids = context.get('active_ids', [])
            req = order_obj.browse(cr, uid, requisition_ids, context=context)
            order_ids = order_obj.browse(cr, uid, picking_id)
            for wizard in self.browse(cr,uid,ids):
                all_the_new_quantity = 0.0
                for move_line in wizard.products_ids:
                    new_qty = move_line.desired_qty
                    all_the_new_quantity += new_qty
                    if new_qty > (move_line.order_product_id.product_qty - move_line.order_product_id.picking_quantity):
                       raise osv.except_osv(('Wrong Amount Of Quantity !'), ("The Quantity for product '%s' is more than the Remaining Quantity")%(move_line.order_product_id.name))

                    new_picking_qty = move_line.order_product_id.picking_quantity + new_qty
                    order_line_obj.write(cr, uid,move_line.order_product_id.id, {'picking_quantity':new_picking_qty})
                    if new_picking_qty == move_line.order_product_id.product_qty:
                       order_line_obj.write(cr, uid,move_line.order_product_id.id, {'all_quantity_picking': True})
                done_moves = []
                for item in req[0].order_line: 
                    if item.all_quantity_picking:
                        done_moves.append(item.id)
                    if len(done_moves) == len(req[0].order_line):
                        order_obj.write(cr, uid,req[0].id, {'state':'approved'})
                return {}


    def create_partial_picking(self, cr, uid, ids, context=None):
        """Create picking and appropriate stock moves for given order lines, then
         confirms the moves, makes them available, and confirms the picking.
        """
        order_obj = self.pool.get('purchase.order')
        order_line_obj = self.pool.get('purchase.order.line')
        partial_move_obj = self.pool.get('create.partial.move')
        picking_obj = self.pool.get('stock.picking')
        stock_move = self.pool.get('stock.move')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        for order in self.browse(cr,uid,ids):
            print "order.order_id.id :::",order.order_id.id
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
#             voucher_record = voucher_obj.search(cr,uid,[('reference' , '=' , order.order_id.name )])
#             if not voucher_record and order.order_id.invoice_method != 'manual' and not order.order_id.contract_id:
#                #invoive_id = order_obj.action_invoice_create(cr,uid,[order.order_id.id],context)
#                voucher_id = voucher_obj.create(cr, uid, {
#                                         'amount': order.order_id.amount_total,
#                                         'type': 'purchase',
#                                         'date': time.strftime('%Y-%m-%d'),
#                                         'partner_id': order.order_id.partner_id.id , 
#                                         'account_id': order.order_id.partner_id.property_account_payable.id , 
#                                         'journal_id': order.order_id.company_id.purchase_foreign_journal.id,
#                                         'reference':  order.order_id.name ,
#                                         'state': 'draft',
#                                         'name':'Purchase Order Ref : ' + order.order_id.name })
#                
#                for move_line in order.products_ids :
#                    #account = clearance.get_account(clearance, bill.price_type)
#                    vocher_line_id = voucher_line_obj.create(cr, uid, {
#                                         'amount': move_line.price_unit ,
#                                         'voucher_id': voucher_id,
#                                         'type': 'dr',
#                                         'account_id': move_line.product_id.product_tmpl_id.categ_id.property_account_expense_categ.id,
#                                         'name': move_line.product_id.name or '',
#                                          })
#                voucher_obj.compute_tax(cr, uid, [voucher_id], context=context)
        return True 

        

       
          




class create_partial_move(osv.osv_memory):




    def _check_negative(self, cr, uid, ids, context=None):

        """ 
        Constrain function to check the quantity and price and frieght and packing should be greater than 0
        @return Boolean True or False
        """
        record = self.browse(cr, uid, ids[0], context=context)
        if record.product_qty <= 0 :
           raise osv.except_osv(_('Error !'), _('Product Quantity must be greater than zero'))
        if record.desired_qty <= 0 :
           raise osv.except_osv(_('Error !'), _('Desire Quantity must be greater than zero'))
        if record.picking_qty >  record.product_qty :
           raise osv.except_osv(_('Error !'), _('Picking Quantity must be Less than or equal Product Quantity '))
        if record.remain_qty <= 0:
           raise osv.except_osv(_('Error !'), _('Remain Quantity must be greater than zero'))

        return True


    

               



    _description="create partial Moves"
    _name = "create.partial.move"
    _columns = {
        'product_id' : fields.many2one('product.product', string="Product"),
        'product_qty' : fields.float("Product Quantity"),
        'price_unit' : fields.float("Price Unit"),
        'price_unit_total' : fields.float("Subtotal"),
        'desired_qty' : fields.float("Desired  Quantity"),
        'picking_qty' : fields.float("Deliverd Quantity"),
        'remain_qty' : fields.float("Remaining Quantity"),
        'order_product_id' : fields.many2one('purchase.order.line', "Products"),
        'wizard_id' : fields.many2one('create.partial.picking', string="Wizard"),
        }    


    _constraints = [

         (_check_negative, 'One of this Fields[ Quantity ,Product UOM , Freight and Packing ] is less than one ... ',['product_qty']),
                   ]              
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

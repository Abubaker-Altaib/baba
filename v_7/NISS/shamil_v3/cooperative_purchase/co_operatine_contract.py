# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv
import netsvc
import time
import datetime
from tools.translate import _
import datetime as timedelta
from base_custom import amount_to_text_ar as amount_to_text_ar

class purchase_co_operative_contract(osv.osv):
#*********************************************************************************
# To manage the contract basic concepts and the purchase contracts operations 
#**********************************************************************************

    _inherit = "purchase.contract"
    _description = "Purchase Co-operative Contract"

    def _get_type(self, cr, uid,context=None):
        """Determine the contract's type"""
        contract_purpose = 'purchase'
        if context:
            if context.has_key('contract_purpose'): contract_purpose = context['contract_purpose']
        return contract_purpose

    _columns = {

        'contract_purpose': fields.selection([('purchase', 'Purchase'),
                                              ('co_operative', 'Co-operative'),
                                              ('other', 'Other'),], 'Purpose', select=True, readonly=True),
        'co_operative_type': fields.selection([('murabaha', 'Murabaha'),('direct_payment', 'Direct Payment'),], 'co-operative type', select=True),
        'state': fields.selection([ ('draft', 'Draft'),
	                                ('confirmed', 'Confirmed'),
                                    ('approve', 'approve'),
                                    ('done', 'Done'),
                                    ('cancel', 'Cancel'),], 'State', readonly=True, help="The state of the contract.", select=True),
        'voucher_ids':fields.one2many('account.voucher', 'contract_id' , 'Vouchers', readonly=True),
               }

    _defaults = {
        'contract_purpose': _get_type,
        'state':'draft',
        #'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'purchase.co.operative.contract', context=c),
        }


    def approve(self,cr,uid,ids,context={}):

        self.write(cr,uid,ids,{'state' : 'approve'}),
        return True 

    def make_purchase_order(self, cr, uid, ids, context=None): 
        """
        To create purchase order from selected and approved contract 
        and call create_letter_of_credit if required by invoice method.

        @return: creates purchase order id 
        """
        for contract in self.browse(cr, uid, ids): 
            if contract.contract_purpose=='co_operative':
                self.write(cr,uid,ids,{'state' : 'done'}),
                return True 
            return super(purchase_co_operative_contract, self).make_purchase_order(cr, uid, ids, context)

    def write_scheduler(self, cr, uid, ids=None, use_new_cursor=False, context=None):
        """Scheduler to check the status of contract periodically 
        @return True
        """
        record = self.search(cr,uid,[('fees_total','=','contract_amount'),('state','=','approve')])
        if record:
            for car in self.browse(cr,uid,record):
                self.pool.get('purchase.contract').write(cr, uid,car.id ,{'state':'done'})
        return True

    def modify_co_oprative_contract(self,cr,uid,ids,context=None):
        """
           Method that deletes the modify_co_oprative_contract's workflow and creat a new one in the 'check' state.
           @return: Boolean True 
        """  
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            wf_service.trg_delete(uid, 'purchase.contract', s_id, cr)            
            wf_service.trg_create(uid, 'purchase.contract', s_id, cr)
            res = wf_service.trg_validate(uid, 'purchase.contract',s_id, 'draft', cr) 
            res = wf_service.trg_validate(uid, 'purchase.contract',s_id, 'confirmed', cr) 
            res = wf_service.trg_validate(uid, 'purchase.contract',s_id, 'approved', cr) 
        return True

class contract_co_operative_fees(osv.osv):

    """ Inherits contract fees """
    
    _inherit = 'contract.fees'
    _description = "Contract Fees"

    def button_dummy(self, cr, uid, ids, context={}):
        """ 
        Dummy function to recomputes the functional felids. 

        @return: True
        """
        return True     

            
    def _compute_fees(self, cr, uid, ids, field_name, arg, context=None):
        """
        Functional field function to calculate the total fees

        @return: Dictionary of amount total valus 
        """
        res = {}
        for fees in self.browse(cr, uid, ids, context=context):
            res[fees.id]= {
                'tax_amount':0.0, 
                'total_fees':0.0,
            }
            tax_amount = total_tax = 0.0
            if fees.tax_ids :
                for tax in self.pool.get('account.tax').compute_all(cr, uid, fees.tax_ids,fees.fees_amount, 1)['taxes']:
                    tax_amount = tax.get('amount', 0.0)               
                    total_tax += tax_amount                 
            total_amount=fees.fees_amount
   
            total_amount += fees.clearance_amount
            total_amount += fees.transportation
            total_amount += fees.fright_amount
            total_amount -= fees.discount_amount
            total_amount += total_tax
            
            res[fees.id]= {
                'tax_amount': total_tax,
                'total_fees': total_amount,
             }
        
        return res                          

    _columns = { 
         'purpose': fields.selection([('purchase','Purchase'),('other','Other'),('co_operative','Co-operative')],'Purpose', select=True,), 

         'tax_amount': fields.function(_compute_fees, method=True, string='Tax Amount',
        store={
            'contract.fees': (lambda self, cr, uid, ids, c={}: ids, ['tax_ids','fees_amount','transportation','clearance_amount','fright_amount','discount_amount','packing_amount'], 10), 
            }, multi="sums", help="The amount of taxes"), 

         'transportation': fields.float('Transportation Amount', digits=(16,2)), 
         'clearance_amount': fields.float('Clearance Amount', digits=(16,2)), 
         'fright_amount': fields.float('Fright Amount', digits=(16,2)),      
         'discount_amount': fields.float('Discount Amount', digits=(16,2)),                                                 
         'packing_amount': fields.float('Packing Amount', digits=(16,2)),
 
         'total_fees': fields.function(_compute_fees, method=True, string='Total Fees', store={
            'contract.fees': (lambda self, cr, uid, ids, c={}: ids, ['tax_ids','fees_amount','transportation','clearance_amount','fright_amount','discount_amount','packing_amount'], 11), 

            }, multi="sums", help="The amount of taxes"),  
   
         'tax_ids': fields.many2many('account.tax', 'fees_tax_rel', 'fees_id', 'tax_id', 'Taxes'),                                           
                                           
                }

    _defaults = {
                'transportation': 0.0,
                'clearance_amount': 0.0,
                'fright_amount': 0.0,
                'discount_amount': 0.0,
                'packing_amount': 0.0,
    }

    def done(self,cr,uid,ids,context={}):

	"""
        Workflow function to generates voucher for given ids of purchase 
        contracts Fees and links that voucher ID to the contract and change
        the state to Done.
    
        @return: voucher id
        """
        for fees in self.browse(cr, uid, ids, context=context):
            contract = fees.contract_id
            voucher_id = super(contract_co_operative_fees, self).create_invoice(cr, uid, ids, context)
            fees.write({'state':'done'})
        """user_obj = self.pool.get('res.users')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
	
        for fees in self.browse(cr, uid, ids, context=context):
	    
            contract = fees.contract_id
            
            voucher_id = voucher_obj.create(cr, uid, {
                                        'contract_id': fees.contract_id.id,
                                        'amount': fees.fees_amount,
                                        'type': 'purchase',
                                        'date': time.strftime('%Y-%m-%d'),
                                        'partner_id': contract.partner_id.id , 
                                        #'journal_id': 67,
                                        'reference': contract.name+"/"+ fees.name,
                                        'state': 'draft',
                                       # 'name':'Project fees:'+fees.name +'project :'+contract.department_id.name,
                                       # 'currency_id':contract.currency_id.id,
                                        })
            voucher_obj.write(cr,uid,[voucher_id],{'amount': fees.fees_amount}, context=context)
            
            
            vocher_line_id = voucher_line_obj.create(cr, uid, {
                                        'amount': fees.fees_amount,
                                        'voucher_id': voucher_id,
                                        'type': 'dr',
                                        'account_id': contract.contract_account.id,
                                        'name': fees.name,
                                         })
            contract.write({'voucher_ids': [(4, voucher_id)]}, context=context)
            fees.write({'state':'done'})
	    print "voucher id:",voucher_id
	    print "amount:",fees.fees_amount

        
        Workflow function to change the state to confirm.
    
        @return: True
        """
        currency_obj = self.pool.get('res.currency')
        new_amount = 0.0
        for fees in self.browse(cr, uid, ids):
            
            contract_currency = contract.currency_id.id
            euro_id = currency_obj.search(cr, uid, [('name','=','EUR')],limit=1)
            curren = currency_obj.browse(cr, uid, euro_id)
            new_amount = currency_obj.compute(cr, uid, contract_currency, curren[0].id, fees.fees_amount, fees.fees_date) 
            all_amount = contract.fees_total_amount + fees.fees_amount
            if all_amount > contract.contract_amount :
                raise osv.except_osv(_('Amount exceed  !'), _('The total fees amount well be more than the contract amount ..'))
            else:
                contract.write({'fees_total_amount': all_amount}) 
        self.write(cr,uid,ids,{'fees_amount_in_euro':new_amount })

        return True

class contract_shipment(osv.osv):
    _inherit = 'contract.shipment'

    _columns = { 
        'product_category':fields.many2one('product.category', 'Category' ),
        'location_id': fields.many2one('stock.location', 'Destination', domain=[('usage','=','internal')],),
        'picking_ids':fields.one2many('stock.picking', 'shipment_id' , 'Stock picking', readonly=True),
        'shipment_purpose': fields.related('contract_id', 'contract_purpose', type='char', string='Purpose', readonly=True),
     }

    def _prepare_order_picking(self, cr, uid, order, context=None):
        return {
            'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
            'origin': order.name ,
            'date': time.strftime('%Y-%m-%d'),
            'partner_id': order.contract_id.partner_id.id , 
            'invoice_state':'none',
            'type': 'in',
            'partner_id': order.contract_id.partner_id.id,
            'shipment_id': order.id,
            'company_id': order.contract_id.company_id.id,
            'move_lines' : [],
        }

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        if not order.contract_id.partner_id.property_stock_supplier:
            raise osv.except_osv(_('No location!'), _("Please add 'supplier location' in the supplier"))
        return {
            'name': order_line.name or '',
            'product_id': order_line.product_id.id,
            'product_qty': order_line.product_qty,
            'product_uos_qty': order_line.product_qty,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': time.strftime('%Y-%m-%d'),
            'date_expected': time.strftime('%Y-%m-%d'),
            'location_id': order.contract_id.partner_id.property_stock_supplier.id,
            'location_dest_id': order.location_id.id,
            'picking_id': picking_id,
            'partner_id': order.contract_id.partner_id.id,
            'state': 'draft',
            'type':'in',
            'company_id': order.contract_id.company_id.id,
            'price_unit': order_line.price_unit
        }

    def _create_pickings(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """Creates pickings and appropriate stock moves for given order lines, then
         confirms the moves, makes them available, and confirms the picking.
        :param browse_record order: contract order to which the order lines belong
        :param list(browse_record) order_lines: contract order line records for which picking
                                                and moves should be created.
        :param int picking_id: optional ID of a stock picking to which the created stock moves
                               will be added. A new picking will be created if omitted.
        :return: list of IDs of pickings used/created for the given order lines (usually just one)
        """
        if not picking_id:
            picking_id = self.pool.get('stock.picking').create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
        todo_moves = []
        stock_move = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        for order_line in order_lines:
            if not order_line.product_id:
                continue
            if order_line.product_id.type in ('product', 'consu'):
                move = stock_move.create(cr, uid, self._prepare_order_line_move(cr, uid, order, order_line, picking_id, context=context))
                #if order_line.move_dest_id:
                #    order_line.move_dest_id.write({'location_id': order.location_id.id})
                todo_moves.append(move)
        stock_move.action_confirm(cr, uid, todo_moves)
        stock_move.force_assign(cr, uid, todo_moves)
        wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        return [picking_id]

    def done(self, cr, uid, ids, context={}):
        """ 
        Workflow function to creating Stock picking from the shipment 
        and changes shipment state to done.

        @return: Stock Picking id 
        """
        picking_ids = []
        for order in self.browse(cr, uid, ids):
            contract = order.contract_id
            if contract.contract_purpose !='co_operative':
                return super(contract_shipment, self).done(cr, uid, ids)
            else:
                picking_ids.extend(self._create_pickings(cr, uid, order, order.contract_shipment_line_ids, context))
                self.write(cr, uid, ids, {'state':'done'})
                return picking_ids[0] if picking_ids else False

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
        'shipment_id': fields.many2one('contract.shipment', 'Contract shipment',
            ondelete='set null', select=True),
    }

    _defaults = {
        'shipment_id': False,
    }


"""
    def cancel(self,cr,uid,ids,context={}):
       
        Workflow function to change the state to cancel.
    
        @return: True
       
        for fees in self.browse(cr, uid, ids):
            contract = fees.contract_id
            new_amount = contract.fees_total_amount - fees.fees_amount
            contract.write({'fees_total_amount': new_amount})
        self.write(cr,uid,ids,{'state' : 'cancel'})
        print "===========================",fees.state
        return True
    """

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

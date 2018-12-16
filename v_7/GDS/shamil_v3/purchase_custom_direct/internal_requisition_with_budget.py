#coding:utf-8
from tools.translate import _
from osv import osv,fields
import time
import netsvc

#*****************************************************************************************#
#  This module inherited internal requistion module to add the check for budget feature   #
#  which add additional workflow activity to check budget                                 #
#*****************************************************************************************#
#
# Model definition
#
class direct_ireq_m(osv.osv):
    """
    link purchase requestion with budget confirmation """

    def test_budget(self, cr, uid, ids, name, args, context=None):
        """ 
        This method solve the problem of subworkflow, check the budget state
        and change the requestion state according to it's budget state

        @return: dictionary of records budget state 
        """

        wf_service = netsvc.LocalService("workflow")
        res ={} 
        for ir in self.browse(cr, uid, ids):
            state='/'
            if ir.state in ['wait_budget']:
                state='Waiting for budget'
                confirmation_ids = ir.budget_confirm_id.id
                if confirmation_ids:
		    bud_obj=self.pool.get('account.budget.confirmation').browse(cr, uid, confirmation_ids)
		    if confirmation_ids :
		        if bud_obj.state in ['valid']:
                            state = 'confirmed'
		            self.write(cr, uid,ir.id,{'state':'cancel'})
		            self.ir_action_cancel_draft(cr, uid, [ir.id])  
		            wf_service.trg_validate(uid, 'ireq.m', ir.id, 'budget_checked', cr) 
            res[ir.id] = state
        return res

    _inherit = 'ireq.m'

    STATE_SELECTION = [
             ('draft', 'Draft Request'),
             ('confirmed_d','Department Approved'),
             ('confirmed_s','Supply Department Approved'),
             ('confirmed','Approved to be Procured'),
             ('wait_confirmed','Wait Confirmed'),
             ('approve1','Approved By Purchase Dept'),
             ('approve2','Approved by Supply Dept'),
             ('wait_budget','Wait for budget'),
             ('done','Done'),
             ('cancel', 'Cancelled'),
             ('checked','checked'),
                      ]
    _columns = {
	            'budget_confirm_id': fields.many2one('account.budget.confirmation', 'Confirmation', select=2),
                'account_analytic_id':fields.related('budget_confirm_id','analytic_account_id',type='many2one',relation='account.analytic.account',string='Analytic Account', store=True, readonly=True),
                'purpose': fields.selection([('store', 'Feed Store'),('direct','Direct Issue'),],'Purpose',readonly=True, states={'draft':[('readonly',False)],'confirmed_d':[('readonly',False)],'confirmed_s':[('readonly',False)]}, ),
                'state': fields.selection(STATE_SELECTION, 'Status', readonly=True, select=True),
                'test_budget_state': fields.function(test_budget, method=True, type='char', size=64, string='Budget State'),
                }

    def action_budget_create(self, cr, uid, ids, context=None):
        """
        This method creates budget confirmation for selected quote by sending
        the total price and ordered department to budget confirmation.

        @param self: object pointer
        @param cr: database cursor
        @param confirmation_id: The confirmation id  which is created  
        @return: ID of confirmation_id
        """
        names = ''
        analytic_acc = ''
        for internal_req_obj in self.browse(cr, uid, ids, context=context):
            period = self.pool.get('account.period').find(cr,uid,internal_req_obj.ir_date, context = context)[0] 
            for quote in internal_req_obj.q_ids:
                if quote.state == 'done':
                    if internal_req_obj.department_id :
                        cr.execute("select analytic_account_id as id from hr_department where id=%s", (internal_req_obj.department_id.id,))
                        analytic_acc = cr.dictfetchall()[0]['id']
                    for pro in quote.pq_pro_ids:
                    	names += pro.name+'\n'
                    	ptype='purchase'
                    	if internal_req_obj.purpose == 'store':
                        	ptype='stock_in'
                    	notes = _("Purchase Approval: %s \nPurposes: %s.\nDate: %s  \nProducts: %s ") % (internal_req_obj.name , internal_req_obj.purpose , internal_req_obj.ir_date , names )
                        print"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<hhhh",period
                        if not period: raise osv.except_osv(_('Missing Period !'), _('Please create account period for the invoce date !'))
                    confirmation_id = self.pool.get('account.budget.confirmation').create(cr, uid, {
                            'name': '/',
                            'reference': internal_req_obj.name,
                            'period_id': period,
		                    'partner_id':quote.supplier_id.id,
                            'amount': quote.amount_total,
                            'residual_amount':0.0,
                            'note':notes,
                            'date':internal_req_obj.ir_date,
                            'type':ptype,
                            'analytic_account_id':analytic_acc or False,
                        })
        self.write(cr, uid, [internal_req_obj.id], {'budget_confirm_id': confirmation_id,'state': 'wait_budget'})
        return confirmation_id


# Workflow functions
    def approve2(self,cr,uid,ids,context=None):
        """ 
        Workflow method to change order state to Approve2.

        @return: True 
        """
        self.write(cr, uid, ids, {'state':'approve2'}, context=context)
        return True

    def check(self,cr,uid,ids,context=None):
        """ 
        Check if the order budget done.

        @return: True 
        """
        return True
    
    
# ---------------------------------------------------------
# purchase order customization to add Budget confirmation
# ---------------------------------------------------------

#
# This class inhirt from purchase order to edit some functions
#
class purchase_order(osv.osv):
        
    """
    Add budget information to purchase order """
    _inherit = 'purchase.order' 
       
    
    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        """
        Collects require data from purchase order line that is used to create invoice line 
        for that purchase order line, changing the main function to add these two fields values.

        @param invoice_line_tax_id: taxes per line.
        @param account_analytic_id: Analytic account of the order.
        @return: Value for fields of invoice lines.
        @rtype: dict
        """
        general_account_from_budget = order_line.order_id.ir_id.budget_confirm_id.general_account_id.id
        analytic_account_from_budget = order_line.order_id.ir_id.budget_confirm_id.analytic_account_id.id
        account_id = general_account_from_budget  
        if not account_id:
            account_id = order_line.product_id.categ_id.property_stock_account_output_categ.id
        inv_vals=super(purchase_order,self)._prepare_inv_line(cr, uid, account_id, order_line, context)
        inv_vals.update({
                'invoice_line_tax_id': [(6, 0, [x.id for x in order_line.order_id.taxes_id])],
                'account_analytic_id': analytic_account_from_budget,
                 })
        return inv_vals 
    
    def action_invoice_create(self, cr, uid, ids, context=None):
        """
        This method creates invoice by budget id & general gets them from the budget confirmation
        related to this purchase order and get currency from user company

        @param self: object pointer
        @param cr: database cursor
        @param inv_id: The invoice id  which is created and use this id to edit this invoice by new values 
        @return: returns the id of affected record
        """
        res = {}
        inv_id = super(purchase_order,self).action_invoice_create(cr, uid, ids, context)
        inv_obj = self.pool.get('account.invoice')
        for purchase_obj in self.browse(cr, uid, ids):
            res = { 
                    'budget_confirm_id':purchase_obj.ir_id.budget_confirm_id.id,
                    'currency_id': purchase_obj.company_id.currency_id.id or purchase_obj.pricelist_id.currency_id.id,
                    }        
            inv_obj.write(cr,uid,inv_id,res)
        return inv_id 



    def action_picking_create(self,cr, uid, ids, context=None):
        """
        This method creates picking by analytic & general accounts gets them from the purchase order
        and gets notes and price from purchase order line

        @param self: object pointer
        @param cr: database cursor
        @param inv_id: The picking id  which is created and use this id to edit this picking by new values 
        @param context: standard dictionary
        @return returns the id of affected record
        """
        res = {}
        picking_id = super(purchase_order,self).action_picking_create(cr, uid, ids, context=context)
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        for purchase_obj in self.browse(cr, uid, ids):
            if not purchase_obj.ir_id.budget_confirm_id:
                raise osv.except_osv(_('No Budget!'), _('You have to create purchase for approval first !\nPlease follow the right way of purchasing in your company.'))
            else:
                res = { 
                    'analytic_account_id':purchase_obj.ir_id.budget_confirm_id.analytic_account_id.id or False,
                    'account_id':purchase_obj.ir_id.budget_confirm_id.general_account_id.id or False,                  
                   }
                picking_obj.write(cr,uid,picking_id,res)
                move = {}
                for order_line in purchase_obj.order_line:
                    stock_move_obj = move_obj.search(cr, uid, [('purchase_line_id', '=',order_line.id)], context=context)
                    move = {                                
                            'price_unit': order_line.price_unit_total,
                            }
                    move_obj.write(cr,uid,stock_move_obj,move, context=context)
                
            self.write(cr, uid, ids, {'state': 'approved','date_approve': time.strftime('%Y-%m-%d')}, context=context)
            
        return picking_id
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

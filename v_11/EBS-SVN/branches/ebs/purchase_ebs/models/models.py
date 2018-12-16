# -*- coding: utf-8 -*-

from odoo import api ,osv, fields,exceptions, models,_
from odoo.exceptions import ValidationError, UserError

class productCategory(models.Model):
	_inherit = 'product.category'

	account_id = fields.Many2one('account.account',required=0)

class purchaseOrderLine(models.Model):
	"""docstring for purchaseOrderInherit"""
	_inherit = "purchase.order.line"

	@api.model
	def create(self, vals):
		print("before: ",vals)
		product = self.env['product.product'].search([('id','=',vals.get('product_id',False))])
		order = self.env['purchase.order'].search([('id','=',vals.get('order_id',False))])
		if product and 'name' not in vals:
			vals['name'] = product.name
		if product and 'account_id' not in vals:
			vals['account_id'] = product.categ_id.property_account_expense_categ_id.id
		if order and 'account_analytic_id' not in vals:
			vals['account_analytic_id'] = order.analytic_account_id.id
		print("after: ",vals)
		return super(purchaseOrderLine, self).create(vals)

	budget_confirm_id = fields.Many2one('account.budget.confirmation', readonly=1)

	@api.one
	@api.depends('account_id','account_analytic_id','order_id.date_order')
	def _budget_residual(self):
		budget_line = self.env['crossovered.budget.lines'].search([('analytic_account_id','=',self.account_analytic_id.id),
																	('general_budget_id.account_id','=',self.account_id.id),
																	('date_from','<=',self.order_id.date_order),
																	('date_to','>=',self.order_id.date_order),
																	('crossovered_budget_id.state','=','validate')])

	

		self.budget_residual = budget_line.residual

	# @api.onchange('product_id')
	# def product_set_account(self):
	# 	if self.product_id:
	# 		self.account_id = self.product_id.categ_id.account_id
	# 	else:
	# 		self.account_id = None

	budget_residual = fields.Float(compute='_budget_residual', string='Budget Residual')



class purchaseOrder(models.Model):
	"""docstring for purchaseOrderInherit"""
	_inherit = "purchase.order"

	card= fields.Boolean('card' , default=False)

	paid = fields.Boolean(invisible=True , default = False)
	
	state = fields.Selection([
		('draft', 'Draft RFQ'),
		('sent', 'RFQ Sent'),
		('request_management','Waiting for Requesting Management'),
		('infrastructure','Waiting for Infrastructure'),
		('approve_rfq','Waiting for Service Manager'),
		('approve', 'Waiting for Internal Auditor'),
		('review', 'Waiting for General Manager'),
		('approve2','Invoice Approved'),
		('done', 'Locked'),
		('to approve','Waiting for Service Manager'),
		('purchase', 'Waiting for General Manager'),
		('done_order', 'Done'),
		('cancel_rfq', 'Cancelled'),
		('cancel', 'Cancelled')
		], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

	def button_draft_servMgr(self):
		self.write({'state':'draft'})

	def button_draft_IntAud(self):
		self.write({'state':'draft'})

	def button_confirm(self):
		for line in self.order_line:
			if line.price_unit <= 0:
				raise UserError(_("Price Must Be Bigger Than Zero!!"))
		self.write({'state':'request_management'})

	def button_request_management(self):
		if self.order_type == 'technical':
			return self.write({'state':'infrastructure'})
		else:
			return self.write({'state':'approve_rfq'})

	def button_infrastructure(self):
		self.write({'state':'approve_rfq'})

	def button_approve_servMgr(self):
		self.write({'state':'approve'})

	def button_review(self):
		self.write({'state':'review'})
		self.create_budget_confirmation()

	def button_cancel_rfq(self):
		super(purchaseOrder, self).button_cancel()
		# if record have budget confirmation then delete it
		for line in self.order_line:
			if line.budget_confirm_id:
				line.budget_confirm_id.unlink()
		self.write({'state':'cancel_rfq'})

	def button_cancel(self):
		super(purchaseOrder, self).button_cancel()
		# cancel quotations related to same requisition
		purchase_quotation = self.env['purchase.order'].search([('requisition_id','=',self.requisition_id.id)])
		for line in purchase_quotation:
			line.write({'state':'cancel'})
		# cancel requisition
		self.requisition_id.write({'state':'cancel'})
		# cancel stock picking related to requisition
		picking_id = self.env['stock.picking'].search([('purchase_requisition_id','=',self.requisition_id.id)])
		if picking_id :
			picking_id.action_cancel()

	# purchase order
	def button_confirm_order(self):
		self.write({'state':'to approve'})

	def button_validate(self):
		self.write({'state':'purchase'})

	def button_approve(self):
		super(purchaseOrder, self).button_approve()
		self.write({'state':'done_order'})

		#if card = true ,find related sale order , and make PO field = True 
		if self.card == True :
			purchase_req = self.env['purchase.requisition'].search([('id','=',self.requisition_id.id )])
			print("############################## purcahea req",purchase_req.name)
			sale_order = self.env['sale.order'].search([('purchase_requisition_id','=',purchase_req.id)])
			print("############################################ sale_order",sale_order.name)
			if sale_order :
				sale_order.po = True 

	def button_approve2(self):
		self.write({'state':'approve2'})

	@api.multi
	def unlink(self):
		for line in self:
			if line.state != 'draft' :
				raise UserError(_("You can not delete none Draft purchase quotation/order"))
		''' delete draft order locally without call super, because in odoo standard
			the unlink inherited and only cancelled orders can be deleted'''
		for line in self:
			 self._cr.execute("DELETE FROM purchase_order WHERE id = %s " % line.id)

	def write(self, vals):
		if 'state' in vals and vals['state'] in ['infrastructure','approve_rfq']:
			price = vals.get('price',self.price)
			delivery = vals.get('delivery',self.delivery)
			quality = vals.get('quality',self.quality)
			after_sales_services = vals.get('after_sales_services',self.after_sales_services)
			if not ( price or delivery or quality or after_sales_services ):
				raise UserError(_("Please Enter Reason for Selecting Vendor"))
		return super(purchaseOrder, self).write(vals)

	budget_confirm_id = fields.Many2one('account.budget.confirmation',readonly=1)

	def create_budget_confirmation(self):
		"""
		create budget confirmation for purchase order if amount total more than budget residual
		:return:
		"""
		# check if amount total = or greater than budget residual
		for line in self.order_line:
			if line.price_subtotal > line.budget_residual:
				raise UserError(_("Error!!,All Amount Total must be Greater than Budget Residual")) 
			# if record have budget confirmation then delete it
			if line.budget_confirm_id:
				line.budget_confirm_id.unlink()

			confirmation_pool = self.env['account.budget.confirmation']
			# budget confirmation vals
			val = {
				'reference': self.name + " " + str(self.id),
				'partner_id': self.partner_id.id,
				'account_id': line.account_id.id,
				'date': self.date_order,
				'analytic_account_id': self.analytic_account_id.id,
				'amount': line.price_subtotal,
				# 'residual_amount': total_amount or amount,
				# 'type': self._context.get('type', 'other'),
				'type': 'other',
				'note': self.name or '/',

			}
			confirm = confirmation_pool.create(val)
			# run budget confirmation functions
			confirm.action_cancel_draft()
			confirm.budget_complete()
			# run  check_budget twice because we change check budget function to have effect in seconde trigger
			confirm.check_budget()
			confirm.check_budget()

			line.budget_confirm_id = confirm




class PurchaseRequisition(models.Model):
	"""docstring for PurchaseRequisition Inherit"""
	_inherit ='purchase.requisition'

	card = fields.Boolean(invisibl=True , defualt = False , string="card")
	state = fields.Selection([('draft', 'Draft'), 
							('in_progress', 'Waiting for Department Manager'),
							('confirm','Waiting for General Manager'),
							('open', 'Bid Selection'), 
							('done', 'Done'),
							('cancel', 'Cancelled')],
							'Status', track_visibility='onchange', required=True,copy=False, default='draft')



	@api.multi
	def action_in_progress(self):
		if not all(obj.line_ids for obj in self):
			raise UserError(_('You cannot request call because there is no product line.'))
		self.write({'state': 'in_progress'})


	@api.multi
	def action_confirm(self):
		self.write({'state':'confirm'})


	@api.multi
	def action_cancel(self):
		# try to set all associated quotations and stock order to cancel state
		super( PurchaseRequisition, self).action_cancel()
		picking_id = self.env['stock.picking'].search([('purchase_requisition_id','=',self.id)])
		if picking_id :
			picking_id.action_cancel()

			
class PurchaseRequisitionLine(models.Model): 
	"""docstring for PurchaseRequisitionline Inherit"""
	_inherit ='purchase.requisition.line'


	@api.one
	@api.depends('account_id','account_analytic_id','requisition_id.ordering_date')
	def _budget_residual(self):
		for line in self.requisition_id.line_ids :
			budget_line = self.env['crossovered.budget.lines'].search([('analytic_account_id','=',line.account_analytic_id.id),
																	('general_budget_id.account_id','=',line.account_id.id),
	 															('date_from','<=',line.requisition_id.ordering_date),
																	('date_to','>=',line.requisition_id.ordering_date),
		 															('crossovered_budget_id.state','=','validate')])

			line.budget_residual = budget_line.residual


	budget_residual = fields.Float(compute="_budget_residual" , string='Budget Residual')

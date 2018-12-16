# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_
from datetime import datetime, timedelta
from lxml import etree
from odoo.exceptions import UserError, ValidationError

class saleOrder(models.Model):
	"""docstring for saleOrder"""
	_inherit = 'sale.order'

	crm = fields.Boolean(string='crm')
	customer_invoice = fields.Boolean(string="Customer Invoice")
	center_id = fields.Many2one('sale.center', string='Center')
	purchase_requisition_id = fields.Many2one('purchase.requisition', readonly=1)

	state = fields.Selection(selection_add=[
		('review','Waiting for Department Manager'),
		('approve','Waiting for Accounting Administrator'),
		('validate','Validated'),
		('dept_approve', 'Waiting for Department approval'),
        ('account_validate', 'Waiting for Financial Manager Validation'),
        #('validated' , 'Validated'),
        ('validated' , 'Waiting for Invoice Payment'),
        ('purchase_req_created','Purchase Requisition Created'),
        ('paid','Invoice Paid')
        #('invoice_created','Invoice Created')
        ])


########################## name of sale order = center code / sequence ##########
	# @api.model
	# def create(self,vals):
	# 	name = ''
	# 	customer_order = self.env['sale.order'].search([('customer_invoice','=',True)],order='id desc',limit=1)
	# 	rec = super(saleOrder, self).create(vals)
	# 	if rec.customer_invoice == True:
	# 		if customer_order:
	# 			num_seq = customer_order.name.split('/')
	# 			name = str(rec.center_id.code)+'/'+str(int(num_seq[len(num_seq)-1])+1)
	# 		else:
	# 			name = str(rec.center_id.code)+'/'+'00'

	# 		rec.update({'partner_invoice_id':rec.partner_id.id,
	# 					'partner_shipping_id':rec.partner_id.id,
	# 					'name':name})
	# 	return rec
######################## tuga ##########################################
	@api.model
	def create(self,vals):
		if 'center_id' in vals and vals.get('customer_invoice',False) :
			center_id = vals['center_id']
			seq_result = self.env['sale.center'].browse(center_id)
			seq = seq_result.sequence_id 
			new_name = seq.next_by_id()
			vals['name'] = new_name
		
		rec=super(saleOrder,self).create(vals)
		if rec.customer_invoice == True:
			rec.update({'partner_invoice_id':rec.partner_id.id,
						'partner_shipping_id':rec.partner_id.id})
		return rec

########################create name of sale order = center /code(000) / sequence #######

	# @api.model
	# def create(self,vals):
	# 	new_name = ''
	# 	customer_order = self.env['sale.order'].search([('customer_invoice','=',True)],order='id desc',limit=1)
	# 	rec = super(saleOrder, self).create(vals)
	# 	if rec.customer_invoice == True:
	# 		if customer_order:
	# 			if 'center_id' in vals :
	# 				center_id = vals['center_id']
	# 				seq_result = self.env['sale.center'].search([('id','=',center_id)])
	# 				seq = seq_result.sequence_id 
	# 				new_name = seq.next_by_id()
	# 				vals['name']= new_name

	# 		rec.update({'partner_invoice_id':rec.partner_id.id,
	# 					'partner_shipping_id':rec.partner_id.id,
	# 					'name':new_name})
	# 	return rec
####################################################################################

########################write name of sale order = center /code(000) / sequence ####

	def write(self,vals):
		if 'partner_id' in vals and self.customer_invoice:
			partner = self.env['res.partner'].search([('id','=',vals['partner_id'])])
			vals.update({'partner_invoice_id':partner.id,
						'partner_shipping_id':partner.id})

		if 'center_id' in vals and self.customer_invoice:
			center_id = vals['center_id']
			seq_result = self.env['sale.center'].search([('id','=',center_id)])
			seq = seq_result.sequence_id 
			new_name = seq.next_by_id()
			vals.update({'name':new_name})

		return super(saleOrder, self).write(vals)
####################################################################################

	##### remove create button from this view #########################
	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

		res = super(saleOrder, self).fields_view_get(
			view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

		if self._context.get('default_crm', False):
			doc = etree.XML(res['arch'])

			for node_form in doc.xpath("//form"):
				node_form.set("create", 'false')

			for node_form in doc.xpath("//tree"):
				node_form.set("create", 'false')

			res['arch'] = etree.tostring(doc)
		return res
####################################################################################
#function printing customer Quadation -->
	def print_report(self, data):
		datas = {
		'ids': [],
		'model': 'sale.order',}
		return self.env.ref('crm_custom.action_invoice_details_print').report_action(self, data=datas)
####################################################################################
	# Workflow functions for Certificate Quotations

	def certificate_button_review(self):
		self.write({'state':'review'})

	def certificate_button_approve(self):
		self.action_invoice_create()
		self.write({'state':'approve'})

	def certificate_button_validate(self):
		self.write({'state':'validate'})

	def certificate_button_cancel(self):
		self.write({'state':'cancel'})

	# workflow functions for CRM Card quotations 
	def superviser_confirm(self):
		self.write({'state':'dept_approve'})

	# create invoice when Department manager approve
	def dept_approve(self):
		self.create_invoice()
		# self.write({'state':'account_validate'})
		self.write({'state':'validated'})

	## create invoice when financial manager validate 
	def financial_validate(self):
		self.create_invoice()
		self.write({'state':'validated'})


	def create_invoice(self):
		self.action_confirm()
		invoice=self.action_invoice_create()

		invoice_id = self.env['account.invoice'].search([('id','=',invoice[0])])
		invoice_id.card = True
	
		#self.write({'state':'invoice_created'})
		
		stock_picking = self.env['stock.picking'].search([('origin','=',self.name)])
		if stock_picking:
			stock_picking.state='draft'

	# workflow functions for Customers Invoices 

	def cus_inv_draft(self):
		self.write({'state':'draft'}) 

	def cus_inv_confirm(self):
		self.write({'state':'confirm'}) 

	def cus_inv_review(self):
		self.write({'state':'review'}) 

	def cus_inv_approve(self):
		self.action_invoice_create()
		self.write({'state':'approve'}) 

	def cus_inv_validate(self):
		self.write({'state':'validate'})

	def cus_inv_cancel(self):
		self.write({'state':'cancel'}) 


	#this function create purchase requisition from CRM card Quotation
	@api.multi
	def create_req(self,vals):
		self.ensure_one()
		lines = self.mapped('order_line')
		if lines.filtered(lambda line: line.product_uom_qty <= 0):
			raise UserError(_("Please Make Ordered Quantity for all Products More than zero"))

		products = [self.__create_products(m) for m in self.order_line]
		self.write({'state':'purchase_req_created'})
                
		if products:
        		purchase_requisition = self.env['purchase.requisition'].create({
                	'name': (_('Purchase Requisition CRM ') + str(self.name)),
                	'type_id': 1,
                	'ordering_date': fields.datetime.now(),
                	'line_ids': products,
                	'state': 'draft',
                	'card':True,
                	'type_id':2 #purchas tender
               })
        		self.purchase_requisition_id = purchase_requisition.id	
        		


	def __create_products(self, product):
		product_memory = (0, 6, {
               		'product_id': product.product_id.id,
               		'product_qty': product.product_uom_qty,
               		'product_uom_id':product.product_uom.id,
               		'price_unit'  :  product.price_unit })

		return product_memory	

# class account_payment(models.Model):
# 	_inherit = 'account.payment'

# 	#this method find PO related to this payment invoice , and change its "paid" field to True 

# 	# def action_validate_invoice_payment(self):
# 	# 	print("##############################3 this is the new function")
# 	# 	super(account_payment, self).action_validate_invoice_payment()
# 	# 	for payment in self:
# 	# 		invoice_ids = self.env['account.invoice'].search([('number','=',payment.communication)])
# 	# 		for invoice_id in invoice_ids :
# 	# 			if invoice_id.state in ['paid','posted'] and invoice_id.card == True :
# 	# 				print("############################################33 after if")
# 	# 				sale_order = self.env['sale.order'].search([('name','=',invoice_id.origin)])
# 	# 				print("###################################### slae_order",sale_order)
# 	# 				sale_order.state= 'paid'
# 	# 				# purchase_req = self.env['purchase.requisition'].search([('id','=',sale_order.purchase_requisition_id.id)])
# 	# 				# purcahse_order = self.env['purchase.order'].search([('origin','=',purchase_req.name)],limit=1)
# 	# 				# purcahse_order.paid=True

# 	@api.multi
# 	def write(self, vals):
# 		for payment in self :
# 			invoice_ids = self.env['account.invoice'].search([('id','=',payment.invoice_id.id)])
# 			print("###########################3 inovice_id",invoice_ids)
# 			for invoice_id in invoice_ids :
# 				if invoice_id.state in ['paid','posted'] and invoice_id.card == True :
# 					print("################################# invoice where card=true")

# 					sale_order = self.env['sale.order'].search([('name','=',invoice_id.origin)])
# 					print("############################### sale_order")
# 					sale_order.state= 'paid'
                
# 		res = super(account_payment, self).write(vals)
# 		return res               

class PurchaseRequisition(models.Model):
	_inherit ='purchase.requisition'
	
	card = fields.Boolean('card',invisible=True , default=False)
	cancel_reson = fields.Text("Cancel Reason")
	#budget_residual = fields.Float('Budget Residual', required=True, readonly=True,digits=0, default=0.0)

class purchaseOrderInherit(models.Model):
	
	_inherit = "purchase.order"

	card = fields.Boolean('card',invisible=True , default=False)

	state = fields.Selection(selection_add=[('crm_approve', 'CRM Approved')])


	@api.multi
	def confirm_by_crm(self):
		self.button_done()
		self.write({'state','crm_approve'})

class saleOrderLine(models.Model):
	_inherit = "sale.order.line"

	quantity = fields.Integer(string='Quantity')
	previous_qty = fields.Integer(string='Previous Qty')

	@api.model
	def create(self, vals):
		order_id = self.env['sale.order'].search([('id','=',vals.get('order_id',False))])
		if order_id.customer_invoice:
			product_id = self.env['product.product'].search([('id','=',vals.get('product_id',False))])
			product_qty = vals.get('quantity', 0.0) + vals.get('previous_qty',0)
			vals['product_uom_qty'] = product_qty
			service_fees_ids = self.env['services.fees'].search([('service_fees_id','=',product_id.product_tmpl_id.id)])
			print(">>>>>>>>>>service_fees_ids:",service_fees_ids)
			service_fees = service_fees_ids.filtered(lambda r:
											 r.range_from <= product_qty and r.range_to >= product_qty or \
											 r.range_from == 0 and r.range_to == 0)
			print(">>>>>>>>>>(1)service_fees:",service_fees)

			if service_fees:
				vals.update({'price_unit':service_fees.fees,
							 'qty_to_invoice':product_qty})
			else:
				raise UserError(_("Cannot find Service with same Range!!"))

		rec = super(saleOrderLine, self).create(vals)
		if rec.order_id.customer_invoice == True:
			rec.update({'name':rec.product_id.name})
		return rec


	@api.one
	def write(self, vals):
		if self.order_id.customer_invoice:
			product_id = self.product_id
			if 'product_id' in vals:
				product_id = self.env['product.product'].search([('id','=',vals.get('product_id',False))])
				vals.update({'name':product_id.name})

			product_qty = vals.get('quantity',self.quantity)
			previous_qty = vals.get('previous_qty',self.previous_qty)
			qty = product_qty + previous_qty
			vals['product_uom_qty'] = qty

			service_fees_ids = self.env['services.fees'].search([('service_fees_id','=',product_id.product_tmpl_id.id)])
			print("write>>>>>>>>>>service_fees_ids:",service_fees_ids)
			service_fees = service_fees_ids.filtered(lambda r:
											 r.range_from <= qty and r.range_to >= qty or \
											 r.range_from == 0 and r.range_to == 0)
			print("write>>>>>>>>>>(1)service_fees:",service_fees)
			if service_fees:
				vals.update({'price_unit':service_fees.fees,
							 'qty_to_invoice':qty})
			else:
				raise UserError(_("write Cannot find Service with same Range!!"))
		return super(saleOrderLine, self).write(vals)


	@api.depends('product_uom_qty','quantity', 'previous_qty', 'discount', 'price_unit', 'tax_id')
	def _compute_amount(self):
		
		"""
		Compute the amounts of price subtotal after discount
		"""
		for line in self:
			if line.order_id.customer_invoice:
				qty = line.quantity + line.previous_qty
				line.product_uom_qty = qty
				service_fees_ids = self.env['services.fees'].search([('service_fees_id','=',line.product_id.product_tmpl_id.id)])
				print(">>>>>>>>>>service_fees_ids:",service_fees_ids)
				service_fees = service_fees_ids.filtered(lambda r:
												 r.range_from <= qty and r.range_to >= qty or \
												 r.range_from == 0 and r.range_to == 0)
				print(">>>>>>>>>>(1)service_fees:",service_fees)
				
				if service_fees:
					line.update({'price_unit' : service_fees.fees})
					ebs_subtotal = qty * line.price_unit
					line.update({'price_subtotal' : ebs_subtotal})	
		
			
			price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
			taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
			line.update({
				'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
				'price_total': taxes['total_included'],
				'price_subtotal': taxes['total_excluded'],
			})


	@api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'previous_qty', 'order_id.state')
	def _get_to_invoice_qty(self):
		"""
		Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
		calculated from the ordered quantity. Otherwise, the quantity delivered is used.
		"""
		for line in self:
			if line.order_id.state in ['sale', 'done']:
				if line.product_id.invoice_policy == 'order':
					line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
				else:
					line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
			else:
				line.qty_to_invoice = 0

			if line.order_id.customer_invoice:
				qty = line.quantity + line.previous_qty
				line.update({'product_uom_qty':qty,
							 'qty_to_invoice':qty})

			if line.order_id.certificate:
				line.update({'qty_to_invoice':line.product_uom_qty})

	@api.onchange('quantity','previous_qty')
	def _compute_product_uom_qty(self):
		self.product_uom_qty = self.quantity + self.previous_qty

class accountInvoice(models.Model):
	_inherit = 'account.invoice'

	def write(self,vals):
		'''
		inherit write func to:
		- make Customer and certificate Quotation Validated if the Invoice in paid or posted state.
		- make Card Quotation Paid if the Invoice in paid or posted state.
		- make Customer Quotation draft if the Invoice in cancel state.
		- force user to add comment if the cancelled Invoice created from Customer Quotation.
		'''
		rec = False
		context = self._context
		if self.origin:
			sale_order = self.env['sale.order'].search([('name','like',self.origin)],limit=1)
			if sale_order.id:
				if sale_order.customer_invoice and 'button' in context and context['button'] == 'button_revenue_draft2':
					print(">>>>>>>> if (1)")
					if not self.note and 'note' not in vals:
						raise UserError(_("Please Enter the reason of cancelling in the Note page"))
					vals.update({'state':'cancel',
								 'sale_order':True})

				res = super(accountInvoice, self).write(vals)
				if self.state in ['paid','posted']:
					print(">>>>>>>> if (2)")
					if sale_order.customer_invoice or sale_order.certificate:
							sale_order.state = 'validate'
					##### tuga added this code to check invoice state from card quotation
					if sale_order and sale_order.card == True :
						sale_order.state = 'paid'	

				if self.state == 'cancel':
					print(">>>>>>>> if (3)")
					if sale_order.customer_invoice:
						sale_order.state = 'draft'

		if rec:
			return res
		else:
			return super(accountInvoice, self).write(vals)


class accountInvoiceLine(models.Model):
	_inherit = "account.invoice.line"
		
	# @api.one
	# @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
	# 	'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
	# 	'invoice_id.date_invoice', 'invoice_id.date')
	# def _compute_price(self):
	# 	currency = self.invoice_id and self.invoice_id.currency_id or None
	# 	price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
	# 	taxes = False
	# 	if self.invoice_line_tax_ids:
	# 		taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
	# 	self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
	# 	self.price_total = taxes['total_included'] if taxes else self.price_subtotal
	# 	if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
	# 		price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id._get_currency_rate_date()).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
	# 	sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
	# 	self.price_subtotal_signed = price_subtotal_signed * sign

	# 	'''
	# 	override the standard depend method which calculate price_subtotal and price_total,
	# 	to recalculate price when it comes from CRM Customer Quotation with the following operation:
	# 	price * previous_qty
	# 	'''
	# 	if self.invoice_id.origin:
	# 		sale_order = self.env['sale.order'].search([('name','like',self.invoice_id.origin)],limit=1)
	# 		if sale_order and sale_order.customer_invoice:
	# 			quantity = sale_order.product_uom_qty + sale_order.previous_qty
	# 			self.quantity = quantity
	# 			service_fees = self.env['services.fees'].search([('service_fees_id','=',self.product_id.product_tmpl_id.id),
	# 															 ('range_from','<=',self.quantity),
	# 															 ('range_to','>=',self.quantity),
	# 															 ('fees','=',self.price_unit)],limit=1)
	# 			if service_fees.id :
	# 				self.price_subtotal = self.price_subtotal * service_fees.ebs_percentage / 100
	# 				self.price_total = self.price_total * service_fees.ebs_percentage / 100



class productTemplate(models.Model):
	_inherit = 'product.template'

	@api.multi
	def unlink(self):
		for line in self:
			if line.service:
				sale_order = self.env['sale.order.line'].search([('product_id.product_tmpl_id','=',line.id)])
				if len(sale_order) > 0:
					raise UserError(_("The Operation Cannot complete because the service is used in Customer Quotation"))
		return super(productTemplate, self).unlink()



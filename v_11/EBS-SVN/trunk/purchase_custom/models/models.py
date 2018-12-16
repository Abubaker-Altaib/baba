# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime, timedelta
from odoo.exceptions import UserError ,ValidationError
import re


class purchaseOrderInherit(models.Model):
	"""docstring for purchaseOrderInherit"""
	_inherit = "purchase.order"

	department_id = fields.Many2one('hr.department','Department', default=lambda self: self.env['hr.employee'].search(
                                        [('user_id', '=', self.env.user.id)]).department_id.id or False)

	analytic_account_id = fields.Many2one('account.analytic.account','Analytic Account', default=lambda self: self.env['hr.employee'].search(
                                        [('id', '=', self.env.user.id)]).department_id.analytic_account_id or False)

	purchase_type = fields.Selection([('local','Local'),('global','Global')], string="Purchase Type", default="local")

	quality = fields.Boolean(string="Quality")

	price = fields.Boolean(string="Price")

	delivery = fields.Boolean(string="Delivery")

	after_sales_services = fields.Boolean(string="After-sales services")

	#override prepare_piking from standerd purchase.order model to get  department_id from purchase_order
	@api.model
	def _prepare_picking(self):
		if not self.group_id:
			self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
		if not self.partner_id.property_stock_supplier.id:
			raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
		return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
            'department_id':self.department_id.id,
        }



class purchaseOrderLineInherit(models.Model):
	"""docstring for purchaseOrderLineInherit"""
	_inherit = 'purchase.order.line'

	account_id = fields.Many2one('account.account','Account')


	@api.onchange('product_id')
	def _onchange_product_id(self):
		self.account_id = self.product_id.categ_id.property_account_expense_categ_id.id




class PurchaseRequisition(models.Model):
	"""docstring for PurchaseRequisit Inherit"""
	_inherit ='purchase.requisition'

	department_id = fields.Many2one('hr.department',string='Department', default=lambda self: 
		    self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]).department_id.id or False)


	@api.model
	def default_get(self, fields):
		res = super(PurchaseRequisition, self).default_get(fields)
		res['ordering_date'] = datetime.now()
		emp = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
		res.update({'account_analytic_id': emp.department_id.analytic_account_id.id})
		return res


	@api.onchange('department_id')
	def onchange(self):
		res={}
		if self._context.get('department_id'):
			res={}
			dept= self.env['hr.department'].search([('id','=',self._context.get('department_id'))])
			res = {'domain':{'account_analytic_id':[('id','=',dept.analytic_account_id.id )]},'value': {'account_analytic_id': dept.analytic_account_id.id}}
		else:
			res = {'domain':{'account_analytic_id':[('id','in',[])]},'value': {'account_analytic_id': False}}
		return res

		
	@api.onchange('account_analytic_id')
	def onchange_analytic(self):
		if self.account_analytic_id:
			self.line_ids = False

	@api.multi
	def unlink(self):
		for line in self:
			if line.state != 'draft':
				raise UserError(_("You Can Not Delete None Draft Requisition."))


class PurchaseRequisitionLine(models.Model): 
	"""docstring for PurchaseRequisitionline Inherit"""
	_inherit ='purchase.requisition.line'

	account_id =fields.Many2one('account.account', string="Account")


	@api.multi
	def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
		self.ensure_one()
		requisition = self.requisition_id
		return {
			'name': name,
			'product_id': self.product_id.id,
			'product_uom': self.product_id.uom_po_id.id,
			'product_qty': product_qty,
			'price_unit': price_unit,
			'taxes_id': [(6, 0, taxes_ids)],
			'date_planned': requisition.schedule_date or fields.Date.today(),
			'account_analytic_id': self.account_analytic_id.id,
			'move_dest_ids': self.move_dest_id and [(4, self.move_dest_id.id)] or [],
			'account_id':self.account_id.id
		}

	@api.onchange('product_id')
	def onchange_product_id(self):
		self.account_id = self.product_id.categ_id.property_account_expense_categ_id


	def write(self, vals):
		if 'product_id' in vals:
			product_id = self.env['product.product'].search([('id','=',vals['product_id'])])
			expense_account = product_id.categ_id.property_account_expense_categ_id.id
			if expense_account:
				vals['account_id'] = expense_account
			else:
				raise UserError(_("Product has no Expense Account"))

		return super(PurchaseRequisitionLine, self).write(vals)


	@api.model
	def create(self, vals):
		product_id = self.env['product.product'].search([('id','=',vals['product_id'])])
		expense_account = product_id.categ_id.property_account_expense_categ_id.id
		if expense_account:
			vals['account_id'] = expense_account
		else:
			raise UserError(_("Product has no Expense Account"))

		res=super(PurchaseRequisitionLine, self).create(vals)

		if res.account_analytic_id.id == False:
			res.write({'account_analytic_id':res.requisition_id.account_analytic_id.id})
		return res
     

"""docstring for ProductCategory Inherit to required field"""
# class ProductCategory(models.Model):
# 	_inherit = 'product.category'

# 	property_account_expense_categ_id =fields.Many2one('account.account' ,required=True)

class resPartner(models.Model):
	_inherit='res.partner'

	#this function to check email format 
	@api.multi
	@api.constrains('email')
	def _check_email_format(self):
		for rec in self:
			if rec.email and not re.match("[^@]+@[^@]+\.[^@]+", rec.email):
				raise UserError(_("The email you entered is not in the correct formatting  .")) 
			if rec.email and len(rec.email) > 320 :
				raise UserError(_("The email you entered should be less than 320 characters  .")) 
					
	#this function to check phone format
	@api.multi
	@api.constrains('phone')
	def _check_phone_format(self):
		for rec in self:
			if rec.phone and not rec.phone.isdigit() :
				raise UserError(_("phone should contain numbers only .")) 
			if rec.phone and len(rec.phone) > 25 :
				raise UserError(_("The phone number you entered should be less than 25 number .")) 				


class purchaseRequisitionType(models.Model):
	_inherit = 'purchase.requisition.type'

	#don't delete any purchaer requisition type used in purchase requisition
	@api.multi
	def unlink(self):
		for rec in self :
			purchase_req = self.env['purchase.requisition'].search([('type_id','=',rec.id)])
			if purchase_req :
				raise UserError(_(" you can not delete used purchase agreement type ."))
		return super(purchaseRequisitionType, self).unlink()
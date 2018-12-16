# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError


class stockPicking(models.Model):
    _inherit = "stock.picking"
    _order = 'name desc'

    is_qut =fields.Boolean(string='Quantity', default=False)
    is_spec =fields.Boolean(string='Specifications', default=False)
    is_qul =fields.Boolean(string='Quality', default=False)
   

    def print_receive_note(self, data):
        datas = {
            'ids': [],
            'model': 'stock.picking',            
            }
        if self.group_id and self.picking_type_id.code == 'incoming':    
        	return self.env.ref('stock_ebs.good_receive_note').report_action(self, data=datas)
        else:
        	raise ValidationError(" this move is not from purchase order !")



    @api.multi
    def unlink(self):
    	for state in self.read(['state']):
    		if state['state'] != 'draft':
    			raise ValidationError("you can not delete none draft  move !")

    	return super(stockPicking, self).unlink()	    



class stock_scrap(models.Model):
	_inherit = 'stock.scrap'

	state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm','Confirm'),
        ('done', 'Done'),
        ('cancel','Cancelled')], string='Status', default="draft")



	@api.multi
	def confirm_scrap(self):	
		self.write({'state': 'confirm'})

	@api.multi
	def cancel_scrap(self):	
		self.write({'state': 'cancel'})	


	@api.multi
	def unlink(self):
		for state in self.read(['state']):
			if state['state'] != 'draft':
				raise ValidationError("you can not delete none draft scrap move !")

		return super(stock_scrap, self).unlink()


class stock_inventory(models.Model):
	_inherit = 'stock.inventory'

	note = fields.Text('Note')

	state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('confirm', 'In Progress'),
        ('service_review','Waiting for Service Manager Review'),
        ('account_review', 'Waiting for Finance Review'),
        ('internal_review', 'Waiting for Internal Auditor Review'),
        ('done', 'Validated'),
        ('cancel', 'Cancelled'),
         ],
        copy=False, index=True, readonly=True,
        default='draft')
    

	@api.multi 
	def confirm_inventory(self):
		if self.line_ids:
			self.write({'state': 'service_review'})
		else:
			raise UserError(_("Please enter Inventory Details"))


	@api.multi
	def service_review(self):
		if self.line_ids:
			self.write({'state': 'account_review'})
		else:
			raise UserError(_("Please enter Inventory Details"))



	@api.multi
	def account_review(self):	
		self.write({'state': 'internal_review'})

	@api.multi
	def cancel_inventory(self):	
		self.write({'state': 'cancel'})



	@api.multi
	def unlink(self):
		for state in self.read(['state']):
			if state['state'] != 'draft':
				raise UserError(_("you can not delete none draft inventory adjusment !"))

		return super(stock_inventory, self).unlink()


	# @api.constrains('name')
	# def name_constrains(self):
	# 	if not all(x.isalpha() or x.isspace() for x in self.name ):
	# 		raise UserError(_("inventory adjusment name should not contains symbols or numbers "))


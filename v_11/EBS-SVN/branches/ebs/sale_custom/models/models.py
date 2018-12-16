# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from num2words import num2words

class productTemplate(models.Model):

	_inherit = 'product.template'

	service = fields.Boolean(default=False)
	channel = fields.Boolean(default=False)
	channel_id = fields.Many2one('product.template', string="Channel")
	center_id = fields.Many2one('sale.center', string='Center')
	line_ids=fields.One2many('services.fees','service_fees_id',string='Service Line')

	@api.constrains('name')
	def _constrains_name(self):
		if self.channel:
			channel_ids = self.search([('name','=',self.name),('channel','=',True)])
			if len(channel_ids) > 1:
				raise UserError(_('channel name must be unique.'))

	@api.multi
	def action_open_view(self):
		return {
			'name': _('Services'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'product.template',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('channel_id', '=', self.id)],
		}


class SaleCenter(models.Model):
	_name ='sale.center'
	_description = 'sale channel'
    
	# code= fields.Char(string='Code')
	name= fields.Char(string='name')
	code= fields.Char(string='Code',required=True , size = 5 )
	sequence_id = fields.Many2one('ir.sequence',string='sequence')


	_sql_constraints = [
			('name_channel_uniq', 'unique (name)', _('center name must be unique.')),
			('code_channel_uniq', 'unique (code)', _('center code must be unique.')),
		]

	###########  code #################
	@api.model
	def _create_sequence(self,vals):
		prefix = vals['code'] + '/' 

		seq = {
		  'name' : vals['name'],
		  'implementation' : 'no_gap' ,
		  'prefix' : prefix ,
		  'padding' : 4 ,
		  'number_increment' : 1,
		}

		seq = self.env['ir.sequence'].create(seq)
		return seq 

	##########################################
	@api.multi
	def write(self,vals):
		for center in self :
			if ('code' in vals and center.code != vals['code'] ):
				if self.env['sale.order'].search([('center_id','in',self.ids)] , limit=1):
					raise UserError (_('you can not modify code for this record'))
			if center.sequence_id:
				center.sequence_id.write({'prefix':vals['code']})
			else :
				name = 'name' in vals and vals['name'] or center.name
				vals.update({'sequence_id':self.sudo()._create_sequence({'code':vals['code'] , 'name' : name}).id})
			result = super(SaleCenter,self).write(vals)
	#####################################################

	@api.model
	def create(self,vals):
		if not vals.get('sequence_id'):
			vals.update({'sequence_id':self.sudo()._create_sequence(vals).id})
		return super(SaleCenter,self).create(vals)

	###################################################						

class saleOrder(models.Model):
	_inherit = 'sale.order'

	certificate = fields.Boolean(string="Certificate")
	card = fields.Boolean(string="card",default=False , invisible=True)
	order_type = fields.Selection([('card','Card'),('other','Other')],default='card')
	description = fields.Text(string='Description')
	note = fields.Text(string='Notes')
	subject= fields.Text(String='Subject')

	def num2words(self , num):
		num2=num2words(num, lang='ar')
		return num2
	
	#did purcahse order workflow is done or not 
	po = fields.Boolean(string='po',default=False ,invisible=True)

	state = fields.Selection([
		('draft', 'Draft'),
		('sent', 'Quotation Sent'),
		('sale', 'Sales Order'),
		('done', 'Locked'),
		('cancel', 'Cancelled'),
		('confirm','Waiting for Supervisor'),
		
		('markiting_manager','Waiting for Markiting Manager'),
		('direct_manager','Waiting for Direct Manager'),
		('financial_manager','Waiting for finicial manager'),
        ('client_approve','Waiting for client approval'),
		('crm_approve','Waiting for CRM Superviser approval'),
		], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')


########################create name of sale order = year/increment ########################
	@api.model
	def create(self,vals):
		name = ''
		certificate_order = self.env['sale.order'].search([('certificate','=',True)],order='id desc',limit=1)
		rec = super(saleOrder, self).create(vals)
		if rec.certificate == True:
			if certificate_order:
				num_seq = certificate_order.name.split('/')
				name = str(datetime.now().year)+'/'+str(int(num_seq[len(num_seq)-1])+1)
			else:
				name = str(datetime.now().year)+'/'+'00'
				
			rec.update({'partner_invoice_id':rec.partner_id.id,
						'partner_shipping_id':rec.partner_id.id,
						'name':name})
		return rec

	def write(self,vals):
		if 'partner_id' in vals and self.certificate:
			partner = self.env['res.partner'].search([('id','=',vals['partner_id'])])
			vals.update({'partner_invoice_id':partner.id,
						'partner_shipping_id':partner.id})
		return super(saleOrder, self).write(vals)
####################################################################################

	# Workflow functions for Certificate Quotations

	def certificate_button_draft(self):
		self.write({'state':'draft',
					'crm':False})

	def certificate_button_confirm(self):
		if not self.order_line:
			raise UserError(_("Certificate Lines must contains at least one line"))

		self.write({'state':'confirm',
					'crm':True})
		
	#workflow functions for card quotation	

	@api.multi
	def officer_confirm(self):
		if self.order_type == 'card': 
			if not self.order_line:
				raise UserError(_("Order Line must contains at least one service"))
			return self.write({'state': 'markiting_manager'})
		else:
			return self.write({'state':'direct_manager'})

	@api.multi
	def markiting_confirm(self):
		if self.order_type == 'card':
			return self.write({'state': 'financial_manager'})
		else:
			return self.write({'state': 'crm_approve'})

	@api.multi
	def financial_confirm(self):
			return self.write({'state': 'client_approve'})    

	@api.multi
	def crm_approve(self):
		if self.order_type == 'card':
			return self.write({'state': 'crm_approve'})
		else:
			return self.write({'state':'markiting_manager'}) 

	@api.multi
	def set_to_draft(self):
		return self.write({'state':'draft'})

	@api.multi
	def sale_officer(self):
		return self.write({'state':'sale_officer'})

	@api.multi
	def direct_manager(self):
		return self.write({'state':'direct_manager'})


	def print_report(self, data):
		datas = {
		'ids': [],
		'model': 'sale.order',}
		return self.env.ref('sale_custom.action_certificate_quotation').report_action(self, data=datas)

	def print_report_invoice(self, data):
		datas = {
		'ids': [],
		'model': 'sale.order',}
		return self.env.ref('sale_custom.action_certificate_invoice').report_action(self, data=datas)

class saleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	sale_certificate_id = fields.Many2one('sale.certificate')
	type_of_support = fields.Many2one('support.type',string="Type of Support")


	@api.model
	def create(self,vals):
		if 'sale_certificate_id' and 'type_of_support' in vals:
			type_of_support = self.env['support.type'].search([('id','=',vals['type_of_support'])])
			support_id = self.env['support.type'].search([('sale_certificate_id','=',vals['sale_certificate_id']),
															 ('support_type','=',type_of_support.support_type)])

			if support_id:
				vals.update({'price_unit':support_id.fees})
		rec = super(saleOrderLine,self).create(vals)
		if rec.order_id.certificate == True:
			rec.update({'name':rec.sale_certificate_id.channel_id.name})
		return rec

	def write(self,vals):
		if 'product_id' in vals and self.order_id.certificate:
			product_id = self.env['product.product'].search([('id','=',vals.get('product_id',False))])
			vals.update({'name':product_id.name})

		if 'sale_certificate_id' or 'type_of_support' in vals:
			sale_certificate_id = vals.get('sale_certificate_id',self.sale_certificate_id.id)
			type_of_support = vals.get('type_of_support',self.type_of_support.id)
			type_of_support = self.env['support.type'].search([('id','=',type_of_support)])
			support_id = self.env['support.type'].search([('sale_certificate_id','=',sale_certificate_id),
															 ('support_type','=',type_of_support.support_type)])
			if support_id:
				vals.update({'price_unit':support_id.fees})
		return super(saleOrderLine,self).write(vals)

	@api.onchange('sale_certificate_id')
	def _amount_product_id(self):
		print("sale_certificate_id")
		fees = 0.0
		if self.type_of_support:
			support_id = self.env['support.type'].search([('sale_certificate_id','=',self.sale_certificate_id.id),
															 ('support_type','=',self.type_of_support.support_type)])
			if support_id:
				fees = support_id.fees

		self.update({'product_id':self.sale_certificate_id.channel_id.id,
					 'price_unit':fees})

	@api.onchange('type_of_support')
	def compute_fees(self):
		print("type_of_support")
		for line in self:
			if line.type_of_support:
				line.update({'price_unit':line.type_of_support.fees})
			else:
				line.update({'price_unit':0.0})

	@api.multi
	@api.constrains('sale_certificate_id')
	def _check(self):
		if self.order_id.certificate :
			support_id = self.env['support.type'].search([('sale_certificate_id','=',self.sale_certificate_id.id),
																 ('support_type','=',self.type_of_support.support_type)])
			if not support_id :
				raise UserError(_("This Type Of Opration doesn't supported this Channel"))



class SupportType(models.Model):
	_name = 'support.type'

	_sql_constraints = [
            ('support_type_uniq', 'unique (support_type,sale_certificate_id)', _('Type of Support must be unique per Sale Certification.')),
        ]

	
	support_type=fields.Selection([
		('complete_cer', 'Complete certification'),
		('dev_support', 'Additional Development Support'),
		('qa_test', 'Additional QA Testing')],string='Type of Support')

	fees = fields.Float('Fees')

	sale_certificate_id = fields.Many2one('sale.certificate',string='Sale Certificate')

	def name_get(self):
		result = []
		for line in self:
			name = dict(self._fields['support_type'].selection).get(line.support_type)
			if not name:
				name = "None"
			result.append((line.id, name))
		return result

	@api.one
	@api.constrains('fees')  
	def _check_fees(self):
			if self.fees<=0.0:
				raise UserError(_('Fees , Must Not Be Less Than Zero!.'))





class SaleCertificate(models.Model):
	_name = 'sale.certificate'
	_rec_name = 'channel_id'

	channel_id = fields.Many2one('product.template',string='Channel',domain=[('channel','=',True)] )
	support_type_ids = fields.One2many('support.type','sale_certificate_id',string='Type of Support')
	note = fields.Text('Certification Description')

	_sql_constraints = [
        ('channel_certificate_uniq', 'unique (channel_id)', _('certificate must be unique per channel.')),
        ]



class ServicesFees(models.Model):
	_name='services.fees'
	_description='Services Fees'

	fees =fields.Float(string='Fees')
	range_from =fields.Float(string='Range From')
	range_to =fields.Float(string='Range To')
	# ebs_percentage =fields.Float(string='EBS Percentage(%)')
	# partner_percentage =fields.Float(string='Partner Percentage(%)')
	service_fees_id =fields.Many2one('product.template' ,string='Services Fees')
	#service_fees_id itis product_id

	@api.one
	@api.constrains('fees')  
	def _check_fees(self):
			if self.fees<=0.0:
				raise UserError(_('Fees , Must Not Be Less Than One!.'))

	@api.one
	@api.constrains('range_from')  
	def _check_range_from(self):
			if self.range_from<0.0:
				raise UserError(_('Range From , Must Not Be Less Than Zero !.'))

	@api.one
	@api.constrains('range_to')  
	def _check_range_to(self):
			if self.range_to<0.0:
				raise UserError(_('Range To , Must Not Be Less Than One !.'))

	
	# @api.one
	# @api.constrains('ebs_percentage')  
	# def _check_ebs_percentage(self):
	# 		if self.ebs_percentage > 100:
	# 			raise UserError(_('Ebs Percentage, Must Not Be Grater Than 100% !.'))

	# @api.one
	# @api.constrains('partner_percentage')  
	# def _check_partner_percentage(self):
	# 		if self.partner_percentage > 100:
	# 			raise UserError(_('Partner Percentage , Must Not Be Grater Than 100% !.'))

	# @api.one
	# @api.constrains('ebs_percentage','partner_percentage')  
	# def _check_percentage(self):
	# 		if (self.ebs_percentage + self.partner_percentage) > 100:
	# 			raise UserError(_('Sum Of percentages , Must Not Be Grater Than 100% !.'))
	# 		if (self.ebs_percentage + self.partner_percentage) < 100:
	# 			raise UserError(_('Sum Of percentages , Must Not Be Less Than 100% !.'))


	@api.one
	@api.constrains('range_from','range_to')  
	def _check(self):
        
        #search to get no range 
		service_fees = self.env['services.fees'].search([('service_fees_id','=',self.service_fees_id.id),
														 ('id','!=',self.id),
														 ('range_from','=',0.0),
														 ('range_to','=',0.0)])
		if len(service_fees) > 0:
			raise UserError(_("can not create fees has no Rang with fees has range"))

        #search to get range with conditon
		if self.range_from < self.range_to :
			lines =self.env['services.fees'].search([('service_fees_id','=',self.service_fees_id.id),('id','!=',self.id)])
			for line in lines:
				if line.range_from <= self.range_from and line.range_to >= self.range_from \
					or line.range_from <= self.range_to and line.range_to >= self.range_to \
					or line.range_from >= self.range_from and line.range_to <= self.range_to :
					raise UserError(_("this range Reserved in other ranges"))

        #search to get no range 
		elif self.range_from==0.0 and self.range_to==0.0:
			service_fees = self.env['services.fees'].search([('service_fees_id','=',self.service_fees_id.id),
															 ('id','!=',self.id)])
			if len(service_fees) > 0:
				raise UserError(_("can not create fees has no Rang with fees has range"))

        #give error if range to less than range from 
		else:
			raise UserError(_("Rang from must be less than Range to"))

	
class purchase_order(models.Model):
	_inherit = 'purchase.order'

	#paid field is used to track whether or not the invoice relted to this purcahse order is paid
	paid = fields.Boolean("paid",default=False , invisible=True)

class account_invoice(models.Model):
	_inherit = 'account.invoice'

	card = fields.Boolean('card', default=False  , invisible=True)

	#this method find PO related to this invoice , and change its "paid" field to True 
	def action_invoice_open(self):
		super(account_invoice, self).action_invoice_open()
		if self.card == True and self.state in ['paid','posted'] :
			sale_order = self.env['sale.order'].search([('name','=',self.origin)])
			purchase_req = self.env['purchase.requisition'].search([('id','=',sale_order.purchase_requisition_id.id)])
			purcahse_order = self.env['purchase.order'].search([('origin','=',purchase_req.name)])
			purcahse_order.paid=True

# class account_payment(models.Model):
# 	_inherit = 'account.payment'

# 	#this method find PO related to this payment invoice , and change its "paid" field to True 

# 	def action_validate_invoice_payment(self):
# 		super(account_payment, self).action_validate_invoice_payment()

# 		for payment in self:
# 			invoice_ids = self.env['account.invoice'].search([('number','=',payment.communication)])
# 			for invoice_id in invoice_ids :
# 				if invoice_id.state == 'paid' and invoice_id.card == True :
# 					sale_order = self.env['sale.order'].search([('name','=',invoice_id.origin)])
# 					purchase_req = self.env['purchase.requisition'].search([('id','=',sale_order.purchase_requisition_id.id)])
# 					purcahse_order = self.env['purchase.order'].search([('origin','=',purchase_req.name)],limit=1)
# 					purcahse_order.paid=True

class product_product(models.Model):
	"""docstring for product_product"""
	_inherit = 'product.product'

	channel = fields.Boolean(related= 'product_tmpl_id.channel',String='channel')
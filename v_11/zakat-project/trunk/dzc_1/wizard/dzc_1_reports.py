# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError


class TransportMethodWizard(models.TransientModel):
	_name = 'transport.method.wizard'
	date_from =fields.Date(string='From')
	date_to=fields.Date(string='To')
	transport_type = fields.Selection([('air', 'Air'), ('land', 'Land'), ('sea', 'Sea'),('authorization','Authorization')])
	country_id=fields.Many2many('zakat.country',string='Country')
	@api.multi
	def print_report(self, data):
		[form_values] = self.read()
		if self.date_to <= self.date_from:
			raise exceptions.ValidationError(_("Date From Must Be Greater Than Date To"))
		datas = {
			'ids': [],
			'model': 'zkate.federaltreatment',
			'form_values':form_values
			}
		
		return self.env.ref('dzc_1.transport_type_report_action').report_action(self, data=datas)
		
class TransportMethodAbstract(models.AbstractModel):
	_name="report.dzc_1.transport_type_report_1"
	
	@api.model
	def get_report_values(self,docids, data):
		report_values = []
		air=[]
		land=[]
		auth=[]
		sea=[]
		country_ids = []
		if not data['form_values']['country_id']:
			self._cr.execute('''
								select id from zakat_country 
			''' )
			country_ids=self._cr.fetchall()
			for id in country_ids:
				data['form_values']['country_id'].append(id[0])
			print ('==================================================', data['form_values']['country_id'])
		if data['form_values']['transport_type']:
			if data['form_values']['transport_type'] == 'air':
				orders=self.env['zkate.federaltreatment'].search(['&','&',('type' , '=' , 'at'),('state', '=' , 'done'),'&', '&',('date', '<=' , data['form_values']['date_to']),('date' ,'>=' , data['form_values']['date_from']),'&',('country.id' , 'in', data['form_values']['country_id']),('transport_type','=','air')])
				if not orders:
					raise exceptions.Warning(_('Sorry There is No Data To Display'))
				for order in orders:
					air.append({'name':order.partner_id.name,'p_no':order.passport_no,'country':order.country.name})
				report_values.append({'type':'جوي', 'values':air})
				
			elif data['form_values']['transport_type'] == 'sea':
				orders=self.env['zkate.federaltreatment'].search(['&','&',('type' , '=' , 'at'),('state', '=' , 'done'),'&', '&',('date', '<=' , data['form_values']['date_to']),('date' ,'>=' , data['form_values']['date_from']),'&',('country.id' , 'in', data['form_values']['country_id']),('transport_type','=','sea')])
				if not orders:
					raise exceptions.Warning(_('Sorry There is No Data To Display'))
				for order in orders:
					sea.append({'name':order.partner_id.name,'p_no':order.passport_no,'country':order.country.name})
				report_values.append({'type':'بحري', 'values':sea})
			elif data['form_values']['transport_type'] == 'land':
				orders=self.env['zkate.federaltreatment'].search(['&','&',('type' , '=' , 'at'),('state', '=' , 'done'),'&', '&',('date', '<=' , data['form_values']['date_to']),('date' ,'>=' , data['form_values']['date_from']),'&',('country.id' , 'in', data['form_values']['country_id']),('transport_type','=','land')])
				if not orders:
					raise exceptions.Warning(_('Sorry There is No Data To Display'))
				for order in orders:
					land.append({'name':order.partner_id.name,'p_no':order.passport_no,'country':order.country.name})
				report_values.append({'type':'بري', 'values':land})
			else:
				orders=self.env['zkate.federaltreatment'].search(['&','&',('type' , '=' , 'at'),('state', '=' , 'done'),'&', '&',('date', '<=' , data['form_values']['date_to']),('date' ,'>=' , data['form_values']['date_from']),'&',('country.id' , 'in', data['form_values']['country_id']),('transport_type','=','authorization')])
				if not orders:
					raise exceptions.Warning(_('Sorry There is No Data To Display'))
				for order in orders:
					auth.append({'name':order.partner_id.name,'p_no':order.passport_no,'country':order.country.name})
				report_values.append({'type':'توكيل', 'values':auth})
		else:
			orders=self.env['zkate.federaltreatment'].search(['&','&',('type' , '=' , 'at'),('state', '=' , 'done'),'&', '&',('date', '<=' , data['form_values']['date_to']),('date' ,'>=' , data['form_values']['date_from']),('country.id' , 'in', data['form_values']['country_id']),])
			if not orders:
				raise exceptions.Warning(_('Sorry There is No Data To Display'))
			for order in orders:
				if order.transport_type == 'air':
					air.append({'name':order.partner_id.name,'p_no':order.passport_no,'country':order.country.name})
				elif order.transport_type == 'sea':
					sea.append({'name':order.partner_id.name,'p_no':order.passport_no,'country':order.country.name})
				elif order.transport_type == 'land':
					land.append({'name':order.partner_id.name,'p_no':order.passport_no,'country':order.country.name})
				else:
					auth.append({'name':order.partner_id.name,'p_no':order.passport_no,'country':order.country.name})
			report_values.append({'type':'جوي', 'values':air})
			report_values.append({'type':'بحري', 'values':sea})
			report_values.append({'type':'بري', 'values':land})
			report_values.append({'type':'توكيل', 'values':auth})		
		docargs={
			'doc_ids':[],
			'doc_model':['zkate.federaltreatment'],
			'docs':report_values,	
				}
		return docargs 
		

###################################### Sergury Report ##################
# class SerguryFeesWizard(models.TransientModel):
# 	_name = 'sergury.fees.wizard'
	
# 	sergury_name = fields.Many2one('zakat.illness',string='Sergury Name')
	
# 	@api.multi
# 	def print_report(self, data):
# 		[form_values] = self.read()
		
# 		datas = {
# 			'ids': [],
# 			'model': 'hospital.treatment',
# 			'form_values':form_values
# 			}
		
# 		return self.env.ref('dzc_1.sergury_fees_report_action').report_action(self, data=datas)

from odoo import fields, models, api, exceptions, _
from datetime import datetime, timedelta
from datetime import date

class TreatmentReportWizard(models.TransientModel):
	_name= 'treatment.wizard'
	date_from	=	fields.Date(string='From')
	date_to	=	fields.Date(string='To')
	sectors_ids = fields.Many2many('zakat.diagnostic.sectors' ,string='Diagonistic Sectors')
	countries_ids =	fields.Many2many('zakat.country',string='Country')
	state = fields.Many2many('zakat.state','treatment_wizard_zakat_state','treatment_wizard_id','zakat_state_id', string= 'State')
	catigory = fields.Selection([('state','Per State'),('country','Per Countries'), ('sector', 'Per Diagnostic Sector'),('sc','Per Diagnostic sector and Country'),('ss','Per Diagnostic sector and States')])
	report_type =fields.Selection( [('cases','Cases'),('amounts','Amounts'),('both','Both')])
	treatment_type=fields.Selection([('it','Internaml Treatment'),('at', 'Abroad Treatment'), ('drags', 'Drags')])
	
	@api.constrains('report_type')
	def type_restriction(self):
		if self.report_type == 'both' and self.catigory in ('sc','ss') :
			raise exceptions.UserError('Sorry the System Cannot present this data change type or catigory')
	@api.constrains('catigory')
	def cat_restriction(self):
		if self.catigory in ('sc','country') and self.treatment_type != 'at':
			raise exceptions.UserError('Sorry the You Can not choos this catigory for this treatment Type')
	
	def print_report(self, data):
		[form_values] = self.read()
		if self.date_to <= self.date_from:
			raise exceptions.ValidationError(_("Date From Must Be Greater Than Date To"))

		datas = {
			'ids': [],
			'model': 'zkate.federaltreatment',
			'form_values':form_values
		}
		
		return self.env.ref('dzc_1.treatment_external_report_action').report_action(self, data=datas)

class TreatmentReportAbstract(models.AbstractModel):
	_name="report.dzc_1.federal_treatment_report_1"
	date= fields.Date(default=datetime.today())
	@api.model
	def get_report_values(self,docids, data):
		country_list =[]
		state_list=[]
		sectors_list=[]
		if data['form_values']['countries_ids']:
			country_list =self.env['zakat.country'].search([('id' , 'in' , data['form_values']['countries_ids'] )])
		else:
			country_list =self.env['zakat.country'].search([])
			for c in country_list:
				data['form_values']['countries_ids'].append(c.id)
		if data['form_values']['state']:
			state_list=self.env['zakat.state'].search([('id' , 'in' , data['form_values']['state'] )])
		else:
			state_list=self.env['zakat.state'].search([])
			for state in state_list:
				data['form_values']['state'].append(state.id)
		if data['form_values']['sectors_ids']:
			sectors_list=self.env['zakat.diagnostic.sectors'].search([('id' , 'in' ,data['form_values']['sectors_ids'] )])
		else:
			sectors_list=self.env['zakat.diagnostic.sectors'].search([])
			for s in sectors_list:
				data['form_values']['sectors_ids'].append(s.id)
		
		
		report_values = {'date':self.date,'from':data['form_values']['date_from'],
					'to':data['form_values']['date_to'],'treatment_type' : '','report_type':'','head':[] , 'body':[],'catigory':'','case_total':0,'total':0}
		rowvalues = []
		values = []
		treatment = []
		if data['form_values']['treatment_type'] == 'at':
			treatment = self.env['zkate.federaltreatment'].search(['&','&',('state' , '=' , 'done'),('type' , '=' , 'at'),'&',('date', '<=' , data['form_values']['date_to']),('date' ,'>=' , data['form_values']['date_from']),'&','&',('country.id', 'in' , data['form_values']['countries_ids']),('partner_id.zakat_state.id','in', data['form_values']['state']),('illness_sector_id.id', 'in' , data['form_values']['sectors_ids'])])
		elif data['form_values']['treatment_type'] == 'it':
			treatment = self.env['zkate.federaltreatment'].search(['&','&',('state' , '=' , 'done'),('type' , '=' , 'at'),'&',('date', '<=' , data['form_values']['date_to']),('date' ,'>=' , data['form_values']['date_from']),'&',('partner_id.zakat_state.id','in',data['form_values']['state']),('illness_sector_id.id', 'in' , data['form_values']['sectors_ids'])])
		else:
			treatment = self.env['zkate.federaltreatment'].search(['&','&',('state' , '=' , 'done'),('type' , '=' , 'at'),'&',('date', '<=' , data['form_values']['date_to']),('date' ,'>=' , data['form_values']['date_from']),'&',('partner_id.zakat_state.id','in',data['form_values']['state']),('illness_sector_id.id', 'in' , data['form_values']['sectors_ids'])])
		if not treatment:
			raise exceptions.Warning('Sorry There is no data to Display')
		else:
			t=len(treatment)
			report_values['case_total']=t
			total_amount = 0
			for tr in treatment:
				total_amount += tr.zakat_support
			if data['form_values']['catigory'] == 'sc':
				c = []
				num=0
				index=0
				for x in country_list:
					c.append(x.name)
				if data['form_values']['report_type'] == 'amounts':
					for sector in sectors_list:
						rowvalues = []
						index += 1
						for x in country_list:
							num=0
							for tr in treatment:
								if tr.country == x and tr.illness_sector_id == sector:
									num+=tr.zakat_support
							rowvalues.append(num)
						values.append({'index':index,'sector':sector.name , 'values':rowvalues})
				else:
					for sector in sectors_list:
						rowvalues = []
						index += 1
						for x in country_list:
							num=0
							for tr in treatment:
								if tr.country == x and tr.illness_sector_id == sector:
									num+=1
							rowvalues.append(num)
						values.append({'index':index,'sector':sector.name , 'values':rowvalues})
				report_values['head']=c
				report_values['body']=values
				report_values['report_type']=data['form_values']['report_type']				
				report_values['treatment_type']=data['form_values']['treatment_type']
				report_values['catigory']=data['form_values']['catigory']
				docargs={
					'doc_ids':[],
					'doc_model':['zkate.federaltreatment'],
					'docs':report_values,
					'date':self.date,
					'from':data['form_values']['date_from'],
					'to':data['form_values']['date_to']
				}
			elif data['form_values']['catigory'] in ('state','ss'):
			################################
			#   per state
			###############################
				if data['form_values']['catigory'] == 'state':
					if data['form_values']['report_type'] == 'both':
						num=0
						amount = 0
						index=0
						for state in state_list:
							num=0
							amount=0
							index += 1
							for tr in treatment:
								if tr.state_id == state:
									num+=1
									amount+=tr.zakat_support
									
							report_values['body'].append({'index':index , 'state':state.name,'no_of_cases':num,'amount_per':(amount/total_amount)*100,'amount':amount,'per':(num/t)*100})
					elif data['form_values']['report_type'] == 'cases':	
						num=0
						index=0
						for state in state_list:
							num=0
							amount=0
							index += 1
							for tr in treatment:
								if tr.state_id == state:
									num+=1
									amount+=tr.zakat_support
							report_values['body'].append({'index':index , 'state':state.name,'no_of_cases':num,'per':(num/t)*100})
					else:
						amount=0
						index=0
						for state in state_list:
							num=0
							amount=0
							index += 1
							for tr in treatment:
								if tr.state_id == state:
									amount+=tr.zakat_support
							report_values['body'].append({'index':index , 'state':state.name,'amount_per':(amount/total_amount)*100,'amount':amount})
					report_values['head']=''
					report_values['report_type']=data['form_values']['report_type']				
					report_values['treatment_type']=data['form_values']['treatment_type'] 
					report_values['catigory']=data['form_values']['catigory']
					docargs={
						'doc_ids':[],
						'doc_model':['zkate.federaltreatment'],
						'docs':report_values,
						'date':self.date,
						'from':data['form_values']['date_from'],
						'to':data['form_values']['date_to']
					}
				#################################
				#    per state and diagnostic sector
				##################################
				else:
					c = []
					num=0
					index=0
					for x in sectors_list:
						c.append(x.name)
					if data['form_values']['report_type'] == 'amounts':
						for state in state_list:
							rowvalues = []
							index += 1
							for sector in sectors_list:
								num=0
								for tr in treatment:
									if tr.illness_sector_id == x and tr.state_id == state:
										num+=tr.zakat_support
								rowvalues.append(num)
							values.append({'index':index,'state':state.name , 'values':rowvalues})
					else:
						for state in state_list:
							rowvalues = []
							index += 1
							for sector in sectors_list:
								num=0
								for tr in treatment:
									if tr.illness_sector_id == x and tr.state_id == state:
										num+=1
								rowvalues.append(num)
							values.append({'index':index,'state':state.name , 'values':rowvalues})
					report_values['head']=c
					report_values['body']=values
					report_values['report_type']=data['form_values']['report_type']				
					report_values['treatment_type']=data['form_values']['treatment_type']
					report_values['catigory']=data['form_values']['catigory']
					docargs={
						'doc_ids':[],
						'doc_model':['zkate.federaltreatment'],
						'docs':report_values,
						'date':self.date,
						'from':data['form_values']['date_from'],
						'to':data['form_values']['date_to']
					}
			##########################
			#		per sector
			##########################
			elif data['form_values']['catigory'] == 'sector':
				if data['form_values']['report_type'] == 'both':
					num=0
					amount = 0
					index=0
					for sector in sectors_list:
						num=0
						amount=0
						index += 1
						for tr in treatment:
							if tr.illness_sector_id == sector:
								num+=1
								amount+=tr.zakat_support
						report_values['body'].append({'index':index , 'sector':sector.name,'per':(num/t)*100,'no_of_cases':num,'amount':amount,'amount_per':(amount/total_amount)*100})
						report_values['total']+=amount
				elif data['form_values']['report_type'] == 'cases':	
					num=0
					index=0
					for sector in sector_list:
						num=0
						amount=0
						index += 1
						for tr in treatment:
							if tr.illness_sector_id == sector:
								num+=1
								amount+=tr.zakat_support
						report_values['body'].append({'index':index , 'sector':sector.name,'no_of_cases':num,'per':(num/t)*100})
						report_values['case_total']+=num
				else:
					amount=0
					index=0
					for sector in sector_list:
						num=0
						amount=0
						index += 1
						for tr in treatment:
							if tr.illness_sector_id == sector:
								amount+=tr.zakat_support
						report_values['body'].append({'index':index , 'sector':sector.name,'amount_per':(amount/total_amount)*100,'amount':amount})
						report_values['total']+=amount
				report_values['head']=''
				report_values['report_type']=data['form_values']['report_type']				
				report_values['treatment_type']=data['form_values']['treatment_type'] 
				report_values['catigory']=data['form_values']['catigory']
				docargs={
					'doc_ids':[],
					'doc_model':['zkate.federaltreatment'],
					'docs':report_values,
					'date':self.date,
					'from':data['form_values']['date_from'],
					'to':data['form_values']['date_to']
				}
			########################
			#  per country 
			#######################
			elif data['form_values']['catigory'] == 'country':
				if data['form_values']['report_type'] == 'both':
					num=0
					amount = 0
					index=0
					for country in country_list:
						num=0
						amount=0
						index += 1
						for tr in treatment:
							if tr.country == country:
								num+=1
								amount+=tr.zakat_support
						report_values['body'].append({'index':index , 'country':country.name,'per':round((num/t)*100 , 2 ),'no_of_cases':num,'amount':amount,'amount_per':round((amount/total_amount)*100 , 2)})
						report_values['total']+=amount
				elif data['form_values']['report_type'] == 'cases':	
					num=0
					amount = 0
					index=0
					for country in country_list:
						num=0
						amount=0
						index += 1
						for tr in treatment:
							if tr.country == country:
								num+=1
						report_values['body'].append({'index':index , 'country':country.name,'per':(num/t)*100,'no_of_cases':num})
				else:
					num=0
					amount = 0
					index=0
					for country in country_list:
						num=0
						amount=0
						index += 1
						for tr in treatment:
							if tr.country == country:
								amount+=tr.zakat_support
						report_values['body'].append({'index':index , 'country':country.name,'amount':amount,'amount_per':(amount/total_amount)*100})
						report_values['total']+=amount
				report_values['head']=''
				report_values['report_type']=data['form_values']['report_type']				
				report_values['treatment_type']=data['form_values']['treatment_type'] 
				report_values['catigory']=data['form_values']['catigory']
				docargs={
					'doc_ids':[],
					'doc_model':['zkate.federaltreatment'],
					'docs':report_values,
					'date':self.date,
					
				}
		return docargs 
	

 

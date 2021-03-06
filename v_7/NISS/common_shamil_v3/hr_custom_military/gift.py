# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from datetime import datetime
import time
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from operator import attrgetter


class hr_medal(osv.Model):
	_name = 'hr.medal'
	_columns = {
		'name': fields.char('Name', size=64, required=True),
		'code': fields.char('Code', size=64),
		'type': fields.selection([('wissam', 'Wissam'), ('noode', 'Noode'), ('praise', 'Praise')], string="Type"),
		'scale_id': fields.many2one('hr.salary.scale', string="Salary Scale"),
		'employee_medals_ids': fields.one2many('hr.employee.medal', 'medal_id', string='employees'),
		'company_id': fields.many2one('res.company','company'),
	}
	_defaults = {
        'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
    }

	def write(self, cr, uid, ids, vals, context=None):
		for rec in self.browse(cr, uid, ids, context):
			if 'scale_id' in vals:
				if rec.employee_medals_ids:
					raise osv.except_osv(_('ValidateError'),_("can not edit this record because it linked with other record"))
		return super(hr_medal, self).write(cr, uid, ids, vals, context=context)

	def unlink(self, cr, uid, ids, context=None):
		for rec in self.browse(cr, uid, ids):
			if rec.employee_medals_ids:
				raise osv.except_osv(
				_(''), _("can not delete record linked with other record"))
		return super(hr_medal, self).unlink(cr, uid, ids, context=context)

	def _check_spaces(self, cr, uid, ids, context=None):
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.name and (len(rec.name.replace(' ', '')) <= 0):
				raise osv.except_osv(_('ValidateError'),
				_("name must not be spaces"))
		return True

	_constraints = [
	(_check_spaces, '', ['name'])
	]

	_sql_constraints = [
        ('hr_employee_medal_name_uniqe', 'unique(name)', 'you can not create same name !'),
		('hr_employee_medal_code_uniqe', 'unique(code)', 'you can not create same code !'),
    ]


class hr_employee_medal(osv.Model):
	_name = 'hr.employee.medal'
	_columns = {
		'employee_id': fields.many2one('hr.employee', string='Employee', required=True, states={'done': [('readonly', True)]}, domain=[('state', '=', 'approved')]),
		'medal_id': fields.many2one('hr.medal', string='Gift', required=True, domain=[('type', '=', 'normal')], states={'done': [('readonly', True)]}),
		'date': fields.date('Date', required=True, states={'done': [('readonly', True)]}),
		'notes': fields.text(string='Notes', states={'done': [('readonly', True)]}),
		'state': fields.selection([('draft', 'Draft'), ('done', 'Confirmed')], 'State'),
		'department_id': fields.many2one('hr.department', string='Giver', size=64, help="who give this medal !", states={'done': [('readonly', True)]}),
		'decision': fields.char('Decision', size=64, help="", states={'done': [('readonly', True)]}),
		'discription': fields.char('Gift Discription', size=64, help="", states={'done': [('readonly', True)]}),
		'reason': fields.text('Reason', help="", states={'done': [('readonly', True)]}),
		'company_id': fields.many2one('res.company','company'),
	}
	_sql_constraints = [
        ('hr_employee_medal_uniqe', 'unique(employee_id,medal_id,date)', 'you can not create with same data !'),
    ]

	def onchange_employee(self , cr , uid ,ids ,  employee_id , context=None):
		if employee_id:
			employee = self.pool.get('hr.employee').browse(cr , uid , [employee_id])
			scale_id = employee[0].payroll_id.id
			return {

				'value' : {
					'medal_id' : None ,
				},

				'domain' : {
					'medal_id' : [('scale_id' , '=' , scale_id)] ,
				}
			}

	def do_confirm(self, cr, uid,ids,context=None):
		return self.write(cr , uid , ids , {'state' : 'done'}) 

	_defaults = {
		'date' : time.strftime('%Y-%m-%d') ,
		'state' : 'draft' ,
       'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
	}

	def unlink(self, cr, uid, ids, context=None):
		for rec in self.browse(cr, uid, ids, context):
			if rec.state != 'draft':
				raise osv.except_osv(_('ValidateError'), _("this record is must be in draft state"))
		super(hr_employee_medal, self).unlink(cr, uid, ids, context=context)


class hr_gift(osv.Model):
	_name = 'hr.gift'
	_columns = {
		'name' : fields.char('Name' , size=64 , required=True) ,
		'code' : fields.char('Code' , size=64 ) ,
		'sequence' : fields.integer('Sequence') ,
		'is_cash' : fields.boolean('Cash Gift ?') ,
		'gift' : fields.selection([('wissam' , 'Wissam') , ('noode' , 'Noode')]) ,
		'type' : fields.selection([('main' , 'Main Category') , ('normal' , 'Branch Element')], string="Type" , required=True) ,		
		'period_type' : fields.selection([('connected' , 'Connected') , ('separated' , 'Separated')], string="Period Type") ,				
		'years' : fields.integer('Years') ,
		#'months' : fields.integer('Months') ,
		'last_gift_id' : fields.many2one('hr.gift' , string='Last Gift' , domain=[('type' , '=' , 'normal')]),
		#'days' : fields.integer('Days') ,
		'give_condition' : fields.selection([('employment_date' , 'From Employment Date') , ('last_gift_date' , 'From Last Gift Date')], string="Giving Condtion") ,
		'main_gift_id' : fields.many2one('hr.gift' , string='Main Gift' , domain=[('type' , '=' , 'main')]),
		'allowance_id' :fields.many2one('hr.allowance.deduction', 'Allowance' , domain=[('allowance_type' , '=' , 'in_cycle')]),

		'main_gifts_ids': fields.one2many('hr.long.service', 'main_gift', string='long service'),

		'gift_ids_ids': fields.one2many('hr.long.service', 'gift_id', string='long service'),

		'next_gift_ids_ids': fields.one2many('hr.long.service', 'next_gift_id', string='long service'),

		'own_main_gifts_ids': fields.one2many('hr.gift', 'main_gift_id', string='own main gift'),

		'own_last_gift_id': fields.one2many('hr.gift', 'last_gift_id', string='own last gift'),
		'company_id': fields.many2one('res.company','company'),
	}

	_defaults = {
        'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
    }

	def unlink(self, cr, uid, ids, context=None):
		for rec in self.browse(cr, uid, ids):
			if rec.main_gifts_ids or rec.gift_ids_ids or rec.next_gift_ids_ids or rec.own_main_gifts_ids or rec.own_last_gift_id:
				raise osv.except_osv(
				_(''), _("can not delete record linked with other record"))
		return super(hr_gift, self).unlink(cr, uid, ids, context=context)

	def _check_spaces(self, cr, uid, ids, context=None):
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.name and (len(rec.name.replace(' ', '')) <= 0):
				raise osv.except_osv(_('ValidateError'),
				_("name must not be spaces"))

			if rec.code and (len(rec.code.replace(' ', '')) <= 0):
				raise osv.except_osv(_('ValidateError'),
				_("code must not be spaces"))
		return True

	def _check_type(self, cr, uid, ids, context=None):
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.last_gift_id and rec.last_gift_id.type != 'normal':
				raise osv.except_osv(_('ValidateError'),
				_("Last Gift must be from normal type"))
			
			if rec.allowance_id and rec.allowance_id.name_type != 'allow':
				raise osv.except_osv(_('ValidateError'),
				_("allawnce must be form allow type"))
		return True

	def _check_negative(self, cr, uid, ids, context=None):
		for rec in self.browse(cr, uid, ids, context=context):
			#add rec.type == 'normal' to avoid check in main type
			if rec.type == 'normal' and rec.years <= 0:
				raise osv.except_osv(_('ValidateError'),
				_("The Years Must Be great than Zero !"))			
		return True
	
	_constraints = [
	(_check_negative, '', []),
	(_check_spaces, '', ['name', 'code']),
	(_check_type, '', ['last_gift_id', 'allowance_id']),
	]
	

	

	_sql_constraints = [
		('model_uniq', 'unique(name,model_id)', _('The Model Must Be Unique For Each Name!')),
        ('hr_gift_name_uniqe', 'unique(name)', 'you can not create same name !'),
		('hr_gift_code_uniqe', 'unique(code)', 'you can not create same code !'),
		#('model_uniq', 'unique(sequence , scale_id)', _('Connot enter a same gift sequence number for the same salary scale')),
    ]

	def on_change_type(self , cr , uid , ids , gtype,context=None):
		return {
			'value' : {
				'is_cash' : False ,
				'years' : 0.0 ,
				'months' : 0.0 ,
				'days' : 0.0 ,
			}
		}

	def get_amount(self , cr , uid , allowance_id , emp , sdate,context=None ):
		payroll_obj = self.pool.get('payroll')
		allow_dict= payroll_obj.allowances_deductions_calculation(cr,uid,sdate,emp,{'no_sp_rec':True},[allowance_id], False,[])
		return allow_dict['total_allow']


class hr_long_service(osv.Model):
	_name = 'hr.long.service'
	_columns = {
		'employee_id' : fields.many2one('hr.employee' , string='Employee' , required=True, states={'done':[('readonly',True)]} , domain=[('state' , '=' , 'approved')]) ,
		'main_gift' : fields.many2one('hr.gift' , string='Gift Nature' , required=True , domain=[('type' , '=' , 'main')], states={'done':[('readonly',True)]}),
		'gift_id' : fields.many2one('hr.gift' , string='Gift Type' , required=True , domain=[('type' , '=' , 'normal')], states={'done':[('readonly',True)]}),
		'date' : fields.date('Date' , required=True, states={'done':[('readonly',True)]}) ,
		'next_allow_date' : fields.date('Next Gift Date', states={'done':[('readonly',True)]}) ,
		'next_gift_id' : fields.many2one('hr.gift' , string='Next Gift', states={'done':[('readonly',True)]}),
		'details' : fields.text(string='Details', states={'done':[('readonly',True)]}) ,
		'notes' : fields.text(string='Notes', states={'done':[('readonly',True)]}),
		'gift' : fields.selection([('wissam' , 'Wissam') , ('noode' , 'Noode')] , string='Gift', states={'done':[('readonly',True)]}) ,
		'amount' : fields.float('Cash', states={'done':[('readonly',True)]}) ,
		'service_years' : fields.integer('Service Years', states={'done':[('readonly',True)]}) ,
		'service_months' : fields.integer('Service Months', states={'done':[('readonly',True)]}) ,
		'service_days' : fields.integer('Service Days', states={'done':[('readonly',True)]}) ,
		'added_years' : fields.integer('Additional Years', states={'done':[('readonly',True)]}) ,
		'added_months' : fields.integer('Additional Months', states={'done':[('readonly',True)]}) ,
		'added_days' : fields.integer('Additional Days', states={'done':[('readonly',True)]}) ,
		'total_years' : fields.integer('Total Years', states={'done':[('readonly',True)]}) ,
		'total_months' : fields.integer('Total Months', states={'done':[('readonly',True)]}) ,
		'total_days' : fields.integer('Total Days', states={'done':[('readonly',True)]}) ,
		'state' : fields.selection([('draft' , 'Draft') , ('done' , 'Confirmed')] , 'State') ,
		'voucher_id' : fields.many2one('account.voucher' , string="Voucher" , readonly=True) ,
		'company_id': fields.many2one('res.company','company'),
	} 

	_defaults = {
		'date' : time.strftime('%Y-%m-%d') ,
		'state' : 'draft' ,
       'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
	}


	def set_to_draft(self,cr , uid , ids , context=None):
		for rec in self.browse(cr , uid , ids):
			if rec.voucher_id :
				if rec.voucher_id.state == 'draft' :
					self.pool.get('account.voucher').unlink(cr , uid , [rec.voucher_id.id])
				elif rec.voucher_id.state == 'cancel' :
					self.write(cr , uid , ids ,{'voucher_id' : False})
				else : 
					raise osv.except_osv(_('warning') , _('Please cancel or edit the voucher from Account Payment Screen!!'))
		return self.write(cr , uid , ids ,{'state' : 'draft'})

	def onchange_employee(self , cr , uid , ids , employee_id , context=None):
		res = {}
		if employee_id :
			emp_object = self.pool.get('hr.employee')
			emp = emp_object.browse(cr , uid , [employee_id])[0]
			durations = emp_object.actual_duration_computation(cr , uid , [employee_id])
			res['value'] = {'service_years' : durations['actual_service_years']  , 'service_months' : durations['actual_service_months'], 'service_days':durations['actual_service_days']}	
			res['value'].update({
				'main_gift' : None , 
				'gift_id' : None ,
				'next_gift_id' : None ,
				'next_allow_date' : False ,
				'added_months' : 0 ,
				'added_days' : 0 ,
				'total_years' :0 ,
				'total_months' : 0 ,
				'total_days' : 0 ,
				'amount' : 0 ,
				'gift' : 0 , 
				})
		return res


	def next_gift(self ,cr , uid ,  gift_id , date):
		res = {}
		gift_pool = self.pool.get('hr.gift')
		gift_ids = gift_pool.search(cr , uid , [('last_gift_id' , '=' , gift_id)])
		if gift_ids :	
			gifts = gift_pool.browse(cr , uid , gift_ids)
			next_gift = min(gifts , key=attrgetter('years'))
			res['next_gift_id'] = next_gift.id
			df=datetime.strptime(date,'%Y-%m-%d')
			next_year = df.year + next_gift.years
			next_date = datetime(next_year , df.month , df.day).strftime('%Y-%m-%d')
			res['next_allow_date'] = next_date
		return res

	def onchange_main_gift(self , cr , uid , ids , main_gift, context=None):
		return {
			'value' : {
				'gift_id' : None ,
				'added_years' : 0 ,
				'added_months' : 0 ,
				'added_days' : 0 ,
				'total_years' :0 ,
				'total_months' : 0 ,
				'total_days' : 0 ,
				'amount' : 0 ,
				'gift' : 0 , 
				'next_gift_id' : None ,
				'next_allow_date' : False ,
			}
		}
	
	def name_get(self, cr, uid, ids, context=None):
		return ids and [(item.id, "%s-%s" % (  item.employee_id.name, item.gift_id.name)) for item in self.browse(cr, uid, ids, context=context)] or []

	'''
			summation of 2 periods ex :
			period 1 = 10 years , 3 months , 1 day
			period 2 = 3 years , 2 months , 30 day
			total period = 13 years , 6 months , 0 days
		@param period1 : first period dictionary
		@param period2 : second period dictionary
		@return total perid dictionar with keys years , months , days
	'''
	def period_sum(self ,period1 , period2):
		total = {'total_years' : 0 , 'total_months' : 0 , 'total_days' : 0}
		total['total_days'] = period1['days'] + period2['days']
		if total['total_days'] >= 30 :
			total['total_months'] = total['total_days'] / 30
			total['total_days'] = total['total_days'] % 30
		total['total_months'] = period1['months'] + period2['months'] + total['total_months']
		if total['total_months'] >= 12 :
			total['total_years'] = total['total_months'] / 12
			total['total_months'] = total['total_months'] % 12
		total['total_years'] = period1['years'] + period2['years'] + total['total_years']
		return total


	def onchange_gift(self , cr , uid , ids ,employee_id,gift_id, date ,context=None):
		res = {}
		if gift_id and employee_id:
			emp_object = self.pool.get('hr.employee')
			emp = emp_object.browse(cr , uid , [employee_id])[0]
			gift = self.pool.get('hr.gift').browse(cr , uid , [gift_id])[0]
			durations = {}
	 		if gift.main_gift_id.period_type == 'connected' :
				res['value'] = {
								'added_years' : emp.connected_service_years ,
								'added_months' : emp.connected_service_months ,
								'added_days' : emp.connected_service_days ,
								 }
			elif gift.main_gift_id.period_type == 'separated' :
				res['value'] = {
								'added_years' : emp.separated_service_years ,
								'added_months' : emp.separated_service_months ,
								'added_days' : emp.separated_service_days ,
								#'total_years' : emp.separated_service_years + emp.actual_service_years ,
								#'total_months' : emp.separated_service_months + emp.actual_service_months ,
								#'total_days' : emp.separated_service_days + emp.actual_service_days ,
								 }
			else : raise osv.except_osv(_('ERROR'), _('Uknown Period in Main Gift'))
			period1 = {'years' :  res['value']['added_years'] ,'months' :  res['value']['added_months'] ,'days' :  res['value']['added_days'] , }
			period2 = {'years' :  emp.actual_service_years ,'months' :  emp.actual_service_months ,'days' :  emp.actual_service_days  , }
			total_period = self.period_sum(period1 , period2)
			res['value'].update(total_period)
			next_gift = self.next_gift(cr , uid  ,gift_id , date)
			if next_gift :
				res['value'].update(next_gift)
			else:
				res['value'].update({'next_gift_id' : False})
			amount = gift.is_cash and self.pool.get('hr.gift').get_amount(cr , uid , gift.allowance_id.id ,emp , date )  or 0.0
			res['value'].update({
				'amount' : amount,
				'gift' : gift.gift , 
				})
		return res

	def write(self , cr , uid , ids , vals , context=None):
		for rec in self.browse(cr , uid , ids):
			emp_id = 'employee_id' in vals and vals['employee_id'] or rec.employee_id.id
			gift_id = 'gift_id' in vals and vals['gift_id'] or rec.gift_id.id
			date = 'date' in vals and  vals['date'] or rec.date
			res = self.onchange_gift( cr , uid , [] ,emp_id,gift_id, date ,context)
			vals.update(res['value'])
			emp_object = self.pool.get('hr.employee')
			emp = emp_object.browse(cr , uid , [emp_id])[0]
			durations = emp_object.actual_duration_computation(cr , uid , [emp_id])
			vs = {'service_years' : durations['actual_service_years']  , 'service_months' : durations['actual_service_months'], 'service_days':durations['actual_service_days']}
			vals.update(vs)
		return super(hr_long_service , self).write(cr, uid ,ids, vals , context)

	def create(self ,cr , uid , vals , context=None):
		res = self.onchange_gift( cr , uid , [] ,vals['employee_id'],vals['gift_id'], vals['date'] ,context)
		vals.update(res['value'])
		emp_object = self.pool.get('hr.employee')
		emp = emp_object.browse(cr , uid , [vals['employee_id']])[0]
		durations = emp_object.actual_duration_computation(cr , uid , [vals['employee_id']])
		vs = {'service_years' : durations['actual_service_years']  , 'service_months' : durations['actual_service_months'], 'service_days':durations['actual_service_days']}
		vals.update(vs)
		return super(hr_long_service , self).create(cr, uid , vals , context)

	def get_year(self , date):
		df=datetime.strptime(date,'%Y-%m-%d')
		return df.year

	def _check_validity(self, cr, uid,ids,context=None):
		for record in self.browse(cr, uid, ids, context=context):
			# emp = self.pool.get('hr.employee').browse(cr , uid , [record.employee_id.id])[0] # employee object
			# year = self.get_year(record.date)
			service_pool = self.pool.get('hr.long.service')
			if record.gift_id.give_condition == 'employment_date' :
				if record.total_years < record.gift_id.years :
					raise orm.except_orm(_('Warning'), _("Connot give this Gift  for this employee before completing %s year/s from employment date!!" %(record.gift_id.years)))
			elif record.gift_id.give_condition == 'last_gift_date' :
				gift_ids = service_pool.search(cr , uid , [('employee_id' , '=' , record.employee_id.id) , ('gift_id' , '=' , record.gift_id.last_gift_id.id)])
				if not gift_ids : 
					raise orm.except_orm(_('Warning'), _("this employee Must take take the last gift first !!"))
				last_gift = service_pool.browse(cr , uid ,gift_ids)[0]
				last_gift_year = self.get_year(last_gift.date)
				record_year = self.get_year(record.date)
				condtion_years = record.gift_id.years
				if record_year - last_gift_year < condtion_years :
					  raise orm.except_orm(_('Warning'), _("the diffrence between the date of last Gift and current Gift must be equal or more than %s year/s" %(condtion_years)))
		return True

	def do_confirm(self, cr, uid,ids,context=None):
		self.write(cr , uid , ids , {'state' : 'done'})
		return True

	def do_payment(self , cr , uid , ids , context=None):
		self.payment(cr , uid , ids)
		return True
	
	def payment(self , cr , uid , ids , context=None):
		record = self.browse(cr , uid , ids)[0]
		emp = self.pool.get('hr.employee').browse(cr , uid ,[record.employee_id.id])[0]
		data = {
			'partner_id' : emp.user_id.partner_id.id ,
			'amount' : record.amount ,
			'name' : 'HR/Long Service , ' + record.name_get()[0][1] ,
			'company_id' : emp.user_id.company_id and emp.user_id.company_id.id or False,
			'department_id' : emp.department_id and emp.department_id.id or False,
			'account_id' : record.gift_id.allowance_id.account_id and record.gift_id.allowance_id.account_id.id or False,
			'analytic_id' : emp.department_id and emp.department_id.analytic_account_id.id or False,
			'type' : 'payment' ,
			#'journal_id' : 
		}
		voucher_id = self.pool.get('account.voucher').create(cr , uid , data)
		self.write(cr , uid , ids , {'voucher_id' : voucher_id})

	def _check_negative(self, cr, uid, ids, context=None):
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.amount < 0:
				raise osv.except_osv(_('ValidateError'),
				_("cash must be greater than or equals to zero"))
		return True

	_sql_constraints = [
        ('model_uniq', 'unique(employee_id,gift_id)', _('Connot give employee a gift more than once!')),
    ] 
	_constraints = [
        (_check_validity, "You can not choose this gift now", ['gift_id']),
		(_check_negative, '', ['amount']),
    ] 

	def unlink(self, cr, uid, ids, context=None):
		for rec in self.browse(cr, uid, ids, context):
			if rec.state != 'draft':
				raise osv.except_osv(_('ValidateError'), _("this record is must be in draft state"))
		super(hr_long_service, self).unlink(cr, uid, ids, context=context)


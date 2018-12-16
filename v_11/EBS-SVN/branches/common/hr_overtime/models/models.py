# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import itertools
from lxml import etree
import time
import pytz
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo import SUPERUSER_ID
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning,UserError
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import date
    
class hr_overtime_structure(models.Model):
    _name= "hr.overtime.structure"
    _description = "Overtime Structure"
    
    name= fields.Char(string="Structure Name")
    code = fields.Char(string="Code", required=True)
    department_ids = fields.Many2many('hr.department', string="Department (s)")
    category_ids = fields.Many2many('hr.employee.category',string='Category (s)')
    job_ids = fields.Many2many('hr.job',string='Job (s)')
    overtime_method = fields.Selection([
        ('ov_request','According to Request'),
        ('ov_attendance','According to Attendance'),
    ], string="Overtime Method", required=True,default = 'ov_request')
    hr_ov_structure_rule_ids = fields.One2many('hr.ov.structure.rule','hr_overtime_structure_id', string="Overtime Structure Line")
    state = fields.Selection([
        ('draft','Draft'),
        ('apply','Applied')
    ], string="Status", default="draft")

    calculation_type = fields.Selection([('fixed','Fixed Amount'),('computed','Computed Amount')],'Calculation Type')
    amount = fields.Float('Amount')
    rate = fields.Float('Rate',default=1)
    salary_rule_ids = fields.Many2many('hr.salary.rule',string='Salary Rules')
    overtime_account_id = fields.Many2one('account.account','Overtime Account')
    overtime_journal_id = fields.Many2one('account.journal','Overtime Journal')
    payroll_structure_ids = fields.Many2many('hr.payroll.structure',string="Payroll Structures")

    @api.constrains('payroll_structure_ids')
    def onchange_payroll_structure(self):
        if self.payroll_structure_ids:
            for payroll_structure in self.payroll_structure_ids:
                for structure in self.search([('state','=','apply')]):
                    if payroll_structure.id in structure.payroll_structure_ids.ids:
                        raise UserError(_("Payroll Structure '%s' Already linked to other overtime structure"%(payroll_structure.name,)))

    
    
    @api.model
    def create(self, values):
        values['name'] = values['name'] + "( " + values['code'] + " )"
        res = super(hr_overtime_structure, self).create(values)
        return res
        
    @api.one
    def apply_ov_structure(self):
        emp_list=[]
        domain = []
        job_list = self.job_ids.mapped('id')
        dept_list= self.department_ids.mapped('id')
        categ_list= self.category_ids.mapped('id')
        emp_list = self.env['hr.employee'].search(['|',('department_id','in',dept_list),('job_id','in',job_list)]).mapped('id')
        contract_ids = self.env['hr.contract'].search([('employee_id','in',emp_list)])
        for contract in contract_ids:
            contract.write({'overtime_structure_id': self.id})
        self.write({'state':'apply'})
        
        
class hr_ov_structure_rule(models.Model):
    _name = "hr.ov.structure.rule"
    _description = "Overtime Structure Rule"
    
    type = fields.Selection([
        ('official_leave','Official Leave'),
        ('working_day','Working Day'),
        ('weekend','WeekEnd')
    ], string="Overtime Type", default="working_day")
    
    rate = fields.Float(string="Time", widget="float_time", required=True, default=1)
    begin_after = fields.Float(string="Begin After")
    
    hr_overtime_structure_id = fields.Many2one('hr.overtime.structure', string="Overtime Structure Ref.", ondelete='cascade')


    
class hr_config_settings_inherit(models.Model):
    """Inherits res.company to add feilds that spesify the employee types that can undergone the process.
    """
    _inherit = 'res.company'

    day_max_hours = fields.Float('Max Hours For A day')
    month_max_hours = fields.Float('Max Hours For A month')
    salary_max_percentage = fields.Float('Salary Max Percentage')
    total_hours = fields.Boolean('Total Hours Entry')
    salary_rule_id = fields.Many2one('hr.salary.rule','Basic Salary')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    day_max_hours = fields.Float('Max Hours For A day')
    month_max_hours = fields.Float('Max Hours For A month')
    salary_max_percentage = fields.Float('Salary Max Percentage')
    total_hours = fields.Boolean('Total Hours Entry')
    salary_rule_id = fields.Many2one('hr.salary.rule','Basic Salary')

    @api.model    
    def create(self, vals):

        res=super(ResConfigSettings, self).create(vals)
       
        company=self.env['res.users'].search([('id','=',self._uid)]).company_id

        company.write({'day_max_hours':vals['day_max_hours'],'month_max_hours':vals['month_max_hours'],
                     'salary_max_percentage':vals['salary_max_percentage'],'total_hours':vals['total_hours'],'salary_rule_id':vals['salary_rule_id']})
        return res


    @api.multi
    def write(self, vals):
        company=self.env['res.users'].search([('id','=',self._uid)]).company_id
        res = super(ResConfigSettings, self).write(vals)

        for rec in self :

            day_max_hours = rec.day_max_hours
            if 'day_max_hours' in vals :
                day_max_hours = vals['day_max_hours']
           
            month_max_hours = rec.month_max_hours
            if 'month_max_hours' in vals :
                month_max_hours = vals['month_max_hours']

               
            salary_max_percentage = rec.salary_max_percentage    
            if 'salary_max_percentage' in vals :
                salary_max_percentage = vals['salary_max_percentage']

            total_hours = rec.total_hours
            if 'total_hours' in vals:
                total_hours = vals['total_hours']

            salary_rule_id = rec.salary_rule_id.id
            if 'salary_rule_id' in vals:
            	salary_rule_id = vals['salary_rule_id']

            

            company.write({'day_max_hours':day_max_hours,'month_max_hours':month_max_hours,
                  'salary_max_percentage':salary_max_percentage,'total_hours':total_hours,'salary_rule_id':salary_rule_id})
        
    #     return res


    @api.model
    def default_get(self, fields):

        res = super(ResConfigSettings, self).default_get(fields)
        company=self.env['res.users'].search([('id','=',self._uid)]).company_id

        day_max_hours = company.day_max_hours
        month_max_hours = company.month_max_hours
        salary_max_percentage = company.salary_max_percentage
        total_hours = company.total_hours
        salary_rule_id = company.salary_rule_id.id
        res.update({'day_max_hours': day_max_hours , 'month_max_hours':month_max_hours,
                     'salary_max_percentage':salary_max_percentage,'total_hours':total_hours,'salary_rule_id':salary_rule_id})
        return res



class HrOvertimeRequest(models.Model):
	_name = 'hr.overtime.request'

	date_from = fields.Date(string='Date From')
	date_to = fields.Date(string='Date To')
	employee_id = fields.Many2one('hr.employee','Employee')
	department_id = fields.Many2one(related='employee_id.department_id',string='Department')
	line_ids = fields.One2many('hr.overtime.request.line','request_id')
	total_line_ids = fields.One2many('hr.overtime.request.line','request_id')
	total_time = fields.Float('Total Time',compute="compute_total_time_amount")
	total_amount = fields.Float('Total Amount',compute="compute_total_time_amount")
	overtime_id = fields.Many2one('hr.overtime','Overtime')
	overtime_structure_id = fields.Many2one('hr.overtime.structure','Overtime Structure')
	state = fields.Selection([('draft','Draft'),('confirm','Confirmed'),('reject','Rejected'),('transfer','Transfered')],default='draft')
	total_hours = fields.Boolean(string='Total Hours Entry')
	confirm_id = fields.Many2one('hr.overtime.confirm')
	reject_reason = fields.Text()
	working_day_hours=fields.Float('Working Day Hours')
	weekend_hours = fields.Float('WeekEnd Hours')
	official_leave_hours = fields.Float('Official Leave Hours')
	total_working_day_hours=fields.Float('Total Working Day Hours',compute="compute_total_hours")
	total_weekend_hours = fields.Float('Total WeekEnd Hours',compute="compute_total_hours")
	total_official_leave_hours = fields.Float('Total Official Leave Hours',compute="compute_total_hours")

	def compute_total_hours(self):
		for rec in self:
			if rec.total_hours:
				rec.total_working_day_hours=rec.working_day_hours
				rec.total_official_leave_hours=rec.official_leave_hours
				rec.total_weekend_hours=rec.weekend_hours
			else:
				total_working_day_hours =0.0
				total_official_leave_hours =0.0
				total_weekend_hours=0.0
				for line in rec.line_ids:
					if line.type=='working_day':
						total_working_day_hours+=line.total_time
					if line.type=='official_leave':
						total_official_leave_hours+=line.total_time
					if line.type=='weekend':
						total_weekend_hours+=line.total_time
				rec.total_working_day_hours=total_working_day_hours
				rec.total_official_leave_hours=total_official_leave_hours
				rec.total_weekend_hours=total_weekend_hours





	@api.constrains('overtime_id','employee_id')
	def overtime_id_contrains(self):
		for rec in self:
			if rec.overtime_id:
				requests = self.search([('overtime_id','=',rec.overtime_id.id),('employee_id','=',rec.employee_id.id)])
				if len(requests)>1:
					raise UserError(_('You Can not create more than one record for this employee in this overtime'))

	@api.onchange('employee_id')
	def onchange_employee(self):
		if self.employee_id:
			domain_plans =[]
			overtimes = self.env['hr.overtime'].search([('state','=','approve')])
			for overtime in overtimes:
				if self.employee_id in overtime.employee_ids.mapped('employee_id'):
					domain_plans.append(overtime.id)
			return {'domain':{'overtime_id':[('id','in',domain_plans)]}}
	@api.onchange('overtime_id')
	def onchange_overtime_id(self):
		if self.overtime_id:
			self.date_from=self.overtime_id.date_from
			self.date_to = self.overtime_id.date_to
			return {'domain':{'employee_id':[('id','in',self.overtime_id.employee_ids.mapped('employee_id.id'))]}}


	def confirm(self):
		self.compute_total_time_amount()
		if self.total_time<=0:
			raise UserError(_("Sorry! Total Hours Can't Be Less Or Equals To Zero"))
		config_setting = self.env['res.company'].search([('id','=',self.employee_id.company_id.id)],order='id desc',limit=1)
		if config_setting.id:
			if config_setting.month_max_hours:
				total_time = self.total_working_day_hours+self.total_weekend_hours+self.total_official_leave_hours
				if total_time>config_setting.month_max_hours:
					raise UserError(_("Sorry! You Can't Exceed Month's Max Hours"))
			if not config_setting.total_hours:
				if config_setting.day_max_hours:
					for line in self.line_ids:
						if line.total_time>config_setting.day_max_hours:
							raise UserError(_("Sorry! You Can't Exceed Day's Max Hours"))
			if config_setting.salary_max_percentage:
				if config_setting.salary_rule_id:
					rule=config_setting.salary_rule_id
					if self.employee_id.contract_id:
						contract = self.employee_id.contract_id
						salary_amount = self.env['hr.payslip'].compute_rule_amount(rule,contract,self.employee_id.id)
						if self.total_amount>salary_amount*config_setting.salary_max_percentage/100:
							raise UserError(_("Sorry! You Can't Exceed The Max Salary Persentage"))


		self.write({'state':'confirm'})

	def approve(self):
		self.write({'state':'approve'})

	
	@api.multi
	def reject(self):
		#view=self.env['ir.model.data'].get_object_reference('hr_overtime_custom','tesla_purchase_multiproduct')
		view = self.env.ref('hr_overtime_custom.view_overtime_reject_reason_form')
		return {
					'name': 'Reject Reason',
					'view_type': 'form',
					'view_mode': 'form',
					'view_id': [view.id],
					'res_model': 'hr.overtime.reject.reason',
					'type': 'ir.actions.act_window',
					'nodestroy': True,
					'context':{'default_request_id':self.id},
					'target': 'new',
					'res_id': False
				}


	def draft(self):
		self.write({'state':'draft'})

	def name_get(self):
		result = []
		for rec in self:
			overtime_structures = self.env['hr.overtime.structure'].search([])
			overtime_structure = overtime_structures.filtered(lambda r:rec.employee_id.contract_id.struct_id.id in r.payroll_structure_ids.mapped('id'))
			name=''
			if overtime_structure:
				name+=overtime_structure[0].name +'/'
			if rec.employee_id:
				name+=rec.employee_id.name+'/'
			if rec.date_from:
				name+=rec.date_from
			result.append((rec.id,name))
		return result

	@api.model
	def default_get(self,fields):
		res = super(HrOvertimeRequest,self).default_get(fields)
		res.update({'total_hours':self.env.user.company_id.total_hours})
		return res


	@api.depends('employee_id','department_id')
	def compute_total_time_amount(self):
		for rec in self:
			if rec.employee_id and rec.department_id:
				total_amount = 0.0
				total_time=0.0
				if rec.overtime_structure_id:
					overtime_structure = rec.overtime_structure_id
				elif rec.overtime_id and rec.overtime_id.overtime_structure_id:
					overtime_structure=rec.overtime_id.overtime_structure_id
				else:
					overtime_structures = self.env['hr.overtime.structure'].search([])
					overtime_structure = overtime_structures.filtered(lambda r:rec.employee_id.contract_id.struct_id.id in r.payroll_structure_ids.mapped('id'))
				if not overtime_structure:
					raise UserError(_("Sorry! There is no overtime structure related to this employee"))
				overtime_structure = overtime_structure[0]
				if overtime_structure:
					weekend_rate=1
					working_day_rate=1
					official_leave_rate=1
					for ov in overtime_structure.hr_ov_structure_rule_ids:
						if ov.type=='working_day':
							working_day_rate = ov.rate
						if ov.type=='weekend':
							weekend_rate = ov.rate
						if ov.type=='official_leave':
							official_leave_rate=ov.rate
					if overtime_structure.calculation_type=='fixed':
							total_amount=overtime_structure.amount
					if overtime_structure.calculation_type=='computed':
						for rule in overtime_structure.salary_rule_ids:
							try:
								total_amount+=self.env['hr.payslip'].compute_rule_amount(rule,rec.employee_id.contract_id,rec.employee_id.id) or 0.0
							except:
								continue
						total_amount*=overtime_structure.rate
					if not rec.total_hours:
						for line in rec.line_ids:
							if line.type=='working_day':
								total_time+=line.total_time*working_day_rate
							if line.type=='weekend':
								total_time+=line.total_time*weekend_rate
							if line.type=='official_leave':
								total_time+=line.total_time*official_leave_rate
						
					else:
						total_time=((rec.working_day_hours*working_day_rate)+(rec.weekend_hours*weekend_rate)+(rec.official_leave_hours*official_leave_rate))

				rec.total_time=total_time
				rec.total_amount=total_amount*total_time

class HrOvertimeRequestLine(models.Model):
    _name = "hr.overtime.request.line"
    _description = "HR Overtime"
    
    
    
    @api.one
    def _compute_total(self):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_date = datetime.strptime(self.from_date, DATETIME_FORMAT)
        to_date = datetime.strptime(self.to_date, DATETIME_FORMAT)
        timedelta = to_date - from_date
        diff_day = (float(timedelta.seconds) / 86400) * 24
        self.total_time = diff_day
    
    
    name = fields.Char(string="Name")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    user_id = fields.Many2one('res.users', string="User")
    department_id = fields.Many2one(related="employee_id.department_id", string='Department', required=True)
    reason = fields.Text(string="Overtime Reason")
    from_date = fields.Datetime(srting="From Date")
    to_date = fields.Datetime(srting="To Date",default=date.today())
    actaul_leave_time = fields.Datetime(string="Actual Leave Time", readonly=True)
    total_time = fields.Float(string="Total Time")
    request_id = fields.Many2one('hr.overtime.request')
    working_day_hours=fields.Float('Working Day Hours')
    weekend_hours = fields.Float('WeekEnd Hours')
    official_leave_hours = fields.Float('Official Leave Hours')
    type = fields.Selection([
        ('official_leave','Official Leave'),
        ('working_day','Working Day'),
        ('weekend','WeekEnd'),
    ], string="Overtime Type")
    
    state = fields.Selection([
        ('draft','Draft'),
        ('submit','Submitted'),
        ('confirm','Confirm'),
        ('approve','Approved'),
    ], string="Status", default= "draft")

    @api.onchange('from_date')
    def onchange_employee_request(self):
        if self.request_id:
            if self.from_date:
                if self.from_date>self.request_id.date_to or self.from_date<self.request_id.date_from:
                    raise UserError(_("Date Should Be Between Date From And Date To"))
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.ov.req') or '/'
        res = super(HrOvertimeRequestLine, self).create(vals)
        return res
    
    @api.multi
    def action_sumbit(self):
        return self.write({'state': 'submit'})
    
    @api.multi
    def action_confirm(self):
        return self.write({'state': 'confirm'})
    @api.multi
    def action_approve(self):
        return self.write({'state': 'approve'})
    @api.multi
    def action_set_to_draft(self):
        return self.write({'state': 'draft'})
        
    @api.onchange('from_date','employee_id')
    def onchange_from_date(self):
        day_list =[]
        type = ''
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if self.from_date:
            contract_id = self.env['hr.employee'].browse(self.employee_id.id).contract_id.id
            for con in self.env['hr.contract'].browse(contract_id):
                for con_day in con.resource_calendar_id.attendance_ids:
                    day_list.append(con_day.dayofweek)
            request_date = datetime.strptime(self.from_date, DATETIME_FORMAT).date()
            request_day = request_date.weekday()
            if str(request_day) in day_list:
                type = 'working_day'
            else:
                type = 'weekend'
                
        
            self.type = type
        


class HrOvertimeRejectReason(models.TransientModel):
	_name = 'hr.overtime.reject.reason'

	reason = fields.Text('Rejection Reasons')
	request_id = fields.Many2one('hr.overtime.request')

	@api.multi
	def reject(self):
		self.request_id.write({'reject_reason': self.reason,'state':'reject'})



class HrOvertime(models.Model):
	_name = 'hr.overtime'
	_rec_name = 'department_id'

	department_id = fields.Many2one('hr.department','Department')
	employee_id = fields.Many2one('hr.employee','Responsible')
	overtime_structure_id = fields.Many2one('hr.overtime.structure','Overtime Structure')
	working_type = fields.Selection([('project','Project'),('operational','Operational'),('customer','Customer')],'Working Type')
	project_id = fields.Many2one('account.analytic.account','Project')
	date_from = fields.Date('Date From')
	date_to = fields.Date('Date To')
	employee_ids = fields.One2many('hr.overtime.line','request_id')
	reason = fields.Html('Overtime Reasons')
	services = fields.Html('Services')
	state = fields.Selection([('draft','Draft'),('confirm','Confirmed'),('approve','Approved'),('reject','Rejected'),('transfer','Transfered')],default='draft')

	@api.constrains('date_from','date_to')
	def dates_constrains(self):
		for rec in self:
			if rec.date_from and rec.date_to:
				if rec.date_to<rec.date_from:
					raise UserError(_("Sorry! End Date Can't Be Before Start Date"))

	@api.multi
	def select_employees(self):
		#view=self.env['ir.model.data'].get_object_reference('hr_overtime_custom','tesla_purchase_multiproduct')
		view = self.env.ref('hr_overtime_custom.view_multi_employees_form')
		return {
					'name': 'Multi Employees',
					'view_type': 'form',
					'view_mode': 'form',
					'view_id': [view.id],
					'res_model': 'hr.overtime.multi.employees',
					'type': 'ir.actions.act_window',
					'nodestroy': True,
					'context':{'default_request_id':self.id,'default_department_id':self.department_id.id},
					'target': 'new',
					'res_id': False
				}


	def confirm(self):
		if not self.employee_ids:
			raise UserError(_("Please Add Some Employees First"))
		self.write({'state':'confirm'})

	def approve(self):
		self.write({'state':'approve'})

	def reject(self):
		self.write({'state':'reject'})

	def draft(self):
		self.write({'state':'draft'})


	def name_get(self):
		result = []
		for rec in self:
			name=''
			if rec.department_id:
				name+=rec.department_id.name+'/'
			if rec.date_from:
				name+=rec.date_from+'/'
			if rec.date_from:
				name+=rec.date_to
			result.append((rec.id,name))
		return result

	@api.model
	def default_get(self,fields):
		res = super(HrOvertime,self).default_get(fields)
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
		if employee:
			res.update({'employee_id':employee.id,'department_id':employee.department_id.id})
		return res

	# @api.onchange('overtime_structure_id')
	# def onchange_overtime_structure(self):
	# 	domain=[]
	# 	if self.overtime_structure_id:
	# 		if self.overtime_structure_id.department_ids:
	# 			domain.append(('department_id','in',self.overtime_structure_id.department_ids.ids))
	# 		if self.overtime_structure_id.job_ids:
	# 			domain.append(('job_id','in',self.overtime_structure_id.job_ids.ids))
	# 		employee_ids = self.env['hr.employee'].search(domain) and self.env['hr.employee'].search(domain).ids or False	 
	# 		return {'domain':{'employee_ids':{'employee_id':[('id','in',employee_ids)]}}}


class HrOvertimeLine(models.Model):
	_name = 'hr.overtime.line'
	employee_id = fields.Many2one('hr.employee','Employee')
	expected_time = fields.Float('Expected Time',default=1)
	request_id = fields.Many2one('hr.overtime')

class HrOvertimeMultiEmployees(models.TransientModel):
	_name = 'hr.overtime.multi.employees'
	employee_ids = fields.Many2many('hr.employee',string='Employees')
	request_id = fields.Many2one('hr.overtime')
	department_id = fields.Many2one('hr.department')
	hours = fields.Float('Hours For Each')

	@api.multi
	def generate(self):
		for employee in self.employee_ids:
			self.env['hr.overtime.line'].create({'request_id':self.request_id.id,'employee_id':employee.id,'expected_time':self.hours or 1})


class HrPayslip(models.Model):
	_inherit='hr.payslip'
	active = fields.Boolean('Active',default=True)

	@api.model
	def compute_rule_amount1(self,rules,contracts,employee):
		line = self.env['hr.payslip.line'].search([
			('slip_id.employee_id','=',employee),
			('slip_id.contract_id','=',contracts.id),
			('salary_rule_id','=',rules.id)],order = 'id desc',limit=1)
		if line:
			return line.total
		else:
			raise UserError(_("Please Calculate A payslip For This Employee First"))

	@api.model
	def compute_rule_amount(self,rules,contracts,employee):
		if not self.env['hr.employee'].browse(employee).contract_id or self.env['hr.employee'].browse(employee).contract_id.state!='open':
			raise UserError(_('Employee Has No Open Contract'))
		date_from = time.strftime('%Y-%m-01')
		date_to = str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
		payslip = self.env['hr.payslip'].create({'date_from':date_from ,
			'date_to': date_to,
			'contract_id':contracts.id ,
			'struct_id': contracts.struct_id.id,
			'employee_id':employee,
			'active':False})
		payslip.worked_days_line_ids = payslip.get_worked_day_lines(contracts,date_from,date_to)
		payslip.input_line_ids = payslip.get_inputs(contracts,date_from,date_to)
		payslip.compute_sheet()
		if payslip.line_ids:
			line = payslip.line_ids.filtered(lambda r:r.salary_rule_id.id==rules.id)
			if line:
				amount= line.total
				return amount

# class HrOvertimeType(models.Model):
# 	_name = 'hr.overtime.type'
# 	name = fields.Char('Name')



class HrOvertimeConfirm(models.Model):
	_name = 'hr.overtime.confirm'

	department_id = fields.Many2one('hr.department','Department')
	employee_id = fields.Many2one('hr.employee','Responsible')
	overtime_id = fields.Many2one('hr.overtime','Overtime')
	overtime_structure_id = fields.Many2one('hr.overtime.structure','Overtime Structure')
	date_from = fields.Date(string='Date From')
	date_to = fields.Date(string='Date To')
	line_ids = fields.One2many('hr.overtime.request','confirm_id',string='Lines')
	total_line_ids =fields.One2many('hr.overtime.request','confirm_id')
	total_time = fields.Float('Total Time',compute='compute_time_amount')
	total_amount = fields.Float('Total Amount',compute = 'compute_time_amount')
	state = fields.Selection([('draft','Draft'),('confirm','Confirmed'),('transfer','Transfered'),('reject','Rejected')],default='draft')
	voucher_id = fields.Many2one('account.voucher','Voucher')
	total_hours = fields.Boolean()
	overtime_account_id = fields.Many2one('account.account','Overtime Account')
	overtime_journal_id = fields.Many2one('account.journal','Overtime Journal')

	@api.onchange('overtime_id')
	def onchange_overtime_id(self):
		# print("\n\n\n Boolean",self.total_hours)
		# if self.total_hours:
		self.total_line_ids=False
		if self.overtime_id:
			self.date_from = self.overtime_id.date_from
			self.date_to = self.overtime_id.date_to
			requests = self.env['hr.overtime.request'].search([('overtime_id','=',self.overtime_id.id),('state','=','confirm')])
			for request in requests:
				request.confirm_id = self.id

	def compute_time_amount(self):
		for rec in self:
			rec.total_time = sum(rec.line_ids.filtered(lambda r:r.state in ['draft','confirm','transfer']).mapped('total_time'))
			rec.total_amount = sum(rec.line_ids.filtered(lambda r:r.state in ['draft','confirm','transfer']).mapped('total_amount'))

	@api.model
	def default_get(self,fields):
		res = super(HrOvertimeConfirm,self).default_get(fields)
		employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
		company_id = self.env.user.company_id
		if company_id.total_hours:
			res.update({'total_hours':True})
		if employee:
			res.update({'employee_id':employee.id,'department_id':employee.department_id.id})
		return res

	def name_get(self):
		result = []
		for rec in self:
			name=''
			if rec.department_id:
				name+=rec.department_id.name+'/'
			if rec.date_from:
				name+=rec.date_from+'/'
			if rec.date_from:
				name+=rec.date_to
			result.append((rec.id,name))
		return result

	def confirm(self):
		if self.total_hours:
			for line in self.line_ids:
				line.confirm()
		self.write({'state':'confirm'})

	def reject(self):
		self.write({'state':'reject'})

	def draft(self):
		self.write({'state':'draft'})


	def transfer(self):
		'''
		create employee loan voucher
		'''
		lines = []
		# if not self.overtime_id.overtime_structure_id and not self.overtime_structure_id:
		# 	raise UserError(_("Please choose an overtime structure or select overtime containing overtime structure"))
		# if not self.overtime_id.overtime_structure_id.overtime_account_id and not self.overtime_structure_id.overtime_account_id:
		# 	raise UserError(_("Please enter an Account for %s Overtime" % self.overtime_id.overtime_structure_id.name or self.overtime_structure_id.name))
		# Voucher Data
		date = time.strftime('%Y-%m-%d')
		reference = 'HR/Overtime/ '+" / "+str(date)
		partner_id = self.employee_id.user_id.partner_id.id or False
		# account_id = self.employee_id.user_id.partner_id.property_account_payable_id.id or False
		account_id = self.overtime_account_id.id
		journal_id = self.overtime_journal_id.id
		# if self.overtime_structure_id:
		# 	journal_id = self.overtime_structure_id.overtime_journal_id and self.overtime_structure_id.overtime_journal_id.id or False
		# else:
		# 	journal_id = self.overtime_id.overtime_structure_id.overtime_journal_id and self.overtime_id.overtime_structure_id.overtime_journal_id.id or False
		currency_id_ebs = self.env['res.company'].search([('id','=',self.employee_id.company_id.id)]).currency_id.id
		user_id = self.env.user.id
		department_id = self.department_id.id
		company_id = self.employee_id.company_id.id
		if not account_id:
			raise UserError(_("This Overtime has no Account, Please Assign One"))
		if not journal_id:
			raise UserError(_("This Overtime has no journal, Please Assign One"))
		if not self.department_id.analytic_account_id:
			raise UserError(_("Sorry! This Department Has No Analytic Account"))
		amount=0.0
		for line in self.line_ids:
			if line.state =='confirm':
				if line.total_amount<=0:
					raise UserError(_("Line Amount Can't Be Less Than Or Equals To Zero"))
				amount+=line.total_amount
		if amount:
			lines=[(0,0,{'name':self.overtime_id.overtime_structure_id.name or self.overtime_structure_id.name or '/',
					'account_id':account_id,
					'account_analytic_id':self.department_id.analytic_account_id.id,
					'price_unit':amount,
					'price_subtotal':amount
					})]
		if not lines:
			raise UserError(_("Sorry! Lines Can't Be Empty"))
		voucher = {'date':date,
					'account_date':date,
					'reference':reference,
					'partner_id':partner_id,
					'journal_id':journal_id,
					'currency_id_ebs':currency_id_ebs,
					'state':'draft',
					'user_id':user_id,
					'department_id':department_id,
					'company_id':company_id,
					'account_id':account_id,
					'voucher_type':'purchase',
					'payment_type':'direct_payment',
					'line_ids':lines}
		voucher_id = self.env['account.voucher'].create(voucher)
		self.voucher_id = voucher_id.id
		#self.overtime_id.state='transfer'
		self.line_ids.write({'state':'transfer'})
		self.state='transfer'
		payslips = self.env['hr.payslip'].search([('employee_id','=',self.employee_id.id),('active','=',False)])
		payslips.unlink()

class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	@api.model
	def name_search(self,name,args,operator='ilike',limit=100):
		employees=[]
		if self._context.get('total_line_ids'):
			for employee in self._context.get('total_line_ids'):
				if employee[2]:
					if employee[2].get('employee_id'):
						employees.append(employee[2].get('employee_id'))
		if self._context.get('employee_ids'):
			for employee in self._context.get('employee_ids'):
				if employee[2]:
					if employee[2].get('employee_id'):
						employees.append(employee[2].get('employee_id'))


		args.append(('id','not in',employees))
		return super(HrEmployee,self).name_search(name,args,operator,limit)

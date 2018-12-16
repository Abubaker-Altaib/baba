# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
###############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.addons import decimal_precision as dp
from datetime import datetime

class ProductProduct(models.Model):

    _inherit = "product.product"

    mission= fields.Boolean('Mission')
    mission_type= fields.Selection([('internal','Internal'),('external','External')],string='Mission Type', default='external')
    time_type= fields.Selection([('day','Days'),('hour','Hours')],string='Time Type', default='day')
    partner_id = fields.Many2one('res.partner',string="Destination")      
    journal_id = fields.Many2one('account.journal', string='Journal')
    max_hour=fields.Float(string='Max Hours')
    line_ids=fields.One2many('mission.category.line','product_id', string="Mission Category Line")

class ResPartner(models.Model):
    _inherit = "res.partner"

    destination=fields.Boolean(string='Destination')

class MissionCategoryLine(models.Model):

    _name = "mission.category.line"

    product_id = fields.Many2one('product.product', string='Mission Category')
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure',required=True)
    amount=fields.Float(string='Hour Wage',required=True)

class HrMission(models.Model):

    _name = "hr.mission"
    _description = 'Hr Mission'
    _inherit = ['mail.thread']
    _order = "date desc, id desc"

    name = fields.Char('Name',copy=False ,readonly=True, states={'draft': [('readonly', False)]})
    date= fields.Date('Date',copy=False,readonly=True, states={'draft': [('readonly', False)]}, default=fields.Date.context_today)
    start_date= fields.Datetime('Start Date',readonly=True, states={'draft': [('readonly', False)]})
    end_date= fields.Datetime('End Date',readonly=True, states={'draft': [('readonly', False)]})
    hour=fields.Float(string='Hours',readonly=True, states={'draft': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', string='Department',readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner',string="Partner",readonly=True, states={'draft': [('readonly', False)]}) 
    account_analytic_id = fields.Many2one('account.analytic.account',readonly=True, states={'draft': [('readonly', False)]}, string='Analytic Account' ,domain="[('type', '=', 'normal')]")
    mission_categ_id = fields.Many2one('product.product', string='Mission Category',readonly=True, states={'draft': [('readonly', False)]},domain="[('mission', '=', True)]")
    mission_objective = fields.Text(string='Mission Objective')
    notes = fields.Text(string='Mission Objective')
    total_amount=fields.Float(compute='_compute_totals',string='Total Amount',readonly=True)
    total_service=fields.Float(compute='_compute_totals',string='Total Service',readonly=True)
    total=fields.Float(compute='_compute_totals',string='Total',readonly=True)
    to_pay= fields.Boolean(compute='_compute_to_pay',string='To Pay')
    employee_ids=fields.One2many('hr.mission.employee','mission_id', string="Mission Employees") 
    service_ids=fields.One2many('hr.mission.service','mission_id', string="Mission Services")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('approve', 'Approve'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
        ], 'Status', readonly=True, track_visibility='onchange', copy=False, default='draft')
    voucher_id = fields.Many2one('account.voucher', string='voucher')
    company_id = fields.Many2one('res.company', string='Company',readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.user.company_id)
    time_type= fields.Selection(related='mission_categ_id.time_type',string='Time Type',store=True, readonly=True)


    @api.onchange('time_type')
    def _onchange_time_type(self):
        line_obj=self.env['hr.mission.employee']
        for line in self.employee_ids:
            hour = 0
            day =0
            start_date = line.start_date
            end_date = line.end_date
            if (end_date and start_date) and (start_date <= end_date):
                if self.time_type == 'hour':
                    line.hour = line_obj._get_number_of_hours(start_date, end_date, line.employee_id.id)
                else:
                    line.day = line_obj._get_number_of_days(start_date, end_date, line.employee_id.id)


    @api.depends('employee_ids')
    def _compute_totals(self):
        for mission in self:
            total_amount=0.0
            total_service=0.0
            total=0.0
            total_amount=sum(emp_line.amount for emp_line in mission.employee_ids)
            total_service=sum(service_line.amount for service_line in mission.service_ids)

            mission.total_amount=total_amount
            mission.total_service=total_service
            mission.total=total_amount+total_service

    @api.depends('total')
    def _compute_to_pay(self):
        for mission in self:
            if mission.total > 0:
                mission.to_pay=True
            else:
                mission.to_pay=False

    @api.onchange('mission_categ_id')
    def _onchange_mission_categ_id(self):
        if self.mission_categ_id:
            if not self.name:
                self.name = self.mission_categ_id.name or ''
            if self.mission_categ_id.partner_id:
                self.partner_id = self.mission_categ_id.partner_id.id

    @api.multi
    def unlink(self):
        for mission in self:
            if mission.state not in ('draft', 'cancel'):
                raise UserError(_('You cannot delete an Mission which is not draft or cancelled.'))
        return super(HrMission, self).unlink()

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {}, name=_("%s (Copy)") % self.name)
        return super(HrMission, self).copy(default=default)

    @api.constrains('start_date', 'end_date')
    def _check_date_validity(self):
        """ verifies if start_date is earlier than end_date. """
        for mission in self:
            if mission.start_date and mission.end_date:
                if mission.end_date < mission.start_date:
                    raise ValidationError(_('End Date cannot be earlier than Start Date.'))

    @api.multi
    def action_cancel_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        for rec in self:
            for line in rec.employee_ids:
                line._create_resource_leave()
        self.write({'state': 'approve'})

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        for rec in self:
            for line in rec.employee_ids:
                line._remove_resource_leave()
        self.write({'state': 'cancel'})

    @api.multi
    def action_transfer(self):
        voucher_obj=self.env['account.voucher']
        voucher_line_obj=self.env['account.voucher.line']
        for mission in self:
            employee=self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            voucher = {
                'employee_id': employee.id,
                'department_id': employee.department_id.id,
                'voucher_type': 'purchase',
                'journal_id':mission.mission_categ_id.journal_id.id,
            }
            voucher_id=voucher_obj.create(voucher)
            for emp_line in mission.employee_ids:
                voucher_emp_line={}
                voucher_emp_line['voucher_id'] = voucher_id.id
                voucher_emp_line['name'] = mission.mission_categ_id.name
                voucher_emp_line['product_id'] = mission.mission_categ_id.id
                voucher_emp_line['account_id'] = mission.mission_categ_id.property_account_expense_id.id
                voucher_emp_line['quantity'] = 1
                voucher_emp_line['price_unit'] = emp_line.amount
                voucher_emp_line['partner_id'] = mission.partner_id.id
                voucher_emp_line['account_analytic_id'] = mission.account_analytic_id.id
                voucher_line_obj.create(voucher_emp_line)

            for service_line in mission.service_ids:
                voucher_service_line={}
                voucher_service_line['voucher_id'] = voucher_id.id
                voucher_service_line['name'] = service_line.name
                voucher_service_line['product_id'] = service_line.product_id and service_line.product_id.id or mission.mission_categ_id.id
                voucher_service_line['account_id'] = mission.mission_categ_id.property_account_expense_id.id
                voucher_service_line['quantity'] = 1
                voucher_service_line['price_unit'] = service_line.amount
                voucher_service_line['partner_id'] = service_line.partner_id and service_line.partner_id.id or mission.partner_id.id
                voucher_service_line['account_analytic_id'] = mission.account_analytic_id.id
                voucher_line_obj.create(voucher_service_line)

            voucher_id.write({'state': 'complete'})

        self.write({'state': 'done','voucher_id': voucher_id.id})

class HrMissionEmployee(models.Model):

    _name = "hr.mission.employee"

    mission_id = fields.Many2one('hr.mission', string="Mission")
    employee_id = fields.Many2one('hr.employee', string="Employee",required=True)
    start_date= fields.Datetime('Start Date',required=True)
    end_date= fields.Datetime('End Date',required=True)
    hour=fields.Float(string='Hours')
    hour_wage=fields.Float(string='Hour Wage')
    day=fields.Float(string='Days')
    day_wage=fields.Float(string='Days Wage')
    amount=fields.Float(string='Amount',compute='_compute_amount', digits=dp.get_precision('Account'))

    @api.multi
    def _create_resource_leave(self):
        """ This method will create entry in resource calendar leave object at the time of mission validated """
        for mission in self:
            mission_type = mission.mission_id.mission_categ_id.mission_type == 'internal' and 'in_mission' or 'out_mission'
            self.env['resource.calendar.leaves'].create({
                'name': mission.mission_id.name,
                'type':mission_type,
                'date_from': mission.start_date,
                'date_to': mission.end_date,
                'resource_id': mission.employee_id.resource_id.id,
                'reference': 'hr.mission.employee' + ',' + str(self.id),
            })
        return True

    @api.multi
    def _remove_resource_leave(self):
        """ This method will create entry in resource calendar leave object at the time of holidays cancel/removed """
        'model.name,id'
        return self.env['resource.calendar.leaves'].search([('reference', '=', 'hr.mission.employee' + ',' + str(self.id))]).unlink()

    @api.depends('hour', 'hour_wage','day', 'day_wage')
    def _compute_amount(self):
        for line in self:
            if line.mission_id.time_type == 'hour':
                line.amount = line.hour * line.hour_wage
            else:
                line.amount = line.day * line.day_wage


    @api.multi
    @api.constrains('start_date','end_date')
    def _date_check(self):
        for line in self:
            if line.start_date < line.mission_id.start_date or line.end_date > line.mission_id.end_date:
                raise ValidationError(_("The period of lines must be within the period of Mission"))

    @api.model
    def get_contract(self, employee, date_from, date_to):
        """
        @param employee: recordset of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the contracts for the given employee that need to be considered for the given dates
        """
        # a contract is valid if it ends between the given dates
        clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False), ('date_end', '>=', date_to)]
        clause_final = [('employee_id', '=', employee.id), ('state', '=', 'open'), '|', '|'] + clause_1 + clause_2 + clause_3
        return self.env['hr.contract'].search(clause_final).ids

    def _get_number_of_hours(self, start_date, end_date, employee_id):
        from_dt = fields.Datetime.from_string(start_date)
        to_dt = fields.Datetime.from_string(end_date)
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            days = employee.get_work_days_count(from_dt, to_dt)
            days_seconds= days * 86400
            return round(float(days_seconds)/ 3600,2)

        time_delta = to_dt - from_dt
        days_seconds=time_delta.days *86400
        return round((days_seconds+float(time_delta.seconds))/ 3600,2)

    def _get_number_of_days(self, start_date, end_date, employee_id):
        from_dt = fields.Datetime.from_string(start_date)
        to_dt = fields.Datetime.from_string(end_date)
        days = 0
        date_from=from_dt.date()
        date_to=to_dt.date()
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            days = employee.get_work_days_count(from_dt, to_dt)
        return days

    @api.onchange('start_date','employee_id')
    def _onchange_start_date(self):
        self.hour = 0
        self.day =0
        start_date = self.start_date
        end_date = self.end_date
        if (end_date and start_date) and (start_date <= end_date):
            if self.mission_id.time_type == 'hour':
                self.hour = self._get_number_of_hours(start_date, end_date, self.employee_id.id)
            else:
                self.day = self._get_number_of_days(start_date, end_date, self.employee_id.id)

    @api.onchange('end_date','employee_id')
    def _onchange_end_date(self):
        self.hour = 0
        self.day =0
        start_date = self.start_date
        end_date = self.end_date
        if (end_date and start_date) and (start_date <= end_date):
            if self.mission_id.time_type == 'hour':
                self.hour = self._get_number_of_hours(start_date, end_date, self.employee_id.id)
            else:
                self.day = self._get_number_of_days(start_date, end_date, self.employee_id.id)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        values = {}
        values['hour_wage']=self.mission_id.mission_categ_id.standard_price
        values['day_wage']=self.mission_id.mission_categ_id.standard_price
        contract_ids = self.get_contract(self.employee_id, self.start_date, self.end_date)
        if contract_ids:
            contract = self.env['hr.contract'].browse(contract_ids[0])
            struct = contract.level_id
            for line in self.mission_id.mission_categ_id.line_ids:
                if struct == line.struct_id:
                    if self.mission_id.mission_categ_id.time_type == 'hour':
                        values['hour_wage']=line.amount
                    else:
                        values['day_wage']=line.amount
        return {'value': values}


class HrMissionService(models.Model):

    _name = "hr.mission.service"

    mission_id = fields.Many2one('hr.mission', string="Mission")
    name = fields.Char('Name',required=True)
    product_id = fields.Many2one('product.product', string='Product/Service')
    amount=fields.Float(string='Amount', digits=dp.get_precision('Account'))
    partner_id = fields.Many2one('res.partner',string="Partner")

    @api.onchange('product_id')
    def product_id_change(self):
        values = {}
        company=self.mission_id.company_id
        if self.product_id:
            values['name']= self.product_id.partner_ref
            values['amount'] = self.product_id.standard_price
            if self.product_id.description_purchase:
                values['name'] += '\n' + self.product_id.description_purchase
        return {'value': values}

class HrEmployee(models.Model):

    _inherit = "hr.employee"

    missions_ids=fields.One2many('hr.mission.employee','employee_id', string="Employee Missions") 





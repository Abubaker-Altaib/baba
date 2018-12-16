# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_
from odoo.exceptions import ValidationError
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta, MO
import math

class HolidaysType(models.Model):
    _inherit = "hr.holidays.status"

    code = fields.Char(string="Code", required=True)
    type = fields.Selection([
        ('holiday','Holiday') ,
        ('permit','Permit')], string='Type', default ='holiday', required=True)
    period = fields.Selection([
        ('once','Once') ,
        ('weekly','Weekly') ,
        ('monthly','Monthly') ,
        ('yearly','Yearly') ,
        ('frequency','Frequency')], string="Periodical Leave" , default='yearly', required=True)
    frequency = fields.Integer(string="Frequency")
    days = fields.Float(string="Number Days/hours", required=True)
    max = fields.Float(string="Maximum Days/hours", required=True)
    min = fields.Float(string="Minimum Days/hours", required=True)
    request_time = fields.Float(string="Request Time", required=True)
    payslip_type = fields.Selection([
        ('paid','Paid') ,
        ('unpaid','Unpaid') ,
        ('percentage','Percentage') ,
        ('addition','Addition') ,
        ('exclusion','Exclusion') ] ,string = "Payslip Type" , default="paid", required=True)
    rule_ids = fields.Many2many('hr.salary.rule',string = "Rules")
    required_certificate = fields.Boolean(string="Required Certificate", required=True)
    required_alternative = fields.Boolean(string="Required Alternative", required=True)
    programming = fields.Boolean(string="Annual Programming", required=True)
    save_leave = fields.Boolean(string="Save Leave")
    include_holi = fields.Boolean(string="Include Official Holidays", default='True')
    gender = fields.Selection([
            ('male', 'Male'),
            ('female', 'Female'),
            ])
    religion = fields.Selection([
            ('muslim', 'Muslim'),
            ('christian', 'Christian'),
            ('other', 'Other')
            ], 'Employee Religion')
    country_id = fields.Many2one(
            'res.country', 'Nationality (Country)')
    category_ids =fields.Many2many("hr.employee.category" ,string="Employee Tag")

    @api.multi
    def get_days(self, employee_id):
        # need to use `dict` constructor to create a dict per id
        result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0, virtual_remaining_leaves=0)) for id in self.ids)
        status = self.search([('id', 'in', self.ids)])
        for statu in status:
            start,end=statu.start_end_date_for_period()
            employee = self.env['hr.employee'].search([('id', '=', employee_id)])
            employee_contract = self.env['hr.contract'].search([('employee_id', '=', employee_id)])
            holidays_add = self.env['hr.holidays'].search([
                ('employee_id', '=', employee_id),
                ('state', 'in', ['confirm','validate1', 'validate']),
                ('holiday_status_id', '=', statu.id),
                ('type', '=','add')
            ])
            if statu.save_leave:
                    holidays_remove = self.env['hr.holidays'].search([
                        ('employee_id', '=', employee_id),
                        ('state', 'in',['confirm', 'validate1', 'validate']),
                        ('holiday_status_id', '=', statu.id),
                        ('type', '=', 'remove')
                    ])
            else:
                    holidays_remove = self.env['hr.holidays'].search([
                        ('employee_id', '=', employee_id),
                        ('state', 'in',['confirm', 'validate1', 'validate']),
                        ('holiday_status_id', '=', statu.id),
                        ('type', '=', 'remove'),
                        ('date_from', '>=', start),
                        ('date_to', '<=', end)
                    ])
            if not holidays_add:
                holidays_t=self.env['hr.holidays']
                holidays_r=self.env['hr.holidays']
                holidays_n=self.env['hr.holidays']
                holidays_s=self.env['hr.holidays']
                holidays_g=self.env['hr.holidays']
                holidays_t.search([
                    ('category_id', 'in', employee.category_ids.ids),
                    ('state', 'in',['confirm', 'validate1', 'validate']),
                    ('distribution', '=',False),
                    ('holiday_status_id', '=', statu.id)    
                ])
                if not holidays_t:
                    holidays_s.search([
                                    ('holiday_type', '=','structure'),
                                    ('struct_id', '=', employee_contract.struct_id.id),
                                    ('state', 'in',['confirm', 'validate1', 'validate']),
                                    ('distribution', '=',False),
                                    ('holiday_status_id', '=', statu.id)
                                    ])
                    if not holidays_s:
                        holidays_g.search([
                                ('holiday_type', '=', 'gender'),
                                ('gender', '=', employee.gender),
                                ('state', 'in',['confirm', 'validate1', 'validate']),
                                ('distribution', '=',False),
                                ('holiday_status_id', '=', statu.id)    
                            ])
                        if not holidays_g:
                            holidays_r.search([
                                ('holiday_type', '=','religion'),
                                ('religion', '=', employee.religion),
                                ('state', 'in',['confirm', 'validate1', 'validate']),
                                ('distribution', '=',False),
                                ('holiday_status_id', '=', statu.id)   
                            ])
                            if not holidays_r:
                                holidays_n.search([
                                    ('holiday_type', '=','nationality'),
                                    ('country_id', '=', employee.country_id.id),
                                    ('state', 'in',['confirm', 'validate1', 'validate']),
                                    ('distribution', '=',False),
                                    ('holiday_status_id', '=', statu.id)  
                            ])
                holidays_d =holidays_t+holidays_r+holidays_g+holidays_n+holidays_s
                holidays_add=holidays_d
            for holiday in holidays_add:
                status_dict = result[holiday.holiday_status_id.id]
                if holiday.state == 'validate':
                    # note: add only validated allocation even for the virtual
                    # count; otherwise pending then refused allocation allow
                    # the employee to create more leaves than possible
                    status_dict['virtual_remaining_leaves'] += holiday.number_of_days_temp
                    status_dict['max_leaves'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] += holiday.number_of_days_temp

            for holiday in holidays_remove:
                status_dict = result[holiday.holiday_status_id.id]
                status_dict['virtual_remaining_leaves'] -= holiday.number_of_days_temp
                if holiday.state == 'validate':
                    status_dict['leaves_taken'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] -= holiday.number_of_days_temp
        return result

    def start_end_date_for_period(self):
        """Return the start and end date for a goal period based on today"""
        today = date.today()
        start_date=today
        end_date=today
        if self.period == 'daily':
            start_date = today
            end_date = start_date
        elif self.period == 'weekly':
            start_date = today + relativedelta(weekday=MO(-1))
            end_date = start_date + timedelta(days=7)
        elif self.period == 'monthly':
            start_date = today.replace(day=1)
            end_date = today + relativedelta(months=1, day=1, days=-1)
        elif self.period == 'yearly':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        return fields.Datetime.to_string(start_date), fields.Datetime.to_string(end_date)

class Holidays(models.Model):
    _inherit = "hr.holidays"

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    distribution = fields.Boolean('Distribution')
    holiday_type = fields.Selection([
        ('employee', 'By Employee'),
        ('category', 'By Employee Tag'),
        ('gender', 'By Employee Gender'),
        ('nationality', 'By Employee Nationality'),
        ('religion', 'By Employee Religion'),
        ('structure', 'By Employee Salary Structure')], string='Allocation Mode', readonly=True, required=True, default='employee',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help='By Employee: Allocation/Request for individual Employee, By Employee Tag: Allocation/Request for group of employees in category')
    country_id = fields.Many2one(
        'res.country', 'Employee Nationality')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], 'Employee Gender',groups="hr.group_hr_user", default="male")
    religion = fields.Selection([
        ('muslim', 'Muslim'),
        ('christian', 'Christian'),
        ('other', 'Other')
        ], 'Employee Religion',default="muslim")
    struct_id= fields.Many2one('hr.payroll.structure',string='Salary Structure')
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, readonly=True,
            states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, default=_default_employee, track_visibility='onchange')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ] ,related='employee_id.gender')
    religion = fields.Selection(related='employee_id.religion')
    country_id = fields.Many2one(related='employee_id.country_id')
    category_ids =fields.Many2many(related='employee_id.category_ids')

    _sql_constraints = [
        ('type_value', "CHECK( (holiday_type='employee' AND employee_id IS NOT NULL) or (holiday_type='category' AND category_id IS NOT NULL) or (holiday_type='gender' AND gender IS NOT NULL) or (holiday_type='religion' AND religion IS NOT NULL) or (holiday_type='nationality' AND country_id IS NOT NULL) or (holiday_type='structure' AND struct_id IS NOT NULL))",
         "The employee or employee category of this request is missing. Please make sure that your user login is linked to an employee."),
        ('date_check2', "CHECK ( (type='add') OR (date_from <= date_to))", "The start date must be anterior to the end date."),
        ('date_check', "CHECK ( number_of_days_temp >= 0 )", "The number of days must be greater than 0."),
        ('holiday_type_status_uniq', 'unique (holiday_type,holiday_status_id)', _('leave type with Mode must be unique.')),
    ]

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        super(Holidays, self)._onchange_employee_id()
        return {'domain': {'holiday_status_id': ['&','&','&','|',('gender', '=', self.employee_id.gender),('gender', '=', False),
                                                    '|',('religion', '=', self.employee_id.religion),('religion', '=', False),
                                                    '|', ('country_id', '=', self.employee_id.country_id.id),('country_id', '=', False),
                                                    '|', ('category_ids', 'in', self.employee_id.category_ids.ids ),('category_ids', '=', False)
                                                        ] }}


    @api.constrains('number_of_days_temp')
    def _check_number_of_days_temp(self):
        if self.type=='remove':
            if self.number_of_days_temp:
                if self.holiday_status_id.max:
                    if self.number_of_days_temp >self.holiday_status_id.max:
                        raise ValidationError(_("days/hours are over allow "))
                if self.holiday_status_id.min:
                    if self.number_of_days_temp<self.holiday_status_id.min:
                        raise ValidationError(_("days/hours are under allow "))

    @api.constrains('holiday_status_id')
    def _check_holiday_status(self):
        if self.holiday_status_id:
            start,end=self.holiday_status_id.start_end_date_for_period()
            if self.holiday_status_id.type=='permit':
                if self.holiday_status_id.frequency:
                    holidays_remove = self.env['hr.holidays'].search([
                        ('employee_id', '=', employee_id),
                        ('state', 'in',['confirm', 'validate1', 'validate']),
                        ('holiday_status_type', '=', 'permit'),
                        ('holiday_status_id', '=', statu.id),
                        ('type', '=', 'remove'),
                        ('date_from', '>=', start),
                        ('date_to', '<=', end)
                    ])
                    if len(holidays_remove)==self.holiday_status_id.frequency:
                        raise ValidationError(_("you Exceeded the permitted number of permissions during this period"))
            if self.holiday_status_id.type=='holiday':
                if self.holiday_status_id.frequency:
                    holidays_remove = self.env['hr.holidays'].search([
                        ('employee_id', '=', employee_id),
                        ('state', 'in',['confirm', 'validate1', 'validate']),
                        ('holiday_status_type', '=', 'holiday'),
                        ('holiday_status_id', '=', statu.id),
                        ('type', '=', 'remove'),
                        ('date_from', '>=', start),
                        ('date_to', '<=', end)
                    ])
                    if len(holidays_remove)==self.holiday_status_id.frequency:
                        raise ValidationError(_("you Exceeded the permitted number of leaves during this period"))




    @api.multi
    def action_validate(self):
        self._check_security_action_validate()
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate1']:
                raise UserError(_('Leave request must be confirmed in order to approve it.'))
            if holiday.state == 'validate1' and not holiday.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                raise UserError(_('Only an HR Manager can apply the second approval on leave requests.'))
            holiday.write({'state': 'validate'})
            if holiday.double_validation:
                holiday.write({'second_approver_id': current_employee.id})
            else:
                holiday.write({'first_approver_id': current_employee.id})
            if holiday.holiday_type == 'employee' and holiday.type == 'remove':
                holiday._validate_leave_request()
            elif holiday.holiday_type == 'category':
                if self.distribution:
                    leaves = self.env['hr.holidays']
                    for employee in holiday.category_id.employee_ids:
                        values = holiday._prepare_create_by_category(employee)
                        leaves += self.with_context(mail_notify_force_send=False).create(values)

                # TODO is it necessary to interleave the calls?
                    leaves.action_approve()
                    if leaves and leaves[0].double_validation:
                        leaves.action_validate()
        return True

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)
        time_delta = to_dt - from_dt
        if self.holiday_status_id:
            if self.holiday_status_id.type=='holiday':
                if self.holiday_status_id.include_holi:
                    time_delta = to_dt - from_dt
                    return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)

                else:
                    return super(Holidays, self)._get_number_of_days(date_from, date_to, employee_id)

                return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
            else:
                days=time_delta.days *86400
                return round((days+float(time_delta.seconds))/ 3600,2)



    @api.onchange('holiday_status_id')
    def _onchange_holiday_status(self):
        """ Update the number_of_days. """
        date_from = self.date_from
        date_to = self.date_to
        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
        else:
            self.number_of_days_temp = 0

            
class Employee(models.Model):
    _inherit = "hr.employee"

    religion = fields.Selection([
        ('muslim', 'Muslim'),
        ('christian', 'Christian'),
        ('other', 'Other')
        ], default="muslim")

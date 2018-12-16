# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
###############################################################################

import time
from odoo.exceptions import ValidationError
from odoo import api, fields, models, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.addons.resource.models.resource import to_naive_utc, to_naive_user_tz, to_tz, float_to_time
import dateutil
import pytz

class hr_action_reason(models.Model):
    _name = 'hr.action.reason'

    name = fields.Char(string='Name', required=True)


# not needed now
# class HrEmployee(models.Model):
#     _inherit = "hr.employee"

#     emp_attendance_no= fields.Integer('Attendance No')
#     work_time=fields.Many2one('resource.calendar',string='Working Time',related='resource_id.calendar_id')
#     device_id = fields.Char(string='Biometric Device ID')

class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def _get_default_attendance_ids(self):
        return [
            (0, 0, {'name': _('Monday Morning'), 'dayofweek': '0', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': _('Monday Evening'), 'dayofweek': '0', 'hour_from': 13, 'hour_to': 17}),
            (0, 0, {'name': _('Tuesday Morning'), 'dayofweek': '1', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': _('Tuesday Evening'), 'dayofweek': '1', 'hour_from': 13, 'hour_to': 17}),
            (0, 0, {'name': _('Wednesday Morning'), 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': _('Wednesday Evening'), 'dayofweek': '2', 'hour_from': 13, 'hour_to': 17}),
            (0, 0, {'name': _('Thursday Morning'), 'dayofweek': '3', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': _('Thursday Evening'), 'dayofweek': '3', 'hour_from': 13, 'hour_to': 17}),
            (0, 0, {'name': _('Friday Morning'), 'dayofweek': '4', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': _('Friday Evening'), 'dayofweek': '4', 'hour_from': 13, 'hour_to': 17})
        ]

    employees_ids = fields.Many2many('hr.employee', string='Employees', required=True)
    working_hours = fields.Float(string='Deutey Hours', required=False, default=8)
    excuse = fields.Float(string='Excuse')
    priority = fields.Integer('Priority', required=True, help="Max priority For Basic calendar")
    include_on_deduction = fields.Boolean(string='Included on Deduction')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    job_id = fields.Many2one('hr.job', 'Job Position')
    category_ids = fields.Many2many('hr.employee.category', string='Tags')
    class_id = fields.Many2one('calendar.classification', 'Classification')
    max_late = fields.Float(string='Max Late Time', required=False, default=3)

    attendance_ids = fields.One2many(
        'resource.calendar.attendance', 'calendar_id', 'Working Time',
        copy=True, default=_get_default_attendance_ids, domain=[('is_expt', '=', False)])

    attendance_ids_expt = fields.One2many(
        'resource.calendar.attendance', 'calendar_id', 'Working Time',
        copy=True, domain=[('is_expt', '=', True)])

    @api.onchange('gender', 'job_id', 'category_ids')
    def _onchange_user(self):
        domain = []
        if self.employees_ids:
            for emp in self.employees_ids:
                emp.work_time = False
        if self.gender:
            domain.append(('gender', '=', self.gender))
        if self.job_id:
            domain.append(('job_id', '=', self.job_id.id))
        if self.category_ids:
            domain.append(('category_ids', 'in', self.category_ids.ids))
        return {'domain': {'employees_ids': domain}}

    # inherit to add exception attendance
    @api.multi
    def _get_day_attendances(self, day_date, start_time, end_time):
        """ Given a day date, return matching attendances. Those can be limited
        by starting and ending time objects. """
        self.ensure_one()
        weekday = day_date.weekday()
        attendances = self.env['resource.calendar.attendance']

        for attendance in self.attendance_ids.filtered(
            lambda att:
                int(att.dayofweek) == weekday and
                not (att.date_from and fields.Date.from_string(att.date_from) > day_date) and
                not (att.date_to and fields.Date.from_string(att.date_to) < day_date)):
            if start_time and float_to_time(attendance.hour_to) < start_time:
                continue
            if end_time and float_to_time(attendance.hour_from) > end_time:
                continue
            attendances |= attendance

        for attendance_expt in self.attendance_ids_expt.filtered(
            lambda att:
                int(att.dayofweek) == weekday and
                not (att.date_from and fields.Date.from_string(att.date_from) > day_date) and
                not (att.date_to and fields.Date.from_string(att.date_to) < day_date)):
            if start_time and float_to_time(attendance_expt.hour_to) < start_time:
                continues
            if end_time and float_to_time(attendance_expt.hour_from) > end_time:
                continue
            attendances |= attendance_expt

        return attendances


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    rest = fields.Float(string='Rest period', help="Rest period within work time.")
    shift = fields.Selection([('morning', 'Morning Shift'), ('evening', 'Evening Shift')], string='Working Shift')
    is_expt = fields.Boolean('Is Exception', default=False)


class HrAttendanceLog(models.Model):
    _name = 'hr.attendance.log'

    action_datetime = fields.Datetime(string='Date', readonly=True,
                             states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True,
                             states={'draft': [('readonly', False)]})
    action = fields.Selection([('check_in', 'Check In'), ('check_out', 'Check Out')], string='Action', readonly=True,
                             states={'draft': [('readonly', False)]})
    attendance_id = fields.Many2one('hr.attendance', string='Attendance Record')
    state = fields.Selection([('draft', 'Draft'), ('requested', 'Requested'), ('approved', 'approved'), ('fetched', 'Fetched'), ('refused', 'Refused'), ('canceled', 'Canceled')], string='State')
    reason = fields.Many2one('hr.action.reason', "Reason", readonly=True,
                             states={'draft': [('readonly', False)]})

    @api.multi
    def request(self):
        self.write({'state': 'requested'})
    
    @api.multi
    def approve(self):
        self.write({'state': 'approved'})
    
    @api.multi
    def refuse(self):
        self.write({'state': 'refused'})
    
    @api.multi
    def cancel(self):
        self.write({'state': 'canceled'})
    
    @api.multi
    def draft(self):
        self.write({'state': 'draft'})

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    check_in = fields.Datetime(string="Check In", default=False, required=False)
    worked_hours = fields.Float(string='Worked Hours', compute=False, readonly=True, store=True,)
    date = fields.Date('Date', required=True, index=1, readonly=True)
    day_log = fields.One2many('hr.attendance.log', 'attendance_id', 'Day Log', readonly=True)
    total_delay = fields.Float('Late', readonly=True)
    diff_from_duety = fields.Float('Deduct Late', readonly=True)
    early_hours = fields.Float('Early Hours', readonly=True)
    late_hours = fields.Float('Late Hours', readonly=True)
    deduction_amount = fields.Float('Deduction Amount', readonly=True)
    department_id = fields.Many2one(related='employee_id.department_id', string='Department', store=True)
    reason = fields.Many2one('hr.action.reason', "Reason", readonly=True,
                             states={'draft': [('readonly', False)]})
    absence_type = fields.Selection(
        [('holiday', 'Holiday'),
         ('excuse', 'Excuse'),
         ('no_delay', 'No Delay'),
         ('delay', 'Delay'),
         ('exceptional', 'Exceptional'),
         ('absent', 'Absent'),
         ('public_holiday', 'Public Holiday'),
         ('training', 'Training'),
         ('mission', 'Mission')],
        'Type', default='absent', readonly=True)
    excuse_seconds = fields.Float('Excuse Seconds', readonly=True)
    comment = fields.Text('Notes')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirmed'),
         ('approve', 'Approved'),
         ('no_delay', 'No delay')],
        'Status', default='draft', required=True, readonly=True)
    active = fields.Boolean('Active', default=True)
    duty_time = fields.Many2one('resource.calendar.attendance', "Working Hour", readonly=True)
    payslip_id = fields.Many2one('hr.payslip', string='Payslips', readonly=True)
    plan_hours = fields.Float('Plan Hours', compute="_get_plan_hours", store=True, readonly=True)

    calendar_leaves_ids = fields.Many2many('resource.calendar.leaves', 'attendance_calendar_leave_rel','attendance_id', 'leave_id',string="Calendar Leaves")

    @api.multi
    def name_get(self):
        result = []
        for attendance in self:
            result.append((attendance.id, _("%(empl_name)s / %(date)s") % {
                'empl_name': attendance.employee_id.name,
                'date': attendance.date,
            }))

        return result

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """overriding the __check_validity function for employee attendance."""
        pass

    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        pass

    @api.multi
    @api.depends('duty_time', 'duty_time.hour_to', 'duty_time.hour_from')
    def _get_plan_hours(self):
        for rec in self:
            if rec.duty_time:
                rec.plan_hours = rec.duty_time.hour_to - rec.duty_time.hour_from

    @api.multi
    def _get_calendars(self, employee, att_date):
        calendars = self.env['resource.calendar']
        employee_calendar_ids = self.env['resource.calendar'].search([])
        for calendar in employee_calendar_ids.filtered(
                lambda ca:
                employee.id in ca.employees_ids.ids and
                not (ca.start_date and fields.Date.from_string(ca.start_date) > att_date) and
                not (ca.end_date and fields.Date.from_string(ca.end_date) < att_date)):
            calendars |= calendar

        if calendars:
            calendars = calendars.sorted(key=lambda x: x.priority, reverse=True)

        return calendars

    @api.multi
    def _get_attendances(self, employee, att_date):
        att_date = str(att_date).split(' ')[0]
        att_date = fields.Date.from_string(att_date)
        attendances = result_attendances = self.env['resource.calendar.attendance']
        calendars = self._get_calendars(employee, att_date)
        for calendar in calendars:
            attendances |= calendar._get_day_attendances(att_date, False, False)

        # get the higher priority attenance in the two shifts

        morning_attendance = attendances.filtered(lambda att: att.shift == 'morning' and att.date_from and att.date_to)
        if morning_attendance:
            morning_attendance = morning_attendance.sorted(key=lambda x: (
                not x.is_expt, (fields.Date.from_string(x.date_to) - fields.Date.from_string(x.date_from)).days))
            result_attendances |= morning_attendance[0]
        if not morning_attendance:
            morning_attendance = attendances.filtered(lambda att: att.shift == 'morning')
            if morning_attendance:
                morning_attendance = morning_attendance.sorted(key=lambda x: x.calendar_id.priority, reverse=True)
                result_attendances |= morning_attendance[0]

        evening_attendance = attendances.filtered(lambda att: att.shift == 'evening' and att.date_from and att.date_to)
        if evening_attendance:
            evening_attendance = evening_attendance.sorted(key=lambda x: (
                not x.is_expt, (fields.Date.from_string(x.date_to) - fields.Date.from_string(x.date_from)).days))
            result_attendances |= evening_attendance[0]
            if not evening_attendance:
                evening_attendance = attendances.filtered(lambda att: att.shift == 'morning')
                if evening_attendance:
                    evening_attendance = evening_attendance.sorted(key=lambda x: x.calendar_id.priority, reverse=True)
                    result_attendances |= evening_attendance[0]

        return result_attendances

    def to_date_time(self, float_time, like):
        """ change float time to date time 
            Arguments:
            `float time `: the time to chang as Ex 8.5 --> 8:30
            `like`: the date time that to be like it as Ex 5/10/2016 09:10:15

            Return:
            date time with the date of like and time of float time 
            5/10/2016 8:30:00
        """
        hours = int(float_time)
        minutes = str((int(str(float_time).split('.')[1]))*60)
        if len(minutes) > 2:
            minutes = minutes[:2]
        if len(minutes) == 1:
            minutes += "0"
        date = str(str(like).split(' ')[0])
        date_time = date+' '+str(hours)+':'+str(minutes)+':00'
        return fields.Datetime.from_string(str(date_time))

    @api.multi
    def create_attendance_record(self, employees_ids, att_date):
        for emp in employees_ids:
            attendance_calendar = self._get_attendances(emp, att_date)
            if attendance_calendar:
                for res in attendance_calendar:
                    basicTrue = self.search(
                        [('date', '=', att_date),
                         ('employee_id', '=', emp.id),
                         ('duty_time', '=', res.id),
                         ('active', '=', False)])
                    basicFalse = self.search(
                        [('date', '=', att_date),
                         ('employee_id', '=', emp.id),
                         ('duty_time', '=', res.id),
                         ('active', '=', True)])
                    recordId = basicTrue + basicFalse
                    if not recordId:
                        recordId = self.create({'employee_id': emp.id, 'date': att_date, 'duty_time': res.id})
                        recordId.record_calculate()
        return True

    @api.multi
    def process_attendance_record(self, start_date, end_date, employees_ids):
        if start_date > end_date:
            raise ValidationError(_('start date must be before end date'))
        if not employees_ids:
            return []
        while start_date <= end_date:
            self.create_attendance_record(employees_ids, start_date)
            start_date += relativedelta(days=1)
        return True

    @api.multi
    def get_duty_order(self, emp, att_date, duty):
        attendance_calendar_obj = self.env['resource.calendar.attendance']
        att_date = str(att_date).split(' ')[0]
        att_date = fields.Date.from_string(att_date)
        attendance_calendar = self._get_attendances(emp, att_date)

        before, after = False, False
        if attendance_calendar:

            if len(attendance_calendar) > 1:
                print("-----------------attendance_calendar", attendance_calendar)
                res = [cal.id for cal in attendance_calendar]
                attendance_calendar_order = attendance_calendar_obj.browse(res).sorted(key=lambda x: x.hour_from)
                print("-----------------attendance_calendar_order", attendance_calendar_order.ids)
                before = attendance_calendar_obj.search(
                    [('hour_to', '<', duty.hour_from),
                     ('id', 'in', attendance_calendar_order.ids)],
                    limit=1)
                after = attendance_calendar_obj.search(
                    [('hour_from', '>', duty.hour_to),
                     ('id', 'in', attendance_calendar_order.ids)],
                    limit=1)
                print("-----------------before,after", before, after)
        return before, after

    def _get_attendance_log(self):
        self.day_log = False
        att_log = self.env['hr.attendance.log']
        start_date = self.date + ' 00:00:00'
        end_date = self.date + ' 23:59:59'
        attendance_log_ids = att_log.search(
            [('employee_id', '=', self.employee_id.id),
             ('action_datetime', '>=', start_date),
             ('action_datetime', '<=', end_date),
             ('state', 'in', ['approved', 'fetched'])])

        attendances = self._get_attendances(self.employee_id, self.date)
        attendances_recs = self.search([('date', '=', self.date), ('duty_time', 'in', attendances.ids)])

        morning_duty = attendances_recs.filtered(lambda x: x.duty_time.shift == 'morning')
        evening_duty = attendances_recs.filtered(lambda x: x.duty_time.shift == 'evening')

        if morning_duty:
            morning_duty = morning_duty[0] or False
            shift_from = self.date + ' ' + str(float_to_time(morning_duty.duty_time.hour_from))
            shift_to = self.date + ' ' + str(float_to_time(morning_duty.duty_time.hour_to))

            shift_from = fields.Datetime.from_string(shift_from)
            shift_to = fields.Datetime.from_string(shift_to)

            if not evening_duty:
                morning_signs = attendance_log_ids
            if evening_duty:
                evening_shift_from = self.date + ' ' + str(float_to_time(evening_duty[0].duty_time.hour_from))
                evening_shift_from = fields.Datetime.from_string(evening_shift_from)

                morning_signs = attendance_log_ids.filtered(lambda x: to_naive_user_tz(fields.Datetime.from_string(x.action_datetime), self.env.user) <= shift_to or (
                    to_naive_user_tz(fields.Datetime.from_string(x.action_datetime), self.env.user) < evening_shift_from and x.action == 'check_out'))
            morning_signs.write({'attendance_id': morning_duty.id})
        if evening_duty:
            evening_duty = evening_duty[0] or False
            shift_from = self.date + ' ' + str(float_to_time(evening_duty.duty_time.hour_from))
            shift_to = self.date + ' ' + str(float_to_time(evening_duty.duty_time.hour_to))

            shift_from = fields.Datetime.from_string(shift_from)
            shift_to = fields.Datetime.from_string(shift_to)

            if not morning_duty:
                evening_signs = attendance_log_ids

            if morning_duty:
                morning_shift_to = self.date + ' ' + str(float_to_time(morning_duty[0].duty_time.hour_to))
                morning_shift_to = fields.Datetime.from_string(morning_shift_to)

                evening_signs = attendance_log_ids.filtered(lambda x: to_naive_user_tz(fields.Datetime.from_string(x.action_datetime), self.env.user) >= shift_from or (
                    to_naive_user_tz(fields.Datetime.from_string(x.action_datetime), self.env.user) > morning_shift_to and x.action == 'chech_in'))
            evening_signs.write({'attendance_id': evening_duty.id})

        return True

    @api.multi
    def _get_calendar_leaves(self):
        calendar_leaves = self.env['resource.calendar.leaves']
        self.calendar_leaves_ids = False

        duty_from = self.date + ' ' + str(float_to_time(self.duty_time.hour_from))
        duty_to = self.date + ' ' + str(float_to_time(self.duty_time.hour_to))
        c_date = self.date + ' 00:00:00'

        duty_from = fields.Datetime.from_string(duty_from)
        duty_to = fields.Datetime.from_string(duty_to)

        duty_from = to_naive_user_tz(duty_from, self.env.user)
        duty_to = to_naive_user_tz(duty_to, self.env.user)
        

        date_leaves = calendar_leaves.search([('resource_id','=',self.employee_id.resource_id.id),('date_from','<=',str(duty_from)),('date_to','>',str(duty_from))])

        date_leaves |= calendar_leaves.search([('resource_id','=',self.employee_id.resource_id.id),('date_from','<',str(duty_to)),('date_to','>=',str(duty_to))])
        
        date_leaves |= calendar_leaves.search([('resource_id','=',self.employee_id.resource_id.id),('date_from','>=',str(duty_from)),('date_to','<=',str(duty_to))])
        self.calendar_leaves_ids = date_leaves.ids

        absence_type = None
        excuse_seconds = 0
        return absence_type, excuse_seconds
    
    @api.multi
    def _set_check_in_out(self):
        signin = signout = False
        self.early_hours = 0.0
        self.late_hours = 0.0
        self.worked_hours = 0.0
        duty_from = self.date + ' ' + str(float_to_time(self.duty_time.hour_from))
        duty_to = self.date + ' ' + str(float_to_time(self.duty_time.hour_to))

        duty_from = fields.Datetime.from_string(duty_from)
        duty_to = fields.Datetime.from_string(duty_to)
        
        self.plan_hours = (duty_to - duty_from).seconds / 3600
        check_in = self.day_log.filtered(lambda log: log.action == 'check_in')
        if check_in:
            signin = min([to_naive_user_tz(fields.Datetime.from_string(
                str(x.action_datetime)), self.env.user) for x in check_in])
            
            if duty_from > signin:
                self.early_hours = (duty_from - signin).seconds / 3600

            signin = to_naive_utc(signin, self.env.user)
            self.check_in = str(signin)
        
        check_out = self.day_log.filtered(lambda log: log.action == 'check_out')
        if check_out:
            signout = max([to_naive_user_tz(fields.Datetime.from_string(
                str(x.action_datetime)), self.env.user) for x in check_out])
            
            if signout > duty_to:
                self.late_hours = (signout > duty_to).seconds / 3600
            
            signout = to_naive_utc(signout, self.env.user)
            self.check_out = str(signout)
        if signin and signout:
            self.worked_hours = (signout - signin).seconds / 3600
    
    @api.multi
    def _get_leaves_durations(self):
        duty_from = self.date + ' ' + str(float_to_time(self.duty_time.hour_from))
        duty_to = self.date + ' ' + str(float_to_time(self.duty_time.hour_to))

        duty_from = fields.Datetime.from_string(duty_from)
        duty_to = fields.Datetime.from_string(duty_to)


        date_leaves_dicts = {}
        date_leaves = self.calendar_leaves_ids.filtered(lambda x : to_naive_user_tz(fields.Datetime.from_string(x.date_from), self.env.user) <= duty_from and to_naive_user_tz(fields.Datetime.from_string(x.date_to), self.env.user) >= duty_to )
        date_leaves_dicts.update({(duty_from,duty_to):x.type for x in date_leaves})

        date_leaves = self.calendar_leaves_ids.filtered(lambda x : to_naive_user_tz(fields.Datetime.from_string(x.date_from), self.env.user) <= duty_from and to_naive_user_tz(fields.Datetime.from_string(x.date_to), self.env.user) < duty_to )
        date_leaves_dicts.update({(duty_from,to_naive_user_tz(fields.Datetime.from_string(x.date_to), self.env.user)):x.type for x in date_leaves})

        date_leaves = self.calendar_leaves_ids.filtered(lambda x : to_naive_user_tz(fields.Datetime.from_string(x.date_from), self.env.user) > duty_from and to_naive_user_tz(fields.Datetime.from_string(x.date_to), self.env.user) < duty_to )
        date_leaves_dicts.update({(to_naive_user_tz(fields.Datetime.from_string(x.date_from), self.env.user),to_naive_user_tz(fields.Datetime.from_string(x.date_to), self.env.user)):x.type for x in date_leaves})

        date_leaves = self.calendar_leaves_ids.filtered(lambda x : to_naive_user_tz(fields.Datetime.from_string(x.date_from), self.env.user) > duty_from and to_naive_user_tz(fields.Datetime.from_string(x.date_to), self.env.user) > duty_to )
        date_leaves_dicts.update({(to_naive_user_tz(fields.Datetime.from_string(x.date_from), self.env.user),duty_to):x.type for x in date_leaves})

        if date_leaves_dicts:
            #get the leave with the most duration
            keys = date_leaves_dicts.keys()
            keys = {(x[1] - x[0]).seconds:x for x in keys}

            #get the max key using diffrence
            max_key = max(keys.keys())

            #get the max key using keys dict
            max_key = keys[max_key]

            #get the max key using date_leaves_dicts dict
            return {max_key : date_leaves_dicts[max_key]}
            
        return {}


    @api.multi
    def _get_late(self):
        signin = signout = False
        duty_from = self.date + ' ' + str(float_to_time(self.duty_time.hour_from))
        duty_to = self.date + ' ' + str(float_to_time(self.duty_time.hour_to))

        duty_from = fields.Datetime.from_string(duty_from)
        duty_to = fields.Datetime.from_string(duty_to)

        excuse = float_to_time(self.duty_time.calendar_id.excuse)
        excuse = excuse.hour * 3600 + excuse.minute * 60 + excuse.second


        max_late = float_to_time(self.duty_time.calendar_id.max_late)
        max_late = max_late.hour * 3600 + max_late.minute * 60 + max_late.second

        

        if self.check_in:
            signin = self.check_in
            signin = fields.Datetime.from_string(signin)
            signin = to_naive_user_tz(signin, self.env.user)

        if self.check_out:
            signout = self.check_out
            signout = fields.Datetime.from_string(signout)
            signout = to_naive_user_tz(signout, self.env.user)
        
        leaves_duration = self._get_leaves_durations()
        
        absence_type = False
        late = 0.0
        diff_from_duety = 0.0
        leave_signin = False
        leave_signout = False

        #there is at least one leave
        if leaves_duration:
            (leave_signin, leave_signout),temp_absence_type  = leaves_duration.popitem()
            if not signin or leave_signin < signin:
                signin = leave_signin
            if not signout or leave_signout > signout:
                signout = leave_signout
        
        if not signin or not signout:
            self.absence_type = 'absent'
            self.total_delay = (duty_to - duty_from).seconds / 3600.0
            self.diff_from_duety = (duty_to - duty_from).seconds / 3600.0
            return
        
        delta = 0.0
        if signin > duty_from:
            delta += (signin - duty_from).seconds
        if duty_to > signout:
            delta += (duty_to - signout).seconds

        if delta > excuse:
            diff_from_duety = delta - excuse
            if diff_from_duety > max_late:
                self.absence_type = 'absent'
                self.total_delay = (duty_to - duty_from).seconds / 3600.0
                self.diff_from_duety = (duty_to - duty_from).seconds / 3600.0
                return
        
        if not absence_type:
            if delta == 0:
                absence_type = 'no_delay'
            if delta > 0:
                absence_type = 'delay'

        self.absence_type = absence_type
        self.total_delay = delta  / 3600.0
        self.diff_from_duety = diff_from_duety / 3600.0
        return


         



    @api.multi
    def record_calculate(self):
        for record in self:
            vals = {
                'absence_type': 'absent',
                'total_delay': record.plan_hours,
                'diff_from_duety': record.plan_hours,
                'worked_hours': 0.0,
                'early_hours': 0.0,
                'late_hours': 0.0,
            }
            absence_type, excuse_seconds = record._get_calendar_leaves()
            if absence_type:
                vals.update({'absence_type': absence_type})
            record._get_attendance_log()
            record._get_calendar_leaves()
            record._set_check_in_out()
            record._get_late()
        return True

    @api.multi
    def reload(self):
        self.record_calculate()
        return True


class CalendarClassification(models.Model):
    _name = 'calendar.classification'

    name = fields.Char(string='Classification Name', required=True)
    calendars_ids = fields.One2many('resource.calendar', 'class_id', 'Working Times', readonly=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
